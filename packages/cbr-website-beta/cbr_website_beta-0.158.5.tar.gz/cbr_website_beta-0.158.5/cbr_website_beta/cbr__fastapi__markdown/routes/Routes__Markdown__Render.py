from pydantic import BaseModel

from cbr_website_beta.cbr__fastapi__markdown.markdown.Markdown_Parser import Markdown_Parser
from cbr_website_beta.config.CBR__Config__Data                         import cbr_config
from cbr_website_beta.config.CBR__Config__Data import cbr_config_active
from cbr_website_beta.config.CBR__Site_Info                     import CBR__Site_Info, cbr_site_info
from cbr_website_beta.utils.health_checks.CBR__Health_Checks    import CBR__Health_Checks, cbr_health_checks
from osbot_fast_api.api.Fast_API_Routes                         import Fast_API_Routes

ROUTE_PATH__SITE_INFO     = 'render'
EXPECTED_SITE_INFO_ROUTES = ['/extensions']

class Markdown_Text(BaseModel):
    text : str

class Routes__Markdown__Render(Fast_API_Routes):
    markdown_parser : Markdown_Parser
    tag             : str = ROUTE_PATH__SITE_INFO

    def extensions(self):
        return f'{self.markdown_parser.extensions()}'

    def markdown_to_html(self, markdown_text: Markdown_Text):
        return self.markdown_parser.markdown_to_html(markdown_text.text)

    def setup_routes(self):
        self.add_route_get (self.extensions)
        self.add_route_post(self.markdown_to_html)
