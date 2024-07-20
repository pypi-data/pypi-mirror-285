# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from cbr_website_beta.config.CBR__Config__Data   import cbr_config
from cbr_website_beta.utils.Site_Utils  import Site_Utils
from cbr_website_beta.utils.Version import version
from cbr_website_beta.utils.Web_Utils   import Web_Utils



class Config(object):
    ENV            = cbr_config.env()
    ASSETS_ROOT    = os.getenv('ASSETS_ROOT', cbr_config.assets_root())
    GTA_ENABLED    = cbr_config.gta_enabled()
    VERSION        = version
    ASSETS_DIST    = cbr_config.assets_dist()
    CBR_LOGO       = cbr_config.cbr_logo()

    
class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY  = cbr_config.session_cookie_httponly  ()
    REMEMBER_COOKIE_HTTPONLY = cbr_config.remember_cookie_httponly ()
    REMEMBER_COOKIE_DURATION = cbr_config.remember_cookie_duration ()
    LOGIN_ENABLED            = cbr_config.login_enabled            ()

class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
