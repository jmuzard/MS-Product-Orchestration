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

usage: asa_cfg_backup.py [-h] [-t {running,startup}] customer device

Backup startup or running configuration from ASA device

positional arguments:
  customer              Customer name
  device                Device name

optional arguments:
  -h, --help            show this help message and exit
  -t {running,startup}, --type {running,startup}
                        specify configuration to be saved: startup_config or
                        runing_config
examples:

python3 asa_cfg_backup.py customer1 asav1 -> this will save the running config

python3 asa_cfg_backup.py customer1 asav1 -t startup -> this will save the startup config

"""
import os, os.path
from datetime import datetime
import netmiko
import argparse
from MSPO_utils import netmiko_connect, get_MSPO_env
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        description="Backup startup or running configuration from ASA device"
                        )
    parser.add_argument('customer', help="Customer name")
    parser.add_argument('device', help="Device name")
    parser.add_argument('-t', '--type', choices=['running', 'startup'], default='running', help="specify configuration to be saved: startup_config or runing_config")
    args = parser.parse_args()
# Connect to the ASA
    ssh_conn = netmiko_connect(args.customer, args.device)
    ssh_conn.send_command("terminal parse 0")
    if args.type == 'running':
        config = ssh_conn.send_command("show running-config")
    else:
        config = ssh_conn.send_command("show startup-config")
# set up config file name = devicename + timestamp + .txt
    cfg = get_MSPO_env()
    CUSTOMER_CFG_DIR = cfg.get('customer_configs') + "/" + args.customer
    if os.path.isdir(CUSTOMER_CFG_DIR) == False:
        os.mkdir(CUSTOMER_CFG_DIR)
    DEVICE_DIR = CUSTOMER_CFG_DIR + "/" + args.device
    if os.path.isdir(DEVICE_DIR) == False:
        os.mkdir(DEVICE_DIR)
    if args.type == 'running':
        CFG_FILE = DEVICE_DIR+ "/" + "running_config" + datetime.now().strftime("%Y-%b-%d-%H-%M-%S") + ".txt"
    else:
        CFG_FILE = DEVICE_DIR+ "/" + "startup_config" + datetime.now().strftime("%Y-%b-%d-%H-%M-%S") + ".txt"
# write config
    f = open(CFG_FILE, "w")
    f.write(config)
    f.close
    print("configuration saved to backup file: ", CFG_FILE)
# Disconnect from ASA
    ssh_conn.disconnect()
