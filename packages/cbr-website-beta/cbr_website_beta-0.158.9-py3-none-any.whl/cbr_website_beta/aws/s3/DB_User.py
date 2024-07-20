from botocore.exceptions import ClientError
from cbr_website_beta.aws.s3.S3_DB_Base import S3_DB_Base
from osbot_utils.utils.Str import str_safe
from osbot_utils.utils.Json import json_dumps, json_loads



class DB_User(S3_DB_Base):
    def __init__(self, user_id):
        self.user_id  = str_safe(user_id)
        super().__init__()

    def __enter__(self                        ): return self
    def __exit__ (self, type, value, traceback): pass
    def __repr__ (self                        ): return f"<DB_User: {self.user_id}>"

    def create(self):
        metadata_as_str = json_dumps(self.default_metadata())
        kwargs = dict(file_contents = metadata_as_str,
                      bucket        = self.s3_bucket(),
                      key           = self.s3_key_user_metadata())
        return self.s3().file_create_from_string(**kwargs)

    def delete(self):
        kwargs = dict(bucket        = self.s3_bucket(),
                      key           = self.s3_key_user_metadata())
        return self.s3().file_delete(**kwargs)

    def exists(self):
        return self.s3().file_exists(self.s3_bucket(), self.s3_key_user_metadata())

    def metadata(self):
        try:
            raw_data = self.s3().file_contents(self.s3_bucket(), self.s3_key_user_metadata())
            return json_loads(raw_data)
        except ClientError:
            return {}

    def metadata_update(self, metadata):
        metadata_as_str = json_dumps(metadata)
        kwargs = dict(file_contents = metadata_as_str,
                      bucket        = self.s3_bucket(),
                      key           = self.s3_key_user_metadata())
        return self.s3().file_create_from_string(**kwargs)


    def default_metadata(self):
        return { 'user_id': self.user_id ,
                 'type'   : 'pytest_user'}

    # def s3_folder_user_profile(self, user_id):
    #     return f'{self.s3_folder_user_profiles()}/{user_id}'

    def get_metadata_value(self, key):
        return self.metadata().get(key)

    def s3_key_user_metadata(self):
        users_metadata     = self.s3_folder_users_metadata()
        file_user_metadata = f'{users_metadata}/{self.user_id}.json'
        return file_user_metadata

    def set_metadata_value(self, key,value):
        metadata = self.metadata()
        metadata[key] = value
        return self.metadata_update(metadata)

    def set_metadata_values(self, values):
        metadata = self.metadata()
        for key,value in values.items():
            metadata[key] = value
        return self.metadata_update(metadata)

