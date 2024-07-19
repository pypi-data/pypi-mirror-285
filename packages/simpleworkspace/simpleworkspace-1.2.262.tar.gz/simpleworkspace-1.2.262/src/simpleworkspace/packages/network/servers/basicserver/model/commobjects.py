from http import HTTPStatus
from http.client import HTTPMessage
from functools import cached_property
from io import BytesIO
from socket import socket
from http.cookies import SimpleCookie

class ParsedUrl:
    '''Replaces intellisense for ParseResult from urlparse method'''
    Scheme: str
    '''>>> urlparse("scheme://hostname:port/path?query#fragment")\n"scheme"'''
    Hostname: str|None
    '''>>> urlparse("scheme://hostname:port/path?query#fragment")\n"hostname"'''
    Port: int|None
    '''>>> urlparse("scheme://hostname:port/path?query#fragment")\n"port"'''
    Path: str
    '''>>> urlparse("scheme://hostname:port/path?query#fragment")\n"/path"'''
    Query: str
    '''>>> urlparse("scheme://hostname:port/path?query#fragment")\n"query"'''
    Fragment: str
    '''>>> urlparse("scheme://hostname:port/path?query#fragment")\n"fragment"'''

    @property
    def FullUrl(self):
        urlBuilder = f'{self.Scheme}://{self.Hostname}:{self.Port}{self.Path}'
        if(self.Fragment):
            urlBuilder += f'#{self.Fragment}'        
        return urlBuilder

class RequestContainer:
    class _ParsedQueryContainer:
        def __init__(self):
            self.GET: dict[str,str] = {}
            ''' Query params in url, example: "https://example.com/pages/index.html?key1=val1" -> {'key1': 'val1'} '''
            self.POST: dict[str,str] = {}
            ''' Query params in request body '''

        @cached_property
        def ANY(self):
            ''' 
            A combined dictionary consisting of both POST and GET parameters.
            If a param exists in both POST and GET query, then GET will be preffered
            '''
            return {**self.POST, **self.GET}

    def __init__(self) -> None:
        self.Headers: HTTPMessage
        '''Dict like object containing the headers of the incoming request'''
        self.Method: str
        ''' The method used in the request, such as "GET", "POST"... '''
        self.URL = ParsedUrl()
        self.Body: bytes = None
        ''' The raw request body '''
        self.Query = self._ParsedQueryContainer()
        self.Cookies = SimpleCookie()

class ClientContainer:
    def __init__(self):
        self.IP:str

class ResponseContainer:
    def __init__(self) -> None:
        self.Headers: dict[str, str] = {'Content-Type': 'text/html'}
        ''' Specify headers that will be sent to client. Note: server might additionally add some extra standard headers by default '''
        self.StatusCode = HTTPStatus.OK
        ''' Specifies the status code client will recieve '''
        self.Data: BytesIO|bytes|str = BytesIO()
        ''' The data client will recieve. By default is an BytesIO which can efficently be written to, otherwise you can also directly set Data to be a str or bytes like object '''
        self.Cookies = SimpleCookie()

    def _GetDataBytes(self):
        dataType = type(self.Data)
        if(dataType is str):
            return self.Data.encode('utf-8')
        elif(dataType is bytes):
            return self.Data
        elif(dataType is BytesIO):
            return self.Data.getvalue()
        else:
            raise TypeError(f'Invalid type supplied in Response.Data... Got: {dataType}')

class CommuncationContainer:
    def __init__(self) -> None:
        self.Request = RequestContainer()
        self.Response = ResponseContainer()
        self.Client = ClientContainer()
