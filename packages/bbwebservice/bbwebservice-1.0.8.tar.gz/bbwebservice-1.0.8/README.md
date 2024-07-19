# bbwebservice

`bbwebservice` is a small Python library for creating simple webservers.

## Installation

To install this library, use the pip command: `pip install bbwebservice`

## Usage

- how to import:

```python
from bbwebservice.webserver import * 
```

1. Register pages for HTTP `GET`:
   - `@register`: When using the `@register` decorator, you must define the named parameters `route` and `type`.
     - `route`: The URL which must be requested via HTTP `GET` method for the decorated function to execute. The decorated function is expected to return the respective response content.
     - `type`: The `type` parameter holds the intended MIME-type of the response.

```python
@register(route='/', type=MIME_TYPE.HTML)
def main_page():
    return load_file('/content/index.html')
```

2. Register pages for HTTP `POST`:
   - `@post_handler`: Works similarly to [1.], with the only difference being that it is mandatory for the decorated function to take a parameter.

```python
@post_handler(route='/makethread', type=MIME_TYPE.HTML)
def makethread(args):
    return load_file('/content/post.html')
```

3. Redirect:
  To redirect a request, you can return a `Redirect` object that specifies the path to which the request should be redirected.

```python
@register(route='/foo', type=MIME_TYPE.HTML)
def redirect():
    return Redirect('/')
```

4. PartialContent and videostreaming:
   To serve partial-content for video streaming or other applications, you can return a `PartialContent` object which takes the location of the streamed file and the chunk size which determines the size of the parts that should be streamed.

```python
@register(route='/video.mp4', type=MIME_TYPE.MP4)
def vid(args):
    return PartialContent("/content/v.mp4", 80000)
```

5. Error handler:
   With the `@error_handler`, it is possible to provide default responses for requests with the specified error code.

```python
@error_handler(error_code=404, type=MIME_TYPE.HTML)
def not_found():
    return load_file('/content/404.html')
```

6. Handler args:
   Setting cookies, getting query strings, or setting custom headers are possible when you give your handler function a parameter.

```python
@post_handler(route='/', type=MIME_TYPE.HTML)
def login(args):
    set_cookie(args, 'id', "test")
    return load_file('/content/index.html')
```

The server-supplied `args` value looks something like this, and changes to the provided value will be reflected in the server answer:

```py
{
    "query_string": {},
    "flags": [],
    "template_args": {},
    "cookies": {},
    "address": ("192.168.56.1", 64361),
    "post": bytearray(b""),
    "request_header": {
        "Host": ["192.168.56.1:5000"],
        "Connection": ["keep-alive"],
        "User-agent": ["Mozilla/5.0 (Windows NT 10.0", "Win64", "x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"],
        "Accept": ["text/html,application/xhtml+xml,application/xml", "q=0.9,image/avif,image/webp,image/apng,*/*", "q=0.8,application/signed-exchange", "v=b3", "q=0.7"],
        "Accept-encoding": ["gzip, deflate"],
        "Accept-language": ["de-DE,de", "q=0.9,en-US", "q=0.8,en", "q=0.7"]
    },
    "response": "<bbwebservice.http_parser.HTTP_Response object at 0x00000151D5718E50>"
}
```

7. Start the server (example of fully functional server):
   To start the server, invoke the `start` function.

```python
from bbwebservice.webserver import *

@register(route='/', type=MIME_TYPE.HTML)
def main():
    return load_file('/content/index.html')

start()
```

8. With URL-templating you are able to match dynamic URLs like `/test/paul/1456379827256`

```py
@register(route= UrlTemplate('/test/{name:str}/{id:int}'), type=MIME_TYPE.TEXT)
def test(args):
    return str(args[STORE_VARS.TEMPLATE_VARS])

```

## Server Configuration

In the directory `/config`, there is a file named `config.json`. Here you can configure the server:

```json
{
    "ip": "localhost",
    "port": 5000,
    "queue_size": 10,
    "SSL": false,
    "cert_path" : "",
    "key_path" : ""
}
```

If you intend to keep the application centrally (online), it is recommended to set the value of `ip` to either `default` or the IP address of the respective server. Additionally, it is advisable to activate `SSL` and set the corresponding paths for `cert_path` and `key_path`. 

### Recommended Ports

- 5000: For testing purposes
- 443: For HTTPS (SSL = true)
- 80: For HTTP (SSL = false)

## Logging

```python
log_to_file()
set_logging(LOGGING_OPTIONS.INFO, True)
set_logging(LOGGING_OPTIONS.TIME, True)
set_logging(LOGGING_OPTIONS.DEBUG, True)
set_logging(LOGGING_OPTIONS.ERROR, True)
```
