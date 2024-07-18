from datetime import datetime
import re
import json
import warnings
import jsonpickle
import os
from datoma.utils import region, _get_creds, _create_sign_request_job, _request_skeleton, _download, _list_outputs, _authenticate_user, _convert_local_s3, _upload_files, _transform_colons


class DatomaJob:
    """A class used to represent a job executed on Datoma's infrastructure
    """
    def __init__(self, tool = None, task = None, import_json = None):
        """Initializes a DatomaJob object.

        :param tool: Name of the tool.
        :type tool: str, optional
        :param task: Name of the task.
        :type task: str, optional
        :param import_json: Path to a JSON file with the job information, defaults to None. If None, the job will be created from scratch.
        :type import_json: str, optional
        """
        self.running_at = None
        self.finished_at = None
        if tool is None and task is None and import_json is not None:
            self._import_json(import_json)

        elif tool is not None and task is not None and import_json is None:
            self.tool = tool
            self.task = task
            self.skeleton = self._get_skeleton() 
            self.model = self._get_model()
            self.status = "unsubmitted"
            self.status_timestamp = None
            self.id = None
            self.name = f'{self.tool}_{self.task}_job'
        else:
            raise ValueError("You must specify tool and task or import a JSON file")

    # Request the skeleton for tool : task
    def _get_skeleton(self):
        """Obtains the skeleton for the tool : task, checking if it exists.

        :raises ValueError: If the skeleton does not exist.
        :return: The skeleton for the tool : task.
        :rtype: dict
        """
        response = _request_skeleton(self.tool, self.task)
        if response.status_code != 200:
            raise ValueError(f"Failed to retrieve skeleton. Make sure that {self.tool} : {self.task} exists. Error code: {response.status_code}")
        skeleton = json.loads(response.text)
        return skeleton
    
    def __describe_skeleton(self):
        """Not implemented yet.
        """
        #TODO: work the JSON skeleton and ask the user for the values
        skeleton = self.skeleton
        for i in range(len(skeleton['parameters'])):
            print(f"{i+1}: {skeleton['parameters'][i]['label']}")    # print the name of the parameter
            for j in range(len(skeleton['parameters'][i]['parameters'])):
                print(f"\t{j+1}: {skeleton['parameters'][i]['parameters'][j]['label']} key: {skeleton['parameters'][i]['parameters'][j]['key']}")    #TODO: some don't have to be shown unless some prior parameter is selected
                #if enable is there we have to check what triggers it
                if 'enable' in skeleton['parameters'][i]['parameters'][j]:
                    print(f"\t\t enable field! depends on {skeleton['parameters'][i]['parameters'][j]['enable']}")    #TODO: some don't have to be shown unless some prior parameter is selected

    def _get_model(self):
        """Obtains the model for the tool : task based on the skeleton.

        :return: The model for the tool : task.
        :rtype: dict
        """
        skeleton = self.skeleton
        model = {"params":{}, "input":{}}   
        if skeleton.get("parameters") is not None:
            for i in range(len(skeleton['parameters'])):
                for j in range(len(skeleton['parameters'][i]['parameters'])):
                    model['params'].update({skeleton['parameters'][i]['parameters'][j]['key'] : skeleton['parameters'][i]['parameters'][j]['model']})
        for i in range(len(skeleton['inputs'])):
            model['input'].update({skeleton['inputs'][i]['key'] : skeleton['inputs'][i]['model']})
        return model
    

    def _create_json(self):
        """Generates the JSON to be sent to Datoma's infrastructure.

        :return: JSON string.
        :rtype: bytes
        """
        json_dict = {}
        params = self.model.get("params", {})
        transformed_params = _transform_colons(params)
        json_dict["params"] = transformed_params
        json_dict["input"] = self.model["input"]
        json_dict["name"] = self.name
        if self.model.get("resources") is not None:
            json_dict["resources"] = self.model["resources"]
        return json.dumps(json_dict)

    def submit(self, job_name = None, get_credits = False, resources = None):
        """Submits the job to Datoma's infrastructure.

        :param job_name: Name of the job, defaults to None. If None, the name will be tool_task_job.
        :type job_name: str, optional
        :param get_credits: If True, the user will be shown the amount of credits expended to execute the Job, will need confirmation, defaults to False.
        :type get_credits: bool, optional
        :param resources: Resources to be used by the job (only works if user has developer access at login) The keys must be 'vcpu' and 'memory' (in MiB), the values are to be specified as integers. defaults to None.
        :type resources: dict, optional
        """
        if get_credits:
            finished = False # Controls the loop in case the user does not input a valid answer
            response = _get_creds(_authenticate_user(region, 'execute-api'), job_name, self.tool, self.task, self.model['input'], self.model['params'])
            if response.status_code < 200 or response.status_code >= 300:
                if response.status_code == 403:
                    raise Exception("The generated output files would exceed your storage limit. Please delete some files to free up space.")
                else:
                    raise Exception(f"There has been an error with the request to Datoma. Error code: {response.status_code}. {response.text}")

            data = json.loads(response.text)
            credits = data.get('cost', None)
            while not finished:
                if credits == 1:
                    agreement = input(f"This Job execution will cost you {credits} credit. Do you want to proceed? (Y/N)")
                else:
                    agreement = input(f"This Job execution will cost you {credits} credits. Do you want to proceed? (Y/N)")
                if agreement.lower() == 'y' or agreement.lower() == 'yes' or agreement.lower() == 'n' or agreement.lower() == 'no':
                    if agreement.lower() == 'n' or agreement.lower() == 'no':
                        print("Job not submitted")
                        return
                    finished = True
                else:
                    print("Please input a valid answer")
                    
        self.model['type'] = self.task
        if job_name is not None:
            if "/" in job_name:
                raise ValueError("Job name cannot contain '/'")
            self.name = job_name
        if resources is not None:
            self.model['resources'] = resources
        body = self._create_json()
        response = _create_sign_request_job(_authenticate_user(region, 'execute-api'), self.tool, self.task, body)
        if response.status_code < 200 or response.status_code >= 300:
            if response.status_code == 403:
                raise Exception("The generated output files would exceed your storage limit. Please delete some files to free up space.")
            else:
                raise Exception(f"There has been an error with the request to Datoma. Error code: {response.status_code}. {response.text}")

        print("Your request to Datoma was sent with a status code: "+str(response.status_code)+"\n")
        data = json.loads(response.text)
        self.id = data.get('id', None)
        self.status = "submitted"
        self.status_timestamp =  datetime.timestamp(datetime.now())
        print(f"Job {self.id} has been submitted at {self.status_timestamp}")

    def __update_status(self, AppSyncClient):
        """Not in use.

        :param AppSyncClient: AppSyncClient object.
        :type AppSyncClient: AppSyncClient
        """
        check_status = AppSyncClient.subscribe_to_job(self.id)
        if self.status != check_status["status"]:
            print(f"Job {self.id} changed status to {check_status['status']} at {check_status['updatedAt']}")
            self.status_timestamp =  check_status['updatedAt']
        self.status = check_status["status"]

    def set_params(self, params_dictionary):
        """Sets the parameters of the job.

        :param params_dictionary: Dictionary with specified values for each parameter.
        :type params_dictionary: dict
        """
        for key in params_dictionary:
            if key not in self.model['params']:
                warnings.warn(f"Parameter {key} is not in the model")
            else: self.model['params'][key] = params_dictionary[key]

    def set_input(self, input_dictionary, preserve_name = False):
        """Sets the input of the job. If the input is a local file, it will be uploaded to S3 (if it isn't already there). You can also specify a directory.


        :param input_dictionary: Dictionary with specified files/folders for each input.
        :type input_dictionary: dict
        :param preserve_name: If True, the name of the file will be preserved in S3, defaults to False.
        :type preserve_name: bool, optional
        """
        check_to_upload = []
        for key in input_dictionary:
            allows_roi = False
            for glo in self.skeleton["inputs"]:
                if glo["key"] == key:
                    if glo.get("useROI") != None:
                        allows_roi = glo["useROI"]
                    break
            for file in input_dictionary[key]:
                if type(file) is str:
                    if re.search(r'^s3://', file) is not None:
                        self.model['input'][key].extend([file])
                        check_to_upload.append([file, ''])
                    elif os.path.isdir(file):
                        #list recursively the files in the directory
                        inner_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(file) for f in filenames]
                        to_upload, dir_str = _convert_local_s3(inner_files, preserve_name, file)
                        self.model['input'][key].extend([dir_str])
                        for file_tu in to_upload:
                            check_to_upload.append(file_tu)
                        

                    else:
                        to_upload = _convert_local_s3([file], preserve_name)
                        self.model['input'][key].extend([to_upload[0][1]])
                        check_to_upload.append(to_upload[0])
                if type(file) is dict:
                    file_roi = 'file'
                    if file.get('roi') != None:
                        if not allows_roi:
                            raise ValueError(f"Input {key} does not allow ROI")
                        else: 
                            file_roi = 'roi'
                    if re.search(r'^s3://', file[file_roi]) is not None:
                        self.model['input'][key].extend([file])
                        check_to_upload.append([file[file_roi], ''])
                    elif os.path.isdir(file):
                        #list recursively the files in the directory
                        inner_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(file) for f in filenames]
                        to_upload, dir_str = _convert_local_s3(inner_files, preserve_name, file)
                        self.model['input'][key].extend([dir_str])
                        for file_tu in to_upload:
                            check_to_upload.append(file_tu)
                    else:
                        to_upload = _convert_local_s3([file[file_roi]], preserve_name)
                        self.model['input'][key].extend([{file_roi: to_upload[0][1]}])
                        check_to_upload.append(to_upload[0])

        _upload_files(check_to_upload)

    async def list_outputs(self, regex = None, job_list = None):
        """Lists the output files of the job filtered (if specified) by a regex. First waits until the job is finished. Must be called with await.

        :param regex: A regex to filter the output, defaults to None.
        :type regex: str, optional
        :param job_list: List of jobs to get start and finsih timestamps, defaults to None.
        :type job_list: list, optional
        :return: A list of the outputs of the job, size in Bytes.
        :rtype: list, int
        """
        return(await _list_outputs(self, regex, job_list))

    async def download(self, output_path = None):
        """Downloads the output files of the job. First waits until the job is finished. Must be called with await.

        :param output_path: The path to download the files generated by the job, defaults to None. If None, the files will be downloaded to the current directory, generating a subfolder.
        :type output_path: str, optional
        """
        await _download(self, output_path)

    def export_json(self, path = None):
        """Exports the job information to a JSON file.

        :param path: Path to export the information to, defaults to None
        :type path: str, optional
        :raises FileNotFoundError: Raises an error if the file could not be created.
        """
        if path is None:
            path = f"{self.name}.json"
        path = os.path.abspath(path)

        try:
            with open(path, 'w') as outfile:
                json.dump(jsonpickle.encode(self), outfile)
            outfile.close()
            print(f"Job information exported to {path}")
        except:
            raise FileNotFoundError(f"File {path} could not be created")
    
    def _import_json(self, path):
        """Imports a JSON file with the job information.

        :param path: Path to the JSON file.
        :type path: str
        :raises Exception: Raises an error if the object inside the JSON file is not a DatomaJob.
        :raises FileNotFoundError: Raises an error if the file does not exist or is not a valid JSON file.
        """
        try:
            path = os.path.abspath(path)
            with open(path, 'r') as outfile:
                json_file = jsonpickle.decode(json.load(outfile))
                if 'DatomaJob' not in str(type(json_file)):
                    raise Exception("The object inside the imported JSON file is not a DatomaJob")
                self.model = json_file.model
                self.tool = json_file.tool
                self.task = json_file.task
                self.skeleton = json_file.skeleton
                self.status = "unsubmitted"
                self.id = None
                self.name = json_file.name
            outfile.close()
        except:
            raise FileNotFoundError(f"File {path} does not exist or is not a valid JSON file")
