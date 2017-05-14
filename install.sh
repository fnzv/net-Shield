#!/bin/bash

echo "Downloading & Installing Python.. \n"

apt-get install -y python

mkdir /etc/nshield


echo "Copying example configuration... \n"

wget -O /etc/nshield/nshield.conf https://raw.githubusercontent.com/fnzv/nShield/master/example/nshield.conf
wget -O /etc/nshield/whitelist https://raw.githubusercontent.com/fnzv/nShield/master/example/whitelist

print "Running nShield update every 1 hour.. \n"
echo "30 * * * * python /home/nshield/nshield-main.py" >> /etc/crontab
