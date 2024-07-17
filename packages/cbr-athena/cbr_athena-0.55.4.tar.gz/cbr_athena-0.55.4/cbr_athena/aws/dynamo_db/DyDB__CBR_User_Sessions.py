from cbr_athena.aws.dynamo_db.DyDB__CBR_Logging import DYNAMO_DB__TABLE___REGION_NAME
from cbr_athena.schemas.User_Session import User_Session
from cbr_athena.utils.Athena__CBR_Config import athena__cbr_config
from cbr_athena.utils.Utils import Utils
from osbot_aws.apis.Session import Session
from osbot_aws.aws.dynamo_db.domains.DyDB__Table_With_Timestamp import DyDB__Table_With_Timestamp
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Misc import date_time_now
from osbot_utils.utils.Status import status_error

DYNAMO_DB__TABLE_NAME__USER_SESSIONS = 'arn:aws:dynamodb:eu-west-2:470426667096:table/{env}__cbr_user_sessions'         # todo: refactor so that the region_name and account_id are not hardcoded
TABLE_USER_SESSIONS__INDEXES_NAMES   = [ 'date', 'user_name']

# todo add code to create the index for user_name which doesn't need the projection of ALL
#

class DyDB__CBR_User_Sessions(DyDB__Table_With_Timestamp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table_name    = DYNAMO_DB__TABLE_NAME__USER_SESSIONS.format(env=Utils.current_execution_env())
        self.table_indexes = TABLE_USER_SESSIONS__INDEXES_NAMES
        self.dynamo_db.client = self.client

    @cache_on_self
    def client(self):
        return Session().client('dynamodb', region_name=DYNAMO_DB__TABLE___REGION_NAME)

    def add_user_session(self, user_session : User_Session):
        if athena__cbr_config.aws_disabled():
            return None
        user_session.date = self.date_today()                                       # make sure date field is set
        document          = user_session.json()
        response          = super().add_document(document)
        if response.get('document'):
            return response.get('document', {}).get('id')
        return response

    # def get_user_session(self, session_id):
    #     with self as _:
    #         return _.quer
    def date_today(self):
        return date_time_now(date_time_format='%Y-%m-%d')       # force the correct value of date

dydb_cbr_user_sessions = DyDB__CBR_User_Sessions