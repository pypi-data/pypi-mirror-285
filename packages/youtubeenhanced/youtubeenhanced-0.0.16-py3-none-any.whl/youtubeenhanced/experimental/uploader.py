
def upload_video_to_youtube(filename, name = 'name', description = 'description', tags = [], category_id = '27'):
    """
    Uploads the provided filename video in our system to the connected Youtube 
    Channel.

    This need the channel to be connected and to have an available token that is
    stored in the 'token files' folder. Read the readme for more information.
    """
    from datetime import datetime
    from googleapiclient.http import MediaFileUpload
    from utils.youtube_api import create_youtube_service

    # Set this as False to avoid uploading it to to Youtube
    do_upload = False

    media_file = MediaFileUpload(filename)
    upload_time = (datetime.datetime.now() + datetime.timedelta(days = 10)).isoformat() + '.000Z'
    request_body = {
        'snippet': {
            'title': name,
            'description': description,
            'categoryId': category_id,
            'tags': tags
        },
        'status': {
            'privacyStatus': 'private',
            'publishedAt': upload_time,
            'selfDeclaredMadeForKids': False
        },
        'notifySubscribers': False
    }

    if do_upload:
        service = create_youtube_service()
        response_video_upload = service.videos().insert(
            part = 'snippet,status',
            body = request_body,
            media_body = media_file
        ).execute()
        print(response_video_upload)
        uploaded_video_id = response_video_upload.get('id')
        print(uploaded_video_id)
        print('Video ' + name + ' uploaded to your Youtube Channel.')
    else:
        print('Fake uploaded')