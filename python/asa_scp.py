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
Created: March 31, 2020

usage: asa_scp.py [-h] [-d {get,put}] customer device sourcefile destfile

scp file to or from ASA device

positional arguments:
  customer              Customer name
  device                Device name
  sourcefile            local file
  destfile              destination file

optional arguments:
  -h, --help            show this help message and exit
  -d {get,put}, --direction {get,put}
                        specify direction put (default) or get
"""

import argparse
from MSPO_utils import scp_copy

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="scp file to or from ASA device"
    )
    parser.add_argument('customer', help="Customer name")
    parser.add_argument('device', help="Device name")
    parser.add_argument('sourcefile', help="local file")
    parser.add_argument('destfile', help="destination file")
    parser.add_argument('-d', '--direction', choices=['get', 'put'], default='put', help="specify direction put (default) or get")
    args = parser.parse_args()

    scp_copy(args.customer, args.device, args.sourcefile, args.destfile, args.direction)
