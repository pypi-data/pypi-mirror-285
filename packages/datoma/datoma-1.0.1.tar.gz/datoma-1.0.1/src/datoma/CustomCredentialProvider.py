from botocore.credentials import CredentialProvider, RefreshableCredentials
from botocore.session import get_session
import boto3
import yaml
from datetime import datetime
import platform
import os

class CustomCredentialProvider(CredentialProvider):
    CANONICAL_NAME = "datoma-custom"
    def __init__(self, session, access_key=None, secret_key=None, token=None, expiry_time=None):
        self.session = session
        self.access_key = access_key
        self.secret_key = secret_key
        self.token = token
        self.expiry_time = expiry_time

    def load(self):
        """Returns refreshable credentials.

        :return: RefreshableCredentials.
        :rtype: botocore.credentials.RefreshableCredentials
        """
        return RefreshableCredentials(access_key=self.access_key, secret_key=self.secret_key,token=self.token, expiry_time=self.expiry_time, refresh_using=self._refresh, method="sts-assume-role")

    def _refresh(self):
        """A proxy function to call the custom refresh function.

        :return: Credentials.
        :rtype: dict
        """
        ret = _check_refresh_needed()
        credentials = {
            "access_key": ret.get("AccessKeyId"),
            "secret_key": ret.get("SecretAccessKey"),
            "token": ret.get("SessionToken"),
            "expiry_time": ret.get("Expiration"),
        }
        return credentials

    
class AWSCredsRefresh:
    def run(self):
        """Initializes and creates a boto3 session with refreshable credentials.

        :raises Exception: If the user is not logged in.
        :return: boto3 session.
        :rtype: boto3.Session
        """
        _check_refresh_needed()
        path = _obtain_datoma_path()
        yaml_data = _read_yaml(path)
        if yaml_data is not None:
            access_key = yaml_data['accesskeyid']
            secret_key = yaml_data['secretaccesskey']
            token = yaml_data['sessiontoken']
            expiry_time = yaml_data['expiration']
            iso8601_format = datetime.fromtimestamp(expiry_time).astimezone()
            session = get_session()
            # session.set_config_variable('session-duration',3600)
            # session.set_config_variable('session-refresh',1200)
            cred_provider = session.get_component('credential_provider')
            cred_provider.insert_before('env', CustomCredentialProvider(session, access_key, secret_key, token, iso8601_format))

            boto3_session = boto3.Session(botocore_session=session, region_name='eu-west-1')

            return boto3_session
        else: raise Exception("You are not logged in. Please, try 'python3 -m datoma login'")

def _check_refresh_needed():
    """Checks if the credentials need to be refreshed.

    :raises Exception: If the user is not logged in.
    :return: AWS credentials.
    :rtype: dict
    """
    file_path = _obtain_datoma_path()
    yaml_data = _read_yaml(file_path)
    if yaml_data is not None:
        if 'expiration' in yaml_data:   #login has been made
            _refresh_tokens(file_path)
            ret=_aws_creds(file_path)
    else:
        raise Exception("You are not logged in. Please, try 'python3 -m datoma login'")
    return ret

def _aws_creds(file_path):
    """Refreshes the AWS credentials.

    :param file_path: Path to the yaml file.
    :type file_path: str
    :return: AWS credentials.
    :rtype: dict
    """
    yaml_data = _read_yaml(file_path)
        
    idToken = yaml_data['idtoken']

    logins = {"cognito-idp.eu-west-1.amazonaws.com/eu-west-1_LPuLcRgih": idToken,}
    client = boto3.client('cognito-identity')

    identity_id_response = client.get_id(
        IdentityPoolId='eu-west-1:2a995f07-0e31-461b-ad87-d80403f2d928',
        Logins=logins
    )
    
    credentials_response = client.get_credentials_for_identity(
        IdentityId=identity_id_response['IdentityId'],
        Logins=logins
    )

    yaml_data['accesskeyid'] = credentials_response['Credentials']['AccessKeyId']
    yaml_data['secretaccesskey'] = credentials_response['Credentials']['SecretKey']
    yaml_data['sessiontoken'] = credentials_response['Credentials']['SessionToken']
    yaml_data['expiration'] = int(credentials_response['Credentials']['Expiration'].timestamp())

    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file)
    file.close()

    iso8601_format = datetime.fromtimestamp(yaml_data['expiration']).astimezone().isoformat()
    return_dict = {"Version": 1, "AccessKeyId": yaml_data['accesskeyid'], "SecretAccessKey": yaml_data['secretaccesskey'], "SessionToken": yaml_data['sessiontoken'], "Expiration": iso8601_format}
    return return_dict


def _refresh_tokens(file_path):
    """Refreshes the tokens to avoid logging every time they expire.

    :param file_path: Path to the yaml file.
    :type file_path: str
    """
    yaml_data = _read_yaml(file_path)
    client = boto3.client('cognito-idp', region_name='eu-west-1')
    refresh_token = yaml_data['refreshtoken']
    response = client.initiate_auth(
        AuthFlow='REFRESH_TOKEN_AUTH',
        AuthParameters={
            'REFRESH_TOKEN': refresh_token
        },
        ClientId='17916fup45s2om1gresf1rfa97'
    )
    tokens = response['AuthenticationResult']
    yaml_data['accesstoken'] = tokens['AccessToken']
    yaml_data['accesstokenexp'] = int(tokens['ExpiresIn']) + int(datetime.timestamp(datetime.now()))
    yaml_data['idtoken'] = tokens['IdToken']
    with open(file_path, 'w') as file:
        yaml.dump(yaml_data, file)
    file.close()


def _obtain_datoma_path():
    """Copy of datoma.utils function, needed because of circularity.
    """
    if platform.system() == 'Windows':
        file_path = os.path.join(os.environ['USERPROFILE'], '.datoma.yml')
    else:
        file_path = os.path.join(os.environ['HOME'], '.datoma.yml')
    return file_path

def _read_yaml(file_path):
    """Copy of datoma.utils function, needed because of circularity.
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