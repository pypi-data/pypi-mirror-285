import subprocess
import json
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize AWS S3 client
s3 = boto3.client('s3')

s3_bucket = os.getenv('S3_BUCKET')
s3_region = os.getenv('S3_REGION')

def s3_check_bucket():
    try:
        s3.head_bucket(Bucket=s3_bucket)
        print(f"Bucket {s3_bucket} exists")
        return True
    except Exception as e:
        print(f"Bucket {s3_bucket} does not exist")
        return False
    
def s3_check_key(s3_key):
    try:
        s3.get_object(Bucket=s3_bucket, Key=s3_key)
        print(f"Key {s3_key} exists")
        return True
    except Exception as e:
        print(f"Key {s3_key} does not exist")
        return False
    
def s3_get_key(s3_key):
    try:
        response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        print(f"Could not get key {s3_key}")
        return False
    
def s3_put_key(s3_key, data):
    try:
        response = s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=data)
        return True
    except Exception as e:
        print(f"Could not put key {s3_key}")
        return False
    
def s3_delete_key(s3_key):
    try:
        response = s3.delete_object(Bucket=s3_bucket, Key=s3_key)
        return True
    except Exception as e:
        print(f"Could not delete key {s3_key}")
        return False
    
def s3_create_bucket():
    try:
        response = s3.create_bucket(Bucket=s3_bucket)
        return True
    except Exception as e:
        print(f"Could not create bucket {s3_bucket}")
        return False

def s3_delete_bucket():
    try:
        response = s3.delete_bucket(Bucket=s3_bucket)
        return True
    except Exception as e:
        print(f"Could not delete bucket {s3_bucket}")
        return False
    

def s3_create_credentials_file():
    credentials_file = f"""
[default]
aws_access_key_id = {os.getenv('AWS_ACCESS_KEY_ID')}
aws_secret_access_key = {os.getenv('AWS_SECRET_ACCESS_KEY')}
"""
    with open('/root/.aws/credentials', 'w') as file:
        file.write(credentials_file)
    config_file = f"""
[default]
region = {os.getenv('AWS_REGION')}
output = json
"""
    with open('/root/.aws/config', 'w') as file:
        file.write(config_file)





# Get the Swarm Node ID from Docker
def get_swarm_node_id():
    docker_info = subprocess.run(
        ['docker', 'system', 'info', '-f', 'json'],
        capture_output=True,
        text=True
    )
    print(docker_info.stdout)
    try: 
        id = json.loads(docker_info.stdout)['Swarm']['NodeID']
    except KeyError:
        print("Node is not part of a swarm")
        return False
    print(f"Node ID: {id}")
    return id

# Get the Swarm Node ID from s3

def mount_datadisk():
    # blkid holds the UUID of the disk
    try:
        datadisk = os.getenv('DATA_DISK')
    except KeyError:
        print("DATA_DISK environment variable not set")
        return False
    print(f"Data disk: {datadisk}")
    if datadisk == None:
        print("DATA_DISK environment variable not set")
        print("Please set the DATA_DISK environment variable to the path of the data disk")
        print("Example: /dev/sdb")
        print("export DATA_DISK=/dev/sdb")

        return False
    
    #blkid = subprocess.run(
     #   ['blkid', datadisk],
    #    capture_output=True,
    #    text=True
    #)
    # check if /var/lib/docker is mounted and exists in /etc/fstab
    with open('/etc/fstab', 'r') as file:
        fstab = file.read()

def main():
    mount_datadisk()

if __name__ == '__main__':
    main()
