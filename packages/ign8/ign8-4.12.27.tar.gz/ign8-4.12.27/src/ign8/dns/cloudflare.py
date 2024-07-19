import requests
import dns.resolver
import json
import pprint
import os
from cryptography.fernet import Fernet

from ..common import prettyllog


def save_secret(secret, value):
    env = getenv()
    encrypted = encrypt_text(value).decode()
    add_record({"name": secret, "domain": env["IGN8_DNS_DOMAIN"], "type": "TXT", "ttl": 1, "proxied": False, "ipaddress": encrypted})

def load_secret(secret):
    env = getenv()
    mytxt = get_txt_records(secret + '.' + env["IGN8_DNS_DOMAIN"])
    if mytxt == None:
        exit(1)
    decrypted = decrypt_text(mytxt)
    print(decrypted)
    return decrypted


def delete_secret():   
    env = getenv()
    records = list_dns()
    try:
        encrypted = records["secret." + env["IGN8_DNS_DOMAIN"]]
    except:
        print("Record not found")
        exit(1)
    return True

def delete_record(id):
    myenv = getenv()
    url = os.environ.get("IGN8_DNS_URL") + "/client/v4/zones/" + os.environ.get("IGN8_DNS_ZONEID") + "/dns_records/" + id 
    bearer = "Bearer " + os

def generate_key():
    key = Fernet.generate_key()
    print(key.decode())
    return key.decode()

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
        




def getenv():
    env = {}
    env['IGN8_DNS_TYPE'] = os.getenv('IGN8_DNS_TYPE')
    env['IGN8_DNS_URL'] = os.getenv('IGN8_DNS_URL')
    env['IGN8_DNS_TOKEN'] = os.getenv('IGN8_DNS_TOKEN')
    env['IGN8_DNS_DOMAIN'] = os.getenv('IGN8_DNS_DOMAIN')
    env['IGN8_DNS_PROVIDER'] = os.getenv('IGN8_DNS_PROVIDER')
    if env['IGN8_DNS_TYPE'] != "cloudflare":
        print("DNS type not supported")
        exit(1)
    if env['IGN8_DNS_URL'] == None:
        print("DNS URL not set")
        exit(1)
    # if url ends with /, remove it
    if env['IGN8_DNS_URL'][-1] == "/":
        env['IGN8_DNS_URL'] = env['IGN8_DNS_URL'][:-1]

    if env['IGN8_DNS_TOKEN'] == None:
        print("DNS TOKEN not set")
        exit(1)
    if env['IGN8_DNS_DOMAIN'] == None:
        print("DNS DOMAIN not set")
        exit(1)
    if env['IGN8_DNS_PROVIDER'] == None:
        print("DNS PROVIDER not set")
        exit(1)
    return env




def check_access():
    print("Checking access #1")
    env = getenv()
    url = env["IGN8_DNS_URL"] + "/client/v4/user/tokens/verify"
    bearer = "Bearer " + os.environ.get("IGN8_DNS_TOKEN", "")
    headers = {
    "Authorization": bearer,
    "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    try:
        pprint.pprint(response.json())  
    except:
        print(response.status_code)
    if response.status_code == 200:
        if response.json()["result"]["status"] == "active":
            return True
    else:
        return False

def list_dns():
    domain = os.environ.get("IGN8_DNS_DOMAIN")
    myenv = getenv()
    #  --url https://api.cloudflare.com/client/v4/zones/zone_identifier/dns_records \
    url = os.environ.get("IGN8_DNS_URL") + "/client/v4/zones/" + os.environ.get("IGN8_DNS_ZONEID") + "/dns_records"
    bearer = "Bearer " + os.environ.get("IGN8_DNS_TOKEN", "")
    headers = {
    "Authorization": bearer,
    "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    records = {}
    if response.status_code == 200:
        for record in response.json()["result"]:
          records[record["name"]] = record["id"]
    else:
        print("Error: " + str(response.status_code))
        exit(1)
    return records

def delete_record(id):
    myenv = getenv()
    url = os.environ.get("IGN8_DNS_URL") + "/client/v4/zones/" + os.environ.get("IGN8_DNS_ZONEID") + "/dns_records/" + id 
    bearer = "Bearer " + os.environ.get("IGN8_DNS_TOKEN", "")
    headers = {
    "Authorization": bearer,
    "Content-Type": "application/json"
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        print("DNS record delete failed")
        return False
    


def get_txt_records(domain):
    mytxt = ""
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        for txt_record in txt_records:
            mytxt += txt_record.to_text()
    except dns.resolver.NoAnswer:
        print("No TXT records found for", domain)
    except dns.resolver.NXDOMAIN:
        print("Domain does not exist:", domain)
    except Exception as e:
        print("Error occurred:", e)
    return mytxt



def add_record(myitem = None):
    prettyllog("manage", "network", "DNS", "new", "000", "add record")
    myenv = getenv()
    records = list_dns()
    prettyllog("manage", "network", "DNS", "new", "000", "list dns records : " + str(len(records))) 
    if os.environ.get("IGN8_DNS_RECORD_NAME") == None:
        recordname = myitem["name"]
    else:
        recordname = os.environ.get("IGN8_DNS_RECORD_NAME")
    if myitem["type"] == "TXT":
        recordname = myitem["name"]

    if os.environ.get("IGN8_DNS_DOMAIN") == None:
        domain = myitem["domain"]
    else:
        domain = os.environ.get("IGN8_DNS_DOMAIN")
    
    if os.environ.get("IGN8_DNS_RECORD_TYPE") == None:
        recordtype = myitem["type"]
    else:
        recordtype = os.environ.get("IGN8_DNS_RECORD_TYPE")

    if os.environ.get("IGN8_DNS_RECORD_TTL") == None:
        recordttl = myitem["ttl"]
    else:
        recordttl = os.environ.get("IGN8_DNS_RECORD_TTL")

    if os.environ.get("IGN8_DNS_RECORD_PROXIED") == None:
        recordproxied = myitem["proxied"]
    else:
        recordproxied = os.environ.get("IGN8_DNS_RECORD_PROXIED")

    

    key = recordname + "." + domain   
    prettyllog("manage", "network", "DNS", "new", "000", "check if record exists : " + key)
    try:
      value =records[key]
    except:
        value = None
    if value != None:
        delete_record(records[key])
    prettyllog("manage", "network", "DNS", "new", "000", "adding : " + key)
    url = os.environ.get("IGN8_DNS_URL") + "/client/v4/zones/" + os.environ.get("IGN8_DNS_ZONEID") + "/dns_records"
    bearer = "Bearer " + os.environ.get("IGN8_DNS_TOKEN", "")
    headers = {
    "Authorization": bearer,
    "Content-Type": "application/json"
    }
    proxied = False
    if os.environ.get("IGN8_DNS_RECORD_PROXIED") == "true":
        proxied = True

    if os.environ.get("IGN8_DNS_CONTENT") == None:
        content = myitem["ipaddress"]
    else:
        content = os.environ.get("IGN8_DNS_CONTENT")

    if myitem["type"] == "TXT":
        content = myitem["ipaddress"]

    data = {
    "content": content, 
    "name": key,
    "proxied": proxied,
    "type": recordtype,
    "comment": "DNS record created by IGN8",
    "ttl": recordttl
    }
    pprint.pprint(data)
    print("-------------------------"   )

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return True
    else:
        return False
    






