#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

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
Created: March 30, 2020

This script connect to a Cisco asa device using netmiko python libray and saves the device running configuration

usage: asa_cfg_retore.py [-h] customer device cfgfile

Restore ASA device configuration

positional arguments:
  customer    Customer name
  device      Device name
  cfgfile     Name of the configuration file to be restored

optional arguments:
  -h, --help  show this help message and exit

example:

python3 asa_cfg_restore.py customer1 asav1 running_config2020-Apr-03-14-20-21.txt

"""
import yaml
import os, os.path
from datetime import datetime
import netmiko
import argparse
from MSPO_utils import netmiko_connect, get_MSPO_env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Restore ASA device configuration "
    )
    parser.add_argument('customer', help="Customer name")
    parser.add_argument('device', help="Device name")
    parser.add_argument('cfgfile', help="Name of the configuration file to be restored")
    args = parser.parse_args()
# Check if configuration file exist
    cfg = get_MSPO_env()
    CUSTOMER_CFG_DIR = cfg.get('customer_configs') + "/" + args.customer
    if os.path.isdir(CUSTOMER_CFG_DIR) == False:
        print("Customer folder not found: ", CUSTOMER_CFG_DIR)
        exit(1)
    DEVICE_DIR = CUSTOMER_CFG_DIR + "/" + args.device
    if os.path.isdir(DEVICE_DIR) == False:
        print("Device folder not found: ", DEVICE_DIR)
        exit(1)
    CFG_FILE = DEVICE_DIR + "/" + args.cfgfile
    if os.path.isfile(CFG_FILE) == False:
        print("Configuration File not found: ", CFG_FILE)
        exit(1)
# Connect to the ASA
    ssh_conn = netmiko_connect(args.customer, args.device)
# Send the configuration, asa will close the communication channel when applying the configuration
    try:
        ssh_conn.send_config_from_file(config_file=CFG_FILE)
    except EOFError as err:
        pass
    except NetMikoTimeoutException as _err:
        pass
    print("configuration uploaded from file: ", CFG_FILE)
# Disconnect from ASA
    ssh_conn.disconnect()
