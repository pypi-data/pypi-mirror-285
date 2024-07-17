import cbr_website_beta
from cbr_website_beta.config.CBR__Config__Active    import CBR__Config__Active
from osbot_utils.utils.Misc                         import date_time_now
from osbot_utils.utils.Status                       import status_ok, status_error
from osbot_utils.utils.Toml                         import toml_dict_from_file
from osbot_utils.utils.Env                          import get_env
from cbr_website_beta.config.CBR__Config            import CBR__Config
from osbot_utils.base_classes.Type_Safe             import Type_Safe
from osbot_utils.utils.Files                        import files_names, folder_files, path_combine_safe

ENV_VAR_NAME__CBR__CONFIG_FILE     = 'CBR__CONFIG_FILE'
DEFAULT__CBR__CONFIG_FILE          = 'cbr-website.community.toml'
FOLDER__CBR__CONFIG_FILES          = './config'

class CBR__Config__Data(Type_Safe):
    #cbr_config : CBR__Config

    # def __init__(self):
    #     super().__init__()
    #     load_dotenv()

    def current_config(self):
        return self.load_config_file(self.current_config_file_name())

    def config_files(self):
        return files_names(folder_files(self.path_config_files(), pattern="*.toml"))

    def current_config_file_name(self):
        return get_env(ENV_VAR_NAME__CBR__CONFIG_FILE) or DEFAULT__CBR__CONFIG_FILE

    def load_config_file(self, config_file_name):
        try:
            path_config_file = self.path_config_file(config_file_name)
            config_data      = toml_dict_from_file(path_config_file)
            cbr_config       = CBR__Config(**config_data)
            return status_ok(data=cbr_config)
        except Exception as error:
            return status_error(message='In CBR__Config failed to load config file', error=f'{error}', data={})

    def create_cbr_config_active__from_current_config_file(self):
        config_file_name = self.current_config_file_name()
        return self.create_cbr_config_active(config_file_name)

    def create_cbr_config_active(self, config_file_name):
        load_cbr_config     = self.load_config_file(config_file_name)
        file_loaded_at      = date_time_now()
        if load_cbr_config.get('status') == 'ok':
            status      = "config file loaded ok"
            cbr_config_data  = self.load_config_file(config_file_name).get('data')
            kwargs      = dict(cbr_config       = cbr_config_data      ,
                               config_file_name = config_file_name,
                               file_loaded_at   = file_loaded_at  ,
                               status           = status          )
            return CBR__Config__Active(**kwargs)
        else:
            status = f"error: config file failed to load: {load_cbr_config.get('error')}"
            cbr_config_data  = CBR__Config()                                                # use default values
            kwargs           = dict(cbr_config   = cbr_config_data ,
                               config_file_name  = config_file_name,
                               file_loaded_at    = file_loaded_at  ,
                               status            = status          )
            return CBR__Config__Active(**kwargs)


    def path_config_file(self, file_name):
        return path_combine_safe(self.path_config_files(), file_name)

    def path_config_files(self):
        return path_combine_safe(cbr_website_beta.path, FOLDER__CBR__CONFIG_FILES)

cbr_config_active = CBR__Config__Data().create_cbr_config_active__from_current_config_file()
cbr_config = cbr_config_active.cbr_config