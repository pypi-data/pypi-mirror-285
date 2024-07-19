import webbrowser
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import rich
from vanty.config import config

DJANGO_AUTH_URL = "https://www.advantch.com/api/v1/cli/login/"

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Authentication complete. You can close this window.")
        
        query = urlparse(self.path).query
        params = parse_qs(query)
        self.server.auth_code = params.get('code', [None])[0]


def start_local_server():
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.auth_code = None
    server.handle_request()
    return server.auth_code


def authenticate():
    # get machine id
    import platform
    machine_id = platform.node()
    
    client_id = config.get("client_id", 'unknown')
    node_id = config.get("node_id", machine_id)
    
    auth_url = f"{DJANGO_AUTH_URL}?client_id="
    webbrowser.open(auth_url)
    
    rich.print("Waiting for authentication...")
    auth_code = start_local_server()
    
    if auth_code:
        # Exchange auth code for token (implement this part based on your Django app's API)
        # token = exchange_code_for_token(auth_code)
        print("Authentication successful!")
        return auth_code
    else:
        print("Authentication failed.")
        return None
