## Edgewise v1 REST API

### Quick Start Guide

#### Prerequisites
* Python 3.x
* Requests
* PyYAML

Convert your mTLS .pfx file to cert/key PEM format:  
`openssl pkcs12 -in <mtls_cert_file>.pfx -nokeys -out cert.pem -nodes`  
`openssl pkcs12 -in <mtls_cert_file>.pfx -nocerts -out key.pem -nodes`  

#### Instructions
* Clone the repo and cd to `./python`
* Update `config.yaml`
* Install Python 3
* Install the prerequisites: `pip3 install -U requests pyyaml`
* Run the script: `python3 script.py`

#### Config File Options
If the username and/or password are not configured in the config.yaml file, the user will be prompted to enter it at runtime.

### Detailed Scripting Guides

[Scripting Against the API for Linux.pdf](Scripting%20Against%20the%20API%20for%20Linux.pdf)\
[Scripting Against the API for Windows.pdf](Scripting%20Against%20the%20API%20for%20Windows.pdf)

### Script Index & Overview

#### config.yaml
In order to connect to the console you will need to set the parameters contained within the config.yaml file. The url_root is the full https://console.edgewise.services link (specific to your production instance), your site ID which can be found at the console by navigating to Admin > Downloads > Site ID, your username and password, and lastly by splitting your mTLS certificate (in PKCS12 format) and splitting that into seperate files named 'cert.pem' and 'key.pem' which can be performed using OpenSSL.
	
	Sample:
		url_root: 'https://console.edgewise.services'
		site_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
		username: 'zws.admin@zscaler.com'
		password: 'p@$$w0rd'
		cert_file: 'C:\Users\API-User\Documents\cert.pem'
		key_file: 'C:\Users\API-User\Documents\key.pem'
	
#### download-latest-event-logs.py
Downloads the event logs and drops them into the logs folder within the local directory. This is typically used for obtaining the event logs from the console in order to forward them on to a SIEM. 

#### edgeutils.py
This is necessary to create the connection to the ZWS console. 

#### export-host-details.py
Exports a list of Hosts including hostnames, operating system, connection status, status updated, bypass mode, installed on, last reported, installed version, and ip addresses. Specify the output using the -o option and providing a name for the file "sample.csv."
	
#### export-host-perimeter-status.py
Exports a list of the Host with perimeter protection status. As a best practice, we do not advise configuring perimeter protection on Hosts. Instead, we recommend that you create a Host Segment with perimeter protection and nest the Host within. Specify the output using the -o option and providing a name for the file "sample.csv." 

#### export-host-segment-details.py
Exports a list of Host Segments and all hosts contained within each of them including the auto-update field for leveraging wildcards to include specific hostnames. Specify the output using the -o option and providing a name for the file "sample.csv."

#### export-host-segment-resegment-status.py
Exports a list of the Host Segments containing news paths since the last Auto-Segment/Auto-Resegment occurred. This can be run to easily identify what Host Segments require Auto-Resegment due to newly observed paths since the last Auto-Segment/Auto-Resegment occurred. The -a option ignores the autoSegTime timestamp and will indicate which Host Segments contain paths not accounted for in the policy set regardless of the timestamp. Specify the output using the -o option and providing a name for the file "sample.csv."

#### export-host-perimeter-status.py
Exports a list of the Host Segments with perimeter protection status. As a best practice, we do not advise configuring perimeter protection on Hosts. Instead, we recommend that you create a Host Segment with perimeter protection and nest the Host within. Specify the output using the -o option and providing a name for the file "sample.csv." 

#### export-servers-multi-segmented.py
Prints to terminal a list of hosts that are in multiple host segments. If you are using an All Hosts Segment that leverages the * wildcard note that the Host Segment name may not match the defined omitted names in the script logic. Verify that your All Hosts Segment name is accounted for in the script before running for best results. Specify the output using the -o option and providing a name for the file "sample.csv."

#### export-servers-not-segmented.py
Prints to terminal a list of hosts that are not included in any host segments. If you are using an All Hosts Segment that leverages the * wildcard note that the Host Segment name may not match the defined omitted names in the script logic. Verify that your All Hosts Segment name is accounted for in the script before running for best results. Specify the output using the -o option and providing a name for the file "sample.csv."

#### prefix-app-segment-names.py
Appends all App Segments with the "AS-" prefix. This prefix is used to easily identify App Segments when building and reviewing policies.

#### prefix-host-segment-names.py
Appends all Host Segments with the "HS-" prefix. This prefix is used to easily identify Host Segments when building and reviewing policies.

#### set-segment-inbound-block.py
This script can be used to update the inbound perimeter configuration for a host segment. It will switch from a simulated block to a full block. If no host perimeter is configured then the script will error out. Specify the Host Segment using the -s option and providing the name of the Host Segment (case sensitive). 

#### update-host-segments.py
This script can be used to create and update host segments via API. This script reads in a CSV file formatted with columns SegmentName and ServerName. The servers.csv contained within the Python directory can be modified for use with this script. No options are required to input the servers.csv file. As long as the update-host-segments.csv file is contained in the same local directory as the script it will automatically pull in the input. For the SegmentName column enter the name of the Host Segment, and for the ServerName column enter the name of the Host. If you have multiple Hosts within a single Host Segment you will need to input numerous rows.
	
	Input:
		Python\update-host-segments.csv
	
	Example:
		HS-DMZ,DMZ-01
		HS-DMZ,DMZ-02
		HS-DMZ,DMZ-03

#### update-network-segments.py
This script can be used to create and update network segments via API. This script reads in a CSV file formatted with columns Name and CIDR. The networks.csv contained within the Python directory can be modified for use with this script. No options are required to input the networks.csv file. As long as the update-network-segments.csv file is contained in the same local directory as the script it will automatically pull in the input. For the Name column enter the name of the Network Segment, and for the CIDR column enter the CIDR notation for the network. If you have multiple Networks within a single Network Segment you will need to input numerous rows.
	
	Input: 
		Python\update-network-segments.csv
	
	Example: 
		NS-LAN,10.0.0.0/24
		NS-LAN,10.0.1.0/24
		NS-LAN,10.0.2.0/24

#### upgrade-all-agents.py
Upgrades all agents that are actively connected to the console.

#### upgrade-segment-agents.py
Upgrades all agents within a specified Host Segment that are actively connected to the console. Specify the Host Segment using the -s option and providing the name of the Host Segment (case sensitive). 
