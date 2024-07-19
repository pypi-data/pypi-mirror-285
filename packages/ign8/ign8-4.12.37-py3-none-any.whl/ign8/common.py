import os
from cryptography.fernet import Fernet
import datetime
import subprocess 
import hvac
import time 
import warnings
import urllib3
import subprocess


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    DEBUG   = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    INFO    = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


VERIFY_SSL = os.getenv("VERIFY_SSL", "false")
if VERIFY_SSL == "false" or VERIFY_SSL == "False" or VERIFY_SSL == "FALSE" or VERIFY_SSL == "no" or VERIFY_SSL == "NO" or VERIFY_SSL == "No":
  VERIFY_SSL = False
else:
  VERIFY_SSL = True

def line_in_file(file_path, search_text):
    with open(file_path, 'r') as f:
        for line in f:
            if search_text in line:
                return True
    return False
def runme(command):
  commandlist = command.split(" ")
  result = subprocess.run(commandlist, capture_output=True)
  payload = {"returncode": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr }
  return payload

    

def get_file_content(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def get_file_content_lines(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()
    
# 127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
    #    127.0.0.1 is the IP address of the client (remote host) which made the request to the server.
    # user-identifier is the RFC 1413 identity of the client. Usually "-".
    #frank is the userid of the person requesting the document. Usually "-" unless .htaccess has requested authentication.
    #[10/Oct/2000:13:55:36 -0700] is the date, time, and time zone that the request was received, by default in strftime format %d/%b/%Y:%H:%M:%S %z.
    #"GET /apache_pb.gif HTTP/1.0" is the request line from the client. The method GET, /apache_pb.gif the resource requested, and HTTP/1.0 the HTTP protocol.
    #200 is the HTTP status code returned to the client. 2xx is a successful response, 3xx a redirection, 4xx a client error, and 5xx a server error.
    #2326 is the size of the object returned to the client, measured in bytes.
# we need to rewrite prettylog to use this format
    
def encrypt_text(text):
    key = os.environ.get("IGN8_ENCRYPTION_KEY")
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(text.encode())
    return encrypted_text

def decrypt_text(encrypted_text):
    key = os.environ.get("IGN8_ENCRYPTION_KEY")
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(encrypted_text).decode()
    return decrypted_text

def prettyllog(function, action, item, organization, statuscode, text, severity="INFO"):
  silence = False
  try:
    if os.getenv("IGN8_SILENCE", "false").lower() == "true":
      silence = True
  except:
    silence = False
    
  if silence:
    return True

  d_date = datetime.datetime.now()
  reg_format_date = d_date.strftime("%Y-%m-%d %I:%M:%S %p")
  if severity == "INFO":
    print(f"{bcolors.INFO}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  elif severity == "WARNING":
    print(f"{bcolors.WARNING}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  elif severity == "ERROR":
    print(f"{bcolors.FAIL}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  elif severity == "DEBUG":
    print(f"{bcolors.OKCYAN}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  else:
    print(f"{bcolors.INFO}%-20s: %-12s %20s %-50s %-20s %-4s %-50s " %( reg_format_date, function,action,item,organization,statuscode, text))
  print(f"{bcolors.ENDC}", end='')
  return True


def prettylog(severity, text, json = {}):
  silence = False
  try:
    if os.getenv("IGN8_SILENCE", "false").lower() == "true":
      silence = True
  except:
    silence = False
    
  if silence:
    return True

  d_date = datetime.datetime.now()
  reg_format_date = d_date.strftime("%Y-%m-%d %I:%M:%S %p")
  if severity == "INFO":
    print(f"{bcolors.INFO}%-20s: %-12s %s" %( reg_format_date, severity, text))
  elif severity == "WARNING":
    print(f"{bcolors.WARNING}%-20s: %-12s %s " %( reg_format_date, severity, text))
  elif severity == "ERROR":
    print(f"{bcolors.FAIL}%-20s: %-12s %s " %( reg_format_date, severity, text))
  elif severity == "DEBUG":
    print(f"{bcolors.OLCYAN}%-20s: %-12s %s " %( reg_format_date, severity, text))
  else:
    print(f"{bcolors.INFO}%-20s: %-12s %s " %( reg_format_date, severity, text))
  print(f"{bcolors.ENDC}", end='')
  return True



def get_vault_client():
  vault_addr = os.getenv("VAULT_ADDR")
  vault_token = os.getenv("VAULT_TOKEN")
  vault_namespace = os.getenv("VAULT_NAMESPACE")
  if vault_namespace:
    vault_namespace = vault_namespace + "/"
  if vault_addr == None:
    prettylog("ERROR", "VAULT_ADDR not set")
    return None
  if vault_token == None:
    prettylog("ERROR", "VAULT_TOKEN not set")
    return None
  try:
    client = hvac.Client(url=vault_addr, token=vault_token, namespace=vault_namespace, verify=VERIFY_SSL)
    return client
  except Exception as e:
    prettylog("ERROR", f"Error connecting to vault: {e}")
    return None
  
def get_vault_secret(secret_path):
  client = get_vault_client()
  if client == None:
    return None
  try:
    secret = client.secrets.kv.v2.read_secret_version(path=secret_path)
    return secret
  except Exception as e:
    prettylog("ERROR", f"Error reading secret from vault: {e}")
    return None
  
def get_vault_secret_data(secret_path):
  secret = get_vault_secret(secret_path)
  if secret == None:
    return None
  try:
    data = secret["data"]["data"]
    return data
  except Exception as e:
    prettylog("ERROR", f"Error reading secret data from vault: {e}")
    return None
  
def get_vault_secret_field(secret_path, field):
  data = get_vault_secret_data(secret_path)
  if data == None:
    return None
  try:
    value = data[field]
    return value
  except Exception as e:
    prettylog("ERROR", f"Error reading secret field from vault: {e}")
    return None
  
def get_vault_secret_field_decrypt(secret_path, field):
  value = get_vault_secret_field(secret_path, field)
  if value == None:
    return None
  try:
    decrypted_value = decrypt_text(value)
    return decrypted_value
  except Exception as e:
    prettylog("ERROR", f"Error decrypting secret field from vault: {e}")
    return None
  
def get_vault_secret_field_encrypt(secret_path, field):
  value = get_vault_secret_field(secret_path, field)
  if value == None:
    return None
  try:
    encrypted_value = encrypt_text(value)
    return encrypted_value
  except Exception as e:
    prettylog("ERROR", f"Error encrypting secret field from vault: {e}")
    return None
  
def put_vault_secret(secret_path, data):
  client = get_vault_client()
  if client == None:
    return None
  try:
    secret = client.secrets.kv.v2.create_or_update_secret(path=secret_path, secret=data)
    return secret
  except Exception as e:
    prettylog("ERROR", f"Error writing secret to vault: {e}")
    return None
  
