## nShield

An Easy and Simple Anti-DDoS solution for VPS,Dedicated Servers and IoT devices
![](nshield-scheme.png?raw=true)

-----------------

## Requirements

- Linux System with python, iptables
- Nginx (Will be installed automatically by install.sh)

## Installation

```cd /home/ && git clone https://github.com/fnzv/nShield.git && bash nShield/install.sh```

### WARNING: This script will replace all your iptables rules so take that into account

## Usage

The above quickstart/installation script will install python if not preset and download all the repo with example config files, after that will be executed a bash script to setup a cron that will run every 30 minutes to check connections against common ipsets.

 Config file is /etc/nshield/nshield.conf (An example can be found in the repo)
 

## How it works

- Get latest Bot,Spammers,Bad IP/Net reputation lists and blocks if those Bad guys are attacking your server (Thank you FireHol http://iplists.firehol.org/ )
- Enables basic Anti-DDoS methods to deny unwanted/malicious traffic 
- Rate limits when under attack 
- Allows HTTP Proxying to protect your site with an external proxy/server  (HTTPS with Let's Encrypt in TODO)

## Demo
[![asciicast](https://asciinema.org/a/elow8qggzb7q6durjpbxsmk6r.png)](https://asciinema.org/a/elow8qggzb7q6durjpbxsmk6r)

## Contributors

Feel free to open issues or send me an email

## License

Code distributed under MIT licence.
