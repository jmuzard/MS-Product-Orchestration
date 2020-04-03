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
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from MSPO_utils import yaml_load, get_MSPO_env
from ftd_token import ftd_token, revoke_token

def ftd_get_hostname(connection_data,token):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    FTD_VERSION = connection_data.get('version')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    try:
        request = requests.get(
                        "https://{}:{}/api/fdm/latest/devicesettings/default/devicehostnames".format(FTD_HOST, FTD_PORT,FTD_VERSION),
						verify=False,
                        headers=headers
                        )
        if request.status_code == 200:
            return request.json()
    except requests.exceptions.HTTPError as errh:
        print("Http Error:",errh)
        sys.exit(1)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:",errc)
        sys.exit(1)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:",errt)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print("Resquests error",err)
        sys.exit(1)

def ftd_export_config(connection_data,token,config_entity):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    FTD_VERSION = connection_data.get('version')

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    if config_entity == "FULL":
        payload = {
            "doNotEncrypt": "true",
            "configExportType": "FULL_EXPORT",
            "type": "scheduleconfigexport"
            }
    else:
        payload = {
            "doNotEncrypt": "true",
            "configExportType": "PARTIAL_EXPORT",
        "entityIds": [
            "type=" + config_entity
        ],
        "type": "scheduleconfigexport"
        }
    try:
        response = requests.post(
                    "https://{}:{}/api/fdm/latest/action/configexport".format(FTD_HOST, FTD_PORT,FTD_VERSION),
                     verify = False,
                     headers = headers,
                     json = payload)
        if response.status_code == 200:
            return response.json()
    except:
        raise Exception('Error exporting ftd config : '+ response.status_code)

def ftd_get_export_status(connection_data,token,job_id):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    FTD_VERSION = connection_data.get('version')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization":"Bearer {}".format(token)
        }
    try:
        response = requests.get(
                    "https://{}:{}/api/fdm/latest/jobs/configexportstatus/{}".format(FTD_HOST, FTD_PORT ,job_id ),
                     verify = False,
                     headers = headers
                     )
        if response.status_code == 200:
            return response.json()
    except:
        raise Exception('Error getting export status: '+response.status_code)

def ftd_download_file(connection_data,token,filename):
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/octet-stream",
        "Authorization":"Bearer {}".format(token)
        }
    try:
        response = requests.get(
                    "https://{}:{}/api/fdm/latest/action/downloadconfigfile/{}".format(FTD_HOST, FTD_PORT ,filename ),
                     verify = False,
                     headers = headers,
                     stream = True,
                     )
        if response.status_code == 200:
            return response
    except:
        raise Exception('Error downloading config file code: '+response.status_code)

def beautify_json(config_path, config_entity):
    if config_entity == "FULL":
        f = open(config_path + "/" + "full_config.txt", "r")
        d = open(config_path + "/" + "full_config.json", "w")
    else:
        f = open(config_path + "/" + config_entity + ".txt", "r")
        d = open(config_path + "/" + config_entity + ".json", "w")
    data = f.readlines()
    output = "[\n"
    for line in data:
        if '{"hardwareModel":"Cisco Firepower Threat Defense' in line:
            parsed = json.loads(line)
            output = output + json.dumps(parsed, indent=2) + '\n,\n'
        if '"}}' in line:
            parsed = json.loads(line)
            output = output + json.dumps(parsed, indent=2) + '\n,\n'
    output = output + ("]")
    d.write(output.replace(",\n]", "]"))
    f.close()
    d.close()
    if config_entity == "FULL":
        os.rename(config_path + "/" + "full_config.json", config_path + "/" + "full_config.txt")
    else:
        os.rename(config_path + "/" + config_entity + ".json", config_path + "/" + config_entity + ".txt")
    return

if __name__ == "__main__":
#  load cfg parameters
    parser = argparse.ArgumentParser(
        description="Export full or partial config from FTD devices"
    )
    parser.add_argument('customer', help="customer name")
    parser.add_argument('device', help="FTD device name")
    parser.add_argument('config_entity',choices=[
                                            "FULL",
                                            "aaasetting",
                                            "accesspolicy",
                                            "accessrule",
                                            "ampcloudconnection",
                                            "datasslciphersetting,"
                                            "datadnssettings",
                                            "devicehostname,"
                                            "devicednssettings",
                                            "devicelogsettings",
                                            "dhcpservercontainer",
                                            "dnsservergroup",
                                            "domainnamegroup",
                                            "hafailoverconfiguration",
                                            "filepolicyconfiguration",
                                            "httpaccesslist",
                                            "identitypolicy",
                                            "intrusionsettings",
                                            "manualnatrule",
                                            "manualnatrulecontainer",
                                            "networkobject",
                                            "networkobjectgroup",
                                            "ntp",
                                            "physicalinterface",
                                            "portobject",
                                            "portobjectgroup",
                                            "ravpngrouppolicy,"
                                            "securityintelligencednspolicy",
                                            "securityintelligencenetworkpolicy",
                                            "securityintelligencepolicy",
                                            "securityintelligenceurlpolicy",
                                            "securityzone",
                                            "sslpolicy",
											"subinterface",
                                            "user",
                                            "webuicertificate"
                                            ],
                                            help="configuration entity: FULL or entity name"
                        )
    args = parser.parse_args()
    cfg = get_MSPO_env()
    CUSTOMER_VARS = cfg.get('customer_vars')
    CUSTOMER_CONFIGS = cfg.get('customer_configs')
# Load connection data
    CONNECTION_DATA = yaml_load(CUSTOMER_VARS + "/" + args.customer + "/sites/" + args.device + "/connect.yml")
# Get FTD token
    token = ftd_token(CONNECTION_DATA)
# Get hostname
    #result = ftd_get_hostname(CONNECTION_DATA,token)
    #hostname = result.get("hostname")
    #print("export and download configuration for hostname: ", hostname)
    #print(json.dumps(result,indent=2))
# Export FTD configuration
    result = ftd_export_config(CONNECTION_DATA,token, args.config_entity)
    job_id = result.get("jobHistoryUuid")
#print(json.dumps(result,indent=2))
    print("export job id: ", job_id)
# Get export file name
    result = ftd_get_export_status(CONNECTION_DATA,token,job_id)
    #print(json.dumps(result,indent=2))
    exported_filename = result.get("diskFileName")
    print("exported file name: ", exported_filename)
# Download configuration file from FTD
    result = ftd_download_file(CONNECTION_DATA,token,exported_filename)
    f = open("export.zip", 'wb')
    for chunk in result:
        f.write(chunk)
    f.close()
# Unzip the exported zip filename and delete zip file
    cfg_configs_path = CUSTOMER_CONFIGS + "/" + args.customer + "/" + args.device
    zip_file = zipfile.ZipFile("export.zip", 'r')
    zip_file.extractall(cfg_configs_path)
    os.remove("export.zip")
    if args.config_entity != "FULL":
        os.rename(cfg_configs_path + "/partial_config.txt", cfg_configs_path + "/" + args.config_entity + ".txt")
# Beautify json config
    beautify_json(cfg_configs_path, args.config_entity)
# Release FTD token
    revoke_token(CONNECTION_DATA, token)
