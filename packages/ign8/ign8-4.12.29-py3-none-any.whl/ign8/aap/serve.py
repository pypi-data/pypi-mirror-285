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




