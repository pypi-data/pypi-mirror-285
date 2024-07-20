import requests

from cbr_website_beta.bots.Athena_Rest_API              import Athena_Rest_API
from cbr_website_beta.bots.schemas.Create_User_Session  import Create_User_Session
from cbr_website_beta.cbr__flask.utils.current_server   import current_server
from osbot_aws.AWS_Config import aws_config
from osbot_utils.utils.Status import status_ok, status_error


ERROR_MESSAGE__COGNITO_AUTH = 'could not authenticate user, please contact the Support team'

class Cognito_Auth_Flow:

    def convert_auth_code_to_auth_data(self, sign_in_code, redirect_uri):
        project     = 'the-cbr-beta.auth'
        region      = "eu-west-2"
        client_id   = "5ij6l5kdho4umoks5rjfh9cbid"
        grant_type  = "authorization_code"

        token_url = f"https://{project}.{region}.amazoncognito.com/oauth2/token"

        payload = {
            "grant_type"  : grant_type,
            "client_id"   : client_id            ,
            "code"        : sign_in_code,
            "redirect_uri": redirect_uri
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(token_url, data=payload, headers=headers)
        return response.json()

    def create_cbr_token_cookie_from_cognito_code(self, sign_in_code):
        try:

            aws_config.set_aws_session_region_name('eu-west-2')     # todo: remove this from here
            redirect_uri   = f"{current_server()}web/sign-in"
            cognito_tokens = self.convert_auth_code_to_auth_data(sign_in_code, redirect_uri)
            access_token   = cognito_tokens.get('access_token')
            user_info      = self.parse_jwt_token(access_token)
            metadata       = {'source': 'cognito'}
            db_session     = self.create_session(user_info, metadata)           # todo: take away this session
            session_id     = self.create_session_in_athena(user_info, cognito_tokens)          # create the session and use the current document id as the cookie session id
            cookie_value   = session_id
            #cookie_value  = db_session.session_id                                               # give the session_id to the user as a cookie
            data = {'cookie_value': cookie_value, 'user_info': user_info}
            return status_ok(data=data)
        except Exception as error:
            return status_error(message = ERROR_MESSAGE__COGNITO_AUTH ,
                                error   = f'{error}'                  )

    def create_session(self, user_info, metadata=None):
        from cbr_website_beta.aws.s3.DB_Sessions import DB_Sessions
        db_sessions = DB_Sessions()
        user_name   = user_info.get('username')
        user_jti    = user_info.get('jti')
        session_id  = f"{user_name}__{user_jti}"
        db_session  = db_sessions.db_session(session_id)
        db_session.create(user_info, metadata)
        return db_session

    def create_session_in_athena(self, user_info, cognito_tokens):
        user_name       = user_info.get('username')
        session_id      = user_info.get('jti')
        source          = 'CognitoAuth'
        athena_rest_api = Athena_Rest_API()
        kwargs = dict(user_name     = user_name ,
                      session_id    = session_id,
                      source        = source    ,
                      cognito_tokens = cognito_tokens)
        create_user_session = Create_User_Session(**kwargs)
        response            = athena_rest_api.user__create_session(create_user_session)
        if 'session_id' in response:
            session_id           = response.get('session_id')
            return session_id
        raise Exception(f'no session_id in response: {response}')



    def parse_jwt_token(self, access_token):
        import jwt
        decoded_access_token = jwt.decode(access_token, algorithms=["RS256"], options={"verify_signature": False})
        return decoded_access_token
