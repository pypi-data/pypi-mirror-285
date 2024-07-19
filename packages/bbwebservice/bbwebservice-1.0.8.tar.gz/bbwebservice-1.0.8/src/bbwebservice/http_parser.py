import socket
import re
from datetime import datetime
from . import url_utils
from .special_media_type import PartialContent
from .special_media_type import Redirect

import traceback

HEADER_SIZE_MAX = 8000

LOGGING_OPTIONS:dict = {'response':False, 'request':False, 'debug':False, 'info':False, 'warning':False, 'error':False, 'critical':False, 'time':False}
LOGGING_CALLBACK = []

def get_http_date():
    now = datetime.utcnow()
    http_date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return http_date

def log(*msg, log_lvl='info', sep=None) -> None:
    #TODO: Encoding safe logging
    if LOGGING_OPTIONS['time']:
        msg = (f'({get_http_date()})', *msg)
    if LOGGING_CALLBACK:
        try:
            message = sep.join(map(str, msg)) if sep else ' '.join(map(str, msg))
            time_stamp = get_http_date()
            for callback in LOGGING_CALLBACK:
                callback(message ,time_stamp ,log_lvl)
        except Exception as e:
            print('[LOGGING]',e) 
                   
    if sep and LOGGING_OPTIONS[log_lvl]:
        print(*msg, sep=sep)
    elif LOGGING_OPTIONS[log_lvl]:
        print(*msg)

def approach(func, args=None, switch=None):
    try:
        if args:
            return func(*args)
        return func()
    except Exception as e:
        if switch:
            log(f'[APP][{switch}] error: {e}', log_lvl='debug')
        else:
            log(f'[APP] error: {e}', log_lvl='debug')
        

def get_class_fields(klass) -> dict:
    
    class_attrs = vars(klass)
    res = {}
    for key in class_attrs:
        if not key.startswith("__"):  # Exclude attributes starting with '__'
            res[key] = class_attrs[key]
    return res

def merge_dicts(*dicts):
    result = {}
    for d in dicts:
        result.update(d.copy())
    return result
    

class HTTP_Message_Type:
    REQUEST = 'REQUEST'
    RESPONSE = 'RESPONSE'


class Mime_Type:

    HTML = 'text/html'
    JAVA_SCRIPT = 'text/javascript'
    CSS = 'text/css'
    ICO = 'image/x-icon'
    PNG = 'image/png'
    JPEG = 'image/jpeg'
    SVG = 'image/svg+xml'
    TEXT = 'text/plain'
    MP4 = 'video/mp4'
    JSON = 'application/json'
    WEBM_AUDIO = 'audio/webm'
    PDF = 'application/pdf'
    XML = 'application/xml'
    MPEG = 'audio/mpeg'
    CSV = 'text/csv'


class CSP_Directive:

    DEFAULT_SRC = 'default-src'
    SCRIPT_SRC = 'script-src'
    STYLE_SRC = 'style-src'
    IMG_SRC = 'img-src'
    FONT_SRC = 'font-src'
    CONNECT_SRC = 'connect-src'
    FRAME_SRC = 'frame-src'
    OBJECT_SRC = 'object-src'

class CSP_Values:

    NONE = '\'none\''
    SELF = '\'self\''
    UNSAFE_INLINE = '\'unsafe-inline\''
    UNSAFE_EVAL = '\'unsafe-eval\''    


class CSP_Policy:

    def __init__(self, csp_directive:str, csp_value: str|list) -> None:
        self.csp_directive = csp_directive
        self.csp_value = csp_value

    def __str__(self) -> str:
        res = ''
        if isinstance(self.csp_value,str):
            res = f'{self.csp_directive} {self.csp_value}'
        if isinstance(self.csp_value,list):
            res += self.csp_directive
            for val in self.csp_value:
                res += f' {val}'
        return res

class CSP:

    def __init__(self) -> None:
        self.policies = []
    
    def add_policy(self, policy:CSP_Policy) -> None:
        self.policies.append(policy)

    def is_set(self):
        return not bool(self.policies)

    def __str__(self) -> str:
        return '; '.join([str(x) for x in self.policies])
    
    
#<https://en.wikipedia.org/wiki/List_of_HTTP_status_codes>

class HTTP_Status_Code:
    CONTINUE = [100,'Continue']
    SWITCHING_PROTOCOLS = [101,'Switching Protocols']
    PROCESSING = [102, 'Processing']
    EARLY_HINTS = [103,'Early Hints']
    OK = [200,'OK']
    CREATED = [201,'Created']
    ACCEPTED = [202,'Accepted']
    NON_ATHORITATIVE_INFORMATION = [203, 'Non-Authoritative Information']
    NO_CONTENT = [204, 'No Content']
    RESET_CONTENT = [205, 'Reset Content']
    PARTIAL_CONTENT = [206, 'Partial Content']
    MULTI_STATUS = [207, 'Multi-Status']
    ALREADY_REPORTED = [208, 'Already Reported']
    IM_USED = [226, 'IM Used']
    MULTIPLE_CHOICES = [300, 'Multiple Choices']
    MOVED_PERMANENTLY = [301,'Moved Permanently']
    FOUND = [302, 'Found']
    SEE_OTHER = [303, 'See Other']
    NOT_MODIFIED = [304, 'Not Modified']
    USE_PROXY = [305, 'Use Proxy']
    SWITCH_PROXY = [306, 'Switch Proxy']
    TEMPORARY_REDIRECT = [307, 'Temporary Redirect']
    PERMANENT_REDIRECT = [308, 'Permanent Redirect']
    BAD_REQUEST = [400, 'Bad Request']
    UNAUTHERIZED = [401, 'Unautherized']
    PAYMENT_REQUIRED = [402, 'Payment Required']
    FORBIDDEN = [403, 'Forbidden']
    NOT_FOUND = [404, 'Not Found']
    METHOD_NOT_ALLOWED = [405, 'Method Not Allowed']
    NOT_ACCEPTABLE = [406, 'Not Acceptable']
    PROXY_AUTHENTICATION_REQUIRED = [407, 'Proxy Authentication Required']
    REQUEST_TIMEOUT = [408, 'Request Timeout']
    CONFLICT = [409, 'Conflict']
    GONE = [410, 'Gone']
    LENGTH_REQUIRED = [411, 'Length Required']
    PRECONDITION_FAILED = [412,'Precondition Failed']
    PAYLOAD_TOO_LARGE = [413, 'Payload Too Large']
    URI_TOO_LONG = [414, 'URI Too Long']
    UNSUPPORTED_MEDIA_TYPE = [415, 'Unsupported Media Type']
    RANGE_NOT_SATISFIABLE = [416, 'Range Not Satisfiable']
    EXCEPTION_FAILED = [417, 'Exception Failed']
    IM_A_TEAPOT = [418, "I'm a teapot"]
    MISDIRECTED_REQUEST = [421, 'Misdirected Request']
    UNPROCESSABLE_ENTITY = [422, 'Unprocessable Entity']
    LOCKED = [423, 'Locked']
    FAILED_DEPENDENCY = [424, 'Failed Dependency']
    TOO_EARLY = [425, 'Too Early']
    UPGRADE_REQUIRED = [426, 'Upgrade Required']
    PRECONDITION_REQUIRED = [428, 'Precondition Required']
    TOO_MANY_REQUESTS = [429, 'Too Many Requests']
    REQUEST_HEADER_FIELDS_TOO_LARGE = [431, 'Request Header Fields Too Large']
    UNAVAILABLE_FOR_LEGAL_REASONS = [451, 'Unavailable For Legal Reasons']
    INTERNAL_SERVER_ERROR = [500, 'Internal Server Error']
    NOT_IMPLEMENTED = [501,'Not Implemented']
    BAD_GATEWAY = [502, 'Bad Gateway']
    SERVICE_UNAVAILABLE = [503, 'Service Unavailable']
    GATEWAY_TIMEOUT = [504, 'Gateway Timeout']
    HTTP_VERSION_NOT_SUPPORTED = [505, 'HTTP Version Not Supported']
    VARIANT_ALSO_NEGOTIATES = [506, 'Variant Also Negotiates']
    INSUFFICIENT_STORAGE = [507, 'Insufficient Storage']
    LOOP_DETECTED = [508, 'Loop Detected']
    NOT_EXTENDED = [510, 'Not Extended']
    NETWORK_AUTHENTICATION_REQUIRED = [511, 'Network Authentication Required']




class HTTP_Method:
    GET     =  'GET'
    POST    =  'POST'
    PUT     =  'PUT'
    HEAD    =  'HEAD'
    DELETE  =  'DELETE'
    TRACE   =  'TRACE'
    OPTIONS =  'OPTIONS'
    CONNECT =  'CONNECT'

class HTTP_Protocol_Version:
        HTTP_1_0 = "HTTP/1.0"
        HTTP_1_1 = "HTTP/1.1"




class HTTP_Access_Control_Headers:
    ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
    ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
    ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Expose-Headers'
    ACCESS_CONTROL_MAX_AGE = 'Access-Control-Max-Age:'
    ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
    ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'
    ACCESS_CONTROL_REQUEST_METHOD = 'Access-Control-Request-Method'
    ACCESS_CONTROL_REQUEST_HEADERS = 'Access-Control-Request-Headers'
    ORIGIN = 'Origin'



# <https://de.wikipedia.org/wiki/Liste_der_HTTP-Headerfelder>

class HTTP_Message_Request_Header_Tag:

    '''This class holds all HTTP message header tags that are supportet by this webserver'''

    ACCEPT = 'Accept'
    ACCEPT_CHARSET = 'Accept-Charset'
    ACCEPT_ENCODING = 'Accept-Encoding'
    ACCEPT_LANGUAGE = 'Accept-Language'
    AUTHORISATION = 'Authroisation'
    CACHE_CONTROL = 'Cache-Control'
    CONNECTION = 'Connection'
    COOKIE = 'Cookie'
    CONTENT_LENGTH = 'Content-Length'
    CONTENT_TYPE = 'Content-Type'
    CONTENT_LANGUAGE = 'Content-Language'
    DATE = 'Date'
    EXPECT = 'Expect'
    FORWARDED = 'Forwarded'
    FROM = 'From'
    HOST = 'Host'
    IF_MATCH = 'If-Match'
    IF_MODIFIED_SINCE = 'If-Modified-Since'
    IF_NONE_MATCH = 'If-None-Match'
    IF_RANGE = 'If-Range'
    IF_UNMODIFIED_SINCE = 'If-Unmodified-Since'
    MAX_FORWARDS = 'Max-Forwards'
    PRAGMA = 'Pragma'
    PROXY_AUTHORISATION = 'Proxy-Authorisation'
    RANGE = 'Range'
    REFERER = 'Referer'
    TE = 'TE'
    TRANSEFER_ENCODING = 'Transfer-Encoding'
    UPGRADE = 'Upgrade'
    USER_AGENT = 'User-Agent'
    VIA = 'Via'
    WARNING = 'Warning'

class HTTP_Message_Response_Header_Tag:

    '''This class holds all HTTP message header tags that are supportet by this webserver'''

    ACCEPT_RANGES = 'Accept-Ranges'
    AGE = 'Age'
    ALLOW = 'Allow'
    CACHE_CONTROL = 'Cache-Control'
    CONNECTION = 'Connection'
    CONTENT_ENCODING = 'Content-Encoding'
    CONTENT_LANGUAGE = 'Content-Language'
    CONTENT_LENGTH = 'Content-Length'
    CONTENT_LOCATION = 'Content'
    CONTENT_DISPOSITION = 'Content-Disposition'
    CONENT_RANGE = 'Content-Range'
    CONTENT_SECURITY_POLICY = 'Content-Security-Policy'
    CONTENT_TYPE = 'Content-Type'
    DATE = 'Date'
    ETAG = 'ETag'
    EXPIRES = 'Expires'
    LAST_MODIFIED = 'Last-Modified'
    LINK = 'Link'
    LOCATION = 'Location'
    P3P = 'P3P'
    PRAGMA = 'Pragma'
    REFRESH = 'Refresh'
    RETRY_AFTER = 'Retry-After'
    SERVER = 'Server'
    SET_COOKIE = 'Set-Cookie'
    TRAILER = 'Trailer'
    TRANSFER_ENCODING = 'Transfer_Encoding'
    VARY = 'Vary'
    VIA = 'Via'
    WARNING = 'Warning'
    WWW_Authenticate = 'WWW-Authenticate'

class HTTP_Message_Header_Line():

    '''Defines form and functionalities of the lines which compose an HTTP Header'''
    
    def __init__(self, header_tag:str, values:str|list) -> None:
            self.header_tag = '_'.join(part.capitalize() for part in header_tag.split('_'))
            if isinstance(values,list):
                self.values = values
            if isinstance(values,str):
                self.values = [values]

    def add_value(self, value:str) -> None:
        self.values.append(value)

    def __str__(self) -> str:
        res = ''
        if isinstance(self.values,list):
            res = self.header_tag + ": " + '; '.join(self.values)
        if isinstance(self.values,str):
            res = self.header_tag + ": " + self.values
        return res


class HTTP_Message_Header():
    def __init__(self) -> None:
        self.header_lines = []
    
    def add_header_line(self, header_line:HTTP_Message_Header_Line) -> None:
            self.header_lines.append(header_line)

    #TODO: remove heade line
    def remove(self, key) -> None:
        for idx, val in enumerate(self.header_lines):
            if val.header_tag == key:
                del self.header_lines[idx]
                return 

    def add_values_to_header(self, header_line:HTTP_Message_Header_Line) -> bool:
            header = [h for h in self.header_lines if h.header_tag.lower() == header_line.header_tag.lower()]
            if header:
                header = header[0]
                values  = [val for val in header_line.values if val not in header.values]
                if values:
                    for value in values:
                        header.add_value(value)
                    return True
            return False
                                
    
    def parse_header(self, raw_message:str) -> None:
        for line in raw_message.split('\n'):
            if len(line.split(':',1)) == 2:
                if line.split(':',1)[0].lower() in [x.lower() for x in get_class_fields(HTTP_Message_Request_Header_Tag).values()]:
                    tokens = line.split(':',1)
                    normalized_header = '_'.join(part.capitalize() for part in tokens[0].split('_'))
                    header_line = HTTP_Message_Header_Line(normalized_header,[x.strip() for x in tokens[1].split(';')])
                    self.header_lines.append(header_line)

                else:
                    #TODO: append other list so user can work with it
                    log(f'[parse_header] \'{line.split(":",1)[0]}\' is not a recognized header.',log_lvl='debug')

    def get_fields(self)->dict:
        res = {}
        for line in self.header_lines:
            res[line.header_tag] = line.values
        return res


    def bin(self) -> bytes:
        return self.__str__().encode('utf-8')

    def __contains__(self, item):
        return item .lower() in [x.lower() for x in self.get_fields().keys()]

    def __str__(self) -> str:
        return '\n'.join([str(x) for x in self.header_lines])


class HTTP_Response:

    def __init__(self, header:HTTP_Message_Header, error_handler = None, content:bytes=None) -> None:
        
        self.header = header
        self.protocol_version = HTTP_Protocol_Version.HTTP_1_1
        self.http_status_code = HTTP_Status_Code.BAD_REQUEST
        self.content = b''
        self.error_handler = {}

        if error_handler:
            self.error_handler = error_handler

        if content:
            self.content += content

    def set_status(self, http_status_code) -> None:
            self.http_status_code = http_status_code
            status_code = http_status_code[0]
            if  status_code > 300:

                if status_code in self.error_handler:
                    handler = self.error_handler[status_code][0]
                    content_type = self.error_handler[status_code][1]
                    content = handler()

                    if isinstance(content, bytes):
                        self.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_TYPE,content_type))
                        self.append_content(content)

                    if isinstance(content, str):
                        self.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_TYPE,[content_type, 'charset=utf-8']))
                        self.append_content(content.encode('utf-8'))
                else:
                    self.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_TYPE,[Mime_Type.TEXT, 'charset=utf-8']))
                    self.append_content(f'{self.http_status_code[0]} {self.http_status_code[1]}'.encode('utf-8'))


        #TODO: error handling

    def set_protocol(self, http_protocol_version) -> None:
        self.protocol_version = http_protocol_version

    def set_csp(self, csp:CSP):
        self.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_SECURITY_POLICY, str(csp)))
    
    def append_content(self, content:bytes) -> None:
        self.content += content

    def get_first_line(self) -> bytes:
        return f'{self.protocol_version} {self.http_status_code[0]} {self.http_status_code[1]}\n'.encode('utf-8')

    def bin(self):
        if self.content:
            self.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_LENGTH,str(len(self.content))))
        return self.get_first_line() + self.header.bin() + b'\r\n\r\n' + self.content

    def __str__(self) -> str:
        return str(self.bin(),'utf-8')


class HTTP_Message_Factory:
    def __init__(self, connection:socket.socket, addr, get_handler:dict, get_templates:list, post_handler:dict, post_templates:list ,error_handler:dict) -> None:
        try:
            self.stay_alive:bool = False
            self.get_handler:dict = get_handler
            self.get_templates:list = get_templates
            self.post_templates:list = post_templates
            self.post_handler:dict = post_handler
            self.error_handler:dict = error_handler
            
            raw_message,_,post = connection.recv(HEADER_SIZE_MAX).partition(b'\r\n\r\n')
            
            self.mime_type = Mime_Type.TEXT
            self.post = bytearray(post)
            self.message_temp = str(raw_message,'utf-8')
            self.connection = connection
            self.addr = addr
            self.request_header:HTTP_Message_Header = HTTP_Message_Header()
            self.request_header.parse_header(self.message_temp)
            self.response_header:HTTP_Message_Header = HTTP_Message_Header()
            self.response_message:HTTP_Response = HTTP_Response(self.response_header,error_handler=self.error_handler)
            self.http_parser:HTTP_Parser = HTTP_Parser(self)
            self.http_parser.parse()
            self.request_header.get_fields()
            
            self.range = None

            log('\n\nREQUEST:',self.message_temp+'\n\n', log_lvl='request', sep="\n")
        
        except Exception as e:
            log(f'[PARSER] error: {e.args[0]}', log_lvl='debug')


    def get_message(self) -> bytes:
        status = self.response_message.http_status_code
        if status == HTTP_Status_Code.BAD_REQUEST:
                self.response_message.set_status(HTTP_Status_Code.BAD_REQUEST)
        log(f'[{status[0]}] [{self.http_parser.http_request_path}] {status[1]}', log_lvl='info')
        return self.response_message.bin()
    
class HTTP_Parser():

    def __init__(self, http_message_factory:HTTP_Message_Factory) -> None:
        self.http_message_factory = http_message_factory


    def parse_first_line(self) -> tuple:

        first_line = self.http_message_factory.message_temp.split('\n')[0]
        err = Exception(f'[parse_first_line] failing to parse first line. \'{first_line}\'')
        first_line_tokens = [x for x in re.split('\s+',first_line) if x]
        if len(first_line_tokens) == 3:
            http_message_method = first_line_tokens[0]
            http_request_path = first_line_tokens[1]
            http_protocol = first_line_tokens[2]

            if http_message_method not in get_class_fields(HTTP_Method).values():
                self.http_message_factory.response_message.set_status(HTTP_Status_Code.BAD_REQUEST)
                raise err
            
            if http_protocol not in get_class_fields(HTTP_Protocol_Version).values():
                self.http_message_factory.response_message.set_status(HTTP_Status_Code.BAD_REQUEST)
                raise err

            return (http_message_method, http_request_path, http_protocol)
        else:
            self.http_message_factory.response_message.set_status(HTTP_Status_Code.BAD_REQUEST)
            raise err
        

    def set_default_header(self):

        server = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.SERVER,'unknown')
        date = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.DATE,get_http_date())
        cache_control = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CACHE_CONTROL,'no-store')
        self.http_message_factory.response_message.header.add_header_line(cache_control)
        self.http_message_factory.response_message.header.add_header_line(date)
        self.http_message_factory.response_message.header.add_header_line(server)


#TODO 1: Refector that hot mess  

    def set_content(self) -> None:

        content = None

        if self.http_message_method == HTTP_Method.GET:
            if self.http_request_path in self.http_message_factory.get_handler:
                handler = self.http_message_factory.get_handler[self.http_request_path][0]
                self.http_message_factory.mime_type = self.http_message_factory.get_handler[self.http_request_path][1]
                if handler.__code__.co_argcount == 1:
                    content = approach(handler, args=(self.args,), switch=self.http_request_path)
                else:
                    content = approach(handler, switch=self.http_request_path)
            elif template := next((x for x in self.http_message_factory.get_templates if x == self.http_request_path), None):
                handler = template.handler
                self.args['template_args'] = template.extract(self.http_request_path)
                self.http_message_factory.mime_type = template.type
                if handler.__code__.co_argcount == 1:
                    content = approach(handler, args=(self.args,), switch=self.http_request_path)
                else:
                    content = approach(handler, switch=self.http_request_path)
                
            else:
                self.http_message_factory.response_message.set_status(HTTP_Status_Code.NOT_FOUND)
                #TODO: check for other err

        if self.http_message_method == HTTP_Method.POST:
            if self.http_request_path in self.http_message_factory.post_handler:
                handler = self.http_message_factory.post_handler[self.http_request_path][0]
                self.http_message_factory.mime_type = self.http_message_factory.post_handler[self.http_request_path][1]
                if handler.__code__.co_argcount == 1:
                    content = approach(handler, args=(self.args,), switch=self.http_request_path)
                else:
                    content = approach(handler, switch=self.http_request_path)
                    
            elif template := next((x for x in self.http_message_factory.post_templates if x == self.http_request_path), None):
                handler = template.handler
                self.args['template_args'] = template.extract(self.http_request_path)
                self.http_message_factory.mime_type = template.type
                if handler.__code__.co_argcount == 1:
                    content = approach(handler, args=(self.args,), switch=self.http_request_path)
                else:
                    content = approach(handler, switch=self.http_request_path)
    
            else:
                self.http_message_factory.response_message.set_status(HTTP_Status_Code.NOT_FOUND)
                #check if in other paths and if not 400err
                pass
        if self.http_message_method == HTTP_Method.CONNECT:
            pass
        if self.http_message_method == HTTP_Method.DELETE:
            pass
        if self.http_message_method == HTTP_Method.PUT:
            pass
        if self.http_message_method == HTTP_Method.TRACE:
            pass
        if self.http_message_method == HTTP_Method.HEAD:
            pass
        
        if isinstance(content, bytes):
            content_type_header = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_TYPE,self.http_message_factory.mime_type)
            self.http_message_factory.response_message.header.add_header_line(content_type_header)
            self.http_message_factory.response_message.set_status(HTTP_Status_Code.OK)
            self.http_message_factory.response_message.append_content(content)
        if isinstance(content, str):
            content_type_header = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_TYPE,[self.http_message_factory.mime_type,'charset=utf-8'])
            self.http_message_factory.response_message.header.add_header_line(content_type_header)
            self.http_message_factory.response_message.set_status(HTTP_Status_Code.OK)
            self.http_message_factory.response_message.append_content(content.encode('utf-8'))

        if isinstance(content, PartialContent):
            partial_content:PartialContent = content
            range = self.http_message_factory.range
            if range:
                start = range[0]
                end = range[1] if range[1] else start + partial_content.default_size
                content = content.get_range(start,end)
                content_type_header = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONENT_RANGE,f'bytes {start}-{min(end,partial_content.get_size()-1)}/{partial_content.get_size()}')
                content_type_header1 = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONTENT_TYPE,self.http_message_factory.mime_type)
                self.http_message_factory.response_message.header.add_header_line(content_type_header)
                self.http_message_factory.response_message.header.add_header_line(content_type_header1)
                self.http_message_factory.response_message.set_status(HTTP_Status_Code.PARTIAL_CONTENT)
                self.http_message_factory.response_message.append_content(content)
        
        if isinstance(content, Redirect):
            redirect:Redirect = content
            if redirect.status:
                self.http_message_factory.response_message.set_status(redirect.status)
                self.http_message_factory.response_message.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.LOCATION, redirect.path))
            else:
                self.http_message_factory.response_message.set_status(HTTP_Status_Code.SEE_OTHER)
                self.http_message_factory.response_message.header.add_header_line(HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.LOCATION, redirect.path))


    def analyze_header(self):

        for header, value in self.http_message_factory.request_header.get_fields().items():
            header = header.lower()
           

            #If the request Message to the server holds content which makes the message larger than 8kb fetch the rest
            if header == HTTP_Message_Request_Header_Tag.CONTENT_LENGTH.lower():
                length = int(value[0])
                missing_bytes = length - len(self.http_message_factory.post)
                if missing_bytes > 0:
                    self.http_message_factory.post.extend(self.http_message_factory.connection.recv(missing_bytes))

            if header == HTTP_Message_Request_Header_Tag.CONNECTION.lower():
                if 'keep-alive' in value:
                    self.http_message_factory.stay_alive = True
                    connection_header = HTTP_Message_Header_Line(HTTP_Message_Response_Header_Tag.CONNECTION,'keep-alive')
                    self.http_message_factory.response_header.add_header_line(connection_header)
                if 'close' in value:
                    self.http_message_factory.stay_alive = False
            
            if header == HTTP_Message_Request_Header_Tag.COOKIE.lower():
                for val in value:
                    cookie_tokens = val.split("=")
                    if len(cookie_tokens) == 2:
                        self.args['cookies'][cookie_tokens[0]] = cookie_tokens[1]

            if header == HTTP_Message_Request_Header_Tag.CONTENT_TYPE.lower():
                content_type = value[0]
                if content_type == 'application/x-www-form-urlencoded':
                    self.args['flags'].append('urlencoded')

            if header == HTTP_Message_Request_Header_Tag.RANGE.lower():
                if value:
                    value_tokens = value[0].split('=')

                    if len(value_tokens) == 2:
                        whole_range = value_tokens[1]
                        range_parts = whole_range.split('-')
                        start = 0
                        end = 0
                        if len(range_parts) == 2:
                            start = int(range_parts[0])
                            if range_parts[1]:
                                end = int(range_parts[1])
                        self.http_message_factory.range = [start,end]
                        self.args['flags'].append('partial')


    def get_query_string(self, query_string) -> dict:
        
        inner_args = {}
        key_value = query_string.split('&')
        for pair in key_value:
            p = pair.split('=')
            if len(p) == 2:
                inner_args[url_utils.unescape_url(p[0])] = url_utils.unescape_url(p[1])
        self.args['query_string'] = inner_args
   

    def parse(self) -> None:
        
        try:
            self.args = {   
                            'query_string':{},
                            'flags':[],
                            'template_args':{},
                            'cookies': {},
                            'address': self.http_message_factory.addr,
                            'post' : self.http_message_factory.post,
                            'request_header': self.http_message_factory.request_header.get_fields(),
                            'response':self.http_message_factory.response_message
                        }
            
            self.http_message_method, self.http_request_path, self.http_protocol = self.parse_first_line()
            path_tokens = re.split('\?(?!.+\/)',self.http_request_path)
            
            #Parse query_string 
            if len(path_tokens) == 2:
                self.http_request_path = url_utils.unescape_url(path_tokens[0])
                self.get_query_string(path_tokens[1])
            else:
                self.http_request_path = url_utils.unescape_url(path_tokens[0])
                
                
            self.http_message_factory.response_message.set_protocol(self.http_protocol)

            if self.http_message_factory.response_message.protocol_version == HTTP_Protocol_Version.HTTP_1_1:
                self.http_message_factory.stay_alive = True

            self.analyze_header()
            self.set_default_header()
            self.set_content()
            
        except Exception as e:
            #trace = traceback.print_exc()
            log(f'[PARSE] {e}',log_lvl='debug')