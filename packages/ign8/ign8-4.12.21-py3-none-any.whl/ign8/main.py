from .common import prettylog
from .common import get_vault_client
from .common import decrypt_text
from .common import encrypt_text
from .common import get_vault_secret
from .common import get_vault_secret_data
from .common import get_vault_secret_field
from .common import get_vault_secret_field_decrypt
from .common import get_vault_secret_field_encrypt


import os
import subprocess
import time
import sys
import redis
import pprint
import json
import socket
import random
import string

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_port_open(hostname, port):
  """
  This function checks if a remote host is listening on a specific port.

  Args:
      hostname: The hostname or IP address of the remote host.
      port: The port number to check.

  Returns:
      True if the port is open, False otherwise.
  """
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
      s.settimeout(1)  # Set a timeout of 1 second
      s.connect((hostname, port))
      return True
    except socket.error:
      pass
  return False




def get_swarm_status():
    command = "docker info -f json |jq .Swarm.LocalNodeState -r"
    result = subprocess.run(command, capture_output=True, shell=True)
    if result.returncode == 0:
        return result.stdout.decode().strip()
    else:
        return False

def check_docker():
    command = "docker info"
    result = subprocess.run(command, capture_output=True, shell=True)
    if result.returncode == 0:
        prettylog("INFO", "Docker is running")
        return True
    else:
        prettylog("ERROR", "Docker is not running")
        return False
    
def check_remote_host(host):
    print("-------------------------------------" + host)
    port2377 = is_port_open(host, 2377)

    if port2377:
        prettylog("INFO", f"Port 2377 is open on {host}")
        return True
    else:
        prettylog("ERROR", f"Port 2377 is closed on {host}")
        return False
    
    


    



def read_dns_txt_record(domain):
    command = f"dig {domain} TXT"
    prettylog("INFO", f"Reading DNS TXT record for {domain}")
    result = subprocess.run(command, capture_output=True, shell=True)
    if result.returncode == 0:
        output = result.stdout.decode()
        start_index = output.find('"')
        end_index = output.rfind('"')
        txt_record = output[start_index:end_index + 1]
        txt_record_cleaned = txt_record.strip('"').replace('\\010', '').replace('\\', '')
        pprint.pprint(txt_record_cleaned)

        txt_dict = json.loads(txt_record_cleaned)
        return txt_dict
    else:
        prettylog("ERROR", f"Error reading DNS TXT record for {domain}")
        return False
    

def cloudflare():
    cf = CloudFlare.CloudFlare()
    zones = cf.zones.get()
    return cf


def getenv(key, default):
    if key in os.environ:
        return os.environ[key]
    else:
        return default

def main():
    return True

def in_venv():
    return sys.prefix != sys.base_prefix

def initdocker():
    if in_venv():
        prettylog("INFO", "Running in virtual environment")
        if os.path.exists("/usr/bin/docker"):
            prettylog("INFO", "Docker is installed")
        else:
            prettylog("ERROR", "Docker is not installed")
            return False
    else:
        prettylog("ERROR", "Not running in virtual environment")
        return False
    return True

def init_service():
    orchestrator = getenv("ORCHESTRATOR", "swarm")
    if orchestrator == "swarm":
        prettylog("INFO", "Orchestrator is swarm")
    else:
        prettylog("ERROR", "Orchestrator is not set")
        return False
    if not check_docker():
        initdocker()
        prettylog("ERROR", "Docker is not running")
        return False
    prettylog("INFO", "Docker is running")



    servicefile = "\
[Unit]\n\
Description=Ign8 Service\n\
After=network.target\n\
\n\
[Service]\n\
Type=simple\n\
User=root\n\
ExecStart=/usr/local/bin/ign8 serve\n\
Restart=always\n\
\n\
[Install]\n\
WantedBy=multi-user.target\n\
"
    servicefilename = "/etc/systemd/system/ign8.service"
    write_string_to_file(servicefilename, servicefile )
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "ign8"])

def check_redis():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
    except redis.ConnectionError:
        subprocess.run(["systemctl", "start", "redis"])
    prettylog("INFO", "Redis is running")

    
def host_is_up(peer):
    response = os.system("ping -c 1 " + peer)
    if response == 0:
        return True
    else:
        return False




def write_string_to_file(filename, content):
    with open(filename, 'w') as file:
        file.write(content)
    
    # Create and overwrite the service file"
def create_config_file():
    # create the directory
    if not os.path.exists('/etc/ign8'):
        os.makedirs('/etc/ign8')
    configfile = "\
{\n\
    \"ign8\": {\n\
        \"organisation\": \"ignite\"\n\
    \n\
}\n\
"
    configfilename = "/etc/ign8/config.json"
    write_string_to_file(configfilename, configfile)
    return True

def read_config():
    #check if the file exists
    if not os.path.exists('/etc/ign8/config.json'):
        if not create_config_file():
            return False
    open('/etc/ign8/config.json', 'r').read()
    myconfig = json.loads(open('/etc/ign8/config.json', 'r').read())
    return myconfig

def start_service():
    prettylog("INFO", "start service")
    subprocess.run(["systemctl", "start", "ign8"])


def stop_service():
    subprocess.run(["systemctl", "stop", "ign8"])

def cluster(myconfig):
    cstat = {}

    try: 
        myorg = myconfig['organisation']
    except:
        myorg = "ajax"
        prettylog("INFO", "No organisation found")
    try: 
        mycluster = myconfig['cluster']
    except:
        mycluster = "default"
        prettylog("INFO", "No cluster found")
    try:
        myservices= myconfig['core_services']
    except:
        prettylog("INFO", "No core services found")

    # is the cluster up on my local machine
    if get_swarm_status() == "active":
        cstat["local"] = "up"
    else:
        cstat["local"] = "down"
        cstat["swarm"] = False


    for clusterserver in mycluster:
        cstat[clusterserver] = {}
        
        if host_is_up(clusterserver):
            cstat[clusterserver]['ip'] = "up"
            swarmdetect = check_remote_host(clusterserver)
            if swarmdetect:
                cstat[clusterserver]['swarm'] = "up"
                cstat["swarm"] = True
            else:
                cstat[clusterserver]['swarm'] = "down"
        else:
            cstat[clusterserver]['ip'] = "down"
    print("=============================================    ")
    pprint.pprint(cstat)
    if not cstat["swarm"] and cstat["local"] == "down":
        prettylog("INFO", "No swarm cluster is up")
        # initiate a new swarm cluster
        prettylog("INFO", "Initiating a new swarm cluster")
        command = "docker swarm init"
        result = subprocess.run(command, capture_output=True, shell=True)
        if result.returncode == 0:
            prettylog("INFO", "Swarm cluster initiated")
        else:
            prettylog("ERROR", "Swarm cluster initiation failed")
    if cstat["local"] == "up":
        prettylog("INFO", "Swarm cluster is up")

        command = "docker swarm join-token manager"
        result = subprocess.run(command, capture_output=True, shell=True)
        if result.returncode == 0:
           pprint.pprint(  result.stdout.decode())


        # check if the cluster is up
        # check if the services are up
        

    print("=============================================    ")


        


    for service in myservices:
        prettylog("INFO", "Service", service)
        prettylog("INFO", "Sleeping")
    prettylog("INFO", "Config file found")
    prettylog("INFO", "Sleeping")
    time.sleep(3)


def serve():
    init_service()
    while True:
        check_redis()
        myconfig = read_dns_txt_record("core.ign8.it")
        prettylog("INFO", "Reading DNS TXT record for ign8.it")
        cluster(myconfig)



def therest():
        myconfig = read_config()
        try: 
            myorg = myconfig['organisation']
        except:
            myorg = "ajax"
            prettylog("INFO", "No organisation found")
        try: 
            mycluster = myconfig['cluster']
        except:
            mycluster = "default"
            prettylog("INFO", "No cluster found")
        try:
            myservices= myconfig['core_services']
        except:
            prettylog("INFO", "No core services found")

        for clusterserver in mycluster:
            prettylog("INFO", "Cluster server", clusterserver)
            if host_is_up(clusterserver):
                prettylog("INFO", "Host is up     : %s" % clusterserver)
            else:
                prettylog("ERROR", "Host is down  : %s" % clusterserver)
        for service in myservices:
            prettylog("INFO", "Service", service)
            prettylog("INFO", "Sleeping")
        prettylog("INFO", "Config file found")
        prettylog("INFO", "Sleeping")
        time.sleep(3)




