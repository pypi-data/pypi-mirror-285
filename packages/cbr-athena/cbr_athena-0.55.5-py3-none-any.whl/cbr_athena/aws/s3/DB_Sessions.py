from cbr_athena.aws.s3.DB_Session import DB_Session
from cbr_athena.aws.s3.S3_DB_Base import S3_DB_Base


class DB_Sessions(S3_DB_Base):

    def db_session(self, user_id):
        return DB_Session(user_id)

    def db_sessions_ids(self):
        return self.s3_folder_list(folder=self.s3_folder_users_sessions())

    def sessions(self):
        for session_id in self.db_sessions_ids():
            yield self.db_session(session_id)

    def sessions__all_data(self, max=None):
        all_data = {}
        for session in self.sessions():
            all_data[session.session_id] = session.session_data()
            if max and len(all_data) >= max:
                break
        return all_data