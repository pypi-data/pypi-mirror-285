
from cbr_website_beta.aws.s3.S3_DB_Base import S3_DB_Base
from osbot_utils.utils.Misc             import lower, random_string_and_numbers
from cbr_website_beta.aws.s3.DB_User    import DB_User

class DB_Users(S3_DB_Base):

    def db_user(self, user_id):
        return DB_User(user_id)

    def db_users(self):
        db_users = []
        for user_id in self.db_users_ids():
            db_users.append(self.db_user(user_id))
        return db_users

    def db_users_ids(self):
        # todo: refactor all these .s3() calls to helper methods
        # todo: refactor this method to use self.s3().folder_list(s3_bucket=self.s3_bucket(), parent_folder=parent_folder, return_full_path=return_full_path)
        s3_keys = self.s3().find_files(self.s3_bucket(), self.s3_folder_users_metadata())  # Fetch S3 keys for user metadata files
        usernames = []                                                                           # Initialize an empty list to store usernames
        for s3_key in s3_keys:
            filename = s3_key.split('/')[-1]                                                     # Extract the filename from the S3 key
            username = filename.replace('.json', '')                                             # Remove the '.json' extension to get the username
            usernames.append(username)                                                           # Append the username to the list

        return usernames

    def random_db_user(self, prefix='pytest_user'):
        user_id = self.random_user_id(prefix=prefix)
        return self.db_user(user_id)

    def random_user_id(self, prefix='pytest_user'):
        return f'{prefix}__{lower(random_string_and_numbers())}'

    def users__all_metadatas(self,max=None):
        user_data = {}
        db_users = self.db_users()
        if max:
            db_users = db_users[:max]
        for db_user in db_users:
            user_data[db_user.user_id] = db_user.metadata()

        return user_data
