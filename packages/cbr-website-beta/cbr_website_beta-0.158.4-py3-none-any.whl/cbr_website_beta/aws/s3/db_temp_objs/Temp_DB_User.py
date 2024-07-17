from cbr_website_beta.aws.s3.DB_Users import DB_Users


class Temp_DB_User:

    def __init__(self, prefix='pytest__temp_db_user'):
        self.db_users = DB_Users()
        self.db_users.s3().dont_use_threads()
        self.db_user  = self.db_users.random_db_user(prefix=prefix)

    def __enter__(self):
        assert self.db_user.create() is True
        return self.db_user

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self.db_user.delete() is True
