from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
import re
import webbrowser
import time


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_creds(credentials_path, token_path, scopes):
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        try:
            creds.refresh(Request())
        except:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def read_message_subject(msg):
    payload = msg['payload']
    headers = payload.get("headers")
    if headers:
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == "subject":
                return value
    return None


def read_message_text(msg):
    payload = msg['payload']
    parts = payload.get("parts")
    part = parts[0]
    body = part.get("body")
    data = body.get("data")
    text = urlsafe_b64decode(data).decode()
    return text


def find_link(text):
    return re.search("(?P<url>https?://[^\s]+)", text).group("url")[:-1]


def next_creds(creds_and_tokens_dict, idx):
    idx = idx % len(creds_and_tokens_dict)
    return creds_and_tokens_dict[idx]['creds'], creds_and_tokens_dict[idx]['token']


if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
    # credentials_path = r'C:\Users\Fatemeh\Desktop\paper_shift_transfer\credentials_mtn.json'
    credentials1_path = 'credentials/credentials_mtn.json'
    token1_path = 'tokens/token_mtn.json'
    credentials2_path = 'credentials/credentials_fati.json'
    token2_path = 'tokens/token_fati.json'

    creds_and_tokens_path = [{'creds': credentials1_path, 'token': token1_path},
                             {'creds': credentials2_path, 'token': token2_path}]

    creds_index = 0
    credentials_path = creds_and_tokens_path[creds_index]['creds']
    token_path = creds_and_tokens_path[creds_index]['token']

    creds = get_creds(credentials_path, token_path, scopes)
    service = build('gmail', 'v1', credentials=creds)
    make_read_body = {"addLabelIds": [], "removeLabelIds": ['UNREAD']}

    while True:
        try:
            messages = service.users().messages().list(userId='me', maxResults=1, labelIds='UNREAD').execute()
            if 'messages' in messages.keys():
                for message in messages['messages']:
                    message_id = message['id']
                    msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
                    if read_message_subject(msg) == 'Shift Transfer Request':
                        text = read_message_text(msg)
                        link = find_link(text)
                        webbrowser.open(link)
                        print(f'{bcolors.OKBLUE}{time.ctime(time.time())}')
                        print(link)
                        print(f'{bcolors.WARNING}-----------------------------------')
                        service.users().messages().modify(userId='me', id=message_id, body=make_read_body).execute()
        except Exception as e:
            print(f'{bcolors.FAIL}{time.ctime(time.time())}')
            print(f'{bcolors.FAIL}{e}')
            print(f'{bcolors.WARNING}-----------------------------------')

            if e.args[0] == 'invalid_grant: Token has been expired or revoked.':
                creds = get_creds(credentials_path, token_path, scopes)
                service = build('gmail', 'v1', credentials=creds)
            elif 'User-rate limit exceeded' in e.reason:
                creds_index += 1
                credentials_path, token_path = next_creds(creds_and_tokens_path, creds_index)
                creds = get_creds(credentials_path, token_path, scopes)
                service = build('gmail', 'v1', credentials=creds)
                print('token and creds were changed due to the user-rate limit. Current index:',
                      creds_index % len(creds_and_tokens_path))

        time.sleep(0.05)

