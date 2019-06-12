### Edgewise v2 GraphQL API

#### Prerequisites
* Python 3.x
* [Pipenv](https://github.com/pypa/pipenv)

Convert your mTLS .pfx file to cert/key PEM format:  
`openssl pkcs12 -in <mtls_cert_file>.pfx -nokeys -out cert.pem -nodes`  
`openssl pkcs12 -in <mtls_cert_file>.pfx -nocerts -out key.pem -nodes`  

#### Instructions
* Clone the repo and cd to this folder
* Start a Pipenv shell: `pipenv shell`
* Run the script: `python script.py`
