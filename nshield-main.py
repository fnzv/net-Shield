#!/usr/bin/python
# Author: Sami Yessou - samiii@protonmail.com
# nShield - An Easy and Simple Anti-DDoS solution for VPS,Dedicated Servers and IoT devices
#    (To be)*Features: Blocks known attackers from the Web and allows users to CDN/Proxying their site with an offsite VPS/Servers
# Still in beta


import os,argparse,ConfigParser,sys

config = ConfigParser.ConfigParser()

config.read("/etc/nshield/nshield.conf")


# Log check
os.popen('find /var/log/syslog -type f -size +500k -delete >/dev/null 2>&1')

#read conf and save variables
dryrun = int(config.get("conf","dryrun"))
basic_ddos = int(config.get("conf","basic_ddos"))
under_attack = int(config.get("conf","under_attack"))
nshield_proxy = int(config.get("conf","nshield_proxy"))

#print "Configuration loaded: \n"
#print "dryrun: "+dryrun
#print "\nbasic_ddos: "+basic_ddos
#print "\nunder_attack: "+under_attack
#print "\nnshield_proxy: "+nshield_proxy


parser = argparse.ArgumentParser()

parser.add_argument('-ssl', action='store_true', default=False,dest='autossl', help='Enable SSL on proxy domains')

parser.add_argument('-dry', action='store_true', default=False,dest='standalone', help='Standalone mode')

results = parser.parse_args()



if results.standalone: 
	dryrun = 1
	print "Running nShield in standalone mode.. Dryrun is now enabled for safety\n"
autossl = results.autossl


	


#Update firehol ip/netsets

os.popen("wget -O firehol_level1.netset https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset  >/dev/null 2>&1")
os.popen("wget -O botscout_1d.ipset  https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/botscout_1d.ipset >/dev/null 2>&1")
os.popen("wget -O bi_any_2_30d.ipset https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/bi_any_2_30d.ipset  >/dev/null 2>&1")
os.popen("wget -O snort_ipfilter.ipset https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/snort_ipfilter.ipset  >/dev/null 2>&1")

#Load all sets from cwd
blocklist_ipset=os.popen("cat *.ipset").read()
blocklist_netset=os.popen("cat *.netset").read()
whitelist=os.popen("cat /etc/nshield/whitelist").read()

# Get top 10 Nginx reqs
nginx_iplist=os.popen("cat /var/log/nginx/access.log | awk ' { print $1}' | sort -n | uniq -c | sort -rn | head").read()


splitted_nginx_iplist = nginx_iplist.split()


# For every IP check ASN & Reputation

print "Top 10 NGINX Requests are coming from these IPs : \n"+nginx_iplist


print "Top 10 ASN by NGINX Requests: \n"
for ip in splitted_nginx_iplist:
       if "." in ip:
  	print ip+" - MNT BY: "+os.popen("curl -s ipinfo.io/"+ip+"/org").read()
if dryrun is 1:
	os.popen("iptables -F")
	os.popen('iptables -I INPUT -j LOG --log-prefix "nShield: " --log-level 7')
ipt_iplist=os.popen("cat /var/log/nshield.log | awk '{ print $12 }' | sed s'/SRC=//' | sort -n | uniq -c | grep -v DST").read()
top_ipt_iplist=os.popen("cat /var/log/nshield.log | awk '{ print $12 }' | sed s'/SRC=//' | sort -n | uniq -c | sort -rn | grep -v DST | head").read()
splitted_ipt_iplist=ipt_iplist.split()
splitted_top_ipt_iplist=top_ipt_iplist.split()

print "Top 10 TCP Requests are coming from these IPs : \n"+top_ipt_iplist

print "Top 10 ASN of ipt logged Requests: \n"
for ip in splitted_top_ipt_iplist:
       if "." in ip:
        print ip+" - MNT BY: "+os.popen("curl -s ipinfo.io/"+ip+"/org").read()
        


for ip in splitted_ipt_iplist:
 	if "." in ip:
          if ip in blocklist_ipset and conns >= 10:
		print "Blocking "+ip+" because found in ipsets and more than 10 reqs"
 		iptblock="iptables -I INPUT -s "+ip+"  -m comment --comment nShield-Blocked-from-ipset+10reqs  -j DROP"
		if dryrun is 1:
 			print "Dry Run.."
		else:
			os.popen(iptblock)
                subnet=ip.split('.') 
		netset=subnet[0]+"."+subnet[1]+"."+subnet[2]
		if netset in blocklist_netset:
 			print "Blocking "+ip+" because found in netsets"
			iptblock="iptables -I INPUT -s "+netset+".0/24  -m comment --comment nShield-Blocked-from-netsets  -j DROP"
                	if dryrun is 1:
                        	print "Dry Run.."
                	else:
				os.popen(iptblock)
        else:
              conns=ip




if dryrun is not 1:
	print "Setting up whitelist .."
	os.popen("iptables -I INPUT -i lo -j ACCEPT && iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
	#check if its real ip before
	for ip in whitelist.split():
	    print ip
	    os.popen("iptables -I INPUT -s "+ip+" -j ACCEPT -m comment --comment nShield-whitelist")	



if basic_ddos is 1 and dryrun is 0:
	print "Setting up Basic DDoS Protection"

	# Block SYN FLOOD
	os.popen("iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP")
	# Block XMAS Scan
	os.popen("iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP")
	# Smurf attack protection
	os.popen("iptables -A INPUT -p icmp -m icmp --icmp-type timestamp-request -j DROP && iptables -A INPUT -p icmp -m limit --limit 1/second -j ACCEPT")

	os.popen("/sbin/sysctl -w net/netfilter/nf_conntrack_tcp_loose=0")

	os .popen("echo 1000000 > /sys/module/nf_conntrack/parameters/hashsize && /sbin/sysctl -w net/netfilter/nf_conntrack_max=2000000 &&  /sbin/sysctl -w net.ipv4.tcp_syn_retries=2 &&  /sbin/sysctl -w net.ipv4.tcp_rfc1337=1  && /sbin/sysctl -w net.ipv4.tcp_synack_retries=1")

	print "\nBlocking XMAS scan, Smurf, ICMP attacks & SYN flood"



if under_attack is 1 and dryrun is 0:
	# burst connections and add rate limits
	os.popen('iptables -A INPUT -p tcp --syn -m hashlimit --hashlimit 15/s --hashlimit-burst 30 --hashlimit-mode srcip --hashlimit-name synattack -j ACCEPT && iptables -A INPUT -p tcp --syn -j DROP')

	
	
if nshield_proxy is 1 and dryrun is 0:
        print "Setting up nShield proxy for domains found in /etc/nshield/proxydomains\n"
        # Generates nginx proxy_pass from /etc/nshield/proxydomains and checks if already present in nginx conf
        with open("/etc/nshield/proxydomains") as f:
             for line in f:
                line = line.split(' ')
                domain = line[0]
                ip = line[1]
                if domain not in os.popen("cat /etc/nginx/sites-enabled/dynamic-vhost.conf").read():
                    print "I Will generate proxy configuration for site "+domain+" on IP: "+ip
                    os.popen("""echo 'server {
        listen 80;

        root /var/www/html;
        index index.html index.htm index.nginx-debian.html;

        server_name """+domain+""";

        location / {
    proxy_pass       http://"""+ip+""";
    proxy_set_header Host      $host;
    proxy_set_header X-Real-IP $remote_addr;
}
}
' >> /etc/nginx/sites-enabled/dynamic-vhost.conf""")
                    os.popen('service nginx restart')
                else:
                    print "Domain already configured"

        print "Now you can test that your site is reachable via nShield proxy by changing the domain DNS or via your PC hosts file or directly DNS A record"


# Is triggered only if run from commandline and not cron
if autossl and dryrun is 0:
    with open("/etc/nshield/proxydomains") as f:
                content = f.readlines()
                content1 = content[0].split(' ')
                ip = content1[1].strip('\n')
                domain = content1[0]
                if domain not in os.popen("cat /etc/nginx/sites-enabled/dynamic-ssl-vhost.conf").read():
                    print "I Will generate SSL certs for "+domain+" with Let's Encrypt DNS challenge"
		    email = str(raw_input("Insert your email address? (Used for cert Expiration and Let's Encrypt TOS agreement \n"))
		    os.system("certbot --text --agree-tos --email "+email+" -d "+domain+" --manual --preferred-challenges dns --expand --renew-by-default  --manual-public-ip-logging-ok certonly")
		    print "Setting up Nginx configuration...\n"
		    os.popen("""echo 'server {
        listen 443 ssl;

        root /var/www/html;
        index index.html index.htm index.nginx-debian.html;
    ssl_certificate     /etc/letsencrypt/live/"""+domain+"""/cert.pem;
    ssl_certificate_key /etc/letsencrypt/live/"""+domain+"""/privkey.pem;
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
        server_name """+domain+""";

        location / {
    proxy_pass       http://"""+ip+""";
    proxy_set_header Host      $host;
    proxy_set_header X-Real-IP $remote_addr;
}
}
' >> /etc/nginx/sites-enabled/dynamic-ssl-vhost.conf && service nginx restart""") 

print "TOP Current Connections by IP \n"

print os.popen("""netstat -atun | grep -v "Addr" | grep -v "and" | awk '{print $5}' | cut -d: -f1 | sed -e '/^$/d' |sort | uniq -c | sort -n""").read()
