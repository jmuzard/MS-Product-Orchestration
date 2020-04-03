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
Created: March 27, 2020
"""
from jinja2 import Environment, FileSystemLoader
import os, os.path
import yaml
from MSPO_utils import get_MSPO_env

def renderjinja2(customer, device, cfg_entity):

    cfg = get_MSPO_env()
# We first need to merge global, all_device, device specific yaml in to a single one
# set golbal config parameter file path
    CFG_GLOBAL = cfg.get('vars') + "/global.yml"
    if not os.path.isfile(CFG_GLOBAL):
        print ("global.yml does'not not exist:", CFG_GLOBAL)
        exit(1)
# set customer all parameter file path
    CFG_CUSTOMER = cfg.get('customer_vars') + "/"+  customer + "/all.yml"
# set device model specific parameter file path
# for this we need to know the device model from teh device specific connect.yml files
    CONNECT_FILE = cfg.get('customer_vars') + "/"+  customer + "/sites/" + device + "/" + "connect.yml"
    if not os.path.isfile(CONNECT_FILE):
        print ("connect.yml does'not not exist:", CONNECT_FILE)
        exit(1)
    connect_data = yaml.safe_load(open(CONNECT_FILE))
    model = connect_data.get('device_model')
    CFG_ALL = cfg.get('customer_vars') + "/"+  customer + "/devices/" + model + ".yml"
    if not os.path.isfile(CFG_ALL):
        print ("all.yml does'not not exist:", CFG_ALL)
        exit(1)
# set device specific configuration file path, existence of this file is not mandatory as some template only use parameters from above file
    CFG_DEVICE = cfg.get('customer_vars') + "/"+  customer + "/sites/" + device + "/" + cfg_entity + ".yml"
# now that we haev the path to the files, merge them into a single one
    STAGING_DIR = cfg.get('staging') + "/" +  customer
    if os.path.isdir(STAGING_DIR) == False:
        os.mkdir(STAGING_DIR)
    CFG_MERGED_FILE = STAGING_DIR + "/" + cfg_entity + ".yml"
    fout = open(CFG_MERGED_FILE, 'w')
    fin = open(CFG_GLOBAL, 'r')
    fout.writelines(fin.readlines())
    fin.close()
    fin = open(CFG_CUSTOMER, 'r')
    fout.writelines(fin.readlines()[1:])
    fin.close()
    fin = open(CFG_ALL, 'r')
    fout.writelines(fin.readlines()[1:])
    fin.close()
    if os.path.isfile(CFG_DEVICE):
        fin = open(CFG_DEVICE, 'r')
        fout.writelines(fin.readlines()[1:])
        fin.close()
    fout.close()
    config = yaml.safe_load(open(CFG_MERGED_FILE))
# load jinja2 template
    TEMPLATES = cfg.get('templates') + "/" + model
    env = Environment(loader = FileSystemLoader(TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    TEMPLATE_FILE = cfg_entity + ".j2"
    template = env.get_template(TEMPLATE_FILE)
# Check if configuration directory exist for the device
    CUSTOMER_CFG_DIR = cfg.get('customer_configs') + "/" + customer
    if os.path.isdir(CUSTOMER_CFG_DIR) == False:
        os.mkdir(CUSTOMER_CFG_DIR)
    DEVICE_DIR = CUSTOMER_CFG_DIR + "/" + device
    if os.path.isdir(DEVICE_DIR) == False:
        os.mkdir(DEVICE_DIR)
    CFG_FILE = DEVICE_DIR+ "/" + cfg_entity + ".txt"
# render cfg_entity
    f = open(CFG_FILE, "w")
    f.write(template.render(config))
    f.close
