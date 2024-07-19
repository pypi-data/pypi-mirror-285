from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

class CBR_Logging(Kwargs_To_Self):
    # auto populated
    id          : str           # to be set by Dynamo_DB__Table
    timestamp   : int           # to be set by the request
    # indexes
    date        : str   = 'NA'
    level       : str   = 'NA'
    message     : str   = 'NA'
    source      : str   = 'NA'
    topic       : str   = 'NA'

    # other
    city        : str   = 'NA'
    country     : str   = 'NA'
    user_id     : str   = 'NA'
    extra_data  : dict
