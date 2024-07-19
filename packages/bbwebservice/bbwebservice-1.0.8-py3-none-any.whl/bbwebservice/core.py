import socket
from threading import Thread, Event, current_thread
import ssl
import os
from .config_loader import Config
from .http_parser import HTTP_Message_Factory, log, LOGGING_OPTIONS

# Define globals
SESSIONS = {}
PAGES = {}
GET_TEMPLATES = []
POST_HANDLER = {}
POST_TEMPLATES = []
ERROR_HANDLER = {}
SERVER_THREADS = []
CONFIG = Config()

def servlet(conn, addr, worker_state):
    """Handle a client connection in a separate thread."""
    try:
        while worker_state.is_set():
            log(f'[THREADING] thread {current_thread().ident} listens now.', log_lvl='debug')
            
            message_factory = HTTP_Message_Factory(conn, addr, PAGES, GET_TEMPLATES, POST_HANDLER, POST_TEMPLATES, ERROR_HANDLER)
            resp = message_factory.get_message()
            conn.sendall(resp)
            
            header, _, content = resp.partition(b'\r\n\r\n')
            log('\n\nRESPONSE:', str(header, 'utf-8'), content, '\n\n', log_lvl='response', sep='\n')
            
            if not message_factory.stay_alive:
                log(f'[THREADING] thread {current_thread().ident} closes because stay_alive is set to False', log_lvl='debug')
                break

    except TimeoutError:
        log(f'[THREADING] thread {current_thread().ident} closes due to a timeout error.', log_lvl='debug')
    except Exception as err:
        log(f'[THREADING] thread {current_thread().ident} closes due to an error: "{err}"', log_lvl='debug')
    finally:
        try:
            conn.settimeout(1.0)
            conn.close()
        except Exception as e:
            log(f'[THREADING] thread {current_thread().ident} encountered an error while closing connection: {e}', log_lvl='debug')

def main(server, state):
    """Accept and dispatch client connections to servlets."""
    print(f'[SERVER] {CONFIG.SERVER_IP} running on port {CONFIG.SERVER_PORT}...')
    while state.is_set():
        global SERVER_THREADS
        SERVER_THREADS = [t for t in SERVER_THREADS if t[0].is_alive()]

        if len(SERVER_THREADS) >= CONFIG.MAX_THREADS:
            continue

        try:
            conn, addr = server.accept()
            worker_state = Event()
            worker_state.set()
            if conn:
                worker_thread = Thread(target=servlet, args=(conn, addr, worker_state))
                SERVER_THREADS.append([worker_thread, worker_state, conn])
                worker_thread.start()
                conn.settimeout(15)
        except TimeoutError:
            pass
        except Exception as e:
            if state.is_set():
                log(f'[CONNECTION_ERROR] A connection failed due to the following error: {e}.\n', log_lvl='debug')

def shutdown_server(server, server_thread, server_state):
    """Shutdown the server and clean up resources."""
    server_state.clear()
    for worker_thread, worker_state, conn in SERVER_THREADS:
        worker_state.clear()
        try:
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except Exception as e:
            print(f"[SERVER] Error while closing client connection: {e}")
        worker_thread.join(timeout=1)

    try:
        server.shutdown(socket.SHUT_RDWR)
        server.close()
    except Exception as e:
        print(f"[SERVER] Error while closing server: {e}")
    server_thread.join(timeout=1)
    print('[SERVER] Closed...')

#in the future bbwebservice will be wrapped in Klasses so multible server instanzes can be hosted in one process
def sni_callback(sock, server_name, context):
    try:
        if server_name == CONFIG.HOST:
            context.load_cert_chain(certfile=CONFIG.CERT_PATH, keyfile=CONFIG.KEY_PATH)
            log(f'[SNI CALLBACK] Successfully loaded certificate for {server_name}', log_lvl='debug')
        else:
            log(f'[SNI CALLBACK] Unknown server name: {server_name}', log_lvl='debug')
    except Exception as e:
        log(f'[SNI CALLBACK] Error loading certificate: {e}', log_lvl='debug')

def start():
    """Start the server and initiate the main dispatcher."""
    if CONFIG.SERVER_IP == 'default':
        CONFIG.SERVER_IP = socket.gethostbyname(socket.gethostname())
    try:
        socket.setdefaulttimeout(2)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((CONFIG.SERVER_IP, CONFIG.SERVER_PORT))
        server.listen(CONFIG.QUE_SIZE)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if CONFIG.SSL:
            SERVER_HOSTNAME = CONFIG.HOST
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(CONFIG.CERT_PATH, CONFIG.KEY_PATH)
            server = context.wrap_socket(server, server_side=True)
            log(f'[SERVER] ssl active', log_lvl='debug')
            if SERVER_HOSTNAME:
                context.sni_callback = sni_callback
                log(f'[SERVER] SNI is active for {SERVER_HOSTNAME}\n', log_lvl='debug')
    except Exception as e:
        log(f'[SERVER] Error while attempting to start the server: {e}\n', log_lvl='debug')
        os._exit(1)

    server_state = Event()
    server_state.set()
    server_thread = Thread(target=main, args=(server, server_state))
    server_thread.start()

    try:
        while True:
            state = input()
            if state in ['quit', 'q', 'exit', 'e', 'stop']:
                shutdown_server(server, server_thread, server_state)
                break
    except KeyboardInterrupt:
        shutdown_server(server, server_thread, server_state)
        os._exit(0)
