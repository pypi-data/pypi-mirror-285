import os 
from . import MAIN_PATH


def load_bin_file_partial(path, start_byte, end_byte) -> bytes:

    path = MAIN_PATH+path
    with open(path, 'rb') as file:
        file.seek(start_byte)
        data = file.read(end_byte - start_byte)
    return data


def get_file_size(path: str) -> int:
    try:
        size = os.path.getsize(MAIN_PATH+path)
        return size
    except FileNotFoundError:
        return -1


class PartialContent:

    def __init__(self, path, default_size) -> None:
        self.path = path
        self.default_size = default_size
    
    def get_range(self, start, end) -> bytes:
        
        end = end if end else end + self.default_size
        return load_bin_file_partial(self.path, start,min(self.get_size(), end+1))
    
    def get_size(self) -> int:
        return get_file_size(self.path)
    

class Redirect:
    
    def __init__(self, path, status= None) -> None:
        self.path = path
        self.status = status 