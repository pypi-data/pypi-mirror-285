from http.cookies import SimpleCookie

from flask                                      import request, g, has_request_context
from jinja2                                     import pass_context
from cbr_website_beta.config.CBR__Config__Data  import cbr_config
from cbr_website_beta.aws.s3.DB_Session         import DB_Session

USER_DATA_WITH_NO_CBR_TOKEN = ''
USER_DATA_WITH_BAD_FIELD    = 'bad_field'
DEFAULT_USER_NAME           = 'default_user_name'
DEFAULT_USER_GROUPS         = ['default_group']
DEFAULT_ADMIN_GROUPS        = ['CBR-Team']

class Current_User:

    filter_name = 'current_user'

    def __init__(self, app=None):
        if app:
            app.jinja_env.filters[self.filter_name] = self.current_user # todo: find a better way to register these filters

    @pass_context           # this is needed to allow the filter to access the context
    def current_user(self, context, field):
        try:
            user_data = g_user_data()
            if user_data:
                #self.decode_cbr_token(cbr_token)
                return user_data.get(field, USER_DATA_WITH_BAD_FIELD)
        except Exception as error:
            #todo: add logging
            pass
        return USER_DATA_WITH_NO_CBR_TOKEN


    def is_logged_in(self):
        return g_user_data() != {}

    # this is the key method (since it is the one that returns the user data
    #todo: need to add this to the g object, or there will be tons of calls to the S3
    def user_data_from_s3(self):
        if cbr_config.aws_disabled():
            return {}
        if request.path.endswith('js'):             # todo: add a better to handle the need to not map the user data for static requests like .js
            return {}
        cbr_token  = request.cookies.get('CBR_TOKEN')
        if cbr_token:
            admin_token   = None
            impersonating = False
            if '|' in cbr_token:                                        # todo: find a better solution to handle the user and admin token
                user_and_admin_tokens = cbr_token.split('|')            #       this was the solution put in place to work around the limitation of not being able to set multiple cookies in TBC Flask serverless environment
                if len(user_and_admin_tokens) == 2:
                    cbr_token   = user_and_admin_tokens[0]
                    admin_token = user_and_admin_tokens[1]
                    impersonating = cbr_token != admin_token
                else:
                    return {}       # something went wrong, return empty data
            if '__' in cbr_token and len(cbr_token) < 100:                                   # todo: handle better the cases when the cookie is not valid
                session_id = cbr_token
                db_session = DB_Session(session_id)
                if db_session.exists():
                    #print(f'\n>>>>>> s3 call for session: {session_id}, {request.path} \n')
                    user_data = db_session.session_data().get('data')
                    if admin_token:
                        user_data['admin_token'  ] = admin_token
                        user_data['impersonating'] = impersonating
                    else:
                        user_data['admin_token'  ] = ''
                        user_data['impersonating'] = False
                    return user_data
        return {}


# HELPER METHODS for testing
# todo: refactor these methods into a separate file and make them instance methods (i.e. not static methods)

def set_g_user_data(user_name=None, user_groups=None, jti='pytest_session'):
    user_data = {"cognito:groups": user_groups, 'jti': jti, 'username': user_name}
    if has_request_context():
        g.user_data = user_data
    return user_data

def reset_g_user_data():
    if has_request_context():               # can't access the g variable when request doesn't exist
        g.user_data = {}
        return True
    return False

def g_user_data():
    if has_request_context() and hasattr(g, 'user_data'):
        return g.user_data
    return {}

def g_user_data_current_username():
    return g_user_data().get('username')

def client__logged_in(app, user_name = None, user_groups=None):
    if not user_name:
        user_name = DEFAULT_USER_NAME
    if not user_groups:
        user_groups = DEFAULT_USER_GROUPS
    client      = app.test_client()
    app.secret_key = 'your_secret_key_for_testing'
    app.aaa = 42
    #user_data = {"cognito:groups": user_groups, 'jti': 'pytest_session' , 'username': user_name}

    # def before_request_func():
    #     g.user_data = user_data
    # app.before_request_funcs.setdefault(None, []).append(before_request_func)       # Attach the function to be called before each request within the test client session

    #user_groups = ['CBR-Team']
    #user_name = 'an_temp_user'
    user_data = set_g_user_data(user_name, user_groups)
    app.user_data = user_data                              # todo: find a better way to set this value that is currently being used to sync this data with populate_variable_g
    #with app.test_request_context():
        # Simulate login by setting session variables


    return client

    #cookie_data = Current_User().get_cookie_value_for_username(user_name=user_name, user_groups=user_groups)
    #cookie_data = ''
    ##client.set_cookie('localhost', 'CBR_TOKEN', cookie_data)
    #return client