from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class Chat_Thread(Kwargs_To_Self):
    # auto populated
    id              : str           # to be set by Dynamo_DB__Table
    timestamp       : int           # to be set by the request
    # indexes
    date            : str
    user_name       : str
    chat_thread_id  : str

    # other
    session_id      : str   = 'NA'
    user_prompt     : str   = 'NA'
    gpt_response    : str   = 'NA'
    source          : str   = 'NA'
    prompt_data     : dict
    request_headers : dict