from cbr_athena.aws.s3.S3_DB_Base import S3_DB_Base
from osbot_utils.utils.Misc             import timestamp_utc_now
from osbot_utils.utils.Str              import str_safe

FILE_NAME_CURRENT_SESSION = 'session-data.json'

class DB_Session(S3_DB_Base):

    def __init__(self, session_id):
        self.session_id  = str_safe(session_id)
        super().__init__()

    def __enter__(self                        ): return self
    def __exit__ (self, type, value, traceback): pass
    def __repr__ (self                        ): return f"<DB_Session: {self.session_id}>"

    def cbr_cookie(self):
        return f"CBR_TOKEN={self.session_id}"

    def create(self, data=None, metadata=None):
        session_data = self.create_session_data(data, metadata)
        s3_key       = self.s3_key_user_session()
        return self.s3_save_data(data=session_data, s3_key=s3_key)

    def create_session_data(self, data=None, metadata=None):
        session_data = { 'session_id' : self.session_id     ,
                         'timestamp'  : timestamp_utc_now() ,
                         'data'       : data or {}          }
        if metadata:
            session_data.update(metadata)
        return session_data

    def delete(self):
        return self.s3_file_delete(self.s3_key_user_session())

    def exists(self):
        return self.s3_file_exists(self.s3_key_user_session())

    def s3_key_user_session(self):
        users_metadata     = self.s3_folder_users_sessions()
        file_user_metadata = f'{users_metadata}/{self.session_id}/{FILE_NAME_CURRENT_SESSION}'
        return file_user_metadata

    def session_data(self, include_timestamp=True):
        if self.exists():
            session_data = self.s3_file_data(self.s3_key_user_session())
            if include_timestamp is False and 'timestamp' in session_data:
                del session_data['timestamp']
            return session_data
        return {}

    def source(self):
        return self.session_data().get('source')