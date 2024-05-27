from __future__ import print_function
import datetime
import os.path
import pickle
import re
from base64 import urlsafe_b64decode
import dateutil.parser as dparser
import pandas as pd
import requests
import unidecode
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta


class Bcolors:
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
        end = end + timedelta(days=1)
    return pd.Interval(pd.Timestamp(start), pd.Timestamp(end))


def send_telegram_message(botID, channelID, message):
    msgs = [message[i:i + 4096] for i in range(0, len(message), 4096)]
    response = None
    for text in msgs:
        telegram_api_url = f"https://api.telegram.org/bot{botID}/sendMessage?chat_id=@{channelID}&text={text}"
        try:
            response = requests.get(telegram_api_url)
        except:
            print('Telegram error in sending a message!')

    return response


def save_error(path, error):
    with open(path, 'wb') as file:
        pickle.dump(error, file, pickle.HIGHEST_PROTOCOL)


def occasional_times_overlap(interval1: pd.Interval, interval2: pd.Interval):
    return interval1.overlaps(interval2)


def normalize_interval(start, end):
    """Ensure the interval is valid by rolling over the end time if it's less than the start time."""
    start_dt = pd.Timestamp.combine(pd.Timestamp.min, start)
    if end < start:
        end_dt = pd.Timestamp.combine(pd.Timestamp.min + timedelta(days=1), end)
    else:
        end_dt = pd.Timestamp.combine(pd.Timestamp.min, end)

    # Create additional intervals for comprehensive checking
    start_prev_day = start_dt - timedelta(days=1)
    end_prev_day = end_dt - timedelta(days=1)

    intervals = [
        pd.Interval(start_dt, end_dt),  # Original interval
        pd.Interval(start_prev_day, end_prev_day),  # Interval with start one day earlier
    ]

    return intervals


def fixed_times_overlap(interval1, interval2):
    # Extract time component from interval bounds
    start1 = interval1.left.time()
    end1 = interval1.right.time()
    start2 = interval2.left.time()
    end2 = interval2.right.time()

    # Normalize the intervals to handle day rollover
    interval1_times = normalize_interval(start1, end1)
    interval2_times = normalize_interval(start2, end2)

    # Check if any of the intervals overlap
    for interval1_time in interval1_times:
        for interval2_time in interval2_times:
            if interval1_time.overlaps(interval2_time):
                return True

    return False


def times_overlap(unable_times: dict, request_interval: pd.Interval):
    is_fixed_times = any([fixed_times_overlap(i, request_interval) for i in unable_times['fixed']])
    is_occasional_times = any([occasional_times_overlap(i, request_interval) for i in unable_times['occasional']])
    return is_fixed_times or is_occasional_times
