from os import environ

from cbr_athena.aws.dynamo_db.DyDB__CBR_User_Sessions   import DyDB__CBR_User_Sessions
from cbr_athena.schemas.for_fastapi.Create_User_Session import Create_User_Session
from cbr_athena.schemas.User_Session                    import User_Session
from osbot_aws.apis.Cognito_IDP                         import Cognito_IDP
from osbot_utils.base_classes.Kwargs_To_Self            import Kwargs_To_Self


class Odin__User_Auth(Kwargs_To_Self):
    dydb_user_sessions : DyDB__CBR_User_Sessions
    cognito            : Cognito_IDP


    def cognito__client_id(self):
        return environ.get("COGNITO_CLIENT_ID")

    def cognito__user_data(self, user_name):
        return self.cognito.user_info(user_pool_id=self.cognito__user_pool_id(), user_name=user_name)

    def cognito__user_login(self, username, password):
        client_id = self.cognito__client_id()
        return self.cognito.auth_initiate(client_id=client_id, username=username, password=password)

    def cognito__user_pool_id(self):
        return environ.get("COGNITO_USER_POOL_ID")

    def session_data_from_session_id(self, session_id):
        return self.dydb_user_sessions.document(session_id)

    def user_sessions(self, user_name):
        return self.dydb_user_sessions.query_index('user_name', 'S', user_name)


    # todo: the workflow below needs to be changed to support the new auth flow that is 100% based on web services

    # todo: delete method since this is just returning the user cognito data
    def user_session_and_data(self, user_name, session_id):
        cognito_data    = self.cognito__user_data(user_name=user_name)
        if cognito_data:
            return { #'cognito_session' : cognito_session,
                     'cognito_data'    : cognito_data   }
        return {}


    def dydb__create_session(self, user_name, session_id, source=None, cognito_tokens=None):
        user_session = self.dydb__user_session(user_name, session_id, source=source, cognito_tokens=cognito_tokens)
        if user_session:
            return self.dydb_user_sessions.add_user_session(user_session)

    def dydb__user_session(self, user_name, session_id, source=None, cognito_tokens=None):
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

    def create_user_session(self, create_user_session: Create_User_Session):
        kwargs = dict(user_name      = create_user_session.user_name                     ,
                      session_id     = create_user_session.session_id                    ,
                      source         = create_user_session.source         or 'Athena_API',
                      cognito_tokens = create_user_session.cognito_tokens or {}          )
        session_id = self.dydb__create_session(**kwargs)
        return session_id

    def s3_session_id(self, user_name, session_id):
        return f'{user_name}__{session_id}'

    def resolve_display_name(self, session_data, user_data):
        display_name = session_data.get('user_name')
        if user_data.get('username'):
            display_name = user_data.get('username')
        return display_name
