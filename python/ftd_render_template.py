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
Created: April 3, 2020
"""
import argparse
from renderjinja2 import renderjinja2
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate ftd configuration file from jinja2 template"
        )
    parser.add_argument('customer', help="customer name")
    parser.add_argument('device', help="Device name")
    parser.add_argument('template', help="template name")
    args = parser.parse_args()
    renderjinja2(args.customer, args.device, args.template)
