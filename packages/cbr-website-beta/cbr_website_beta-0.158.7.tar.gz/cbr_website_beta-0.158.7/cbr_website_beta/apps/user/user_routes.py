from cbr_website_beta.apps.user.user_profile                    import user_profile
from cbr_website_beta.aws.cognito.Cognito_Auth_Flow             import Cognito_Auth_Flow
from cbr_website_beta.cbr__flask.decorators.allow_annonymous    import allow_anonymous
from cbr_website_beta.apps.user                                 import blueprint
from flask                                                      import redirect, request, make_response, render_template, jsonify, g
from cbr_website_beta.cbr__flask.filters.Current_User           import DEFAULT_ADMIN_GROUPS
from cbr_website_beta.cbr__flask.utils.current_server           import current_server

LOCAL_DEV_SERVER     = 'http://localhost:5000/'
COGNITO_PROJECT      = 'the-cbr-beta'
COGNITO_REGION       = 'eu-west-2'
COGNITO_CLIENT_ID    = '5ij6l5kdho4umoks5rjfh9cbid'
COGNITO_SIGN_IN      = f'https://{COGNITO_PROJECT}.auth.{COGNITO_REGION}.amazoncognito.com/login?client_id={COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+phone&'
COGNITO_SIGN_OUT     = f'https://{COGNITO_PROJECT}.auth.{COGNITO_REGION}.amazoncognito.com/logout?client_id={COGNITO_CLIENT_ID}&response_type=code&scope=email+openid+phone&'
EXPECTED_USER__HOME  = [ '/admin/impersonate_user/<user_token>' ,
                         '/admin/restore_admin_user'            ,
                         '/login'                               ,
                         '/logout'                              ,
                         '/sign-in'                             ,
                         '/sign-out'                            ,
                         '/unauthorized'                        ,
                         '/user/profile'                        ]


@blueprint.route('/login')
@allow_anonymous
def login():
    url = COGNITO_SIGN_IN + f"redirect_uri={current_server()}web/sign-in"
    return redirect(url)

@blueprint.route('/sign-in')
@allow_anonymous
def sign_in():
    sign_in_code      = request.args.get('code')                    # todo: refactor this logic out of this method

    cognito_auth_flow = Cognito_Auth_Flow()
    result = cognito_auth_flow.create_cbr_token_cookie_from_cognito_code(sign_in_code=sign_in_code)

    if result.get('status') != 'ok':
        return result                                                # todo: add better error page
    cookie_data = result.get('data')
    cbr_token       = cookie_data.get('cookie_value')
    user_info       = cookie_data.get('user_info' , {})
    role            = user_info.get('cognito:groups')
    render_kwargs   = {"template_name_or_list": "/home/accounts/logging_in.html",
                     "session_id" : cbr_token                                        }
    response_html   = render_template(**render_kwargs)
    #response_html     = render_template('home/accounts/logging_in.html')
    response        = make_response(response_html)


    if role == DEFAULT_ADMIN_GROUPS:                                            # if the user is admin then use both values for cookie (which is mainly used for making UI decisions,i.e. this CANNOT be a security control)
        cbr_token = f"{cbr_token}|{cbr_token}"                                  # todo: figure out why seeting up two cookies here didn't work, initial version of this code was seeting an CBR_ADMIN_TOKEN, but that was not working in prod
        response.set_cookie('CBR_TOKEN', cbr_token)
    else:
        response.set_cookie('CBR_TOKEN', cbr_token)
    return response




@blueprint.route('/unauthorized')
@allow_anonymous
def unauthorized():
    return render_template('home/accounts/unauthorized.html')

@blueprint.route('/sign-out')
def sign_out():
    redirect_to = redirect(current_server())
    response    = make_response(redirect_to)
    response.set_cookie('CBR_TOKEN'      , '', expires=0)
    #response.set_cookie('CBR_ADMIN_TOKEN', '', expires=0)                  # todo: figure out why this is not working, in prod, only the first cookie is beeing reset ok
    return response

# todo: see if we need this (since at the moment this is not wired)
@blueprint.route('/logout')
@allow_anonymous
def logout():
    url = COGNITO_SIGN_OUT + f"logout_uri={current_server()}sign-out"

    return redirect(url)

@blueprint.route('/user/profile', methods=['GET', 'POST'])
@allow_anonymous
def profile():
    return user_profile()


@blueprint.route('/admin/impersonate_user/<user_token>', methods=['GET'])            # todo: change to POST method
def admin__impersonate_user(user_token):
    redirect_to = redirect(current_server())
    response = make_response(redirect_to)
    from flask import g
    if g.user_data:                                                                 # todo: refactor all this login into an impersonation class
        if g.user_data.get('admin_token'):
            admin_token = g.user_data.get('admin_token')
            impersonated_cookie_value = f'{user_token}|{admin_token}'
            response.set_cookie('CBR_TOKEN', impersonated_cookie_value)
    return response

@blueprint.route('/admin/restore_admin_user', methods=['GET'])                      # todo: change to POST method
def admin__restore_admin_user():
    redirect_to = redirect(current_server())
    response = make_response(redirect_to)
    from flask import g
    if g.user_data:                                                                  # todo: refactor all this login into an impersonation class
        if g.user_data.get('admin_token'):
            admin_token = g.user_data.get('admin_token')
            restored_cookie_value = f'{admin_token}|{admin_token}'
            response.set_cookie('CBR_TOKEN', restored_cookie_value)
    return response


# @blueprint.route('/user/save-chat', methods=['POST'])
# def user_save_chat():
#     return jsonify({'status': 'warning', 'message': 'temporarily disabled'})
    # if not g.user_name:
    #     return jsonify({'status': 'error', 'message': 'there was no user available'}), 400
    #
    # if request.is_json:
    #     try:
    #         user_name = g.user_name
    #         post_data   = request.get_json()
    #
    #         thread_id   = post_data.get('thread_id') or random_uuid()
    #         index       = post_data.get('index')
    #         thread_data = post_data.get('thread_data')
    #         data_type   = post_data.get('data_type')
    #         dydb_chat_threads = DyDB__Chat_Threads()
    #         result = dydb_chat_threads.add_chat_thread(user_name, thread_id, index, data_type, thread_data)
    #         return jsonify({'status': 'ok', 'result': result}), 200
    #     except Exception as error:
    #         return jsonify({'status': 'error', 'message': f'Error: {error}'}), 500
    # else:
    #     return jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400

