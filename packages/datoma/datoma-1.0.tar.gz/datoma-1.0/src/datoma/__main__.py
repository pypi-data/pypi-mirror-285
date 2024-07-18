import boto3
from pycognito.aws_srp import AWSSRP
import sys
import pwinput
from datetime import datetime
from datoma.CustomCredentialProvider import _read_yaml, _obtain_datoma_path, _refresh_tokens, _aws_creds

def _login(dev, email = None, password = None): 
    """Performs the login to DATOMA and stores the tokens in a file.

    :param dev: Determines if the user has developer access or not.
    :type dev: bool
    :param email: User's email, defaults to None
    :type email: str, optional
    :param password: User's password, defaults to None
    :type password: str, optional
    """
    if email is None: email = input('Enter your email:\n> ')
    if password is None: password = pwinput.pwinput(prompt='Enter your password:\n> ', mask='*')
    client = boto3.client('cognito-idp')
    aws = AWSSRP(username=email, password=password, pool_id='eu-west-1_LPuLcRgih',
                client_id='17916fup45s2om1gresf1rfa97', client=client)

    try: tokens = aws.authenticate_user()
    except: raise Exception("Wrong email or password. Please, try again.")

    file_path = _obtain_datoma_path()
    with open(file_path, 'w') as f:
        f.write('accesstoken: ' + tokens['AuthenticationResult']['AccessToken'] + '\n')
        f.write('idtoken: ' + tokens['AuthenticationResult']['IdToken'] + '\n')
        f.write('refreshtoken: ' + tokens['AuthenticationResult']['RefreshToken'] + '\n')
        f.write('accesstokenexp: ' + str(int(tokens['AuthenticationResult']['ExpiresIn']) + int(datetime.timestamp(datetime.now()))) + '\n')
        f.write('devaccess: ' + str(dev) + '\n')
    f.close()
    _aws_creds(file_path)


if __name__ == "__main__":
    if sys.argv[1] == 'login':
        email = None
        password = None
        dev = False
        args = sys.argv[2:]
        for i in range(len(args)):
            if args[i] == '--email' and i + 1 < len(args):
                email = args[i + 1]
            elif args[i] == '--password' and i + 1 < len(args):
                password = args[i + 1] 
            elif args[i] == '--dev':
                dev = True
        _login(dev, email, password)
        if dev:
            print("Successfully logged in to the development environment.")
        else:
            print("Successfully logged in to the production environment.")

    elif sys.argv[1] == 'aws-creds':
        file_path = _obtain_datoma_path()
        yaml_data = _read_yaml(file_path)
        if yaml_data is not None:
            if 'expiration' in yaml_data:   #login has been made
                if int(yaml_data['expiration']) < int(datetime.timestamp(datetime.now())):  # session is expired, need to refresh
                    if int(yaml_data['accesstokenexp']) < int(datetime.timestamp(datetime.now())):
                        _refresh_tokens(file_path)
                        ret=_aws_creds(file_path)
                        print(ret)
                    else: 
                        ret=_aws_creds(file_path)
                        print(ret)
                else: # session is still valid
                    if int(datetime.timestamp(datetime.now())) + 900 >= int(yaml_data['expiration']) or int(datetime.timestamp(datetime.now())) + 900 >= int(yaml_data['accesstokenexp']):   #if credentials are about to expire in less than 12 minutes, refresh
                        _refresh_tokens(file_path)
                        ret=_aws_creds(file_path)
                        print(ret)
                    else:
                        dt = datetime.fromtimestamp(yaml_data['expiration'])
                        iso8601_format = dt.isoformat()
                        return_dict = {"Version": 1, "AccessKeyId": yaml_data['accesskeyid'], "SecretAccessKey": yaml_data['secretaccesskey'], "SessionToken": yaml_data['sessiontoken'], "Expiration": iso8601_format}
                        print(return_dict)
            
            elif 'accesstokenexp' in yaml_data: #login has been made but not aws_creds            
                if int(yaml_data['accesstokenexp']) < int(datetime.timestamp(datetime.now())):
                    _refresh_tokens(file_path)
                    ret=_aws_creds(file_path)
                    print(ret)
                else: 
                    ret=_aws_creds(file_path)
                    print(ret)
            else:
                raise Exception("You are not logged in. Please, try 'python3 -m datoma login'")
        else:
            raise Exception("You are not logged in. Please, try 'python3 -m datoma login'")
  
    elif sys.argv[1] == '--help':
        print("Log in to DATOMA and access to credentials from your command line\n")
        print("Usage:\npython3 -m datoma [command]\n")
        print("Available commands:\n login\t\t\tLog in to DATOMA. Accepts the following optional flags:\n  --email EMAIL\t\tSpecify email\n  --password PASSWORD\tSpecify password\n  --dev\t\t\tIf you have developer access")
        print(" aws-creds\t\tGet AWS credentials\n")
    else:
        print(f'Error: unknown command "{sys.argv[1]}" for "datoma"')
        print("Run 'python3 -m datoma --help' for usage.")#show help
