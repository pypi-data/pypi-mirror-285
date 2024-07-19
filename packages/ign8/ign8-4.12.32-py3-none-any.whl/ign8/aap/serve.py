# main file for semaphore

import os
import sys
import time
import json
import hvac
import requests
import pprint


from  ..common import prettyllog


def input_initial_secret(url=None, user=None, password=None):
  if url == None:
    AAP_URL = input("Enter the AAP URL: ")
  if user == None:
    AAP_USER = input("Enter the AAP USER: ")
  if password == None:
    AAP_PASS = input("Enter the AAP PASSWORD: ") # obscufate the password input
  return dict(AAP_URL=AAP_URL, AAP_USER=AAP_USER, AAP_PASS=AAP_PASS)


def get_credentials_from_vault():
  vaultpath = os.getenv('IGN8_VAULT_PATH')
  if vaultpath == None:
    vaultpath = "ignite"


  # Get credentials from vault
  try:
    client = hvac.Client()
  except:
    return False

  try:
    read_response = client.secrets.kv.read_secret_version(path=vaultpath)
  except:
    # If the path does not exist, create it
    # read the aap user, url and password from vault , obscufate the password input
    # create the path if it does not exist
    secret = input_initial_secret()
    client.secrets.kv.v2.create_or_update_secret(
      path=vaultpath,
      secret=secret
    )
  read_response = client.secrets.kv.read_secret_version(path=vaultpath)
  # check if the path secret contains the AAP_URL, AAP_USER and AAP_PASS
  try:
    URL = read_response['data']['data']['AAP_URL']
  except:
    URL = None
  try:
    USER = read_response['data']['data']['AAP_USER']
  except:
    USER = None
  try:
    PASS = read_response['data']['data']['AAP_PASS']
  except:
    PASS = None

  if URL == None or USER == None or PASS == None:
    secret  = input_initial_secret(URL, USER, PASS)
    client.secrets.kv.v2.create_or_update_secret(
      path=vaultpath,
      secret=secret
    )
    read_response = client.secrets.kv.read_secret_version(path=vaultpath)
  return read_response['data']['data']

  

def check_aap_login():
  # Check if the user is logged in

  return True  

def login_aap_basicauth(url, user, password):
  headers = {"User-agent": "python-awx-client", "Content-Type": "application/json"} 
  data = {"username": user, "password": password}
  url = url + "/api/v2/ping"
  resp = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
  if resp.status_code != 200:
    print("Login failed")
    return False
  # we need to create a token
  url = url + "/api/v2/tokens"
  resp = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
  if resp.status_code == 200:
    print("Token created")
    return resp.json()
  else:
    return False






def getawxdata(item, mytoken, r):
  headers = {"User-agent": "python-awx-client", "Content-Type": "application/json","Authorization": "Bearer {}".format(mytoken)}
  url = os.getenv("TOWER_HOST") + "/api/v2/" + item
  intheloop = "first"
  while ( intheloop == "first" or intheloop != "out" ):
    try:
      resp = requests.get(url,headers=headers, verify=VERIFY_SSL)
    except:
      intheloop = "out"
    try:
      mydata = json.loads(resp.content)
    except:
      intheloop = "out"
    try:
      url = os.getenv("TOWER_HOST") + "/api/v2/" + (mydata['next'])
    except: 
      intheloop = "out"
    savedata = True
    try:
      myresults = mydata['results'] 
    except:
      savedata = False
    if ( savedata == True ):
      for result in mydata['results']:
        key = os.getenv("TOWER_HOST") + item +":id:" + str(result['id'])
        r.set(key, str(result), 600)
        key = os.getenv("TOWER_HOST") + item +":name:" + result['name']
        r.set(key, str(result['id']), 600 )
        key = os.getenv("TOWER_HOST") + item +":orphan:" + result['name']
        r.set(key, str(result), 600)

  
def refresh_awx_data(mytoken,r ):
  items = { 
    "ad_hoc_commands",
    "analytics,applications",
    "credential_input_sources",
    "credentials",
    "credential_types",
    "execution_environments",
    "groups",
    "hosts",
    "inventory_sources",
    "inventory_updates",
    "jobs",
    "job_templates",
    "labels",
    "metrics",
    "notifications",
    "notification_templates",
    "organizations",
    "projects",
    "project_updates",
    "roles",
    "schedules",
    "system_jobs",
    "system_job_templates",
    "teams",
    "unified_jobs",
    "unified_job_templates",
    "workflow_approvals",
    "workflow_job_nodes",
    "workflow_jobs",
    "workflow_job_template_nodes",
    "workflow_job_templates"
  }
  #items = {"organizations", "projects", "credentials", "hosts", "inventories", "credential_types", "labels" , "instance_groups", "job_templates", "execution_environments"}    
  for item in items:
    getawxdata(item, mytoken, r)




def read_config():
  # Read config
  return True



  open("/etc/ign8/ign8.d/%s.json" % subproject, 'w').close()
  with open("/etc/ign8/ign8.d/%s.json" % subproject, 'w') as f:
    json.dump(data, f)
  return True


def main():
    prettyllog("serve", "init", "login", "automation platform", "0", "Testing", "INFO")
    secrets = get_credentials_from_vault()
    login_aap_basicauth(secrets['AAP_URL'], secrets['AAP_USER'], secrets['AAP_PASS'])


    read_config()
    return 0




