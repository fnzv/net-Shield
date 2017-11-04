## nShield 

An Easy and Simple Anti-DDoS solution for VPS,Dedicated Servers and IoT devices based on iptables

![](nshield-scheme.png?raw=true)

-----------------

## Requirements

- Linux System with python, iptables
- Nginx (Will be installed automatically by install.sh)


## Quickstart

Running as a standalone software (No install.sh required) via DryRun option (-dry) to only check connections agains ip/netsets and do not touch iptables firewall.

```python nshield-main.py -dry```

<br>
For complete install: <br>

```cd /home/ && git clone https://github.com/fnzv/nShield.git && bash nShield/install.sh```

### WARNING: This script will replace all your iptables rules and installs Nginx so take that into account

## Proxy Domains
To configure proxydomains you need to enable the option on /etc/nshield/nshield.con (nshield_proxy: 1) and be sure that the proxydomain list (/etc/nshield/proxydomain ) is following this format:<br>
<br>
```
mysite.com 123.123.123.123
example.com 111.111.111.111
```
<br>
## Usage

The above quickstart/installation script will install python if not present and download all the repo with the example config files, after that will be executed a bash script to setup some settings and a cron that will run every 30 minutes to check connections against common ipsets.
You can find example config files under examples folder.

HTTPS Manually verification is executed with this command under the repository directory:

 ``` python nshield-main.py -ssl ```

The python script after reading the config will prompt you to insert an email address (For Let's Encrypt) and change your domain DNS to the nShield server for SSL DNS Challenge confirmation.
Example:
 ``` 
I Will generate SSL certs for sami.pw with Let's Encrypt DNS challenge
Insert your email address? (Used for cert Expiration and Let's Encrypt TOS agreement
samiii@protonmail.com
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Renewing an existing certificate
Performing the following challenges:
dns-01 challenge for sami.pw

-------------------------------------------------------------------------------
Please deploy a DNS TXT record under the name
_acme-challenge.sami.pw with the following value:

wFyeYk4yl-BERO6pKnMUA5EqwawUri5XnlD2-xjOAUk

Once this is deployed,
-------------------------------------------------------------------------------
Press Enter to Continue
Waiting for verification...
Cleaning up challenges
 ``` 
 Now your domain is verified and a SSL cert is issued to Nginx configuration and you can change your A record to this server.


## How it works
Basically this python script is set by default to run every 30 minutes and check the config file to execute these operations:

- Get latest Bot,Spammers,Bad IP/Net reputation lists and blocks if those Bad guys are attacking your server (Thank you FireHol http://iplists.firehol.org/ )
- Enables basic Anti-DDoS methods to deny unwanted/malicious traffic 
- Rate limits when under attack 
- Allows HTTP(S) Proxying to protect your site with an external proxy/server (You need to manually run SSL Verification first time)

## Demo
[![asciicast](https://asciinema.org/a/elow8qggzb7q6durjpbxsmk6r.png)](https://asciinema.org/a/elow8qggzb7q6durjpbxsmk6r)

Tested on Ubuntu 16.04 and 14.04 LTS

## Contributors

Feel free to open issues or send me an email

## License

Code distributed under MIT licence.
