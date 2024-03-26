from __future__ import print_function

import argparse
import json
import time
import traceback
import webbrowser

from googleapiclient.discovery import build

from utils.config import *
from utils.functions import *
import datetime
from utils.logger import setup_logging

parser = argparse.ArgumentParser(description='gmail shift transfer script')
parser.add_argument('-w', '--who', help='who is running this script', required=True, type=str)
args = vars(parser.parse_args())
who = args['who']
user_config = user_configs(who)

# now_str = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
# log_file = os.path.join(user_config.log_path, "log_{}.txt".format(now_str))
# logger = setup_logging('INFO', log_file)
# logger.info('whatever')

creds = get_creds(user_config.credentials_path, user_config.token_path, scopes)
service = build('gmail', 'v1', credentials=creds)

unable_file = open(user_config.unable_path)
unable_times = array_to_time_intervals(json.load(unable_file))

user_used_quota = 0
total_user_used_quota = 0
last_time = time.time()
start_time = time.time()
hr_print_time = time.time()
n_trials = 0

while True:
    try:
        messages = service.users().messages().list(userId='me', maxResults=1, labelIds='UNREAD').execute()
        user_used_quota += 5
        n_trials += 1
        message_id = messages['messages'][0]['id']
        msg_email = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        user_used_quota += 5
        if read_message_subject(msg_email) == 'Shift Transfer Request':
            service.users().messages().modify(userId='me', id=message_id, body=make_read_body).execute()
            text = read_message_text(msg_email)
            request_interval = find_time_interval(text)
            for interval in unable_times:
                if interval.overlaps(request_interval):
                    msg_fati = f'A shift transfer request rejected due to overlap with: {interval}'
                    print(msg_fati + '\n-------------------------------------')
                    send_telegram_message(botID=bot_token_fati, channelID=channel_id_fati, message=msg_fati)
                    raise Exception('Rejection due to overlap')
            link = find_link(text)
            webbrowser.open(link)
            msg_fati = f'A shift transfer request opened with the link: \n{link}'
            user_used_quota += 5
        else:
            msg_fati = "You have an unread message in your inbox. If you don't mark it as read, I won't work!!!"
            time.sleep(5)
        print(msg_fati + '\n-------------------------------------')
        send_telegram_message(botID=bot_token_fati, channelID=channel_id_fati, message=msg_fati)
    except KeyError:
        pass  # in case there is no new emails, we'll get a KeyError on messages['messages'][0]['id']
    except Exception as e:
        err_tb = traceback.format_exc()
        now = time.ctime(time.time())

        if err_tb.find('Rejection due to overlap') != -1:
            msg_fati = 'Rejection due to overlap!'
            send_telegram_message(botID=bot_token_fati, channelID=channel_id_fati, message=msg_fati)
            print(msg_fati + '\n-------------------')
            
        elif err_tb.find('Token has been expired or revoked') != -1:
            msg_fati = (f'>>>URGENT<<<'
                        f'\n-------------------'
                        f'\nToken has been expired. '
                        f'\nCheck your browser to grant access to a new one.'
                        f'\nat: {now}')
            print(msg_fati + '\n-------------------')
            send_telegram_message(botID=bot_token_fati, channelID=channel_id_fati, message=msg_fati)
            
            creds = get_creds(user_config.credentials_path, user_config.token_path, scopes)
            service = build('gmail', 'v1', credentials=creds)
            
        elif err_tb.find('User-rate limit exceeded') != -1:
            msg_fati = (f'DO NOT RERUN!'
                        f'\nUser-rate limit exceeded '
                        f'\n-------------------'
                        f'\n{e}'
                        f'\n-------------------'
                        f'\nat: {now}')
            print(msg_fati + '\n-------------------------------------')
            send_telegram_message(botID=bot_token_fati, channelID=channel_id_fati, message=msg_fati)
            break

        elif err_tb.find('TimeoutError') != -1:
            msg_fati = (f'NO NEED TO RERUN!'
                        f'\nTimeoutError'
                        f'\nat: {now}')
            print(msg_fati + '\n-------------------------------------')

            msg_err = (f'NO NEED TO RERUN!'
                       f'\nTimeoutError:'
                       f'\n-------------------'
                       f'\n'
                       f'\n{err_tb} '
                       f'\n-------------------'
                       f'\nat: {now}')
            send_telegram_message(botID=bot_token_err, channelID=channel_id_err, message=msg_err)

        elif err_tb.find('HttpError 400') != -1:
            msg_fati = (f'NO NEED TO RERUN!'
                        f'\nHttpError 400'
                        f'\nat: {now}')
            print(msg_fati + '\n-------------------------------------')

            msg_err = (f'NO NEED TO RERUN!'
                       f'\nHttpError 400'
                       f'\n'
                       f'\n-------traceback--------'
                       f'\n{err_tb}'
                       f'\n'
                       f'\n======error======='
                       f'\n{e}'
                       f'\n-------------------'
                       f'\nat: {now}')
            send_telegram_message(botID=bot_token_err, channelID=channel_id_err, message=msg_err)

        elif err_tb.find('HttpError 500') != -1:
            msg_fati = (f'NO NEED TO RERUN!'
                        f'\nHttpError 500'
                        f'\nat: {now}')
            print(msg_fati + '\n-------------------------------------')

            msg_err = (f'NO NEED TO RERUN!'
                       f'\nHttpError 500'
                       f'\n'
                       f'\n-------traceback--------'
                       f'\n{err_tb}'
                       f'\n'
                       f'\n======error======='
                       f'\n{e}'
                       f'\n-------------------'
                       f'\nat: {now}')
            send_telegram_message(botID=bot_token_err, channelID=channel_id_err, message=msg_err)

        elif err_tb.find('HttpError 503') != -1:
            msg_fati = (f'NO NEED TO RERUN!'
                        f'\nHttpError 503'
                        f'\nat: {now}')
            print(msg_fati + '\n-------------------------------------')

            msg_err = (f'NO NEED TO RERUN!'
                       f'\nHttpError 503'
                       f'\n'
                       f'\n-------traceback--------'
                       f'\n{err_tb}'
                       f'\n'
                       f'\n======error======='
                       f'\n{e}'
                       f'\n-------------------'
                       f'\nat: {now}')
            send_telegram_message(botID=bot_token_err, channelID=channel_id_err, message=msg_err)

        else:
            msg_fati = (f'YOU SHOULD PROBABLY RERUN!'
                        f'\nUndefined Error'
                        f'\nat: {now}')
            send_telegram_message(botID=bot_token_fati, channelID=channel_id_fati, message=msg_fati)
            print(msg_fati + '\n-------------------')

            msg_err = (f'YOU SHOULD PROBABLY RERUN!'
                       f'\nUndefined Error:'
                       f'\n-------------------'
                       f'\n'
                       f'\n{err_tb} '
                       f'\n-------------------'
                       f'\nat: {now}')
            send_telegram_message(botID=bot_token_err, channelID=channel_id_err, message=msg_err)
            break

    if user_used_quota > 250:
        now = time.ctime(time.time())
        period = time.time() - last_time
        last_time = time.time()
        total_user_used_quota += user_used_quota
        user_used_quota = 0

        if period < 1:
            msg_quota = (f'\n>>>>WARNINING<<<<'
                         f'quota >250 in <1s'
                         f'\ntotal: {total_user_used_quota} '
                         f'\nelapsed time: {period}'
                         f'\n-------------------'
                         f'\nat: {now}')
            send_telegram_message(botID=bot_token_quota, channelID=channel_id_quota, message=msg_quota)

        time_delta = time.time() - hr_print_time
        if time_delta > 3600:
            start_delta = time.time() - start_time
            hr_print_time = time.time()
            msg_quota = (f'1 hour passed'
                         f'\ntotal: {total_user_used_quota} '
                         f'\nrunning time: {datetime.timedelta(start_delta / 86400)}'
                         f'\naverage: {total_user_used_quota / start_delta}'
                         f'\nn_trials: {n_trials}'
                         f'\n-------------------'
                         f'\nat: {now}')
            send_telegram_message(botID=bot_token_quota, channelID=channel_id_quota, message=msg_quota)

    time.sleep(0.0004)
