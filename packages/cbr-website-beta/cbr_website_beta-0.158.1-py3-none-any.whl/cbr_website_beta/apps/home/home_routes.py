import os

from cbr_website_beta._cbr_shared.dynamo_db.DyDB__CBR_Logging   import DyDB__CBR_Logging
from cbr_website_beta.cbr__flask.decorators.allow_annonymous    import allow_anonymous
from cbr_website_beta.config.CBR__Site_Info import cbr_site_info
from cbr_website_beta.utils.Page_Utils                          import Page_Utils
from cbr_website_beta.apps.home                                 import blueprint
from flask                                                      import render_template, request, make_response
from jinja2                                                     import TemplateNotFound
from cbr_website_beta.utils.Version                             import version


COGNITO_SIGN_IN       = 'https://the-cbr-beta.auth.eu-west-2.amazoncognito.com/login?client_id=5ij6l5kdho4umoks5rjfh9cbid&response_type=code&scope=email+openid+phone&redirect_uri={cbr_domain}/web/sign-in'
COGNITO_SIGN_OUT      = 'https://the-cbr-beta.auth.eu-west-2.amazoncognito.com/logout?client_id=5ij6l5kdho4umoks5rjfh9cbid&response_type=code&scope=email+openid+phone&logout_uri={cbr_domain}/web/sign-out'
CBR_DOMAIN            = 'https://www.thecyberboardroom.com'
#DEV_DOMAIN            = 'http://localhost:5000'
EXPECTED_ROUTES__HOME = [ '/<path:path>' , '/terms_and_conditions', '/service-worker.js']

EXPECTED_METHODS_HOME = ['home_blueprint.path_path'                 ,
                         'home_blueprint.service_worker'            ,
                         'home_blueprint.terms_and_conditions'      ,
                         'llms_blueprint.just_chat_ui'              ,
                         'llms_blueprint.multiple_athenas'          ,
                         'llms_blueprint.no_system_prompt'          ]

dydb_cbr_logging = DyDB__CBR_Logging()

def running_in_aws():
    return 'AWS_EXECUTION_ENV' in os.environ


@blueprint.route('/service-worker.js')
@allow_anonymous
def service_worker():
    content  = render_template('scripts/service-worker.js', version=version)
    response = make_response(content)
    response.headers['Content-Type'] = 'application/javascript'
    return response


@blueprint.route('/terms_and_conditions')
@allow_anonymous
def terms_and_conditions():
    return render_template('home/terms_and_conditions.html')

@blueprint.route('/<path:path>')
@allow_anonymous
def path_path(path):            # todo: remove the need for this route
    try:
        #if path == 'athena'  : path = 'athena/index.html'           # todo: find a better to map these top level paths
        if path == 'content' : path = 'content/index.html'
        if path.endswith("/"): path += "index.html"
        elif not path.endswith('.html'):    path += '.html'

        # Detect the current page
        kwargs = dict(template_name_or_list = "home/" + path                                             ,
                      breadcrumbs           = map_breadcrumbs(request)                                   ,
                      url_athena            = cbr_site_info.target_athena_url() + '/open_ai/prompt_with_system__stream',  # todo: refactor direct render of the multiple athena UIs
                      page_title            = 'title'                                                    )

        return render_template(**kwargs)

    except TemplateNotFound as error:
        print(f"***** error 404 : {error}")
        return render_template('home/page-404.html', path=path), 404

    except Exception as error:
        print(f"***** error 500 : {error}")
        dydb_cbr_logging.log_exception(error)
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def map_breadcrumbs(request):

    return Page_Utils().map_breadcrumbs(request)
    # breadcrumbs = [
    #     # {'name': 'Home', 'url'  : '#'},
    #     # {'name': 'Section A'    , 'url': '#'},
    #     # {'name': 'Blank Page!!!', 'url': None}
    # ]
    # path = ''
    # for key in request.path.split('/'):
    #     path += '/{key}'
    #     breadcrumbs.append({'name': key, 'url': path})
    # pprint(breadcrumbs)
    # return breadcrumbs
    # try:
    #     segment = request.path.split('/')[-1]
    #     if segment == '':
    #         segment = 'index'
    #     return segment
    # except:
    #     return None
