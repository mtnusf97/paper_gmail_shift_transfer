from dotmap import DotMap


scopes = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

make_read_body = {"addLabelIds": [], "removeLabelIds": ['UNREAD']}

bot_token_fati = "6012344665:AAHWB1qnazCeh6Rk2A0PE5WcEoZ6GVm3FAU"
channel_id_fati = 'codenewsforfati'

bot_token_err = "6770485318:AAHGoz0QM0BdKayhi9uXADAR9TQHNCHbJsg"
channel_id_err = 'codeerrorsformatin'

bot_token_quota = "6935242835:AAHEO53hwysGCXE8ttdrJdd9H2VpjQXr3Do"
channel_id_quota = 'usedquotaformatin'


def user_configs(who='fati'):
    user_config = DotMap()

    if who == 'fati':
        user_config.log_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\logs'
        user_config.credentials_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\tokens_and_creds\credentials.json'
        user_config.token_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\tokens_and_creds\token.json'
        user_config.fixed_unable_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\utils\fixed_unable_times.json'
        user_config.occasional_unable_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\utils\occasional_unable_times.json'
        user_config.used_quota_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\utils\used_quota.txt'
        user_config.error_path = r'C:\Users\Fatemeh\Desktop\paper_gmail_shift_transfer\errors'
    if who == 'simone':
        user_config.log_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\logs'
        user_config.credentials_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\tokens_and_creds\credentials.json'
        user_config.token_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\tokens_and_creds\token.json'
        user_config.fixed_unable_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\utils\fixed_unable_times.json'
        user_config.occasional_unable_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\utils\occasional_unable_times.json'
        user_config.used_quota_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\utils\used_quota.txt'
        user_config.error_path = r'C:\Users\Simone\Desktop\paper_gmail_shift_transfer\errors'
    elif who == 'fati_new':
        user_config.log_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\logs'
        user_config.credentials_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\tokens_and_creds\credentials.json'
        user_config.token_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\tokens_and_creds\token.json'
        user_config.fixed_unable_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\utils\fixed_unable_times.json'
        user_config.occasional_unable_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\utils\occasional_unable_times.json'
        user_config.used_quota_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\utils\used_quota.txt'
        user_config.error_path = r'C:\Users\Alvand\Desktop\paper_gmail_shift_transfer\errors'
    elif who == 'mtn':
        user_config.log_path = '/home/matin/paper_gmail_shift_transfer/logs'
        user_config.credentials_path = '/home/matin/paper_gmail_shift_transfer/tokens_and_creds/credentials.json'
        user_config.token_path = '/home/matin/paper_gmail_shift_transfer/tokens_and_creds/token.json'
        user_config.fixed_unable_path = '/home/matin/paper_gmail_shift_transfer/utils/fixed_unable_times.json'
        user_config.occasional_unable_path = '/home/matin/paper_gmail_shift_transfer/utils/occasional_unable_times.json'
        user_config.used_quota_path = '/home/matin/paper_gmail_shift_transfer/utils/used_quota.txt'
        user_config.error_path = '/home/matin/paper_gmail_shift_transfer/errors'
    elif who == 'mtn_mac':
        user_config.log_path = '/Users/matin/paper_gmail_shift_transfer/logs'
        user_config.credentials_path = '/Users/matin/paper_gmail_shift_transfer/tokens_and_creds/credentials.json'
        user_config.token_path = '/Users/matin/paper_gmail_shift_transfer/tokens_and_creds/token.json'
        user_config.fixed_unable_path = '/Users/matin/paper_gmail_shift_transfer/utils/fixed_unable_times.json'
        user_config.occasional_unable_path = '/Users/matin/paper_gmail_shift_transfer/utils/occasional_unable_times.json'
        user_config.used_quota_path = '/Users/matin/paper_gmail_shift_transfer/utils/used_quota.txt'
        user_config.error_path = '/Users/matin/paper_gmail_shift_transfer/errors'
    else:
        raise Exception('The person who is running this code is unknown')

    return user_config
