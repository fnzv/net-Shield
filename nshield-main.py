#!/usr/bin/python
# Author: Sami Yessou - samiii@protonmail.com
# nShield - An Easy and Simple Anti-DDoS solution for VPS,Dedicated Servers and IoT devices
#    (To be)*Features: Blocks known attackers from the Web and allows users to CDN/Proxying their site with an offsite VPS/Servers
# Still in beta


import os



#Enables logging
os.popen('iptables -I INPUT -m limit --limit 20/min -j LOG --log-prefix "nShield: " --log-level 7

#read conf and save variables
dryrun = os.popen("cat /etc/nshield/nshield.conf | grep dry | awk '{print $3}'").read()
basic_ddos = os.popen("cat /etc/nshield/nshield.conf | grep basic_ddos | awk '{print $3}'").read()
under_attack = os.popen("cat /etc/nshield/nshield.conf | grep under_attack | awk '{print $3}'").read()
resolve_asn = os.popen("cat /etc/nshield/nshield.conf | grep resolve_asn | awk '{print $3}'").read()


#Update firehol ip/netsets

os.popen("rm -rf firehol_level1.netset && wget -qN https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset")
os.popen("rm -rf botscout_1d.ipset && wget -qN https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/botscout_1d.ipset")
os.popen("rm -rf bi_any_2_30d.ipset && wget -qN https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/bi_any_2_30d.ipset")
os.popen("rm -rf snort_ipfilter.ipset && wget -qN https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/snort_ipfilter.ipset")

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

os.popen("iptables -F")
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





print "Setting up whitelist .."
os.popen("iptables -I INPUT -i lo -j ACCEPT && iptables -I INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
#check if its real ip before
for ip in whitelist.split():
    print ip
    os.popen("iptables -I INPUT -s "+ip+" -j ACCEPT -m comment --comment nShield-whitelist")	



if basic_ddos:
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



if under_attack:
	# burst connections and add rate limits
	os.popen('iptables -A INPUT -p tcp --syn -m hashlimit --hashlimit 15/s --hashlimit-burst 30 --hashlimit-mode srcip --hashlimit-name synattack -j ACCEPT && iptables -A INPUT -p tcp --syn -j DROP')
