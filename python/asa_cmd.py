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

This script connect to a Cisco asa device using netmiko python libray and execute a CLI send_command

Example:

python3 asa_cmd.py customer1 asav1 "sh version"
python3 asa_cmd.py customer1 asav1 "sh run webvpn"

"""
import netmiko
import argparse
from MSPO_utils import netmiko_connect

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate configuration file from jinja2 template"
    )
    parser.add_argument('customer', help="customer name")
    parser.add_argument('device', help="Device name")
    parser.add_argument('command', help="command to be sent to teh device")
    args = parser.parse_args()
    ssh_conn = netmiko_connect(args.customer, args.device)
    print(ssh_conn.send_command(args.command))
