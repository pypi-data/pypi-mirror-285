
import re
HEX_CHARS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']


#TODO: unefficient af fix that 

def leading_ones_count(encoded_byte):
    byte_value = int(encoded_byte, 16)
    count = 0
    mask = 0x80 
    while mask != 0 and byte_value & mask:
        count += 1
        mask >>= 1
    return count

def unescape_url(url:str) -> str:
    unescaped = ''
    escape_sequence = ''
    index = 0
    count = 0
    url_len = len(url)
    
    while index < url_len:
        
        if len(escape_sequence) == 0 and url[index] == '%' and index + 3 <= url_len and url[index+1] in HEX_CHARS and url[index+2] in HEX_CHARS:
            escape_byte = url[index+1:index+3]
            count =  leading_ones_count(escape_byte)
            escape_sequence += escape_byte
            index += 3
            
        elif url[index] == '%' and index + 3 <= url_len and url[index+1] in HEX_CHARS and url[index+2] in HEX_CHARS and count > 1:
            escape_byte = url[index+1:index+3]
            count -= 1
            escape_sequence+= escape_byte
            index += 3
            
        elif escape_sequence:
            unescaped += decode_hex_string(escape_sequence)
            escape_sequence = ''
            count = 0
        else:
            unescaped += url[index]
            index += 1

    return unescaped if not escape_sequence else unescaped + decode_hex_string(escape_sequence)
            

def decode_hex_string(hex_string:str) ->str:
    try:
        decoded_bytes = bytes.fromhex(hex_string)
        unicode_char = decoded_bytes.decode('utf-8')
        return unicode_char
    except UnicodeDecodeError:
        return ''


#TODO: native URL matching withoug re for better performance 
#TODO: special hashing where string gets hash of matching template 
import re

class UrlTemplate:
    def __init__(self, template_string):
        self.template = template_string
        self.regex_pattern = '^' + re.sub(r'\{(\w+):(\w+)\}', self._repl, template_string) + '$'
        self.handler = None
        self.type = None
    
    def _repl(self, match):
        type_ = match.group(2)
        if type_ == 'int':
            return r'(\d+)'
        elif type_ == 'str':
            return r'(\w+)'
        elif type_ == 'float':
            return r'(\d+\.\d+)'
        elif type_ == 'bool':
            return r'(True|False)'
        elif type_ == 'path':
            return r'(.+)'
        else:
            raise ValueError(f"Unknown type: {type_}")
        
    def convert(self, value, type_):
        if type_ == 'int':
            return int(value)
        elif type_ == 'float':
            return float(value)
        elif type_ == 'bool':
            return value == 'True'
        else:
            return value
        
    def extract(self, url):
        match = re.match(self.regex_pattern, url)
        if match:
            return {k: self.convert(v, t) for (k, t), v in zip(re.findall(r'\{(\w+):(\w+)\}', self.template), match.groups())}
        else:
            return None
        
    def __eq__(self, url):
        if isinstance(url, str):
            return re.match(self.regex_pattern, url) is not None
        if isinstance(url, self.__class__):
            return self.template == url.template
        
        return False
