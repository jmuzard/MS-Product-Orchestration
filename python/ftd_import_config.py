#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python Template for Cisco Sample Code.

Copyright (c) 2020 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

Author: Jean-Pierre Muzard <jmuzard@cisco.com>
Created: March 13, 2020
"""
import sys, os
import argparse
import requests
import json
import zipfile
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from MSPO_utils import yaml_load, get_MSPO_env
from ftd_token import ftd_token, revoke_token

def upload_config(connection_data, token, file):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
# Check if file exits and is valid
    if not os.path.isfile(config_file_path):
        print('Import file does not exist')
        exit(1)
    file_name_without_path = os.path.split(file)[1]
    if file_name_without_path.split(".")[1] != "txt":
        print('Import file extension must be: .txt')
        exit(1)
    file_dict = open(file, "r").read()
# In case a file with same name exist on the FTD delete it
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    print(os.path.split(file)[1])
    response = requests.delete(
                    "https://{}:{}/api/fdm/latest/action/configfiles/{}".format(FTD_HOST, FTD_PORT, os.path.split(file)[1]),
                    verify=False,
                    headers=headers
                    )
    print(response.status_code)
# Upload the file
    randtoken = random.randint(1000000, 500000000)
    randtoken2 = random.randint(1000000, 500000000)
    multipart_separator = (str(randtoken)+str(randtoken2))
    # Next form the body of the request
    body = '--' + multipart_separator + '\r\n'
    body += 'Content-Disposition: form-data; name="fileToUpload"; filename="%s"\r\n' % file_name_without_path
    body += 'Content-Type: text/plain\r\n\r\n'
    # File goes here
    body += file_dict + '\r\n'
    body += '\r\n--' + multipart_separator + '--\r\n'
    headers = {
        "Content-Type": "multipart/form-data; boundary=" + multipart_separator,
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    try:
        response = requests.post(
                        "https://{}:{}/api/fdm/latest/action/uploadconfigfile".format(FTD_HOST, FTD_PORT),
						body,
                        verify=False,
                        headers=headers
                        )
        if response.status_code == 200:
            return response.json()
        else:
            print("Error uploading file:", file, str(response.status_code))
            sys.exit(1)
    except response.exceptions.HTTPError as errh:
        print("Http Error:",errh)
        sys.exit(1)
    except response.exceptions.ConnectionError as errc:
        print("Error Connecting:",errc)
        sys.exit(1)
    except response.exceptions.Timeout as errt:
        print("Timeout Error:",errt)
        sys.exit(1)
    except response.exceptions.RequestException as err:
        print("Resquests error",err)
        sys.exit(1)

def import_config(connection_data, token, cfg_file):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    payload = {
        "diskFileName": cfg_file,
        "preserveConfigFile": "true",
        "autoDeploy": "true",
        "allowPendingChange": "true",
        "type": "scheduleconfigimport"
        }
    try:
        response = requests.post(
                        "https://{}:{}/api/fdm/latest/action/configimport".format(FTD_HOST, FTD_PORT),
                        verify = False,
                        headers = headers,
                        json = payload
                        )
        if response.status_code == 200:
            return response.json()
        else:
            print("Error importing file:", cfg_file, str(response.status_code))
            sys.exit(1)
    except response.exceptions.HTTPError as errh:
        print("Http Error:",errh)
        sys.exit(1)
    except response.exceptions.ConnectionError as errc:
        print("Error Connecting:",errc)
        sys.exit(1)
    except response.exceptions.Timeout as errt:
        print("Timeout Error:",errt)
        sys.exit(1)
    except response.exceptions.RequestException as err:
        print("Resquests error",err)
        sys.exit(1)

def ftd_get_import_status(connection_data,token,job_id):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    headers = {
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    try:
        response = requests.get(
                    "https://{}:{}/api/fdm/latest/jobs/configimportstatus".format(FTD_HOST, FTD_PORT),
                     verify = False,
                     headers = headers
                     )
        if response.status_code == 200:
            return response.json()
        else:
            print('Error getting import status: ' + str(response.status_code))

    except:
        raise Exception('Error getting import status: '+response.status_code)



if __name__ == "__main__":
#  load cfg parameters
    parser = argparse.ArgumentParser(
        description="Export full or partial config from FTD devices"
    )
    parser.add_argument('customer', help="customer name")
    parser.add_argument('device', help="FTD device name")
    parser.add_argument('cfg_file',help="FTD configuration file")
    args = parser.parse_args()
    cfg = get_MSPO_env()
    CUSTOMER_VARS = cfg.get('customer_vars')
    CUSTOMER_CONFIGS = cfg.get('customer_configs')
# Load connection data
    CONNECTION_DATA = yaml_load(CUSTOMER_VARS + "/" + args.customer + "/sites/" + args.device + "/connect.yml")
# Get FTD token
    token = ftd_token(CONNECTION_DATA)
# upload config file
    config_file_path = CUSTOMER_CONFIGS + "/" + args.customer + "/" + args.device + "/" + args.cfg_file
    result = upload_config(CONNECTION_DATA, token, config_file_path)
    print("file upload:", args.cfg_file, " - success")
# import the uplaoded configuration filename
    result = import_config(CONNECTION_DATA, token, args.cfg_file)
    job_id = result.get("jobHistoryUuid")
# check if import job was successfull
    result = ftd_get_import_status(CONNECTION_DATA,token,job_id)
# Release FTD token
    revoke_token(CONNECTION_DATA, token)
