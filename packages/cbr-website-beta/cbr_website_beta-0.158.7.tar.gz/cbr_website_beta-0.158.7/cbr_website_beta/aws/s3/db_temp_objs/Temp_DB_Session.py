from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import random_string
from cbr_website_beta.aws.s3.DB_Session import DB_Session


class Temp_DB_Session:
    def __init__(self, data=None, metadata=None, session_id = None, prefix='temp_db_session_'):
        self.session_data     = data
        self.session_id       = session_id or random_string(prefix=prefix)
        self.session_metadata = metadata
        self.db_session       = DB_Session(self.session_id)

    def __enter__(self):
        return self.create()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()
        pass

    def create(self):
        self.db_session.create(data=self.session_data, metadata=self.session_metadata)
        return self.db_session

    def delete(self):
        self.db_session.delete()
        return self

    def exists(self):
        return self.db_session.exists()