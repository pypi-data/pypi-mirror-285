from base64 import b64encode
from http import HTTPStatus
from logging import Logger
import http.server
import socketserver
from socketserver import BaseRequestHandler
from urllib.parse import urlparse, parse_qs
from simpleworkspace.logproviders import DummyLogger
import ssl
import subprocess
from socket import socket
from http import HTTPStatus
from .model.commobjects import \
    CommuncationContainer as _CommuncationContainer
from simpleworkspace.utility.regex import Glob
import inspect

class _Route:
    def __init__(self) -> None:
        self.Path:list[str]
        self.Method:str
        self.RequiredParams:list[str] = []
        self.OptionalParams:list[str] = []

def Route(path:str|list[str]='*', method='*'):
    """Generate a route for an instance method

    :param path: glob pattern of which path to match against
    :param method: glob pattern of which method to match against such as GET, POST...
    :param params: query params for this route, the method will recieve these params as kwargs, missing values will default to None
    """
    def decorator(func):
        route = _Route()
        route.Path = [path] if isinstance(path, str) else path
        route.Method = method
        params = inspect.signature(func)

        iterator = iter(params.parameters.items())
        next(iterator) #skip self param
        for name,param in iterator:
            if(param.default is param.empty):
                route.RequiredParams.append(name)
            else:
                route.OptionalParams.append(name)
        
        func.__route__ = route
        return func
    return decorator
        
class BasicRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Class should always be derived and supplied into BasicServer

    Properties for implementer:
    - COMM.Request    , contains all necessary request info in one place
    - COMM.Response   , set the properties here to alter the final response to the client
    
    Methods for implementer that may be overridden:
    - BeforeRequest()   , Runs before OnRequest can be overriden to perform routines before processing the request
    - OnRequest()       , this is the main entry point to start processing the request and preparing the response, implementer can override this to suite api needs.
    - AfterRequest()    , Runs after OnRequest can be overriden to perform routines after processing the request
    - Any method can be decorated with Route to trigger on corresponding request
    """

    #region Boilerplate methods
    
    # @Route(method='GET', path=['/','/index.html'])
    # def GetPage_Index(self):
    #     '''boilerplate method'''
    #     self.COMM.Response.Data = sw.io.file.Read('./index.html')

    # @Route('/api')
    # def ActionRequestHandler(self, action: str, data: str=None): #action would in this case be mandatory to supply
    #     '''boilerplate method for when an action is specified'''

    #endregion

    server:'BasicServer' = None # just to update intellisense
    connection: socket
    COMM: _CommuncationContainer
    _Cached_RouteList:list[str]

    class Signals:
        class StopRequest(Exception):
            '''
            Can be used to stop processing of a request in a graceful way by calling
            >>> raise self.Signals.StopRequest()
            '''

    #region Routines
    def _Routine_Authentication_Basic(self):
        if self.server.Config.Authentication._BasicKey is None:
            return # no auth configured

        if(self.COMM.Request.Headers.get('Authorization') == self.server.Config.Authentication._BasicKey):
            return

        self.COMM.Response.Headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
        self.COMM.Response.Data = 'Authorization required.'
        self.COMM.Response.StatusCode = HTTPStatus.UNAUTHORIZED
        raise self.Signals.StopRequest()
    
    #endregion Routines

    def _Default_BeforeRequest(self):
        '''Default Hook for BeforeRequest'''
        # when basic auth is enabled, checks if current client is authorized
        self._Routine_Authentication_Basic()

    def BeforeRequest(self):
        '''Hook before a request has been processed'''
    
    def _Default_OnRequest(self):
        '''Default Hook for OnRequest'''

    def OnRequest(self):
        '''This can be overriden freely, below is simply implementing boilerplate code'''

        for propertyName in self._Cached_RouteList:
            method = getattr(self, propertyName)
            route:_Route = method.__route__
            
            if not (Glob(route.Method, self.COMM.Request.Method)):
                continue
            if not(any(Glob(path, self.COMM.Request.URL.Path, ignoreCase=False) for path in route.Path)):
                continue

            kwargs = {}
            args = []
            for requiredParam in route.RequiredParams:
                if not requiredParam in self.COMM.Request.Query.ANY:
                    continue
                args.append(self.COMM.Request.Query.ANY[requiredParam])
            if(len(args) != len(route.RequiredParams)):
                continue #if there was required args that were not provided then this route is not the correct path

            for optionalParam in route.OptionalParams:
                kwargs[optionalParam] = self.COMM.Request.Query.ANY.get(optionalParam)
            method(*args, **kwargs)
        

    def _Default_AfterRequest(self):
        '''Default hook for AfterRequest'''

    def AfterRequest(self):
        '''Hook after a request has been processed'''
    

    #region Overrides
    # override, original writes to standard outputs, which fails if app is pyw
    def log_message(self, format, *args):
        self.server.logger.debug(f"{self.address_string()} - {format % args}")
    
    def handle_one_request(self):
        """Handle a single HTTP request.

        You normally don't need to override this method; see the class
        __doc__ string for information on how to handle specific HTTP
        commands such as GET and POST.

        """
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ""
                self.request_version = ""
                self.command = ""
                self.send_error(HTTPStatus.REQUEST_URI_TOO_LONG)
                return
            if not self.raw_requestline:
                self.close_connection = True
                return
            if not self.parse_request():
                return # An error code has been sent, just exit
            
            
            parsedUrl = urlparse(self.path)
            
            self.COMM = _CommuncationContainer()
            self.COMM.Client.IP = self.connection.getpeername()[0]

            self.COMM.Request.Headers = self.headers
            self.COMM.Request.Method = self.command
            self.COMM.Request.URL.Scheme =  "https" if type(self.connection) is ssl.SSLSocket else 'http'
            self.COMM.Request.URL.Hostname, self.COMM.Request.URL.Port = self.connection.getsockname()
            self.COMM.Request.URL.Path = parsedUrl.path
            self.COMM.Request.URL.Query = parsedUrl.query
            self.COMM.Request.URL.Fragment = parsedUrl.fragment
            if('cookie' in self.headers):
                self.COMM.Request.Cookies.load(self.headers.get('cookie'))
            

            def ParseUrlEncodedQuery(query:str) -> dict[str,str]:
                parsedQuery = parse_qs(query)
                #only keep the first matching query key, discard duplicates/arrays for simplicity
                for key in parsedQuery.keys():
                    parsedQuery[key] = parsedQuery[key][0]
                return parsedQuery
            
            self.COMM.Request.Query.GET = ParseUrlEncodedQuery(self.COMM.Request.URL.Query)
            if('Content-Length' in self.headers):
                self.COMM.Request.Body = self.rfile.read(int(self.headers['Content-Length']))
                if(self.headers.get('Content-Type') == 'application/x-www-form-urlencoded'):
                    self.COMM.Request.Query.POST = ParseUrlEncodedQuery(self.COMM.Request.Body.decode('utf-8'))
            
            try:
                self._Default_BeforeRequest()
                self.BeforeRequest()
                self._Default_OnRequest()
                self.OnRequest()
                self._Default_AfterRequest()
                self.AfterRequest()
            except self.Signals.StopRequest:
                pass  # a graceful request cancellation
            finally:
                self.send_response(self.COMM.Response.StatusCode)
                for morsel in self.COMM.Response.Cookies.values():
                    self.send_header("Set-Cookie", morsel.OutputString())
                for key, value in self.COMM.Response.Headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(self.COMM.Response._GetDataBytes())
        except TimeoutError as e:
            # a read or a write timed out.  Discard this connection
            self.server.logger.exception("Request timed out")
            self.close_connection = True
            return
    #endregion Overrides
        


class _BasicServerConfiguration:
    class _Authentication:
        _BasicKey:str = None
    class _SSL:
        _Filepath_Certificate:str = None
        _Filepath_Privatekey:str = None
    
    def __init__(self):
        self.Port: int = None
        self.Host:str = ''
        self.Authentication = self._Authentication()
        self.SSL = self._SSL()


class BasicServer(socketserver.ThreadingTCPServer):
    def __init__(self, port: int, requestHandler: BasicRequestHandler):
        self.Config = _BasicServerConfiguration()
        self.logger = DummyLogger.GetLogger()

        self._MapRoutes(requestHandler)
        super().__init__(("", port), requestHandler, bind_and_activate=False)

    def _MapRoutes(self, requestHandler: BasicRequestHandler):
        requestHandler._Cached_RouteList = []
        for propName,obj in inspect.getmembers(requestHandler, predicate=inspect.isfunction):
            if not ('__route__' in obj.__dict__):
                continue
            if not (isinstance(obj.__route__, _Route)):
                continue

            requestHandler._Cached_RouteList.append(propName)

    def UseLogger(self, logger: Logger):
        self.logger = logger
        return self

    def UseAuthorization_Basic(self, username: str, password: str):
        """Uses http basic auth before any request is accepted, one of username or password can be left empty"""
        self.Config.Authentication._BasicKey = "Basic " + b64encode(f"{username}:{password}".encode()).decode()
        return self

    def GenerateSelfSignedSSLCertificates(self, certificateOutPath = 'cert.crt', PrivateKeyOutPath = 'cert.key'):
        if(not certificateOutPath.endswith(".crt")) or (not PrivateKeyOutPath.endswith('.key')):
            raise Exception("wrong file extensions used for certs")
        result = subprocess.run(
            ["openssl", 
                "req", "-x509", ""
                "-newkey", "rsa:4096", 
                "-keyout", PrivateKeyOutPath, "-out", certificateOutPath, 
                "-days", str(365 * 10), 
                "-nodes",
                "-subj", "/C=US/CN=*"
            ],text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:  # something went bad
            raise Exception(result.stderr, result.stdout)
        return self

    def UseSSL(self, certificatePath: str, PrivateKeyPath: str):
        self.Config.SSL._Filepath_Certificate = certificatePath
        self.Config.SSL._Filepath_Privatekey = PrivateKeyPath
        return self

    def serve_forever(self, poll_interval: float = 0.5) -> None:
        if self.Config.SSL._Filepath_Certificate is not None:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=self.Config.SSL._Filepath_Certificate, keyfile=self.Config.SSL._Filepath_Privatekey)
            self.socket = context.wrap_socket(self.socket, server_side=True)
        try:
            self.server_bind()
            self.server_activate()
        except:
            self.server_close()
            raise

        self.logger.info(f"Server started at port {self.server_address[1]}")
        super().serve_forever(poll_interval)

#BasicRequestHandler would be overriden for implementer
# server = BasicServer(1234, BasicRequestHandler)
# server.UseLogger(StdoutLogger.GetLogger())
# server.UseAuthorization_Basic("admin", "123")
# server.serve_forever()
