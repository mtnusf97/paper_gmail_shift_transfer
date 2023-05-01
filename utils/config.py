from dotmap import DotMap


scopes = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

make_read_body = {"addLabelIds": [], "removeLabelIds": ['UNREAD']}

bot_token = "6012344665:AAHWB1qnazCeh6Rk2A0PE5WcEoZ6GVm3FAU"
channel_id = 'codenewsforfati'


def user_configs(who='fati'):
    user_config = DotMap()

    if who == 'fati':
        user_config.log_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\logs'
        user_config.credentials_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\tokens_and_creds\credentials.json'
        user_config.token_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\tokens_and_creds\token.json'
        user_config.unable_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\unable_times.json'
        user_config.used_quota_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\used_quota.txt'
        user_config.error_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\errors'
    elif who == 'mtn':
        user_config.log_path = '/home/matin/paper_gmail_shift_transfer/logs'
        user_config.credentials_path = '/home/matin/paper_gmail_shift_transfer/tokens_and_creds/credentials.json'
        user_config.token_path = '/home/matin/paper_gmail_shift_transfer/tokens_and_creds/token.json'
        user_config.unable_path = '/home/matin/paper_gmail_shift_transfer/utils/unable_times.json'
        user_config.used_quota_path = '/home/matin/paper_gmail_shift_transfer/utils/used_quota.txt'
        user_config.error_path = '/home/matin/paper_gmail_shift_transfer/errors'
    else:
        raise Exception('The person who is running this code is unknown')

    return user_config
