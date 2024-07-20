API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

def is_youtube_token_valid():
    """
    Checks if the current Youtube Data v3 API token is valid.

    This method returns True if yes, or False if not.
    """
    from .google_api import is_google_token_valid

    return is_google_token_valid(API_NAME, API_VERSION, SCOPES)

def start_youtube_auth_flow():
    """
    Starts the Google auth flow for Youtube Data v3 API.
    """
    from .google_api import start_google_auth_flow

    return start_google_auth_flow(API_NAME, API_VERSION, SCOPES)

def create_youtube_service():
    """
    Creates a Youtube Data v3 API service and returns it.
    """
    from .google_api import create_google_service

    return create_google_service(API_NAME, API_VERSION, SCOPES)
