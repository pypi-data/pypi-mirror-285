import json
import os
import re
import requests
from requests_aws4auth import AWS4Auth
from botocore import UNSIGNED
from botocore.config import Config
from botocore.session import Session
import boto3
import websockets
import yaml
import hashlib
import platform
import traceback
from datoma.AppSyncClient import AppSyncClient
from datoma.transfer_manager import File, Transfer, TransferManager
from datoma.CustomCredentialProvider import AWSCredsRefresh


region = 'eu-west-1'
refreshable_session = None
session_set = False
is_dev_set = False
isdev = None
bucket_name_config = None
bucket_name_storage = None
devstr = None


def _check_storage_limit():
    usage, limit = _check_enough_storage()
    if usage>=limit:
        raise Exception(f"Your storage usage exceeds the limit. Please, delete some files to continue.")
    return usage, limit

def _set_dev():
    """This function sets necessary global variables depending on the devaccess field in the YAML file.
    """
    global isdev, is_dev_set, bucket_name_config, bucket_name_storage, devstr
    isdev = _read_yaml(_get_datoma_yaml())['devaccess']
    if isdev:
        bucket_name_config = 'datoma-frontendconfig-dev'
        bucket_name_storage = 'datoma-userstorage-dev'
        devstr = '.dev'
    else:
        bucket_name_config = 'datoma-frontendconfig-prod'
        bucket_name_storage = 'datoma-userstorage-prod'
        devstr = ''
    is_dev_set = True

def _get_creds(aws_auth = None, job_name = None, tool_name = None, task_name = None, input = None, params = None, wf_dict_list = None):
    """Gets the amount of credits for a tool:task or a workflow.
    :param aws_auth: Authentication object, defaults to None.
    :type aws_auth: AWS4Auth, optional
    :param job_name: Name of the job to search for, defaults to None.
    :type job_name: str, optional
    :param tool_name: Name of the tool to search for, defaults to None.
    :type tool_name: str, optional
    :param task_name: Name of the task to search for, defaults to None.
    :type task_name: str, optional
    :param input: Input for the tool:task, defaults to None.
    :type input: JSON, optional
    :param params: Parameters for the tool:task, defaults to None.
    :type params: JSON, optional
    :param wf_dict_list: List of tool:task tuples on the Workflow, defaults to None.
    :type wf_dir_list: list, optional
    :return: The amount of credits for the specified tool:task or workflow.
    :rtype: int
    """

    if not is_dev_set: _set_dev()
    if wf_dict_list is None:
            url = f'https://api{devstr}.datoma.cloud/quotes/request'  
            http_method = 'POST'
            headers = {'Content-Type': 'application/json'}
            body = {
                "tool": tool_name,
                "task": task_name,
                "params": params,
                "input": input,
                "name": job_name
            }
            body_json = json.dumps(body)

            return requests.request(method=http_method, url=url, headers=headers, data=body_json, auth=aws_auth)
        # check_cli = AppSyncClient(_get_session(), devstr)
        # result = check_cli._get_creds()['listTasks']['items']
        # for dictionary in result:
        #     if dictionary["toolCodename"] == tool_name and dictionary["taskCodename"] == task_name:
        #         return int(dictionary["defaultMaxCost"])
    # else:
    #     cost = 0
    #     check_cli = AppSyncClient(_get_session(), devstr)
    #     result = check_cli._get_creds()['listTasks']['items']
    #     for job in wf_dict_list:
    #         for dictionary in result:
    #             if dictionary["toolCodename"] == job["tool"] and dictionary["taskCodename"] == job["task"]:
    #                 cost += int(dictionary["defaultMaxCost"])
    #     return cost


def _get_session():
    """Sets the global variable refreshable_session to the session object.

    :return: boto3 session with refreshable credentials.
    :rtype: boto3.Session
    """
    global session_set, refreshable_session
    if not session_set:
        refreshable_session = AWSCredsRefresh().run()
        session_set = True
    return refreshable_session

def _check_enough_storage():
    if not is_dev_set: _set_dev()
    check_cli = AppSyncClient(_get_session(), devstr)
    result = check_cli._get_storage_usage()['getStorageUsage']
    storage_usage = result['usage'] * 1000 * 1000   #convert to Bytes
    user_storage_limit = result['limit']* 1000 * 1000
    return storage_usage, user_storage_limit

# this function creates the authentication object given the region and the service
def _authenticate_user(region, service):
    """Authenticates the user to the AWS API.

    :param region: Region where the service is located.
    :type region: str
    :param service: The service to authenticate to.
    :type service: str
    :raises Exception: Exception raised if the profile is not found.
    :return: Authentication object.
    :rtype: AWS4Auth
    """
    try: 
        credentials = _get_session().get_credentials()
    except Exception:
        raise Exception("You are not logged in. Please, try 'python3 -m datoma login'")
    return AWS4Auth(region=region, service=service, refreshable_credentials=credentials)   # create the authentication object

# this function creates the signed request to the API
def _create_sign_request_job(aws_auth, tool_name, task_name, body):
    """Sends a signed request to the API, specifying the authentication, tuple of tool:task and the body for the request.

    :param aws_auth: Authentication object.
    :type aws_auth: AWS4Auth
    :param tool_name: Name of the tool to use.
    :type tool_name: str
    :param task_name: Name of the task to use.
    :type task_name: str
    :param body: Body of the request.
    :type body: JSON
    :return: Request object.
    :rtype: requests.models.Response
    """
    if not is_dev_set: _set_dev()
    _check_enough_storage()
    url = f'https://api{devstr}.datoma.cloud/tools/{tool_name}/dev/{task_name}/submit'  
    http_method = 'POST'
    headers = {'Content-Type': 'application/json'}
    return requests.request(method=http_method, url=url, headers=headers, data=body, auth=aws_auth)

def _request_skeleton(tool_name, task_name):
    """Requests the skeleton of the tool:task from the S3 bucket.

    :param tool_name: Name of the tool to use.
    :type tool_name: str
    :param task_name: Name of the task to use.
    :type task_name: str
    :return: Request object.
    :rtype: requests.models.Response
    """
    if not is_dev_set: _set_dev()
    file_key = f'public/tool/{tool_name}/dev/{task_name}/layout.json'
    url = f'https://{bucket_name_config}.s3.{region}.amazonaws.com/{file_key}'
    return requests.get(url)

def _read_yaml(file_path):
    """Reads a YAML file and returns its content.

    :param file_path: Path to the YAML file.
    :type file_path: str
    :raises Exception: If the YAML file is not valid.
    :raises Exception: If the YAML file doesn't exist.
    :return: Data from the YAML file.
    :rtype: dict
    """
    try:
        with open(file_path, 'r') as file:
            try:
                yaml_data = yaml.safe_load(file)
                return yaml_data
            except yaml.YAMLError as e:
                raise Exception(f"Error reading YAML file: {e}")
    except FileNotFoundError:
        raise Exception(f"File {file_path} not found.")

def _get_specific_field(yaml_data, field_path):
    """Gets a specific field from a YAML file.

    :param yaml_data: Data from the YAML file.
    :type yaml_data: dict
    :param field_path: Name of the field to get.
    :type field_path: str
    :return: The content of the field or None if it doesn't exist.
    :rtype: str
    """
    try:
        for field in field_path.split('.'):
            yaml_data = yaml_data[field]
        return yaml_data
    except KeyError:
        # print(f"Field '{field_path}' not found, proceeding to fetch it.")
        return None

# this function gets the userid from the YAML file
# if it isn't stored there, it will get it from Cognito, using the access token
# we will finally store it in the YAML file
def _get_uuid():
    """Gets the user's UUID from the YAML file. If it isn't stored, it will fetch it authenticating to Cognito.

    :return: The user's UUID.
    :rtype: str
    """
    file_path = _get_datoma_yaml()
    yaml_data = _read_yaml(file_path)
    specific_field = _get_specific_field(yaml_data, 'userid')
    if specific_field is None:
        specific_field = _get_specific_field(yaml_data, 'accesstoken')
        cognito = boto3.client('cognito-idp', config=Config(signature_version=UNSIGNED))
        response = cognito.get_user(AccessToken=specific_field)
        specific_field = response['UserAttributes'][0]['Value']
        yaml_data['userid'] = specific_field
        with open(file_path, 'w') as file:
            yaml.dump(yaml_data, file)
    return specific_field

def _get_datoma_yaml():
    """Gets the Datoma YAML file based on the user's OS.

    :return: The path to the .datoma.yml file.
    :rtype: str
    """
    if platform.system() == 'Windows':
        file_path = os.path.join(os.environ['USERPROFILE'], '.datoma.yml')
    else:
        file_path = os.path.join(os.environ['HOME'], '.datoma.yml')
    return file_path

# returns a list of the files in the user's S3 bucket
def _get_s3_files(folder_path):
    """Gets the files from the user's S3 bucket from a certain path.

    :param folder_path: Path that acts as the root of the search, we will get all files and subfolders from there.
    :type folder_path: str
    :raises Exception: In case the profile is not found.
    :raises Exception: In case the folder path is not valid.
    :return: A list of the files in the specified path (with their respective sizes) and the S3 authentication object.
    :rtype: list of dictionaries, botocore.client.S3
    """
    try:s3 = _get_session().client('s3')
    except: raise Exception(("You are not logged in. Please, try 'python3 -m datoma login'"))
    paginator = s3.get_paginator('list_objects_v2')
    if not is_dev_set: _set_dev()
    operation_parameters = {'Bucket': bucket_name_storage,
                            'Prefix': folder_path}
    page_iterator = paginator.paginate(**operation_parameters)
    file_list = []
    try:
        for page in page_iterator:
            for i in range(len(page['Contents'])):
                file_dict = {}
                file_dict[page['Contents'][i]['Key'][len(folder_path)-1:]] = page['Contents'][i]['Size']
                file_list.append(file_dict)
    except s3.exceptions.ClientError as e:
        raise Exception(f"Error getting files from S3 bucket, check your input folder path: {e}")
    return file_list, s3

def _check_files_exist(filenames):
    """Checks if the files exist in the S3 bucket.

    :param filenames: Paths to the files to check.
    :type filenames: list
    :raises Exception: In case the profile is not found.
    :raises Exception: If a location in s3 is specified but the file doesn't exist.
    :raises Exception: If an error different than non existing file occurs.
    :return: A list of the specified files that don't exist in the S3 bucket, with the format [[local_path, s3_path], ...].
    :rtype: list[list]
    """
    s3 = _get_session().client('s3')
    non_existing_files = []
    flag=False
    if not is_dev_set: _set_dev()
    for filename in filenames:
        if re.search(r'^s3://', filename[0]) is not None: 
            object_key = filename[0][6+len(bucket_name_storage):]
            flag=True
        else: 
            shortened = filename[1][filename[1].find('/files/datoma-lib'):]
            object_key = f'private/user/{_get_uuid()}{shortened}'
            flag=False
        try:
            s3.head_object(Bucket=bucket_name_storage, Key=object_key)
        except s3.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                if flag: raise Exception(f"File '{filename[0]}' not found in S3 bucket. Make sure you specified the correct URL.")
                else: non_existing_files.append(filename)
            else:
                raise Exception(f"An error occurred for file '{filename[0]}': {e}")
        except TypeError as e:
            raise TypeError(f"An unexpected error occurred for file '{filename[0]}': {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred for file '{filename[0]}': {e}")
    return non_existing_files

# memory efficient way to compute the sha256 hash of a file
def _compute_sha256(file_name):
    """Generates the SHA256 hash of a file. It does so in a memory efficient way.

    :param file_name: Name of the file to generate the hash from.
    :type file_name: str
    :return: The hash of the file.
    :rtype: str
    """
    hash_sha256 = hashlib.sha256()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def _list_files_relative_to_innermost_directory(absolute_file_paths):
    """Generates a list of relative file paths with respect to the common prefix among all file paths.

    :param absolute_file_paths: List of absolute file paths.
    :type absolute_file_paths: list
    :return: List of relative file paths.
    :rtype: list
    """
    relative_file_paths = []

    # Find the common prefix among all file paths
    common_prefix = os.path.commonpath(absolute_file_paths)

    # If the common prefix is a file and not a directory, get the directory part
    if not os.path.isdir(common_prefix):
        common_prefix = os.path.dirname(common_prefix)

    # Iterate through each absolute file path
    for file_path in absolute_file_paths:
        # Get the relative path of the file with respect to the common prefix
        relative_path = os.path.relpath(file_path, common_prefix)
        # Add the relative path to the list
        relative_file_paths.append(relative_path)

    return relative_file_paths


# receives a list of files and prepares the path to upload them to S3
def _convert_local_s3(files, preserve_name = False, directory = None):
    """Grabs a file, computes its SHA256 hash and returns the path to upload it to S3 (bucket, uuid, hash.extension).

    :param files: Files to upload to S3.
    :type files: list
    :raises FileNotFoundError: If a specified file doesn't exist.
    :param preserve_name: If True, the name of the file will be preserved in S3, defaults to False.
    :type preserve_name: bool, optional
    :return: A list of [[local_file_path, s3_file_path], ...].
    :rtype: list[list]
    """
    absfiles = []
    for file in files:
        if not os.path.isabs(file):
            file = os.path.abspath(file)
        if not os.path.isfile(file):
            raise FileNotFoundError(f"File {file} not found.")
        absfiles.append(file)

    uuid=_get_uuid()
    origin_dest_list = []
    if not is_dev_set: _set_dev()
    if directory is not None:
        rel_files=_list_files_relative_to_innermost_directory(absfiles)
        directory = os.path.basename(os.path.normpath(directory))
        for file in range(len(absfiles)):
            origin_dest_list.append([absfiles[file], f"s3://{bucket_name_storage}/private/user/{uuid}/files/datoma-lib/{directory}/{rel_files[file]}"])
        return origin_dest_list, f"s3://{bucket_name_storage}/private/user/{uuid}/files/datoma-lib/{directory}/"


    else:
        for file in absfiles:
            if preserve_name: 
                origin_dest_list.append([file, f"s3://{bucket_name_storage}/private/user/{uuid}/files/datoma-lib/{os.path.basename(file)}"])
            else:
                file_extension = os.path.splitext(file)[1]  #includes the dot
                origin_dest_list.append([file, f"s3://{bucket_name_storage}/private/user/{uuid}/files/datoma-lib/{_compute_sha256(file)}{file_extension}"])
        return origin_dest_list

def _upload_files(origin_dest_list):
    """Uploads the specified files to the S3 bucket after checking they don't exist already.

    :param origin_dest_list: Files to upload to s3, with the format [[local_file_path, s3_file_path], ...].
    :type origin_dest_list: list[list]
    """
    #first check there is none already on s3
    usage, limit = _check_storage_limit()
    files_non_existing = _check_files_exist(origin_dest_list)
    if files_non_existing:  # if there are files that don't exist, upload them
        sum_sizes = 0
        for file in files_non_existing:
            sum_sizes += os.path.getsize(file[0])

        if usage + sum_sizes > limit:
            raise Exception(f"Uploading these files would exceed your storage limit. Please, delete some files to continue or contact us at contact@datoma.cloud to request more storage.")
        tm = TransferManager(_get_session())
        upload_list = []
        for file in files_non_existing:
            local_file = File(source="local", path=file[0])
            remote_file = File(source="remote", path=file[1])
            upload_list.append(Transfer(source=local_file, dest=remote_file))
        tm._do_transfer(upload_list)

def _create_sign_request_custom_workflow(aws_auth, yaml_file, json_file, data = None, wf_uuid = None):
    """This function creates the signed request to the API for the workflow, wether it is to create or submit it.

    :param aws_auth: Authentication object.
    :type aws_auth: AWS4Auth
    :param yaml_file: YAML file with the workflow.
    :type yaml_file: bytes
    :param json_file: JSON file with the layout.
    :type json_file: bytes
    :param data: Body to submit the request, defaults to None.
    :type data: Bytes, optional
    :param wf_uuid: UUID of the workflow to submit, defaults to None. If None, the workflow will be created.
    :type wf_uuid: str, optional
    :return: Request object.
    :rtype: requests.models.Response
    """
    if not is_dev_set: _set_dev()
    _check_enough_storage()
    if wf_uuid != None:  
        url = f'https://api{devstr}.datoma.cloud/user/ephemeralworkflows/{wf_uuid}/submit'
        headers = {'Content-Type': 'application/json'}
        return requests.request(method='POST', url=url, headers=headers, data=data, auth=aws_auth)
    else:       
        url = f'https://api{devstr}.datoma.cloud/user/ephemeralworkflows'
        files = {
        'workflow': ('yaml_file.yaml', yaml_file, 'application/yaml'),
        'layout': ('json_file.json', json_file, 'application/json')
        }     #TODO: create a JSON file and use it
        return requests.request(method='POST', url=url, files=files, auth=aws_auth)


def _create_sign_request_official_workflow(aws_auth, workflowcodename, data):
    """This function creates the signed request to the API to submit an official workflow.

    :param aws_auth: Authentication object.
    :type aws_auth: AWS4Auth
    :param workflowcodename: Codename of the workflow to submit.
    :type workflowcodename: str
    :param data: Body to submit the request.
    :type data: Bytes, optional
    :return: Request object.
    :rtype: requests.models.Response
    """
    if not is_dev_set: _set_dev()
    _check_enough_storage()
    url = f'https://api{devstr}.datoma.cloud/workflows/{workflowcodename}/submit'
    headers = {'Content-Type': 'application/json'}
    return requests.request(method='POST', url=url, headers=headers, data=data, auth=aws_auth)

def _transform_colons(input_dict):
    """Transforms the colons in the keys of a dictionary into nested dictionaries.

    :param input_dict: Dictionary to transform.
    :type input_dict: dict
    :return: Transformed dictionary.
    :rtype: dict
    """
    result_dict = {}
    for key, value in input_dict.items():
        # If the value is another dictionary, recursively transform it
        if isinstance(value, dict):
            value = _transform_colons(value)
        # Split keys by colons and build nested dictionaries
        keys = key.split(":")
        current_dict = result_dict
        for k in keys[:-1]:
            current_dict = current_dict.setdefault(k, {})
        current_dict[keys[-1]] = value
    return result_dict

async def _await_finished(job_wf, job_list = None):
    """Subscribes to the job's updates and awaits until the job is finished.

    :param job_wf: Job or workflow to subscribe to.
    :type job_wf: DatomaJob or DatomaWorkflow
    :param job_list: List of jobs to get start and finsih timestamps, defaults to None.
    :type job_list: list, optional
    :raises Exception: If passed object is neither a DatomaJob nor a DatomaWorkflow.
    """
    class_name = str(type(job_wf))

    # Check if the class name contains the desired substring
    if 'DatomaWorkflow' in class_name:
        class_name = 'Workflow'
    elif 'DatomaJob' in class_name:
        class_name = 'Job'
    else: raise Exception("The object is neither a DatomaWorkflow nor a DatomaJob")
    if not is_dev_set: _set_dev()
    check_cli = AppSyncClient(_get_session(), devstr)
    try:
        if job_list is not None:
            async for update in check_cli._subscribe_to_updates():
                for job in job_list:
                    if update["onUpdateJob"]["id"] == job.id:
                        print(f"Received update for {class_name} {job.id}: status is {update['onUpdateJob']['status']} at {update['onUpdateJob']['updatedAt']}")
                        job.status = update["onUpdateJob"]["status"]
                        job.status_timestamp = update["onUpdateJob"]["updatedAt"]
                        if job.status == "running":
                            job.running_at = job.status_timestamp
                        if job.status == "success" or job.status == "failed":
                            job.finished_at = job.status_timestamp
                if all(job.finished_at != None for job in job_list):
                    check_cli._subscribe_to_updates().aclose()
                    break #just in case

        else:
            async for update in check_cli._subscribe_to_updates():
                if update["onUpdateJob"]["id"] == job_wf.id:
                    print(f"Received update for {class_name} {job_wf.id}: status is {update['onUpdateJob']['status']} at {update['onUpdateJob']['updatedAt']}")
                    job_wf.status = update["onUpdateJob"]["status"]
                    job_wf.status_timestamp = update["onUpdateJob"]["updatedAt"]
                    if job_wf.status == "running":
                        job_wf.running_at = job_wf.status_timestamp
                if job_wf.status == "success" or job_wf.status == "failed":
                    job_wf.finished_at = job_wf.status_timestamp
                    check_cli._subscribe_to_updates().aclose()  #instead of break
                    break #just in case
    except websockets.exceptions.ConnectionClosedError:
        print(f"Connection closed waiting for {class_name} with ID {job_wf.id} to finish. There might be an issue with your connection. Please, keep the {class_name} object and retry")
    print(f"{class_name} {job_wf.id} has ended as {job_wf.status}")

def _check_status(job_wf):
    """Checks the status of the job/workflow.

    :param job_wf: Job or workflow to check the status from.
    :type job_wf: DatomaJob or DatomaWorkflow
    """
    if not is_dev_set: _set_dev()
    check_cli = AppSyncClient(_get_session(), devstr)
    job_wf.status = check_cli._get_job(job_wf.id)["status"]

async def _download(job_wf, output_path = None, name = None):
    """Downloads the output files of the job/workflow. First waits until the job/workflow is finished.

    :param job_wf: Job or workflow to download the output from.
    :type job_wf: DatomaJob or DatomaWorkflow
    :param output_path: Path where the output of the job/workflow will be downloaded, defaults to None. If None, the output will be downloaded to the current directory, creating a subfolder with the name of the job/workflow's execution name.
    :type output_path: str, optional
    :param name: DatomaWorkflow's execution name, defined at submit. Defaults to None.
    :type name: str, optional
    :raises Exception: If passed object is neither a DatomaJob nor a DatomaWorkflow.
    :raises ValueError: If the job fails.
    :raises ValueError: If the function is called before the job is submitted.
    :raises ValueError: If the job fails.
    """
    _check_status(job_wf)
    class_name = str(type(job_wf))
    if 'DatomaWorkflow' in class_name:
        class_name = 'Workflow'
    elif 'DatomaJob' in class_name:
        class_name = 'Job'
    else: raise Exception("The object is neither a DatomaWorkflow nor a DatomaJob")

    if job_wf.status == 'running' or job_wf.status == 'submitted' or job_wf.status == 'enqueued' or job_wf.status == 'success':
        if job_wf.status != 'success':  await _await_finished(job_wf)
    
        if job_wf.status == 'success': 
            if output_path is None:
                if name is None: output_path = f'./{job_wf.name}_{job_wf.id[0:8]}'
                else: output_path = f'./{name}_{job_wf.id[0:8]}'
            if not is_dev_set: _set_dev()
            try:
                files, s3 = _get_s3_files(f'private/user/{_get_uuid()}/output/{job_wf.id}/')
            except Exception as e:
                traceback.print_exc()
            output_path = os.path.abspath(output_path)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            for file_dict in files:
                directory = os.path.dirname(list(file_dict.keys())[0])
                if directory and not os.path.exists(f'{output_path}{directory}'):
                    os.makedirs(f'{output_path}{directory}')
                s3.download_file(bucket_name_storage, f'private/user/{_get_uuid()}/output/{job_wf.id}{list(file_dict.keys())[0]}', f'{output_path}{list(file_dict.keys())[0]}') # save to same path
            print(f"All files downloaded successfully and located in {output_path}")
        elif job_wf.status == 'failed': raise ValueError(f"{class_name} {job_wf.id} has failed.")
    elif job_wf.status == 'unsubmitted': raise ValueError(f"The {class_name} has not been submitted yet.")
    elif job_wf.status == 'failed': raise ValueError(f"{class_name} {job_wf.id} has failed.")

async def _list_outputs(job_wf, regex = None, job_list = None):
    """Lists the output files of the job/workflow filtered (if specified) by a regex. First waits until the job/workflow is finished.

    :param job_wf: Job or workflow to list the output from.
    :type job_wf: DatomaJob or DatomaWorkflow
    :param regex: A regex to filter the output, defaults to None.
    :type regex: str, optional
    :param job_list: List of jobs to get start and finsih timestamps, defaults to None.
    :type job_list: list, optional
    :raises Exception: If passed object is neither a DatomaJob nor a DatomaWorkflow.
    :raises Exception: If there is an error on the regex.
    :raises ValueError: If the job fails.
    :raises ValueError: If the function is called before the job is submitted.
    :raises ValueError: If the job fails.
    :return: The matching outputs with the regex (or all if none specified), size in Bytes.
    :rtype: list, int
    """
    _check_status(job_wf)
    class_name = str(type(job_wf))
    if 'DatomaWorkflow' in class_name:
        class_name = 'Workflow'
    elif 'DatomaJob' in class_name:
        class_name = 'Job'
    else: raise Exception("The object is neither a DatomaWorkflow nor a DatomaJob")

    if job_wf.status == 'running' or job_wf.status == 'submitted' or job_wf.status == 'enqueued' or job_wf.status == 'success':
        if job_wf.status != 'success': await _await_finished(job_wf, job_list)
        if job_wf.status == 'success': 
            if not is_dev_set: _set_dev()
            try:
                files = _get_s3_files(f'private/user/{_get_uuid()}/output/{job_wf.id}/')[0]
            except Exception as e:
                traceback.print_exc()
            matching_outputs = []
            size_sum = 0
            for file_dict in files:
                if not list(file_dict.keys())[0].endswith('/'):
                    try:
                        if regex is None or re.search(regex, list(file_dict.keys())[0]) is not None:
                            matching_outputs.append(f's3://{bucket_name_storage}/private/user/{_get_uuid()}/output/{job_wf.id}{list(file_dict.keys())[0]}')
                            size_sum += list(file_dict.values())[0]
                    except re.error:
                        raise Exception(f"There is an error on the specified regex: {regex}")
            return matching_outputs, size_sum
        elif job_wf.status == 'failed': raise ValueError(f"{class_name} {job_wf.id} has failed.")
    elif job_wf.status == 'unsubmitted': raise ValueError(f"The {class_name} has not been submitted yet.")
    elif job_wf.status == 'failed': raise ValueError(f"{class_name} {job_wf.id} has failed.")

def _request_workflow(official_name):
    """Requests the workflow skeleton from the S3 bucket.

    :param official_name: Codename of the workflow to request.
    :type official_name: str
    :return: Request object.
    :rtype: requests.models.Response
    """
    if not is_dev_set: _set_dev()
    file_key = f'public/workflow/{official_name}/layout.json'
    url = f'https://{bucket_name_config}.s3.{region}.amazonaws.com/{file_key}'
    return requests.get(url)

