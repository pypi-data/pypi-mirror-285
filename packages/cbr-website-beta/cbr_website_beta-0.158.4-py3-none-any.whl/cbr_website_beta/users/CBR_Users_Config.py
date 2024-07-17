from osbot_aws.AWS_Config                           import aws_config
from osbot_aws.apis.S3                              import S3
from osbot_utils.decorators.methods.cache_on_self   import cache_on_self

BUCKET_NAME__DB_USERS = "{account_id}-db-users"     # todo: refactor this into a a
S3_FOLDER__USERS_DATA = 'users_data'

class CBR_Users_Config:


    @cache_on_self
    def s3(self):
        return S3()

    def s3_create_file(self, file_key, file_contents):
        if self.s3_file_exists(file_key) is False:
            self.s3_update_file(file_key, file_contents)

            if self.s3_file_exists(file_key):
                return True
            return False            # todo add log entry to cover this case
        return False

    # update or create file
    def s3_update_file(self, file_key, file_contents):
        kwargs = dict(file_contents = file_contents   ,
                      bucket        = self.s3_bucket(),
                      key           = file_key        )
        self.s3().file_create_from_string(**kwargs)
        return True

    def s3_delete_file(self, file_key):
        if self.s3_file_exists(file_key):
            self.s3().file_delete(self.s3_bucket(), file_key)
            if self.s3_file_exists(file_key) is False:
                return True                                 # todo: add log entry to deal with this, which shouldn't realy never happen
        return False

    def s3_file_contents(self, file_key):
        return self.s3().file_contents(self.s3_bucket(), file_key)

    def s3_file_exists(self, file_key):
        return self.s3().file_exists(self.s3_bucket(), file_key)

    @cache_on_self
    def s3_bucket(self):
        return BUCKET_NAME__DB_USERS.format(account_id=aws_config.account_id())

    def s3_folder_users_data(self):
        return f'{S3_FOLDER__USERS_DATA}'

    def s3_folder_list(self, target_folder):
        return self.s3().folder_list(self.s3_bucket(), target_folder)

    def s3_setup(self):     # todo: write this up
        bucket_name = self.s3_bucket()
        if self.s3().bucket_not_exists(bucket_name):
            kwargs = dict(bucket = bucket_name                ,
                          region = aws_config.region_name())
            assert self.s3().bucket_create(**kwargs).get('status') == 'ok'
        return True