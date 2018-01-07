package main

import (
 "os"
 "strings"
 "log"
 "os/exec"

 "github.com/BurntSushi/toml"

)

var (

dryrun int
proxy int
underattack int
basicddos int
autossl int
whitelist []string
proxydomains []string
whitelist_text string

)

// Info from config file
type Config struct {
        DryRun int
        BasicDdos int
        UnderAttack   int
        Proxy int
        Autossl int
        Whitelist []string
        ProxyDomains []string
}
// Reads info from config file
func ReadConfig() Config {
        var configfile = "/etc/nshield/nshield.conf"
        _, err := os.Stat(configfile)
        if err != nil {
                log.Fatal("Config file is missing: ", configfile)
        }

        var config Config
        if _, err := toml.DecodeFile(configfile, &config); err != nil {
                log.Fatal(err)
        }
        //log.Print(config.Index)
        return config
}

func exec_shell(command string) string {
out, err := exec.Command("/bin/bash","-c",command).Output()
    if err != nil {
        log.Fatal(err)
    }
    return string(out)
}



func main() {

var config = ReadConfig()
basicddos = config.BasicDdos
underattack = config.UnderAttack
dryrun = config.DryRun
proxy = config.Proxy
autossl = config.Autossl
whitelist = config.Whitelist
proxydomains = config.ProxyDomains


f, err := os.OpenFile("/var/log/nshield.log", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
if err != nil {
        log.Fatal(err)
}
defer f.Close()
log.SetOutput(f)


log.Println("Loading nshield with these settings:")
log.Println("BasicDdos: ",basicddos)
log.Println("UnderAttack: ",underattack)
log.Println("DryRun: ",dryrun)
log.Println("Proxy: ",proxy)


exec_shell("wget -O /etc/nshield/ipsets/firehol_level1.netset https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/firehol_level1.netset  >/dev/null 2>&1")
exec_shell("wget -O /etc/nshield/ipsets/botscout_1d.ipset  https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/botscout_1d.ipset >/dev/null 2>&1")
exec_shell("wget -O /etc/nshield/ipsets/bi_any_2_30d.ipset https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/bi_any_2_30d.ipset  >/dev/null 2>&1")
exec_shell("wget -O /etc/nshield/snort_ipfilter.ipset https://raw.githubusercontent.com/firehol/blocklist-ipsets/master/snort_ipfilter.ipset  >/dev/null 2>&1")

exec_shell("iptables -F")
log.Println("Cleaning iptables..")
// check if already exists
check_ipset := exec_shell("ipset list | grep -e rate -e block | awk '{print $2}'")
    if strings.Contains(check_ipset,"rate") {
    log.Println("ipset already existing")
    } else {
log.Println("creating ipset")
exec_shell("ipset create ratelimit hash:ip hashsize 4096")
                }

    if strings.Contains(check_ipset,"block") {
    log.Println("ipset already existing")
    } else {
log.Println("creating ipset")
exec_shell("ipset create block hash:ip timeout 0")
                }
exec_shell("iptables -A INPUT -m set --match-set ratelimit src -m hashlimit --hashlimit 25/sec --hashlimit-name ratelimithash -j DROP")
exec_shell("iptables -A INPUT -m set --match-set block src -j DROP")




i1 := 0
for range whitelist {
    log.Println("Adding to whitelist: "+whitelist[i1])
    whitelist_text = whitelist_text + whitelist[i1]
    //fmt.Printf("%s", out)
     if dryrun == 0 {
     exec_shell("iptables -I INPUT -s "+whitelist[i1]+" -j ACCEPT -m comment --comment 'WHITELISTED IP - NSHIELD'")
        }
    i1++
}



log.Println("Setting ipt logs..")
exec_shell(`iptables -I INPUT -m limit --limit 40/min  -j LOG --log-prefix "nShield: " --log-level 7`)

if (basicddos == 1 && dryrun == 0) {
    log.Println("Setting up Basic DDos Protection")
    exec_shell("iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP")
    exec_shell("iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP")
    exec_shell("iptables -A INPUT -p icmp -m icmp --icmp-type timestamp-request -j DROP && iptables -A INPUT -p icmp -m limit --limit 1/second -j ACCEPT")
    exec_shell("/sbin/sysctl -w net/netfilter/nf_conntrack_tcp_loose=0")
    exec_shell("echo 1000000 > /sys/module/nf_conntrack/parameters/hashsize && /sbin/sysctl -w net/netfilter/nf_conntrack_max=2000000 &&  /sbin/sysctl -w net.ipv4.tcp_syn_retries=2 &&  /sbin/sysctl -w net.ipv4.tcp_rfc1337=1  && /sbin/sysctl -w net.ipv4.tcp_synack_retries=1")

}


if (underattack == 1 && dryrun ==0) {
    exec_shell("iptables -A INPUT -p tcp --syn -m hashlimit --hashlimit 15/s --hashlimit-burst 30 --hashlimit-mode srcip --hashlimit-name synattack -j ACCEPT && iptables -A INPUT -p tcp --syn -j DROP")
}


if (proxy == 1 && dryrun ==0) {
  log.Println("Setting up nShield proxy for domains found in configuration")
  i:= 0
  for range proxydomains {
    log.Println(proxydomains[i])
    s := strings.Split(proxydomains[i], " ")
    domain, ip := s[0], s[1]
    log.Println("Generating Nginx conf for "+domain+" on IP "+ip)
    //fmt.Printf("%s", out)
     if strings.Contains(exec_shell("cat /etc/nginx/sites-enabled/dynamic-vhost.conf"),domain) == false {
     if dryrun == 0 {
        exec_shell(`echo 'server {
        listen 80;
        root /var/www/html;
        index index.html index.htm index.nginx-debian.html;
        server_name `+domain+`;
        location / {
    proxy_pass       http://`+ip+`;
    proxy_set_header Host      $host;
    proxy_set_header X-Real-IP $remote_addr;
}
}
' >> /etc/nginx/sites-enabled/dynamic-vhost.conf`)
        exec_shell("service nginx reload")
        }

        } else { log.Println("Domain already present") }
        i++
                        }
}

if (autossl ==1 && dryrun == 0) {

i2 :=0
for range proxydomains {
    log.Println(proxydomains[i2])
    s := strings.Split(proxydomains[i2], " ")
    domain, ip := s[0], s[1]
    if strings.Contains(exec_shell("cat /etc/nginx/sites-enabled/dynamic-ssl-vhost.conf"),domain) == false {
    log.Println("i will generate SSL cert with certbot for ",domain)
    //call certbot
    exec_shell("certbot certonly --webroot --agree-tos --no-eff-email -n -w /var/www/letsencrypt -d "+domain)

   exec_shell(`echo 'server {
        listen 443 ssl;
        root /var/www/html;
        index index.html index.htm index.nginx-debian.html;
    ssl_certificate     /etc/letsencrypt/live/`+domain+`/cert.pem;
    ssl_certificate_key /etc/letsencrypt/live/`+domain+`/privkey.pem;
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
        server_name `+domain+`;
        location / {
    proxy_pass       http://`+ip+`;
    proxy_set_header Host      $host;
    proxy_set_header X-Real-IP $remote_addr;
}
}
' >> /etc/nginx/sites-enabled/dynamic-ssl-vhost.conf && service nginx reload`)

}

i2++
}

}

log.Println("Top current connections: \n ",exec_shell(`netstat -atun | grep -v "Addr" | grep -v "and" | awk '{print $5}' | cut -d: -f1 | sed -e '/^$/d' |sort | uniq -c | sort -n`))

}
