#2.0

import os
import re
from . import core
from .__init__ import MAIN_PATH
from .app_utils import urlencoded_to_dict
from .http_parser import Redirect
from .url_utils import UrlTemplate 
from .http_parser import PartialContent
from .http_parser import HTTP_Status_Code
from .http_parser import HTTP_Response as Response
from .http_parser import HTTP_Message_Header_Line as Header_Line
from .http_parser import HTTP_Message_Request_Header_Tag as Request_Header_Tag
from .http_parser import HTTP_Message_Response_Header_Tag as Response_Header_Tag

class MIME_TYPE:
    HTML = 'text/html'
    JAVA_SCRIPT = 'text/javascript'
    CSS = 'text/css'
    ICO = "image/x-icon"
    PNG = "image/png"
    SVG = "image/svg+xml"
    TEXT = "text/plain"
    MP4 = "video/mp4"
    JSON = "application/json"
    WEBM_AUDIO = "audio/webm"
    ICO = "image/x-icon"

class STORE_VARS:
    #TODO: UPDATE Vars
    '''Keys used to access attributes of the dict provided to the respective handler methods'''

    COOKIES = 'cookies'
    QUERY_STRING = 'query_string'
    RESPONSE = 'response'
    POST = 'post'
    FLAGS = 'flags'
    REQUEST_HEADER = 'request_header'
    TEMPLATE_VARS = 'template_args'
    

class LOGGING_OPTIONS:

    '''Options used to set the logging mode via the ``set_logging`` function'''

    REQUESTS = 'request'
    RESPONSES = 'response'
    DEBUG = 'debug'
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'
    TIME = 'time'

def register(*args, **kwargs):

    '''
    ``General Information:``\n
    The register decorator adds the decorated function to the servers PAGES
    dictionary. The decorater requires a path and a type argument to be specified. The decorated function
    gets called whenever a ``GET request`` is targeted to the speciefied path. The function is expected to return a String
    that's been served under the specified route the type argument must provide the matching MIME-type. If the decorated function
    takes an argument it gets passed a session specific dict.

    ``Usage:``
    ```python
    @register(route= '/', type= MIME_TYPE.TEXT)
    def main(args):
        return str(args)
    ```
    ``Note:`` The ``args`` argument is optional
    '''

    if 'route' not in kwargs:
        raise Exception('The "route" argument is missing.')
    if 'type' not in kwargs:
        raise Exception('The "type" argument is missing.')
    route = kwargs['route']
    def inner(func):
        if isinstance(route, str) and route not in core.PAGES:
                core.PAGES[route] = [func,kwargs['type']]
        
        if isinstance(route, UrlTemplate) and route not in core.GET_TEMPLATES:
                route.type = kwargs['type']
                route.handler = func
                core.GET_TEMPLATES.append(route)
        return func            
    return inner

def post_handler(*args, **kwargs):

    '''
    ``General Information:``\n
    The post_handler decorator adds the decorated function to the servers POST_HANDLER
    dictionary. The decorater requires a path and a type argument to be specified the decorated function
    gets called whenever a post is targeted to the speciefied path. The function is expected to return a string of the
    under the type attribute declared MIME-type. The function decorated gets passed a dictionary containing
    the variables passed with the ``POST so it has to take an argument``
    
    ``Usage:``
    ```python
    @post_handler(route= '/', type= MIME_TYPE.TEXT)
    def main(args):
        return str(args)
    ```
    ``Note:`` The ``args`` argument is necessary!
    '''
    

    if 'route' not in kwargs:
        raise Exception('The "route" argument is missing.')
    if 'type' not in kwargs:
        raise Exception('The "type" argument is missing.')
    route = kwargs['route']
    def inner(func):
        if func.__code__.co_argcount != 1:
            raise Exception('The function decorated with the post_handler decorater has to\n accept one Argument "args":dict')

        if isinstance(route, str) and route not in core.POST_HANDLER:
                core.POST_HANDLER[route] = [func,kwargs['type']]
                
        if isinstance(route, UrlTemplate) and route not in core.POST_TEMPLATES:
                route.type = kwargs['type']
                route.handler = func
                core.POST_TEMPLATES.append(route)
        return func                  
    return inner


def error_handler(*args, **kwargs):

    '''
    ``General Information:``\n
    The error_handler decorator is used to serve a specific page if an error-code occurs.
    ``
    
    ``Usage:``
    ```python
    @error_handler(error_code= 404, type= MIME_TYPE.TEXT)
    def main():
        return str('Page not found!')
    ```
    '''
    

    if 'error_code' not in kwargs:
        raise Exception('The "error_code" argument is missing.')
    if 'type' not in kwargs:
        raise Exception('The "type" argument is missing.')
    err = kwargs['error_code']
    def inner(func):
        if func.__code__.co_argcount != 0:
            raise Exception('The function decorated with the error_handler is not allowed to take arguments.')
        if kwargs['error_code'] not in core.ERROR_HANDLER:
                core.ERROR_HANDLER[err] = [func,kwargs['type']]
        return func            
    return inner

def load_file(path:str) -> str:

    '''The load_file function attempts to read the content of a file with given path and returns it as a utf-8 encoded string'''

    with open(MAIN_PATH+path,'r',encoding='utf-8') as content:
            lines = content.readlines()
            return ''.join(lines)

def load_bin_file(path:str) -> bytes:

    '''The load_file function attempts to read the content of a file with given path and returns it as bytes'''

    path = MAIN_PATH+path
    size = os.path.getsize(path)
    with open(path,'rb') as content:
            return content.read(size)

#TODO: File through new file not found error so status code 404 can be returned
def load_file_from_directory(root_path: str, file_path: str) -> str:
    """The load_file_from_directory function attempts to read the content of a file with given path 
    relative to root_path and returns it as a utf-8 encoded string.
    """
    
    abs_root_path = os.path.abspath(root_path)
    abs_file_path = os.path.abspath(os.path.join(root_path, file_path))
    if os.path.commonpath([abs_root_path]) != os.path.commonpath([abs_root_path, abs_file_path]):
        raise ValueError("Attempt to access file outside the root directory")
    
    with open(abs_file_path, 'r', encoding='utf-8') as content:
        return content.read()

def load_bin_file_from_directory(root_path: str, file_path: str) -> bytes:
    """The load_bin_file_from_directory function attempts to read the content of a file with given path 
    relative to root_path and returns it as bytes.
    """
    
    abs_root_path = os.path.abspath(root_path)
    abs_file_path = os.path.abspath(os.path.join(root_path, file_path))
    

    if os.path.commonpath([abs_root_path]) != os.path.commonpath([abs_root_path, abs_file_path]):
        raise ValueError("Attempt to access file outside the root directory")
    
    with open(abs_file_path, 'rb') as content:
        return content.read()



def render_page(path:str, args:dict) -> str:

    '''The render_page function reads a files content and executes python-code wrapped in double curly braces "{{".
    If a variable name starts with an underscore "_" the python code wrapped in curley braces will be substituded by it's content.
    The values passed with the args dictionary can be accessed with the globals() function in the targeted file'''

    content = ''
    try:
        with open(MAIN_PATH+path,'r',encoding='utf-8') as page:
            content = '\n'.join(page.readlines())
            res_content = content[:]
        to_eval = re.finditer("{{(.|\n)*?}}",content)
        for var in to_eval:
            OUTPUT = {}
            var = content[var.span()[0]:var.span()[1]]
            exec(compile(var.strip('{{}}'),'temp','exec'),args,OUTPUT)
            insert = '\n'.join([str(OUTPUT[x]) for x in OUTPUT.keys() if x[0] == '_'])
            res_content = res_content.replace(var,insert)
    except Exception as e:
        print('[RENDERER] Error with rendering Page.')
        print(e)
    return res_content

def substitude_vars(content:str, vars:dict) -> str:
    
    '''This function accepts a string and substitudes all "%% + key + %%" with the according value from the dictionary'''
    
    try:
        _content = content
        for key in vars:
            _content = re.sub(f'%%{key}%%',vars[key],_content)
    except:
        print('[SUBSTITUDE_VARS] Error substituding vars.')
    return _content

def set_cookie(args, key, value) -> bool:
    if key not in args[STORE_VARS.COOKIES]:
        res:Response = args[STORE_VARS.RESPONSE]
        res.header.add_header_line(Header_Line(Response_Header_Tag.SET_COOKIE,f'{key}={value}'))
        return True
    return False


def is_partial(args) -> bool:
    return 'partial' in args[STORE_VARS.FLAGS]


def set_logging(option:str, state:bool) -> None:
    if option in core.LOGGING_OPTIONS:
        core.LOGGING_OPTIONS[option] = state
        print(f'[LOGGING] logging-option "{option}" set to {state}.')
    else:
        print(f'[LOGGING] Error: There is no logging-option called "{option}".')

def set_logging_callback(callback):
    try:
        assert callable(callback), 'The logging callback is not a callable'
        assert callback.__code__.co_argcount == 3, 'The logging callback needs to accept 3 arguments (message, time_stamp, loglvl)'
        core.LOGGING_CALLBACK.append(callback)
        print('[LOGGING]', "Logging callback has been set")
        
    except Exception as e:
        print('[LOGGING]','Error:',e)

def log_to_file(path='/log.txt', logging_options=[LOGGING_OPTIONS.DEBUG]):
    try:
        for option in logging_options:
            assert option in core.LOGGING_OPTIONS, f'log_to_file: There is no logging-option called "{option}".'

        def file_writer_callback(message, time_stamp, loglvl):
            if  loglvl in logging_options:
                with open(MAIN_PATH+path,'a') as file:
                    file.write(f'({time_stamp}) {message}\n')
        core.LOGGING_CALLBACK.append(file_writer_callback)
        print('[LOGGING]', f"File-logging has been activated path= {path}")
        
    except Exception as e:
        print('[LOGGING]', e)
        
    
 
def get_pages() -> dict:
    return core.PAGES

def get_sessions() -> dict:
    return core.SESSIONS
    
def get_post_handler() -> dict:
    return core.POST_HANDLER

def start() -> None:

    '''The start function causes the server to start by invoking core.start()'''

    core.start()
