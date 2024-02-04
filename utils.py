import subprocess
import requests
import os


def get_active_window_name():
    script = 'tell application "System Events" to get the name of the first process whose frontmost is true'
    return subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()


def send_notification(title, text):
    osascript_command = f'''
    display dialog "{text}" with title "{title}" buttons {{"Logs", "Thanks, Coach! Back to work."}} default button 2
    if the button returned of the result is "Logs" then
        do shell script "open coaching_responses.txt && tail -n +1 coaching_responses.txt"
    end if
    '''
    subprocess.run(['osascript', '-e', osascript_command])


from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


slack_token = os.environ.get('SLACK_API_TOKEN')
client = WebClient(token=slack_token)
channel = "C06GYJ09PT7"

def send_slack_message(text, image_path):
    try:
        response = client.files_upload(
            channels=channel,
            file=image_path,
            initial_comment=text
        )
        print(response)
    except SlackApiError as e:
        print(f"Error uploading file: {e}")
