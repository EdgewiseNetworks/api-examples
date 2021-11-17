#!/bin/bash
# Input site ID
read -p "Enter your site ID: " site

# Convert *.pfx to cert.pem
openssl pkcs12 -in *.pfx -nokeys -out cert.pem -nodes -passin pass:$site

# Convert *.pfx to key.pem
openssl pkcs12 -in *.pfx -nocerts -out key.pem -nodes -passin pass:$site

# Script is complete
echo "Your PKCS12 file has been seperated into cert.pem and key.pem."
