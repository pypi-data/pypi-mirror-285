#  Copyright (c) 2020. WebShotApi All right reserved
from gawsoft.api_client import Request, Response
from .version import __version__
import os

class Client(Request):
    def __init__(
        self,
        api_key: str = "",
        api_version: str ='v1',
        api_host: str = '',
        user_agent: str = f"Webshotapi Python client {__version__}"
     ):
        if (not api_key or len(api_key)==0) and 'WEBSHOTAPI_API_KEY' in os.environ:
            api_key = os.environ['WEBSHOTAPI_API_KEY']

        if (not api_host or len(api_host)==0) and 'WEBSHOTAPI_ENDPOINT' in os.environ:
            api_host = os.environ['WEBSHOTAPI_ENDPOINT']
        elif api_host:
            pass
        else:
            api_host = "https://api.webshotapi.com"

        super().__init__(api_key, api_version, api_host, user_agent)

    def screenshot(self, url:str, params:dict, image_type: str = "jpg") -> Response:

        '''
        Take screenshot and return png image

        :param url:
            link to website to take screenshot
        :param params:
            dict with parameters check available parameters in https://webshotapi.com/docs/rest/
        :example:
           import webshotapi\n
           TOKEN = 'PUT_YOUR_TOKEN_HERE'

           client = webshotapi(TOKEN)

        :return:
            Response object
        '''

        params['url'] = url
        params['image_type'] = image_type
        return self.request(f'/screenshot/image','POST', params)

    def pdf(self, url:str, params:dict) -> Response:
        '''
        Take screenshot and return pdf file

        :param url:
            link to website to take screenshot
        :param params:
            dict with parameters check available parameters in https://webshotapi.com/docs/rest/
        :return:
            Response object
        '''

        params['url'] = url
        params['image_type'] = 'pdf'
        return self.request('/screenshot/image','POST', params)

    def extract(self,url:str, params:dict) -> Response:
        """
        Extract html selectors with css styles, words with coordinates(x,y,width,height).
        You can also extract html of rendered page and clean text

        @param url: url
        @param params: dict with params
        @return: Response
        """
        params['url'] = url
        return self.request('/extract','POST', params)
