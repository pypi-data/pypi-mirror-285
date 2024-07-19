import requests
from cbr_website_beta.aws.s3.S3                     import S3
from osbot_aws.AWS_Config                           import aws_config
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self
from osbot_utils.utils.Dev                          import pprint
from osbot_utils.utils.Json                         import json_dumps, json_parse
from osbot_utils.utils.Misc import random_guid, timestamp_utc_now

BUCKET_NAME__DB_USERS        = "{account_id}-db-users"
S3_FOLDER__USERS_METADATA    = 'users_metadata'
S3_FOLDER__USERS_SESSIONS    = 'users_sessions'
S3_FOLDER__ODIN_DATA         = 'odin_data'
S3_FOLDER__TEMP_FILE_UPLOADS = 'temp_file_uploads'

class S3_DB_Base:

    @cache_on_self
    def s3(self):
        return S3()

    @cache_on_self
    def s3_bucket(self):
        return BUCKET_NAME__DB_USERS.format(account_id=aws_config.account_id())

    def s3_bucket__temp_data(self):
        return aws_config.temp_data_bucket()

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

    def s3_temp_folder__pre_signed_urls_for_object(self, source='NA', reason='NA', who='NA', expiration=3600):
        s3_bucket          = self.s3_bucket__temp_data()
        s3_temp_folder     = self.s3_folder_temp_file_uploads()
        s3_object_name     = random_guid()
        s3_key             = f'{s3_temp_folder}/{s3_object_name}'
        pre_signed_url__get = self.s3_temp_folder__pre_signed_url(s3_bucket, s3_key, operation='get_object', expiration=expiration)
        pre_signed_url__put = self.s3_temp_folder__pre_signed_url(s3_bucket, s3_key, operation='put_object', expiration=expiration)
        pre_signed_data = dict(pre_signed_url__get = pre_signed_url__get ,
                               pre_signed_url__put = pre_signed_url__put ,
                               reason              = reason              ,
                               timestamp           = timestamp_utc_now() ,
                               source              = source              ,
                               who                 = who                 )
        return pre_signed_data

    def s3_temp_folder__pre_signed_url(self, s3_bucket, s3_key, operation,expiration=3600):
        create_kwargs = dict(bucket_name=s3_bucket,
                             object_name=s3_key,
                             operation=operation,
                             expiration=expiration)
        pre_signed_url = self.s3().create_pre_signed_url(**create_kwargs)
        return pre_signed_url

    def s3_temp_folder__download_string(self, pre_signed_url):
        response = requests.get(pre_signed_url)
        if response.status_code == 200:
            return response.text
        pprint(response)

    def s3_temp_folder__upload_string(self, pre_signed_url, file_contents):
        response = requests.put(pre_signed_url, data=file_contents)
        if response.status_code == 200:
            return True
        else:
            return False

    def setup(self):
        bucket_name = self.s3_bucket()
        if self.s3().bucket_not_exists(bucket_name):
            kwargs = dict(bucket = bucket_name                ,
                          region = aws_config.region_name())
            assert self.s3().bucket_create(**kwargs).get('status') == 'ok'
        return True


    def s3_folder_users_sessions(self):
        return S3_FOLDER__USERS_SESSIONS

    def s3_folder_odin_data(self):
        return S3_FOLDER__ODIN_DATA

    def s3_folder_users_metadata(self):
        return S3_FOLDER__USERS_METADATA

    def s3_folder_temp_file_uploads(self):
        return S3_FOLDER__TEMP_FILE_UPLOADS
