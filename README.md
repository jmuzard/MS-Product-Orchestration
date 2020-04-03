# MS-Device_Orchestration

This repository includes sample code that uses python library that Managed Service Provider can use to provision Cisco security devices.

Service Provider requires multi-tenancy, so for every script have required arguments that specify the relevant customer and device. Currently only dedicated device are implemented. Shared device is to be done.

ASA available scripts:

	. asa-day0-config.py -> create day0 config for asav

	. asa_smart_license.py -> create and push smart license configuration

	. asa_ravpn.py -> create and push remote access VPN configuration to ASA

	. asa_ravpn_users.py -> create and push remote access VPN user accounts configuration to ASA

	. asa_ipsecVPN.py -> create and push IPSEC site to site VPN configuration to ASA	

	. asa_cmd.py -> send command line to asa

	. asa_scp.py -> copy or retrieve file to/from ASA flash

	. asa_cfg_backup.py -> backup ASA configuration

	. asa_cfg_restore.py -> restore ASA configuration

	. asa_cfg_restore.py -> restore ASA configuration
