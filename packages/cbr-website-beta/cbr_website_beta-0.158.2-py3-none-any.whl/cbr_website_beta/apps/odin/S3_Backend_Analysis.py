from cbr_website_beta.aws.s3.DB_Odin_Data import DB_Odin_Data
from cbr_website_beta.aws.s3.DB_Sessions import DB_Sessions
from cbr_website_beta.aws.s3.DB_Users import DB_Users
from osbot_utils.testing.Duration import Duration
from osbot_utils.utils.Dev import pprint


class S3_Backend_Analysis:

    def __init__(self):
        self.sessions  = DB_Sessions ()
        self.users     = DB_Users    ()
        self.odin_data = DB_Odin_Data()

    def s3_update_db_sessions_status(self):
        sessions_data = self.sessions.sessions__all_data()
        return self.odin_data.current_sessions__save_to_s3(sessions_data)

    def s3_update_db_users_metadata(self):
        users_metadatas = self.users.users__all_metadatas()
        return self.odin_data.users_metadatas__save(users_metadatas)



