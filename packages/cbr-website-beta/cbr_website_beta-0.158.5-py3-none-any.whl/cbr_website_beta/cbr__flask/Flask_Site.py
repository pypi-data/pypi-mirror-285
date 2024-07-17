import os
from flask import Flask
from importlib import import_module
#from flask_minify import Minify

from cbr_website_beta.cbr__flask.filters.Athena_Html_Content import Athena_Html_Content
from cbr_website_beta.cbr__flask.filters.Current_User        import Current_User
from cbr_website_beta.cbr__flask.filters.Filter__Static_Content import Filter__Static_Content
from cbr_website_beta.cbr__flask.filters.Misc_Filters        import Misc_Filters
from cbr_website_beta.cbr__flask.filters.Obj_Data            import Obj_Data
from cbr_website_beta.cbr__flask.filters.Pretty_Json         import Pretty_Json
from cbr_website_beta.cbr__flask.register_error_handling     import register_error_handling
from cbr_website_beta.cbr__flask.register_hooks              import register_hooks
from cbr_website_beta.cbr__flask.register_logging            import register_logging
#from cbr_website_beta.cbr__flask.register_logging_in_g       import register_logging_in_g
from cbr_website_beta.cbr__flask.register_middlewares        import register_middlewares
from cbr_website_beta.cbr__flask.register_processors         import register_processors
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self

def register_blueprints(app):
    blueprints = [ 'chat', 'docs', 'llms', 'root' ,'dev', 'home', 'minerva', 'user']
    for module_name in blueprints:
        full_module_name = f'cbr_website_beta.apps.{module_name}.{module_name}_routes'
        module = import_module(full_module_name)
        app.register_blueprint(module.blueprint)

def create_flask_app():
    app = Flask(__name__)
    return app

def create_app(config):                         # todo: refactor to class
    app = create_flask_app()
    register_error_handling(app)
    register_middlewares   (app)
    app.config.from_object (config)
    register_blueprints    (app)
    register_processors    (app)
    register_hooks         (app)
    register_logging       (app)
    #register_logging_in_g  (app)


    app.template_folder = '../apps/templates'
    return app




class Flask_Site:

    def __init__(self):
        pass

    @cache_on_self
    def app(self):
        app_config = self.app_config()
        app        = create_app(app_config)
        self.setup(app)
        # if not self.debug():
        #     Minify(app=app, html=True, js=False, cssless=False)

        return app

    def app_config(self):
        from cbr_website_beta.apps.config import config_dict
        return config_dict[self.get_config_mode().capitalize()]


    def debug(self):                                            # todo: refactor this capability to better class
        return os.getenv('DEBUG', 'False') == 'True'

    def get_config_mode(self):                                  # todo: see if this is still neded and refactor into better class
        return 'Debug' if self.debug() else 'Production'

    def setup(self, app):
        self.register_filters(app)

    def register_filters(self, app):           # todo: rename all filters to start with Filter__
        Athena_Html_Content   (app)            # todo: replace these calls with Filter__Static_Content
        Current_User          (app)
        Pretty_Json           (app)
        Obj_Data              (app)
        Misc_Filters          (app)
        Filter__Static_Content(app)
