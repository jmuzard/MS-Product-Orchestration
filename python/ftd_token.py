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
import sys
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def ftd_token(connection_data):
    FTD_USER = connection_data.get('username')
    FTD_PASSWORD = connection_data.get('password')
    FTD_HOST = connection_data.get('ipaddress')
    FTD_PORT = connection_data.get('port')
    headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
	}
    payload = {"grant_type": "password", "username": FTD_USER, "password": FTD_PASSWORD}
    try:
        response = requests.post(
                        "https://{}:{}/api/fdm/latest/fdm/token".format(FTD_HOST, FTD_PORT),
                        json = payload,
                        verify = False,
                        headers = headers
                        )
        if response.status_code == 200:
            access_token = response.json()['access_token']
            return access_token
        else:
            print("host: ", FTD_HOST, "- Error getting ftd token:" + str(response.status_code))
            sys.exit(1)
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

def revoke_token(connection_data, token):
        FTD_HOST = connection_data.get('ipaddress')
        FTD_PORT = connection_data.get('port')
        headers = {
    		"Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization":"Bearer {}".format(token)
    	}
        payload = {
            "grant_type" : "revoke_token",
            "access_token" : token,
            "token_to_revoke" : token
            }
        response = requests.post(
                        "https://{}:{}/api/fdm/latest/fdm/token".format(FTD_HOST, FTD_PORT),
                        json = payload,
                        verify = False,
                        headers = headers
                        )
        if response.status_code != 200:
            print('Unable to release FTD token: ' + str(response.json()))
        else:
            return
