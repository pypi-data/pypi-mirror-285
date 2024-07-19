from cbr_website_beta.users.CBR_User import CBR_User
from cbr_website_beta.users.CBR_Users_Config import CBR_Users_Config
from osbot_utils.utils.Misc import random_text


class CBR_Users(CBR_Users_Config):

    def __init__(self):
        super().__init__()
        #self.db_users     = DB_Users()
        #self.cognito      = Cognito_IDP()
        self.user_pool_id = 'eu-west-2_22vkoIJRJ'


    # def cognito_user_pool(self):
    #     return self.cognito.user_pool(self.user_pool_id)
    #
    # def cognito_users(self, limit=10):
    #     return self.cognito.users(self.user_pool_id,limit=limit)
    #
    # def cognito_user(self, user_name):
    #     return self.cognito.user(self.user_pool_id, user_name=user_name)

    def user(self, user_id):
        return CBR_User(user_id)

    def users_names(self):
        return self.s3_folder_list(self.s3_folder_users_data())

    def random_user(self):
        user_id = random_text('cbr_random_user').lower()
        return self.user(user_id=user_id)



