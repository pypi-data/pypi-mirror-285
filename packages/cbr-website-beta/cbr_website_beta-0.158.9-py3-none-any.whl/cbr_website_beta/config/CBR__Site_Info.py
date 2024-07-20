from os import environ

import cbr_content
import cbr_web_components
from osbot_aws.aws.sts.STS import STS

import cbr_athena

import cbr_static

import cbr_website_beta
from cbr_athena.aws.s3.S3_DB_Base import S3_DB_Base
from cbr_website_beta.config.CBR__Config__Data                     import cbr_config
from osbot_utils.utils.Env                                  import get_env, is_env_var_set, env__old_pwd__remove, env__pwd
from cbr_athena.utils.Version                               import version__cbr_athena
from cbr_static.utils.Version                               import Version as Version__cbr_static
from osbot_aws.AWS_Config                                   import aws_config
from osbot_fast_api.utils.Version                           import Version as Version__osbot_fast_api
from osbot_utils.utils.Status                               import status_error
from osbot_utils.utils.Version                              import Version as Version__osbot_utils
from osbot_utils.base_classes.Type_Safe                     import Type_Safe
from cbr_website_beta.utils.Version import version, version__cbr_website, version__cbr_content, \
    version__cbr_web_components
from osbot_utils.decorators.methods.cache_on_self           import cache_on_self


class CBR__Site_Info(Type_Safe):

    def aws_configured(self):
        with aws_config as _:
            if _.aws_access_key_id():
                if _.aws_secret_access_key():
                    if _.region_name():
                        return True
        return False

    def data(self):
        try:
            return dict(aws      = self.aws      (),
                        dates    = self.dates    (),
                        env_vars = self.env_vars (),
                        paths    = self.paths    (),
                        urls     = self.urls     (),
                        versions = self.versions ())
        except Exception as error:
            return status_error(message="error in CBR__Site_Info.data", error=f'{error}')

    def aws(self):
        caller_identity = STS().caller_identity()
        return dict(caller_identity       = caller_identity          ,
                    region                = aws_config.region_name() ,
                    s3_bucket__s3_db_base = S3_DB_Base().s3_bucket() )

    def dates(self):
        return dict(cbr_site_published_at = get_env('CBR__SITE__PUBLISHED_AT', ''))

    def env_vars(self):
        return dict(status = self.env_vars__status(),
                    values = self.env_vars__values())

    def env_vars__status(self):
        var_names = ['OPEN_AI__API_KEY', 'IP_DATA__API_KEY', 'OPEN_ROUTER_API_KEY',
                     'GROQ_API_KEY', 'COGNITO_USER_POOL_ID', 'TOGETHER_AI_API_KEY']
        status = {}
        for var_name in var_names:
            status[var_name] = is_env_var_set(var_name)
        return status

    def env_vars__values(self):
        var_names = ['CBR__CONFIG_FILE', 'EXECUTION_ENV', 'PORT', 'S3_DEV__VERSION' , 'AWS_LWA_INVOKE_MODE']
        values = {}
        for var_name in var_names:
            values[var_name] = get_env(var_name)
        return values

    def paths(self):
        return dict(cbr_athena         = env__old_pwd__remove(cbr_athena        .path),
                    cbr_content         = env__old_pwd__remove(cbr_content      .path),
                    cbr_static         = env__old_pwd__remove(cbr_static        .path),
                    cbr_web_components = env__old_pwd__remove(cbr_web_components.path),
                    cbr_website_beta   = env__old_pwd__remove(cbr_website_beta  .path),
                    pwd                = env__pwd()                                   )


    def target_athena_url(self):        # todo: refactor out once new setup is stable
        return cbr_config.athena_path()

    def url_athena__internal(self):
        port        = self.cbr_host__port()
        athena_path = cbr_config.athena_path()
        if athena_path.startswith('http'):
            return athena_path
        if port:
            return f'http://localhost:{port}{athena_path}'

    def urls(self):
        return dict(url_athena           = self.target_athena_url   (),
                    url_athena__internal = self.url_athena__internal(),
                    url_assets_dist      = cbr_config.assets_dist     ,
                    url_assets_root      = cbr_config.assets_root     )

    @cache_on_self
    def version(self):
        return version

    def versions(self):
        cbr   = dict(cbr_athena         = version__cbr_athena              ,
                     cbr_content        = version__cbr_content             ,
                     cbr_web_components = version__cbr_web_components      ,
                     cbr_website        = version__cbr_website             ,
                     cbr_static         = Version__cbr_static    ().value() )       # todo create: version__cbr_static
        osbot = dict(osbot_fast_api     = Version__osbot_fast_api().value(),        # todo create: version__osbot_fast_api
                     osbot_utils        = Version__osbot_utils   ().value() )       # todo create: version__osbot_utils

        return dict(cbr      = cbr   ,
                    osbot    = osbot )


    # individual values
    def cbr_host__port(self):
        return get_env('PORT')


cbr_site_info = CBR__Site_Info()