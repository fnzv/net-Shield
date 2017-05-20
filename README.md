## nShield 

An Easy and Simple Anti-DDoS solution for VPS,Dedicated Servers and IoT devices based on iptables

![](nshield-scheme.png?raw=true)

-----------------

## Requirements

- Linux System with python, iptables
- Nginx (Will be installed automatically by install.sh)


## Quickstart

```cd /home/ && git clone https://github.com/fnzv/nShield.git && bash nShield/install.sh```

### WARNING: This script will replace all your iptables rules so take that into account


## Usage

The above quickstart/installation script will install python if not present and download all the repo with the example config files, after that will be executed a bash script to setup some settings and a cron that will run every 30 minutes to check connections against common ipsets.
You can find example config files under examples folder.


## How it works
Basically this python script is set by default to run every 30 minutes and check the config file to execute these operations:

- Get latest Bot,Spammers,Bad IP/Net reputation lists and blocks if those Bad guys are attacking your server (Thank you FireHol http://iplists.firehol.org/ )
- Enables basic Anti-DDoS methods to deny unwanted/malicious traffic 
- Rate limits when under attack 
- Allows HTTP Proxying to protect your site with an external proxy/server  (HTTPS with Let's Encrypt in TODO)

## Demo
[![asciicast](https://asciinema.org/a/elow8qggzb7q6durjpbxsmk6r.png)](https://asciinema.org/a/elow8qggzb7q6durjpbxsmk6r)

Tested on Ubuntu 16.04 LTS

## Contributors

Feel free to open issues or send me an email

## License

Code distributed under MIT licence.
