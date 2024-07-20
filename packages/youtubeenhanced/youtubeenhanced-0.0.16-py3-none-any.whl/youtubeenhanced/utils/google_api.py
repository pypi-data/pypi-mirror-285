from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from yta_general_utils.file_processor import get_project_abspath

import os

PROJECT_ABSOLUTE_PATH = get_project_abspath()
CLIENT_SECRET_PATH = PROJECT_ABSOLUTE_PATH + 'client-secret.json'
TOKEN_FILES_DIRNAME = 'token_files'

def create_google_service(api_name, api_version, *scopes, prefix = ''):
    SCOPES = [scope for scope in scopes[0]]
    
    creds = None
    token_file = f'token_{api_name}_{api_version}{prefix}.json'

    # Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME)):
        print('Creating "token_files" dir')
        os.mkdir(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME))

    if os.path.exists(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file), 'w') as token:
                token.write(creds.to_json())
        else:
            start_google_auth_flow(scopes, token_file)

    try:
        service = build(api_name, api_version, credentials=creds, static_discovery = False)
        print(api_name, api_version, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {api_name}')
        os.remove(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file))
        return None
    
def is_google_token_valid(api_name, api_version, *scopes, prefix = ''):
    try:
        SCOPES = [scope for scope in scopes[0]]

        creds = None
        token_file = f'token_{api_name}_{api_version}{prefix}.json'

        # Check if token dir exists first, if not, create the folder
        if not os.path.exists(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME)):
            return False

        if os.path.exists(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file)):
            creds = Credentials.from_authorized_user_file(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file), SCOPES)
        else:
            return False

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    return False
            else:
                return False
    except Exception as e:
        return False
    
    return True

def start_google_auth_flow(api_name, api_version, *scopes, prefix = ''):
    SCOPES = [scope for scope in scopes[0]]
    token_file = f'token_{api_name}_{api_version}{prefix}.json'

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port = 0)

    with open(os.path.join(PROJECT_ABSOLUTE_PATH, TOKEN_FILES_DIRNAME, token_file), 'w') as token:
        token.write(creds.to_json())