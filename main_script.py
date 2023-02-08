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
import pandas as pd
import json
import unidecode
import dateutil.parser as dparser


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


def array_to_time_intervals(arr):
    time_intervals = [pd.Interval(pd.Timestamp(dparser.parse(i[0])), pd.Timestamp(dparser.parse(i[1]))) for i in arr]
    return time_intervals


def find_time_interval(txt):
    line_of_time = unidecode.unidecode(txt.split('EST')[1]).split(',')
    date = line_of_time[1]
    hours = line_of_time[2].split(' ')
    start = dparser.parse(date + ' ' + hours[3] + ' ' + hours[4], fuzzy=True)
    end = dparser.parse(date + ' ' + hours[6] + ' ' + hours[7], fuzzy=True)

    return pd.Interval(pd.Timestamp(start), pd.Timestamp(end))


if __name__ == '__main__':
    scopes = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
    # credentials_path = r'C:\Users\Fatemeh\Desktop\paper_shift_transfer\credentials_mtn.json'
    credentials1_path = '/home/matin/paper_gmail_shift_transfer/credentials/credentials_mtn.json'
    token1_path = '/home/matin/paper_gmail_shift_transfer/tokens/token_mtn.json'
    credentials2_path = '/home/matin/paper_gmail_shift_transfer/credentials/credentials_fati.json'
    token2_path = '/home/matin/paper_gmail_shift_transfer/tokens/token_fati.json'

    creds_and_tokens_path = [{'creds': credentials1_path, 'token':token1_path},
                             {'creds':credentials2_path, 'token':token2_path}]

    creds_index = 0
    credentials_path = creds_and_tokens_path[creds_index]['creds']
    token_path = creds_and_tokens_path[creds_index]['token']

    creds = get_creds(credentials_path, token_path, scopes)
    service = build('gmail', 'v1', credentials=creds)
    make_read_body = {"addLabelIds": [], "removeLabelIds": ['UNREAD']}

    unable_path = '/home/matin/paper_gmail_shift_transfer/unable_times.json'
    unable_file = open(unable_path)
    unable_times = array_to_time_intervals(json.load(unable_file))

    while True:
        try:
            messages = service.users().messages().list(userId='me', maxResults=1, labelIds='UNREAD').execute()
            message_id = messages['messages'][0]['id']
            msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
            if read_message_subject(msg) == 'Shift Transfer Request':
                text = read_message_text(msg)
                request_interval = find_time_interval(text)
                able = True
                for interval in unable_times:
                    if interval.overlaps(request_interval):
                        able = False
                if able:
                    link = find_link(text)
                    webbrowser.open(link)
                    print(f'{bcolors.OKBLUE}{time.ctime(time.time())}')
                    print(link)
                    print(f'{bcolors.WARNING}-----------------------------------')
                else:
                    print(f'{bcolors.OKBLUE}{time.ctime(time.time())}')
                    print('Rejected - Bad timing')
                    print(f'{bcolors.WARNING}XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
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
                    print('token and creds were change due to user-rate limit')

        time.sleep(0.1)
