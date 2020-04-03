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

This script send ravpn confiration to asa

asa_ravpn.py -h
usage: asa_ravpn.py [-h] customer device

Configure Remote access VPN on ASA

positional arguments:
  customer    customer name
  device      Device name

optional arguments:
  -h, --help  show this help message and exit

Example:

python3 asa_ravpn.py customer1 avav1

"""
import netmiko
import os, os.path
import argparse
from MSPO_utils import yaml_load, get_MSPO_env, scp_copy, send_config
from renderjinja2 import renderjinja2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Configure Remote access VPN on ASA"
    )
    parser.add_argument('customer', help="customer name")
    parser.add_argument('device', help="Device name")
    args = parser.parse_args()
#
# -> send anyconnect packages
#
    cfg = get_MSPO_env()
    IMAGES_DIR = cfg.get('images')
    CFG_DEVICE = cfg.get('customer_vars') + "/"+  args.customer + "/sites/" + args.device + "/" + "ravpn.yml"
    IMAGE_LIST = yaml_load(CFG_DEVICE).get("images")
    for image in IMAGE_LIST:
        for i, r in image.items():
            sourcefile = IMAGES_DIR + "/" + i
            destfile = i
            scp_copy(args.customer, args.device, sourcefile, destfile, "put")
    CUSTOMER_CFG_DIR = cfg.get('customer_configs') + "/" + args.customer
    if os.path.isdir(CUSTOMER_CFG_DIR) == False:
        print("Customer folder not found: ", CUSTOMER_CFG_DIR)
        exit(1)
    DEVICE_DIR = CUSTOMER_CFG_DIR + "/" + args.device
    if os.path.isdir(DEVICE_DIR) == False:
        print("Device folder not found: ", DEVICE_DIR)
        exit(1)
#
# create and send anyconnect xml profile
#
# -> Create anyconnect profile from template
    renderjinja2(args.customer, args.device, "ACVPN_client_profile")
# -> send anyconnect profiles
    sourcefile = DEVICE_DIR + "/ACVPN_client_profile.txt"
    destfile = "ACVPN_client_profile.xml"
    scp_copy(args.customer, args.device, sourcefile, destfile, "put")
#
# create and send remote access VPN configuration
#
# ->create config file from template
    renderjinja2(args.customer, args.device, "ravpn")
# -> send remote access vpn config to ASA
    send_config(args.customer, args.device, "ravpn")
