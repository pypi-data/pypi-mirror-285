from cbr_website_beta.cbr__fastapi.CBR__Fast_API import CBR__Fast_API, cbr_fast_api
from cbr_website_beta.config.CBR__Site_Info import CBR__Site_Info
from osbot_utils.base_classes.Type_Safe          import Type_Safe
from osbot_utils.utils.Dev import pprint


class CBR__Fast_API__Client(Type_Safe):
    cbr_fast_api  : CBR__Fast_API
    cbr_site_info : CBR__Site_Info

    def setup(self):
        self.cbr_fast_api = cbr_fast_api
        return self

    def client(self):
        return self.cbr_fast_api.client()

    def get(self, path):
        response = self.client().get(path)
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            if content_type == 'application/json':
                return response.json()
            if content_type == 'text/plain':
                return response.text
            if content_type == 'image/png':
                return { 'image': response.content , 'image_type': 'png'}
            if content_type == 'text/html; charset=utf-8':
                return f"html object of: {response.text}"       # todo, convert to html Tag (from osbot utils)
            else:                                               # add support for handing binary files (like images), when needed
                return response.text
        return response
