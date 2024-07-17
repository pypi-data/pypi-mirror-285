import sys
import os
import subprocess
import time
import webbrowser
from MediLink_ConfigLoader import log, load_configuration

import requests
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl
import signal
from threading import Thread, Event

import platform

config, _ = load_configuration()
local_storage_path = config['MediLink_Config']['local_storage_path']
downloaded_emails_file = os.path.join(local_storage_path, 'downloaded_emails.txt')

server_port = 8000
cert_file = 'server.cert'
key_file = 'server.key'
openssl_cnf = 'MediLink\\openssl.cnf' # This file needs to be located in the same place as where MediCafe is run from (so MediBot folder?)

httpd = None  # Global variable for the HTTP server
shutdown_event = Event()  # Event to signal shutdown

# Define the scopes for the Gmail API and other required APIs
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/script.external_request',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/script.scriptapp',
    'https://www.googleapis.com/auth/drive'
])

# Path to token.json file
TOKEN_PATH = 'token.json'

# Determine the operating system and version
os_name = platform.system()
os_version = platform.release()

# Set the credentials path based on the OS and version
if os_name == 'Windows' and 'XP' in os_version:
    CREDENTIALS_PATH = 'F:\\Medibot\\json\\credentials.json'
else:
    CREDENTIALS_PATH = 'json\\credentials.json'

# Log the selected path for verification
log("Using CREDENTIALS_PATH: {}".format(CREDENTIALS_PATH), config, level="INFO")

REDIRECT_URI = 'https://127.0.0.1:8000'

def get_authorization_url():
    with open(CREDENTIALS_PATH, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    client_id = credentials['web']['client_id']
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        "response_type=code&"
        "client_id={}&"
        "redirect_uri={}&"
        "scope={}&"
        "access_type=offline"
    ).format(client_id, REDIRECT_URI, SCOPES)
    return auth_url

def exchange_code_for_token(auth_code):
    with open(CREDENTIALS_PATH, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': auth_code,
        'client_id': credentials['web']['client_id'],
        'client_secret': credentials['web']['client_secret'],
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(token_url, data=data)
    log("Token exchange response: Status code {}, Body: {}".format(response.status_code, response.text))
    token_response = response.json()
    token_response['token_time'] = time.time()
    # Ensure refresh_token is saved
    if 'refresh_token' in token_response:
        with open(TOKEN_PATH, 'w') as token_file:
            json.dump(token_response, token_file)
    return token_response

def get_access_token():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as token_file:
            token_data = json.load(token_file)
            log("Loaded token data:\n {}".format(token_data))
            
            if 'access_token' in token_data and 'expires_in' in token_data:
                try:
                    token_expiry_time = token_data['token_time'] + token_data['expires_in']
                except KeyError as e:
                    log("KeyError: {}".format(e))
                    return None
                
                if token_expiry_time > time.time():
                    log("Access token is still valid.")
                    return token_data['access_token']
                else:
                    log("Access token has expired, refreshing token.")
                    new_token_data = refresh_access_token(token_data.get('refresh_token'))
                    if 'access_token' in new_token_data:
                        new_token_data['token_time'] = time.time()
                        with open(TOKEN_PATH, 'w') as token_file:
                            json.dump(new_token_data, token_file)
                        return new_token_data['access_token']
                    else:
                        log("Failed to refresh access token.")
                        return None
    log("Access token not found.")
    return None

def refresh_access_token(refresh_token):
    log("Refreshing access token.")
    with open(CREDENTIALS_PATH, 'r') as credentials_file:
        credentials = json.load(credentials_file)
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'client_id': credentials['web']['client_id'],
        'client_secret': credentials['web']['client_secret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(token_url, data=data)
    log("Refresh token response: Status code {}, Body:\n {}".format(response.status_code, response.text))
    if response.status_code == 200:
        log("Access token refreshed successfully.")
        return response.json()
    else:
        log("Failed to refresh access token. Status code: {}".format(response.status_code))
        return {}

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-type', 'application/json')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_headers()
        self.end_headers()

    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            links = data.get('links', [])

            # Log the content of links
            log("Received links: {}".format(links))

            file_ids = [link.get('fileId', None) for link in links if link.get('fileId')]
            log("File IDs received from client: {}".format(file_ids))
            
            # Proceed with downloading files
            download_docx_files(links)
            self.send_response(200)
            self._set_headers()  # Include CORS headers
            self.end_headers()
            response = json.dumps({"status": "success", "message": "All files downloaded", "fileIds": file_ids})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()
        elif self.path == '/shutdown':
            log("Shutdown request received.")
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Server is shutting down."})
            self.wfile.write(response.encode('utf-8'))
            shutdown_event.set()  # Signal shutdown event instead of calling stop_server directly
        elif self.path == '/delete-files':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            file_ids = data.get('fileIds', [])
            log("File IDs to delete received from client: {}".format(file_ids))
            
            if not isinstance(file_ids, list):
                self.send_response(400)
                self._set_headers()
                self.end_headers()
                response = json.dumps({"status": "error", "message": "Invalid fileIds parameter."})
                self.wfile.write(response.encode('utf-8'))
                return
            
            self.send_response(200)
            self._set_headers()  # Include CORS headers
            self.end_headers()
            response = json.dumps({"status": "success", "message": "Files deleted successfully."})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path.startswith("/?code="):
            auth_code = self.path.split('=')[1]
            log("Received authorization code: {}".format(auth_code))  # Add this line
            token_response = exchange_code_for_token(auth_code)
            log("Token response: {}".format(token_response))  # Add this line
            if 'access_token' in token_response:
                with open(TOKEN_PATH, 'w') as token_file:
                    json.dump(token_response, token_file)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Authentication successful. You can close this window now.".encode())
                initiate_link_retrieval()  # Proceed with link retrieval
            else:
                log("Authentication failed with response: {}".format(token_response))  # Add this line
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Authentication failed. Please check the logs for more details.".encode())
                shutdown_event.set()  # Signal shutdown event after failed authentication
        elif self.path == '/downloaded-emails':
            self.send_response(200)
            self._set_headers()
            self.end_headers()
            downloaded_emails = load_downloaded_emails()
            response = json.dumps({"downloadedEmails": list(downloaded_emails)})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'HTTPS server is running.')

def generate_self_signed_cert(cert_file, key_file):
    log("Checking if certificate file exists: " + cert_file)
    log("Checking if key file exists: " + key_file)
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        log("Generating self-signed SSL certificate...")
        cmd = [
            'openssl', 'req', '-config', openssl_cnf, '-nodes', '-new', '-x509',
            '-keyout', key_file,
            '-out', cert_file,
            '-days', '365'
            #'-subj', '/C=US/ST=...' The openssl.cnf file contains default values for these fields, but they can be overridden by the -subj option.
        ]
        try:
            log("Running command: " + ' '.join(cmd))
            result = subprocess.call(cmd)
            log("Command finished with result: " + str(result))
            if result != 0:
                raise RuntimeError("Failed to generate self-signed certificate")
            log("Self-signed SSL certificate generated.")
        except Exception as e:
            log("Error generating self-signed certificate: {}".format(e))
            raise

def run_server():
    global httpd
    try:
        log("Attempting to start server on port " + str(server_port))
        server_address = ('0.0.0.0', server_port)  # Bind to all interfaces
        httpd = HTTPServer(server_address, RequestHandler)
        log("Attempting to wrap socket with SSL. cert_file=" + cert_file + ", key_file=" + key_file)
        
        if not os.path.exists(cert_file):
            log("Error: Certificate file not found: " + cert_file)
        if not os.path.exists(key_file):
            log("Error: Key file not found: " + key_file)
        
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=cert_file, keyfile=key_file, server_side=True)
        log("Starting HTTPS server on port {}".format(server_port))
        httpd.serve_forever()
    except Exception as e:
        log("Error in serving: {}".format(e))
        stop_server()

def stop_server():
    global httpd
    if httpd:
        log("Stopping HTTPS server.")
        httpd.shutdown()
        httpd.server_close()
        log("HTTPS server stopped.")
    shutdown_event.set()  # Signal shutdown event

def load_downloaded_emails():
    downloaded_emails = set()
    if os.path.exists(downloaded_emails_file):
        with open(downloaded_emails_file, 'r') as file:
            downloaded_emails = set(line.strip() for line in file)
    log("Loaded downloaded emails: {}".format(downloaded_emails))
    return downloaded_emails

def download_docx_files(links):
    # Load the set of downloaded emails
    # TODO Test if any of these have a .csv extension and then move those to the right location locally.
    downloaded_emails = load_downloaded_emails()

    for link in links:
        try:
            url = link.get('url', '')
            filename = link.get('filename', '')
            
            # Log the variables to debug
            log("Processing link: url='{}', filename='{}'".format(url, filename))
            
            # Skip if email already downloaded
            if filename in downloaded_emails:
                log("Skipping already downloaded email: {}".format(filename))
                continue

            log("Downloading .docx file from URL: {}".format(url))
            response = requests.get(url, verify=False)  # Set verify to False for self-signed certs
            if response.status_code == 200:
                file_path = os.path.join(local_storage_path, filename)
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                log("Downloaded .docx file: {}".format(filename))
                # Add to the set and save the updated list
                downloaded_emails.add(filename)
                with open(downloaded_emails_file, 'a') as file:
                    file.write(filename + '\n')
            else:
                log("Failed to download .docx file from URL: {}. Status code: {}".format(url, response.status_code))
        except Exception as e:
            log("Error downloading .docx file from URL: {}. Error: {}".format(url, e))

def open_browser_with_executable(url, browser_path=None):
    try:
        if browser_path:
            log("Attempting to open URL with provided executable: {} {}".format(browser_path, url))
            process = subprocess.Popen([browser_path, url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                log("Browser opened with provided executable path using subprocess.Popen.")
            else:
                log("Browser failed to open using subprocess.Popen. Return code: {}. Stderr: {}".format(process.returncode, stderr))
        else:
            log("No browser path provided. Attempting to open URL with default browser: {}".format(url))
            webbrowser.open(url)
            log("Default browser opened.")
    except Exception as e:
        log("Failed to open browser: {}".format(e))

def initiate_link_retrieval():
    log("Initiating browser via implicit GET.")
    url_get = "https://script.google.com/macros/s/AKfycbzlq8d32mDlLdtFxgL_zvLJernlGPB64ftyxyH8F1nNlr3P-VBH6Yd0NGa1pbBc5AozvQ/exec?action=get_link"
    open_browser_with_executable(url_get)
    
    log("Preparing POST call.")
    url = "https://script.google.com/macros/s/AKfycbzlq8d32mDlLdtFxgL_zvLJernlGPB64ftyxyH8F1nNlr3P-VBH6Yd0NGa1pbBc5AozvQ/exec"
    downloaded_emails = list(load_downloaded_emails())
    payload = {
        "downloadedEmails": downloaded_emails
    }

    access_token = get_access_token()
    if not access_token:
        log("Access token not found. Please authenticate first.")
        shutdown_event.set()  # Signal shutdown event if token is not found
        return

    # Inspect the token to check its validity and permissions
    try:
        inspect_token(access_token)
    except Exception as e:
        log("Error inspecting token: {}".format(e))
        shutdown_event.set()  # Signal shutdown event on exception
        return

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }
    
    log("Request headers: {}".format(headers))
    log("Request payload: {}".format(payload))

    handle_post_response(url, payload, headers)
        
def handle_post_response(url, payload, headers):
    try:
        response = requests.post(url, json=payload, headers=headers)
        log("Response status code: {}".format(response.status_code))
        log("Response body: {}".format(response.text))

        if response.status_code == 200:
            response_data = response.json()
            log("Parsed response data: {}".format(response_data))  # Log the parsed response data
            if response_data.get("status") == "error":
                log("Error message from server: {}".format(response_data.get("message")))
                print("Error: {}".format(response_data.get("message")))
                shutdown_event.set()  # Signal shutdown event after error
            else:
                log("Link retrieval initiated successfully...")
                # What happens now? I think the webapp is supposed to make a call back to the server here to say its ready to download?
        elif response.status_code == 401:
            log("Unauthorized. Check if the token has the necessary scopes.")
            shutdown_event.set()
        elif response.status_code == 403:
            log("Forbidden. Ensure that the OAuth client has the correct permissions and the Apps Script is configured correctly.")
            shutdown_event.set()
        elif response.status_code == 404:
            log("Not Found. Verify the URL and ensure the Apps Script is deployed correctly.")
            shutdown_event.set()
        else:
            log("Failed to initiate link retrieval. Status code: {}".format(response.status_code))
            shutdown_event.set()  # Signal shutdown event on failure
    except requests.exceptions.RequestException as e:
        log("RequestException during link retrieval initiation: {}".format(e))
        shutdown_event.set()
    except Exception as e:
        log("Unexpected error during link retrieval initiation: {}".format(e))
        shutdown_event.set()

def inspect_token(access_token):
    info_url = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}".format(access_token)
    response = requests.get(info_url)
    log("Token info: Status code {}, Body: {}".format(response.status_code, response.text))
    return response.json()

def signal_handler(sig, frame):
    log("Signal received: {}. Initiating shutdown.".format(sig))
    stop_server()
    sys.exit(0)

def auth_and_retrieval():
    access_token = get_access_token()
    if not access_token:
        log("Access token not found or expired. Please authenticate first.")
        print("If the browser does not open automatically, please open the following URL in your browser to authorize the application:")
        auth_url = get_authorization_url()
        print(auth_url)
        open_browser_with_executable(auth_url)
        shutdown_event.wait()  # Wait for the shutdown event to be set after authentication
    else:
        log("Access token found. Proceeding.")
        initiate_link_retrieval()
        shutdown_event.wait()  # Wait for the shutdown event to be set

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Generate SSL certificate if it doesn't exist
        generate_self_signed_cert(cert_file, key_file)

        from threading import Thread
        log("Starting server thread.")
        server_thread = Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        auth_and_retrieval()

        log("Stopping HTTPS server.")
        stop_server()  # Ensure the server is stopped
        log("Waiting for server thread to finish.")
        server_thread.join()  # Wait for the server thread to finish
    except KeyboardInterrupt:
        log("KeyboardInterrupt received, stopping server.")
        stop_server()
        sys.exit(0)
    except Exception as e:
        log("An error occurred: {}".format(e))
        stop_server()
        sys.exit(1)