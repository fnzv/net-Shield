#!/bin/bash

echo "Downloading & Installing Python.. \n"

apt-get install -y python

mkdir /etc/nshield

# Configures ipt connection logging to separate file
echo ':msg, contains, "nShield"       /var/log/nshield.log' >> /etc/rsyslog.conf && service rsyslog restart

echo "/var/log/nshield.log {
    maxsize 100M
    hourly
    missingok
    rotate 4
    compress
    notifempty
    nocreate
}" > /etc/logrotate.d/nshield


echo "Installing Nginx for nShield proxy..\n"
apt install -y nginx



echo "Copying example configuration... \n"

wget -O /etc/nshield/nshield.conf https://raw.githubusercontent.com/fnzv/nShield/master/example/nshield.conf
wget -O /etc/nshield/whitelist https://raw.githubusercontent.com/fnzv/nShield/master/example/whitelist

echo "Running nShield update every 1 hour.. "
echo "30 * * * * python /home/net-Shield/nshield-main.py" >> /etc/crontab
