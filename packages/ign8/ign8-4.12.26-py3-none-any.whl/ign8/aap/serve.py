# main file for semaphore

import os
import sys
import time
import json
import hvac
import requests
import pprint


from  ..common import prettyllog

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
    client.secrets.kv.v2.create_or_update_secret(
    path=vaultpath,
    secret=dict(AAP_URL='awxrpm.openknowoit.com', AAP_USER='admin', AAP_PASS='admin'),
)
  read_response = client.secrets.kv.read_secret_version(path=vaultpath)
  return read_response['data']['data']



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
    pprint.pprint(secrets)
    read_config()
    return 0




