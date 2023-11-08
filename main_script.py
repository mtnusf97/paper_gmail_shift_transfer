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
import argparse
import datetime
import requests
from utils.config import *
from utils.logger import setup_logging
import pickle


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


def read_message_subject(message):
    payload = message['payload']
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
    try:
        line_of_time = unidecode.unidecode(txt.split('EST')[1]).split(',')
    except IndexError:
        line_of_time = unidecode.unidecode(txt.split('EDT')[1]).split(',')
    date = line_of_time[1]
    hours = line_of_time[2].split(' ')
    start = dparser.parse(date + ' ' + hours[3] + ' ' + hours[4], fuzzy=True)
    end = dparser.parse(date + ' ' + hours[6] + ' ' + hours[7], fuzzy=True)
    if start > end:
        end = end + datetime.timedelta(days=1)
    return pd.Interval(pd.Timestamp(start), pd.Timestamp(end))


def send_telegram_message(botID, channelID, message):
    telegram_api_url = f"https://api.telegram.org/bot{botID}/sendMessage?chat_id=@{channelID}&text={message}"
    response = requests.get(telegram_api_url)
    return response


def save_error(path, error):
    with open(path, 'wb') as file:
        pickle.dump(error, file, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='gmail shift transfer script')
    parser.add_argument('-w', '--who', help='who is running this script', required=True, type=str)
    args = vars(parser.parse_args())
    who = args['who']
    
    user_config = user_configs(who)
    
    now_str = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    log_file = os.path.join(user_config.log_path, "log_{}.txt".format(now_str))
    logger = setup_logging('INFO', log_file)

    creds = get_creds(user_config.credentials_path, user_config.token_path, scopes)
    service = build('gmail', 'v1', credentials=creds)

    unable_file = open(user_config.unable_path)
    unable_times = array_to_time_intervals(json.load(unable_file))

    user_used_quota = 0
    total_user_used_quota = 0
    last_time = time.time()

    while True:
        try:
            messages = service.users().messages().list(userId='me', maxResults=1, labelIds='UNREAD').execute()
            user_used_quota += 5
            message_id = messages['messages'][0]['id']
            msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
            user_used_quota += 5
            if read_message_subject(msg) == 'Shift Transfer Request':
                service.users().messages().modify(userId='me', id=message_id, body=make_read_body).execute()
                text = read_message_text(msg)
                request_interval = find_time_interval(text)
                for interval in unable_times:
                    if interval.overlaps(request_interval):
                        msg = f'A shift transfer request rejected due to overlap with: {interval}'
                        print(msg + '\n-------------------------------------')
                        send_telegram_message(botID=bot_token, channelID=channel_id, message=msg)
                        logger.info(msg)
                        raise Exception('Rejection due to overlap')
                link = find_link(text)
                webbrowser.open(link)
                msg = f'A shift transfer request opened with the link: \n{link}'
                print(msg + '\n-------------------------------------')
                send_telegram_message(botID=bot_token, channelID=channel_id, message=msg)
                logger.info(msg)
                user_used_quota += 5
        except KeyError:
            pass
        except Exception as e:
            now_str = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
            error_file = os.path.join(user_config.error_path, str(e) + f"_error_{now_str}.pkl")
            save_error(error_file, e)

            msg = f'\nError occurred:\n{e}' \
                  f'\ncurrent time: {time.ctime(time.time())}'
            print(msg + '\n-------------------------------------')
            send_telegram_message(botID=bot_token, channelID=channel_id, message=msg)
            logger.exception('ERROR!!!')

            if e.args[0] == 'Rejection due to overlap':
                pass
            elif e.args[0] == 'invalid_grant: Token has been expired or revoked.':
                msg = '\n>>>URGENT<<<\nToken has been expired. Check your browser to grant access for a new one.'
                print(msg + '\n-------------------------------------')
                send_telegram_message(botID=bot_token, channelID=channel_id, message=msg)
                creds = get_creds(user_config.credentials_path, user_config.token_path, scopes)
                service = build('gmail', 'v1', credentials=creds)
            elif 'User-rate limit exceeded' in e.reason:
                msg = '\nUser-rate limit exceeded'
                print(msg + '\n-------------------------------------')
                send_telegram_message(botID=bot_token, channelID=channel_id, message=msg)
                break
        if user_used_quota > 250:
            period = time.time() - last_time
            last_time = time.time()
            total_user_used_quota += user_used_quota
            user_used_quota = 0
            msg = f'user quota exceeded 250 - total: {total_user_used_quota} elapsed time: {period}'
            logger.info(msg)
            # with open(user_config.used_quota_path, 'a') as f:
            #     f.write(f'\nuser quota exceeded 250 - total: {total_user_used_quota}\nelapsed time: {period}'
            #             f'\ncurrent time: {time.ctime(time.time())}\n-----------------------')
        time.sleep(1)
