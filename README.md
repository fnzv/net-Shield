## nShield

An Easy and Simple Anti-DDoS solution for VPS,Dedicated Servers and IoT devices


-----------------

## Requirements

- Linux System with python, iptables

## Installation

```cd /home/ && git clone https://github.com/fnzv/nShield.git && bash nShield/install.sh```

### WARNING: This script will replace all your iptables rules so take that into account

## Usage

The above quickstart/installation script will install python if not preset and download all the repo with example config files, after that will be executed a bash script to setup a cron that will run every 30 minutes.

## How it works

- Get latest Bot,Spammers,Bad IP/Net reputation lists and blocks if those Bad guys are attacking your server (Thank you FireHol http://iplists.firehol.org/ )
- Enables basic Anti-DDoS methods to deny unwanted/malicious traffic (Thank you iptables)
- Rate limits when under attack (Thank you again iptables)

## Contributors

Feel free to open issues or send me an email

## License

Code distributed under MIT licence.
