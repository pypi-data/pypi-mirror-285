from cbr_website_beta.users.CBR_Users_Config import CBR_Users_Config
from osbot_utils.utils.Json import json_dumps, json_loads
from osbot_utils.utils.Str import str_safe

FILE_NAME__USER_METADATA = 'metadata.json'
DEFAULT_USER_TYPE        = 'tbd'

class CBR_User(CBR_Users_Config):

    def __init__(self, user_id):
        self.user_id   = str_safe(user_id) or DEFAULT_USER_TYPE
        super().__init__()

    def create(self, user_type=DEFAULT_USER_TYPE):
        metadata = self.default_metadata(user_type=user_type)
        return self.create_from_metadata(metadata)

    def create_from_metadata(self, metadata):
        return self.metadata_update(metadata)

    def default_metadata(self, user_type=DEFAULT_USER_TYPE):
        return { 'user_id'     : self.user_id ,
                 'user_type'   : user_type    }

    def delete(self):
        file_key        = self.s3_file__user_metadata()
        return self.s3_delete_file(file_key)

    def exists(self):
        s3_file__user_metadata = self.s3_file__user_metadata()
        return self.s3_file_exists(s3_file__user_metadata)

    def metadata(self):
        s3_file__user_metadata = self.s3_file__user_metadata()
        s3_file_contents       = self.s3_file_contents(s3_file__user_metadata)
        metadata               = json_loads(s3_file_contents)
        return metadata

    def metadata_update(self, metadata):
        metadata_as_str = json_dumps(metadata)
        file_key        = self.s3_file__user_metadata()
        return self.s3_update_file(file_key=file_key, file_contents=metadata_as_str)

    def metadata_set_value(self, key,value):
        metadata = self.metadata()
        metadata[key] = value
        return self.metadata_update(metadata)

    def metadata_set_values(self, values):
        metadata = self.metadata()
        for key,value in values.items():
            metadata[key] = value
        return self.metadata_update(metadata)

    def s3_file__user_metadata(self):
        return f'{self.s3_folder__user()}/{FILE_NAME__USER_METADATA}'

    def s3_folder__user(self):
        #s3_bucket = str_safe(self.config.s3_bucket())
        user_data = str_safe(self.s3_folder_users_data())
        return f'{user_data}/{self.user_id}'
