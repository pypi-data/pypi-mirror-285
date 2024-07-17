from os import environ

from cbr_athena.aws.dynamo_db.DyDB__CBR_User_Sessions import DyDB__CBR_User_Sessions
from cbr_athena.aws.s3.DB_Session import DB_Session
from cbr_athena.schemas.User_Session import User_Session
from osbot_aws.apis.Cognito_IDP import Cognito_IDP
from osbot_utils.utils.Dev import pprint


# todo: this class is based on the S3 data storage of sessions which is going to be replaced with the version in DynamoDB
#       the current idea is to only use the S3 data storage as an archive of past sessions and the dynamo_db is going to be the main Auth store
class Data__User_Session:

    def __init__(self):
        self.cognito = Cognito_IDP()
        self.dydb_user_sessions = DyDB__CBR_User_Sessions()

    def user_session_and_data(self, user_name, session_id):
        cognito_session = self.s3_cognito_session(user_name=user_name, session_id=session_id)
        cognito_data    = self.user_cognito_data(user_name=user_name)
        if cognito_session:
            return { 'cognito_session' : cognito_session,
                     'cognito_data'    : cognito_data   }
        return {}

    def db_session(self, user_name, session_id):
        s3_session_id = f'{user_name}__{session_id}'
        db_session = DB_Session(session_id=s3_session_id)
        if db_session.exists():
            return db_session

    def s3_cognito_session(self, user_name, session_id):
        db_session = self.db_session(user_name, session_id)
        if db_session:
            return db_session.session_data().get('data')
        return {}

    def s3_session_id(self, user_name, session_id):
        return f'{user_name}__{session_id}'

    def user_cognito_data(self, user_name):
        user_pool_id = self.user_pool_id()
        if user_pool_id:
            return self.cognito.user_info(user_pool_id=user_pool_id, user_name=user_name)
        return {}           # todo: add to healthcheck the user_pool_id setup, also  the add log message that the cognito user pool id is not set

    def user_pool_id(self):
        return environ.get("COGNITO_USER_POOL_ID")

    def user_session(self, user_name, session_id, source=None, cognito_tokens=None):
        user_session_and_data = self.user_session_and_data(user_name, session_id)
        if user_session_and_data:
            session_data = user_session_and_data.get('cognito_session')
            user_data    = user_session_and_data.get('cognito_data'   )
            display_name = self.resolve_display_name(session_data, user_data)
            dydb_id      = self.s3_session_id(user_name, session_id   )
            source       = source or 'NA'
            kwargs       = dict(id             = dydb_id       ,
                                display_name   = display_name  ,
                                user_name      = user_name     ,
                                session_id     = session_id    ,
                                s3_session_id  = dydb_id       ,
                                source         = source        ,
                                session_data   = session_data  ,
                                user_data      = user_data     ,
                                cognito_tokens = cognito_tokens)
            user_session = User_Session(**kwargs)
            user_session.id = dydb_id
            return user_session

    def resolve_display_name(self, session_data, user_data):
        display_name = session_data.get('user_name')
        if user_data.get('username'):
            display_name = user_data.get('username')
        return display_name

    def dydb__create_session(self, user_name, session_id, source=None, cognito_tokens=None):
        user_session = self.user_session(user_name, session_id, source=source, cognito_tokens=cognito_tokens)
        if user_session:
            return self.dydb_user_sessions.add_user_session(user_session)
