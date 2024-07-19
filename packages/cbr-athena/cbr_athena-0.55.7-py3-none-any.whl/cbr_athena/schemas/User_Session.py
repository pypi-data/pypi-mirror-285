from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self


class User_Session(Kwargs_To_Self):
    # auto populated
    id             : str                       # will be set by Dynamo_DB__Table
    timestamp      : int                       # will be set by DyDB__Table_With_GSI
    date           : str                       # will be set by DyDB__CBR_User_Sessions
    # indexes

    display_name   : str                        # this is the value to show in the UI
    user_name      : str                        # this is cognito username
    session_id     : str
    s3_session_id  : str
    # extra data
    cognito_tokens : dict
    source         : str = 'NA'
    session_data   : dict
    user_data      : dict

