#!/bin/bash

echo "Downloading & Installing Golang.. \n"

# Golang quick install

 apt-get update
 wget https://storage.googleapis.com/golang/go1.9.2.linux-amd64.tar.gz
 sudo tar -xvf go1.9.2.linux-amd64.tar.gz
 sudo mv go /usr/local
 echo "export GOROOT=/usr/local/go" >> /root/.bashrc
 echo "export GOPATH=$HOME/Projects" >> /root/.bashrc
 echo "export PATH=$GOPATH/bin:$GOROOT/bin:$PATH" >> /root/.bashrc
 echo "Checking Golang version\n"
 ln -s /usr/local/go/bin/go /usr/bin/go


mkdir /etc/nshield

apt-get install -y jq software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx  -y


echo 'Setting ipt new log file..'
# Configures ipt connection logging to separate file
echo '# Log kernel generated iptables log messages to file
:msg,contains,"nShield" /var/log/iptables.log
& ~' >> /etc/rsyslog.d/10-ipt.conf && service rsyslog restart

echo "/var/log/iptables.log {
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
