from functools import cache

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.S3 import S3
from osbot_utils.utils.Json import json_dumps, json_parse

BUCKET_NAME__DB_USERS     = "{account_id}-db-users"
S3_FOLDER__USERS_METADATA = 'users_metadata'
S3_FOLDER__USERS_SESSIONS = 'users_sessions'
S3_FOLDER__ODIN_DATA      = 'odin_data'

class S3_DB_Base:

    def __init__(self):
        self.aws_config  = AWS_Config()
        self.account_id  = self.aws_config.account_id()
        self.region_name = self.aws_config.region_name()

    @cache
    def s3(self):
        return S3()

    @cache
    def s3_bucket(self):
        return BUCKET_NAME__DB_USERS.format(account_id=self.account_id)

    def s3_file_contents(self, s3_key):
        try:
            return self.s3().file_contents(self.s3_bucket(), s3_key)
        except Exception:
            return {}

    def s3_file_data(self, s3_key):
        return json_parse(self.s3_file_contents(s3_key))

    def s3_file_exists(self, s3_key):
        bucket = self.s3_bucket()
        return self.s3().file_exists(bucket, s3_key)

    def s3_file_delete(self, s3_key):
        kwargs = dict(bucket = self.s3_bucket(),
                      key    = s3_key          )
        return self.s3().file_delete(**kwargs)

    def s3_folder_contents(self, folder, return_full_path=False):
        return self.s3().folder_contents(s3_bucket=self.s3_bucket(), parent_folder=folder, return_full_path=return_full_path)

    def s3_folder_files(self, folder, return_full_path=False):
        return self.s3().folder_files(s3_bucket=self.s3_bucket(), parent_folder=folder, return_full_path=return_full_path)

    def s3_folder_list(self, folder, return_full_path=False):
        return self.s3().folder_list(s3_bucket=self.s3_bucket(), parent_folder=folder, return_full_path=return_full_path)

    def s3_save_data(self, data, s3_key):
        data_as_str = json_dumps(data)
        kwargs = dict(file_contents = data_as_str     ,
                      bucket        = self.s3_bucket(),
                      key           = s3_key          )
        return self.s3().file_create_from_string(**kwargs)

    # def setup(self):
    #     bucket_name = self.s3_bucket()
    #     if self.s3().bucket_not_exists(bucket_name):
    #         kwargs = dict(bucket = bucket_name                ,
    #                       region = self.region_name)
    #         assert self.s3().bucket_create(**kwargs).get('status') == 'ok'
    #     return True


    def s3_folder_users_sessions(self):
        return S3_FOLDER__USERS_SESSIONS

    def s3_folder_odin_data(self):
        return S3_FOLDER__ODIN_DATA

    def s3_folder_users_metadata(self):
        return S3_FOLDER__USERS_METADATA

