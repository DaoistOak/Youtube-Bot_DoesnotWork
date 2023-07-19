import os
import pickle
import shutil
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm

# Path to the folder containing the videos
VIDEO_FOLDER_PATH = '/home/shridal/Videos/results/AskReddit+Redditdev'
DESTINATION_FOLDER_PATH = '/home/shridal/Videos/Posted'
DESCRIPTION_FILE_PATH = 'description.txt'
# ADDITIONAL_TITLE_TEXT = " #Shorts #RedditStories #Reddit #AskReddit"
# The scopes required for the YouTube Data API
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Path to store and load credentials
CREDENTIALS_FILE = 'credentials.pickle'

# Authenticate and authorize the bot
def authenticate():
    # Check if credentials file exists
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as f:
            credentials = pickle.load(f)

        # Check if credentials are valid
        if credentials and credentials.valid:
            return credentials

    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json', SCOPES
    )
    credentials = flow.run_local_server(port=0)

    # Save credentials to file
    with open(CREDENTIALS_FILE, 'wb') as f:
        pickle.dump(credentials, f)

    return credentials

# Read the description from the description file
def read_description():
    with open(DESCRIPTION_FILE_PATH, 'r') as f:
        return f.read().strip()

# Upload a video to YouTube
def upload_video(youtube, title, description, file_path):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
        },
        'status': {
            'privacyStatus': 'public'
        }
    }

    # Call the API's videos.insert method to upload the video
    media_file = MediaFileUpload(file_path)

    response = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media_file
    ).execute()

    print(f"Video '{title}' uploaded successfully!")

    # Move the uploaded video file to the destination folder
    destination_file_path = os.path.join(DESTINATION_FOLDER_PATH, os.path.basename(file_path))
    shutil.move(file_path, destination_file_path)
    print(f"Video '{title}' moved to destination folder.")


# Main function
def main():
    # Authenticate and authorize
    credentials = authenticate()

    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=credentials)

    # Get the total number of videos in the folder
    total_videos = len([file for file in os.listdir(VIDEO_FOLDER_PATH) if os.path.isfile(os.path.join(VIDEO_FOLDER_PATH, file))])

    # Create a progress bar
    progress_bar = tqdm(total=total_videos, desc="Uploading", unit="video(s)")

    # Iterate over the files in the video folder
    for file_name in os.listdir(VIDEO_FOLDER_PATH):
        file_path = os.path.join(VIDEO_FOLDER_PATH, file_name)

        if os.path.isfile(file_path):
            original_title = os.path.splitext(file_name)[0]
            title = original_title

            description = read_description()

            upload_video(youtube, title, description, file_path)

            # Update the progress bar
            progress_bar.update(1)

    progress_bar.close()

    # Check if the destination folder is empty
    if len(os.listdir(DESTINATION_FOLDER_PATH)) == 0:
        print("No videos found in the destination folder.")
        # Send a message or perform any other action
if __name__ == '__main__':
    main()
