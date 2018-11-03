from googleapiclient.discovery import build


DEVELOPER_KEY = 'AIzaSyBkuM7s5AMLBq7Gn0zwGQ43HDjehpXo624'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def youtube_search(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
        q=options.q,
        type='video',
        part='id,snippet',
    ).execute()

    search_videos = []

    # Merge video ids
    for search_result in search_response.get('items', []):
        search_videos.append(search_result['id']['videoId'])
    video_ids = ','.join(search_videos)

    # Call the videos.list method to retrieve location details for each video.
    video_response = youtube.videos().list(
        id=video_ids,
        part='snippet, recordingDetails'
    ).execute()

    videos = []

    # Add each result to the list, and then display the list of matching videos.
    for search_result in search_response.get('items', []):
        videos.append("%s \t %s" % (search_result['snippet']['title'],
                                    search_result['id']['videoId']))
    return videos
