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
Update: March 20 2020, yaml_save(added)
Update: March 31 2020, netmiko_connect & scp_copy added
"""
import yaml
import os, os.path
import netmiko
import socket
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException, FileTransfer
def yaml_load(yaml_file):
	'''
	load yaml file and returns a python dictionnary
    Parameters:
	'''
	f = open(yaml_file, "r")
	yamlrawtext = f.read()
	yamldata = yaml.safe_load(yamlrawtext)
	return yamldata

def yaml_save(yaml_file, obj_dict):
    '''
    This method writes out a python dictionary in YAML format to a file
    Parameters:
    yaml_file -- File to write the data to
    obj_dict -- the structure to write
    '''
    f = open(yaml_file, 'w')
    yaml.dump(obj_dict, f)
    f.close()
    return

def get_MSPO_env():
    '''
    This method read the cfg.yml that must be in same folder as the python scripts,
    it returns either:
    - the cfg dictionnary unchanged if MSPO_ROOT environement variable is not set
    - or replace "$MSPO_ROOT" in cfg.yml by its value
    '''
    cfg = yaml_load("cfg.yml")
    if "MSPO_DIR" in os.environ:
        MSPO_DIR = os.environ.get('MSPO_DIR')
        for k, v in cfg.items():
            if "MSPO_DIR" in v:
                    cfg[k] = v.replace('$MSPO_DIR', MSPO_DIR)
            else:
                print("$MSPO_DIR prefix missing in cfg.yml")
                exit(1)
    return cfg

def netmiko_connect(customer, device):
    '''
    This method connect to network device via netmiko
    Parameters:
    customer -- Customer name
    device -- name of the device
    It uses:
    - cfg.yml to learn the path to the device's connect.yml file
    - connect.yml which includes connection parameter (device IP, device type, username and password)
    '''
    cfg = get_MSPO_env()
    CONNECT_FILE = cfg.get('customer_vars') + "/"+  customer + "/sites/" + device + "/" + "connect.yml"
    if not os.path.isfile(CONNECT_FILE):
        print ("connect.yml does'not not exist:", CONNECT_FILE)
        exit(1)
    connect_data = yaml.safe_load(open(CONNECT_FILE))
    try:
        ssh_conn = netmiko.ConnectHandler(
                                        ip = connect_data.get('ipaddress'),
                                        device_type = connect_data.get('device_type'),
                                        username = connect_data.get('username'),
                                        password = connect_data.get('password'),
                                        timeout = 10
                                    )
    except (NetMikoTimeoutException, NetMikoAuthenticationException) as err:
        print(err)
        exit(1)
    return ssh_conn

def scp_copy(customer, device, sourcefile, destfile, direction):
    ssh_conn = netmiko_connect(customer, device)
    dest_file_system = 'disk0:'
    scp_transfer = FileTransfer(
            ssh_conn = ssh_conn,
            source_file=sourcefile,
            dest_file=destfile,
            file_system=dest_file_system,
            direction=direction,
        )
    if direction == "put":
        if not scp_transfer.check_file_exists():
            if not scp_transfer.verify_space_available():
                raise ValueError("Insufficient space available on remote device")
    else:
        if not scp_transfer.verify_space_available():
            raise ValueError("Insufficient space available on remote device")
# Enable scp on ASA
    ssh_conn.send_config_set("ssh scopy enable")
# Transfer the file
    print("Transferring file:", sourcefile)
    try:
        scp_transfer.establish_scp_conn()
        scp_transfer.transfer_file()
# in case of a get ASA close the scp connection and we get EOFError
    except (Exception, socket.error, EOFError) as err:
        print(err)
# Disable scp on ASA
    ssh_conn.send_config_set("no ssh scopy enable")
# File verification
    print("Verifying file")
    if scp_transfer.verify_file():
        print("Source and destination MD5 matches")
    else:
        raise ValueError("MD5 failure between source and destination files")
    return

def send_config(customer, device, config_entity):
    cfg = get_MSPO_env()
    CUSTOMER_CFG_DIR = cfg.get('customer_configs') + "/" + customer
    if os.path.isdir(CUSTOMER_CFG_DIR) == False:
        print("Customer folder not found: ", CUSTOMER_CFG_DIR)
        exit(1)
    DEVICE_DIR = CUSTOMER_CFG_DIR + "/" + device
    if os.path.isdir(DEVICE_DIR) == False:
        print("Device folder not found: ", DEVICE_DIR)
        exit(1)
    DEVICE_DIR = CUSTOMER_CFG_DIR + "/" + device
    if os.path.isdir(DEVICE_DIR) == False:
        print("Device folder not found: ", DEVICE_DIR)
        exit(1)
    # -> send remote access vpn config to ASA
    CFG_FILE = DEVICE_DIR + "/" + config_entity + ".txt"
    ssh_conn = netmiko_connect(customer, device)
    output = ssh_conn.send_config_from_file(CFG_FILE)
    ssh_conn.disconnect()
