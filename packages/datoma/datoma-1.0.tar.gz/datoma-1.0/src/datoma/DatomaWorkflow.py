from datetime import datetime
import json
import os
import re
import jsonpickle
from datoma.DatomaJob import DatomaJob
from datoma.utils import region, _get_creds, _download, _list_outputs, _create_sign_request_official_workflow, _create_sign_request_custom_workflow, _authenticate_user, _request_workflow, _read_yaml, _convert_local_s3, _upload_files, _get_uuid, _transform_colons

class DatomaWorkflow:
    """This class represents a workflow to be executed on Datoma's infrastructure.
    """
    def __init__(self, path_yaml = None, path_json = None, official_name = None, import_json = None):
        """Initializes a DatomaWorkflow object.

        :param path_yaml: Path where the .yml file is located, defaults to None.
        :type path_yaml: str, optional
        :param path_json: Path where the .json file is located, defaults to None.
        :type path_json: str, optional
        :param official_name: Official name of the workflow, defaults to None.
        :type official_name: str, optional
        :param import_json: Path to a JSON file with the workflow information, defaults to None.
        :type import_json: str, optional
        :raises Exception: If two or more parameters are specified at the same time, besides path_yaml and path_json.
        :raises FileNotFoundError: If the file could not be found.
        :raises Exception: If the official workflow could not be retrieved.        
        """
        self.status = "unsubmitted"
        self.status_timestamp = None
        self.running_at = None
        self.finished_at = None
        self.id = None

        self.jobs = {}
        self.layout_file = None
        self.json_file = json.dumps("{}")
        self.status_timestamp = None
        self.name = None
        self.uuid = None
        self.path_yaml = path_yaml
        self.path_json = path_json
        self.official_name = official_name
        self.is_official = False
        self.global_input = {}
        self.global_parameters = {}
        if (self.path_yaml != None and self.official_name != None and import_json != None) or (self.path_yaml != None and self.official_name != None and import_json == None)  or (self.path_yaml != None and self.official_name == None and import_json != None) or (self.path_yaml == None and self.official_name != None and import_json != None):
            raise Exception("You can't specify two or more parameters at the same time, besides path_yaml and path_json.")
        elif import_json != None:
            self._import_json(import_json)
        elif self.path_yaml != None:
            if not os.path.isabs(self.path_yaml):
                self.path_yaml = os.path.abspath(self.path_yaml)
                if not os.path.isfile(self.path_yaml):
                    raise FileNotFoundError(f"File {self.path_yaml} not found.")
            self.yaml_file = _read_yaml(self.path_yaml)

            if self.path_json != None:
                if not os.path.isabs(self.path_json):
                    self.path_json = os.path.abspath(self.path_json)
                    if not os.path.isfile(self.path_json):
                        raise FileNotFoundError(f"File {self.path_json} not found.")
                self.json_file = json.loads(open(self.path_json, 'r').read())
            self._prepare_jobs()
        elif self.official_name != None:
            request = _request_workflow(self.official_name)
            if request.status_code == 200:
                self.layout_file = json.loads(request.text)
                self.is_official = True
                self._prepare_jobs()
            else:
                raise Exception(f"Error retrieving workflow, check the official workflow's name: {request.status_code}")
        else:   # self created workflow without a base yml file
            self.yaml_file = {"workflow":[]}



    def _register_workflow(self):
        """Registers the ephemeral workflow on Datoma's infrastructure.

        :raises Exception: If the function is called for an official workflow.
        :raises Exception: If there is an error registering the workflow.
        """
        if self.is_official:
            raise Exception("You can't register an official workflow")
        data_str = str(self.yaml_file)
        bytes_data_yaml = data_str.encode('utf-8')

        data_str = str(self.json_file)
        bytes_data_json = data_str.encode('utf-8')

        req = _create_sign_request_custom_workflow(_authenticate_user(region, 'execute-api'), bytes_data_yaml, bytes_data_json)
        if req.status_code < 200 or req.status_code >= 300:
            if req.status_code == 403:
                raise Exception("The generated output files would exceed your storage limit. Please delete some files to free up space.")
            else:
                raise Exception(f"There has been an error with the request to Datoma. Error code: {req.status_code}. {req.text}")
        else :
            self.status = "registered"
            data = json.loads(req.text)
            self.uuid = data.get('id', None)

    def _create_layout_file(self):
        """Creates the layout file to be used by _prepare_jobs.
        """
        self.layout_file = {"steps":[]}
        for job in self.yaml_file["workflow"]:
            self.layout_file["steps"].append({"key":job["id"], "name":job["name"], "tool":job["tool"], "task":job["task"]})
            if job.get("input_mapping") != None:
                hidden_inputs = []
                for par in job["input_mapping"]:
                    hidden_inputs.append(par)
                self.layout_file["steps"][-1]["hiddenInputs"] = hidden_inputs
            if job.get("parameter_mapping") != None:
                linked_global_parameters = {}
                for par in job["parameter_mapping"]:
                    linked_global_parameters[par] = job["parameter_mapping"][par]
                self.layout_file["steps"][-1]["linkedGlobalParameters"] = linked_global_parameters
        if "globalInputs" in self.json_file:
            self.layout_file["globalInputs"] = self.json_file["globalInputs"]
        if "globalParameters" in self.json_file:
            self.layout_file["globalParameters"] = self.json_file["globalParameters"]
        if "parameterOverrides" in self.json_file:
            self.layout_file["parameterOverrides"] = self.json_file["parameterOverrides"]
            

    def _prepare_jobs(self):
        """Prepares the jobs of the workflow based on the official workflow or the specified JSON and YAML files.

        """
        if not self.is_official:
            self._create_layout_file()
        for job in self.layout_file["steps"]:
            new_job = DatomaJob(job["tool"], job["task"])
            new_job.id = job["key"]
            new_job.name = job["name"]
            if job.get("hiddenInputs") != None:
                for hid in job["hiddenInputs"]:
                    del new_job.model["input"][hid] #delete hidden inputs
            if job.get("linkedGlobalParameters") != None:
                for lin in job["linkedGlobalParameters"]:   #for each linked global parameter (job)
                    if job["linkedGlobalParameters"][lin] in self.global_parameters:
                        # Check if the linked global parameter is already in the global_parameters dictionary
                        if job["key"] in self.global_parameters[job["linkedGlobalParameters"][lin]]:
                            # If the key is already in the list for the linked global parameter
                            self.global_parameters[job["linkedGlobalParameters"][lin]][job["key"]].append(lin)
                        else:
                            # If the key is not already in the list for the linked global parameter
                            self.global_parameters[job["linkedGlobalParameters"][lin]][job["key"]] = [lin]
                            # Create a new list with 'lin' as its element for the key
                    else:
                        # If the linked global parameter is not in the global_parameters dictionary
                        self.global_parameters[job["linkedGlobalParameters"][lin]] = {job["key"]: [lin]}
                        # Create a new dictionary entry with 'lin' as the value for the key 'job["key"]'
                    for glo_par in self.layout_file["globalParameters"]: #for each global parameter (global)
                        if glo_par["parameters"][0]["key"] == job["linkedGlobalParameters"][lin]:
                            new_job.model["params"][lin] = glo_par["parameters"][0]["model"]
                            break
            self.jobs[new_job.id] = new_job

        if self.layout_file.get("parameterOverrides") != None:
            for par in self.layout_file["parameterOverrides"]:
                self.jobs[par["stepKey"]].model["params"][par["parameterKey"]] = par["parameterModel"]
        if self.layout_file.get("globalInputs") != None:
            for glo in self.layout_file["globalInputs"]:
                self.global_input[glo["key"]] = glo["model"]

    def set_global_params(self, dictionary):
        """Changes the value to the specified global parameters of the workflow.

        :param dictionary: Dictionary with the global parameters to be changed and the value to change.
        :type dictionary: dict
        """
        for gl_param in dictionary:
            if gl_param in self.global_parameters:
                for job in self.global_parameters[gl_param]:
                    dict_to_add = {}
                    for param in self.global_parameters[gl_param][job]:
                        dict_to_add[param] = dictionary[gl_param]
                    self.set_params(job, dict_to_add, True)

    def set_params(self, job_id, params_dictionary, called_from_global = False):
        """Sets the parameters of a job.

        :param job_id: ID of the job.
        :type job_id: str
        :param params_dictionary: Dictionary with specified parameters for each job.
        :type params_dictionary: dict
        :param called_from_global: If the function was called from set_global_params, defaults to False.
        :type called_from_global: bool, optional
        :raises Exception: If the specified job ID is not found.
        """
        if not called_from_global:
            for param in params_dictionary:
                for gl_param in self.global_parameters:
                    if job_id in self.global_parameters[gl_param]:
                        if param in self.global_parameters[gl_param][job_id]:
                            print(f'Warning: You are modifying {param}, a global parameter')
        try: self.jobs[job_id].set_params(params_dictionary)
        except: raise Exception("Job not found")

    def set_input(self, job_id, input_dictionary, preserve_name = False):
        """Sets the input of a job. You can specify files or directories.

        :param job_id: ID of the job.
        :type job_id: str
        :param input_dictionary: Dictionary with specified files/directories for each input.
        :type input_dictionary: dict
        :param preserve_name: Option to preserve the local file name, necessary for some workflows. Defaults to False
        :type preserve_name: bool, optional
        :raises Exception: If the specified job ID is not found.
        """
        try: self.jobs[job_id].set_input(input_dictionary, preserve_name)
        except: raise Exception("Job not found")

    def set_global_input(self, input_dictionary, preserve_name = False):
        """Sets the global input of the workflow. You can specify files or directories.

        :param input_dictionary: Dictionary with specified files/directories for each input.
        :type input_dictionary: dict
        :param preserve_name: Option to preserve the local file name, necessary for some workflows. Defaults to False.
        :type preserve_name: bool, optional
        :raises Exception: If a specific global input is not found.
        :raises ValueError: If the global input field is not found on the workflow.
        """
        if self.layout_file.get("globalInputs") != None:
            check_to_upload = []
            for key in input_dictionary:
                allows_roi = False
                success = False
                for glo in self.layout_file["globalInputs"]:
                    if glo["key"] == key:
                        self.global_input[key] = input_dictionary[key]
                        if glo.get("useROI") != None:
                            allows_roi = glo["useROI"]
                        success = True
                        break
                if not success:
                    raise Exception(f"Global input {key} not found")
                for input in range(len(input_dictionary[key])):
                    if type(input_dictionary[key][input]) == str:
                        if os.path.isdir(input_dictionary[key][input]):
                                #list recursively the files in the directory
                                inner_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_dictionary[key][input]) for f in filenames]
                                to_upload, dir_str = _convert_local_s3(inner_files, preserve_name, input_dictionary[key][input])
                                input_dictionary[key][input] =dir_str
                                for file_tu in to_upload:
                                    check_to_upload.append(file_tu)
                    else:
                        for file in input_dictionary[key][input]:
                            if input_dictionary[key][input].get('roi') != None and not allows_roi:
                                raise Exception(f"ROI not supported for global input '{key}'")
                            if re.search(r'^s3://', input_dictionary[key][input][file]) is not None:
                                check_to_upload.append([input_dictionary[key][input][file], ''])
                            elif os.path.isdir(input_dictionary[key][input][file]):
                                #list recursively the files in the directory
                                inner_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_dictionary[key][input][file]) for f in filenames]
                                to_upload, dir_str = _convert_local_s3(inner_files, preserve_name, input_dictionary[key][input][file])
                                input_dictionary[key][input][file] =[dir_str]
                                for file_tu in to_upload:
                                    check_to_upload.append(file_tu)
                            else:
                                to_upload = _convert_local_s3([input_dictionary[key][input][file]], preserve_name)
                                input_dictionary[key][input][file] = to_upload[0][1]
                                check_to_upload.append(to_upload[0])
            _upload_files(check_to_upload)
        else:
            raise ValueError("Global input not found")
    
    def add_job(self, job_id, job):
        """Adds a job to the workflow.

        :param job_id: ID of the job.
        :type job_id: str
        :param job: Job to be added.
        :type job: DatomaJob
        :raises Exception: If the workflow is official.
        """
        if self.is_official:
            raise Exception("You can't add jobs to an official workflow")
        self.yaml_file["workflow"].append({"id":job_id, "name":job.name, "tool":job.tool, "task":job.task})
        self.jobs[job_id] = job
        
    def _create_json(self):
        """Creates the JSON file to be sent to Datoma's infrastructure.

        :return: JSON string.
        :rtype: bytes
        """
        json_dict = {}
        json_dict["params"] = {}
        json_dict["input"] = {}
        json_dict["globalInput"] = {}
        json_dict["name"] = self.name
        for job in self.jobs:
            params = self.jobs[job].model.get("params", {})
            transformed_params = _transform_colons(params)

            json_dict["params"][job] = transformed_params
            json_dict["input"][job] = self.jobs[job].model["input"] #same
        json_dict["globalInput"] = self.global_input
        return json.dumps(json_dict)

    def submit(self, name = None):
        """Submits the workflow to Datoma's infrastructure.

        :param name: Execution name of the workflow, defaults to None. If None, the name will be the same as the workflow.
        :type name: str, optional
        :raises ValueError: If there is an error submitting the workflow.
        """

        # if get_credits:
        #     finished = False # Controls the loop in case the user does not input a valid answer
        #     jobs_list = []         
        #     for job in self.layout_file["steps"]:
        #         jobs_list.append({"tool": job["tool"], "task": job["task"]})
        #     credits = _get_creds(wf_dict_list=jobs_list)
        #     while not finished:
        #         if credits == 1:
        #             agreement = input(f"This Workflow execution will cost you {credits} credit. Do you want to proceed? (Y/N)")
        #         else:
        #             agreement = input(f"This Workflow execution will cost you {credits} credits. Do you want to proceed? (Y/N)")
        #         if agreement.lower() == 'y' or agreement.lower() == 'yes' or agreement.lower() == 'n' or agreement.lower() == 'no':
        #             if agreement.lower() == 'n' or agreement.lower() == 'no':
        #                 print("Workflow not submitted")
        #                 return
        #             finished = True
        #         else:
        #             print("Please input a valid answer")

        if not self.is_official:   #if it is an ephemeral wf, register it
            self._register_workflow()
        if name is not None: 
            if "/" in name:
                raise ValueError("Workflow name cannot contain '/'")
            self.name = name
        else: self.name = "workflow_from_datoma_" + _get_uuid()

        body = self._create_json()
        if not self.is_official: response = _create_sign_request_custom_workflow(_authenticate_user(region, 'execute-api'), self.yaml_file, self.json_file, body, self.uuid)
        else: response = _create_sign_request_official_workflow(_authenticate_user(region, 'execute-api'), self.official_name, body)
        
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
        print(f"Workflow {self.id} has been submitted at {self.status_timestamp}")

    
    async def list_outputs(self, regex = None):
        """Lists the output files of the workflow filtered (if specified) by a regex. First waits until the workflow is finished. Must be called with await.

        :param regex: A regex to filter the output, defaults to None.
        :type regex: str, optional
        :return: List of outputs, size in Bytes.
        :rtype: list, int
        """
        return(await _list_outputs(self, regex))
    
    async def download(self, output_path = None):
        """Downloads the output files of the workflow. First waits until the workflow is finished. Must be called with await.

        :param output_path: The path to download the files generated by the workflow, defaults to None. If None, the files will be downloaded to the current directory, generating a subfolder.
        :type output_path: str, optional
        """
        await _download(self, output_path, self.name)

    def export_json(self, path = None):
        """Exports the workflow information to a JSON file.

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
        except:
            raise FileNotFoundError(f"File {path} could not be created")
        
    def _import_json(self, path):
        """Imports a JSON file with the workflow information.

        :param path: Path to the JSON file.
        :type path: str
        :raises Exception: Raises an error if the object inside the imported JSON file is not a DatomaWorkflow.
        :raises FileNotFoundError: Raises an error if the file does not exist or is not a valid JSON file.
        """
        try:
            path = os.path.abspath(path)
            with open(path, 'r') as outfile:
                json_file = jsonpickle.decode(json.load(outfile))
                if 'DatomaWorkflow' not in str(type(json_file)):
                    raise Exception("The object inside the imported JSON file is not a DatomaWorkflow")
                self.yaml_file = json_file.yaml_file
                self.layout_file = json_file.layout_file
                self.json_file = json_file.json_file
                self.is_official = json_file.is_official
                self.name = json_file.name
                self.official_name = json_file.official_name
                self.global_input = json_file.global_input
                self.global_parameters = json_file.global_parameters
                self.jobs = json_file.jobs
            outfile.close()
        except:
            raise FileNotFoundError(f"File {path} does not exist or is not a valid JSON file")