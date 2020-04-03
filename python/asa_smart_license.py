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

asa_smart_license.py -h
usage: asa_smart_license.py [-h] customer device

Configure Smart Lincense on ASA

positional arguments:
  customer    customer name
  device      Device name

optional arguments:
  -h, --help  show this help message and exit

Example:

python3 asa_smart_license.py customer1 avav1

"""
import argparse
from MSPO_utils import send_config
from renderjinja2 import renderjinja2

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Configure Smart Lincense on ASA"
    )
    parser.add_argument('customer', help="customer name")
    parser.add_argument('device', help="Device name")
    args = parser.parse_args()
#
# create and send smart license configuration
#
# -> create config file from template
    renderjinja2(args.customer, args.device, "smart_license")
# -> send config to asa
    send_config(args.customer, args.device, "smart_license")
