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


blocklist_ipset:=exec_shell("cat /etc/nshield/ipsets/*.ipset")
blocklist_netset:=exec_shell("cat /etc/nshield/ipsets/*.netset")

iplist:=exec_shell("cat /var/log/iptables.log  | awk ' { print $11 } ' | sed s'/SRC=//'g | sort -n | uniq -c | sort -rn | head -n25 | grep -v 192.168. | awk '{ print $2 }'")


log.Println("Top incoming requests are: \n"+iplist)

// resolve with curl https://api.iptoasn.com/v1/as/ip/8.8.8.8 | jq '.as_description'

    // Split on comma.
splitted_iplist := strings.Split(iplist, " ")

    // Display all elements.
    for i := range splitted_iplist {
        ip:=splitted_iplist[i]
        if strings.Contains(blocklist_ipset,ip) {
        log.Println("Banning "+ip+" because found in IP blocklists")
        exec_shell("ipset add block "+ip+" timeout 300")
    }
        network:=exec_shell(`echo "+ip+" | awk -F '.' '{ print $1"."$2"."$3 }'`)
        if strings.Contains(blocklist_netset,network) {
        log.Println("Banning "+ip+" because found in Net blocklists")
        exec_shell("ipset add block "+ip+" timeout 300")
        }
    //



}
}
