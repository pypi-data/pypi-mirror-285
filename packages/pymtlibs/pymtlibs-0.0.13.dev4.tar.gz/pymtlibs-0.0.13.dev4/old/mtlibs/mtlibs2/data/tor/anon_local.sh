#!/bin/bash
##
## 这段脚本能在一个标准容器启动为anon_loal模式。
##
set -e
# source /usr/local/globalenv
command -v iptables >/dev/null 2>&1 || { 
    echo "install iptables tool"
    sudo apt sudo apt install -y iptables
}

echo "nameserver 127.0.0.1" | sudo tee  /etc/resolv.conf /dev/null

# 另外一个能直接连接外网的用户。
UNBLOCKNET_USER=unblock_tor
UNBLOCKNET_USER_ID=1080

if id -u $UNBLOCKNET_USER >/dev/null 2>&1; then
    echo "user exists"
else
    echo "UNBLOCKNET_USER用户名:${UNBLOCKNET_USER}"
    sudo useradd -s /sbin/nologin -u 1080 ${UNBLOCKNET_USER}
fi

echo "能直接连接外网的用户${UNBLOCKNET_USER}"

### Set variables
# The UID that Tor runs as (varies from system to system)
# _tor_uid="109" #As per assumption
_tor_uid=`id -u debian-tor` #Debian/Ubuntu
# unblock_tor_uid=`id -u ${UNBLOCKNET_USER}`

# 直接指定用户ID，别管用户名是什么。
_unblock_tor_uid=${UNBLOCKNET_USER_ID}
# echo "允许直连的用户ID:$_unblock_tor_uid"
#_tor_uid=`id -u tor` #ArchLinux/Gentoo

# Tor's TransPort
# _trans_port="9040"

_trans_port=${1:-"9040"}

# Tor's DNSPort
_dns_port="5353"

# Tor's VirtualAddrNetworkIPv4
_virt_addr="10.192.0.0/10"

# Your outgoing interface
_out_if="eth0"

# LAN destinations that shouldn't be routed through Tor
_non_tor="127.0.0.0/8 10.0.0.0/8 192.168.0.0/16 172.16.0.0/16 172.17.0.0/12 172.18.0.0/12 172.19.0.0/12 172.20.0.0/12 172.21.0.0/12"

# Other IANA reserved blocks (These are not processed by tor and dropped by default)
_resv_iana="0.0.0.0/8 100.64.0.0/10 169.254.0.0/16 192.0.0.0/24 192.0.2.0/24 192.88.99.0/24 198.18.0.0/15 198.51.100.0/24 203.0.113.0/24 224.0.0.0/4 240.0.0.0/4 255.255.255.255/32"

### Don't lock yourself out after the flush
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT

### Flush iptables
iptables -F
iptables -t nat -F

### *nat OUTPUT (For local redirection)
# nat .onion addresses
iptables -t nat -A OUTPUT -d $_virt_addr -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j REDIRECT --to-ports $_trans_port

# nat dns requests to Tor
iptables -t nat -A OUTPUT -d 127.0.0.1/32 -p udp -m udp --dport 53 -j REDIRECT --to-ports $_dns_port

# Don't nat the Tor process, the loopback, or the local network
iptables -t nat -A OUTPUT -m owner --uid-owner $_tor_uid -j RETURN
iptables -t nat -A OUTPUT -m owner --uid-owner $_unblock_tor_uid -j RETURN
iptables -t nat -A OUTPUT -o lo -j RETURN

# Allow lan access for hosts in $_non_tor
for _lan in $_non_tor; do
  iptables -t nat -A OUTPUT -d $_lan -j RETURN
done

for _iana in $_resv_iana; do
  iptables -t nat -A OUTPUT -d $_iana -j RETURN
done

# Redirect all other pre-routing and output to Tor's TransPort
iptables -t nat -A OUTPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j REDIRECT --to-ports $_trans_port

### *filter INPUT
# Don't forget to grant yourself ssh access from remote machines before the DROP.
iptables -A INPUT -i $_out_if -p tcp --dport 22 -m state --state NEW -j ACCEPT

iptables -A INPUT -m state --state ESTABLISHED -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT

# Allow INPUT from lan hosts in $_non_tor
# Uncomment these 3 lines to enable.
for _lan in $_non_tor; do
iptables -A INPUT -s $_lan -j ACCEPT
done

# Log & Drop everything else. Uncomment to enable logging
#iptables -A INPUT -j LOG --log-prefix "Dropped INPUT packet: " --log-level 7 --log-uid
# iptables -A INPUT -j DROP

### *filter FORWARD
# iptables -A FORWARD -j DROP

### *filter OUTPUT
# iptables -A OUTPUT -m state --state INVALID -j DROP
iptables -A OUTPUT -m state --state ESTABLISHED -j ACCEPT

# Allow Tor process output
iptables -A OUTPUT -o $_out_if -m owner --uid-owner $_tor_uid -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -m state --state NEW -j ACCEPT
iptables -A OUTPUT -o $_out_if -m owner --uid-owner $_unblock_tor_uid -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -m state --state NEW -j ACCEPT


# Allow loopback output
iptables -A OUTPUT -d 127.0.0.1/32 -o lo -j ACCEPT

# Tor transproxy magic
iptables -A OUTPUT -d 127.0.0.1/32 -p tcp -m tcp --dport $_trans_port --tcp-flags FIN,SYN,RST,ACK SYN -j ACCEPT

# Allow OUTPUT to lan hosts in $_non_tor
# Uncomment these 3 lines to enable.
for _lan in $_non_tor; do
iptables -A OUTPUT -d $_lan -j ACCEPT
done



# Log & Drop everything else. Uncomment to enable logging
#iptables -A OUTPUT -j LOG --log-prefix "Dropped OUTPUT packet: " --log-level 7 --log-uid
# iptables -A OUTPUT -j DROP

### Set default policies to DROP
# iptables -P INPUT DROP
# iptables -P FORWARD DROP
# iptables -P OUTPUT DROP
## Set default policies to DROP
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

### Set default policies to DROP for IPv6
# ip6tables -P INPUT DROP
# ip6tables -P FORWARD DROP
# ip6tables -P OUTPUT DROP


##
## 重点：如果仅仅是使用http代理，那么直接使用7890端口就可以。没有必要设置iptable。
##      如果是vpn客户端的情况，那么，客户端连接进来的时候，vpnhelper.py 会根据具体的客户端连接动态添加对应的iptable设置。
##      所以这里（下面几行）没有必要。
##
# iptables -t nat -A PREROUTING -i eth0 -p udp --dport 53 -j REDIRECT --to-ports ${_dns_port}
# iptables -t nat -A PREROUTING -i eth0 -p udp --dport 5353 -j REDIRECT --to-ports ${_dns_port}
# iptables -t nat -A PREROUTING -i eth0 -p tcp --syn -j REDIRECT --to-ports ${_trans_port}
# # iptables -t nat -A PREROUTING -i tun0 -p udp --dport 53 -j REDIRECT --to-ports ${_dns_port}
# # iptables -t nat -A PREROUTING -i tun0 -p tcp --syn -j REDIRECT --to-ports ${_trans_port}
 

# echo "iptabe 设置完成: trans_port:${_trans_port}, dns_port:${_dns_port}, "
# echo "iptabe 设置完成"

##########################################################################################



# ##########################################################################################

# tor_user=debian-tor
# HIDDEN_SERVER_DIR=/tmp/tor/hidden_service2
# TORCC=/tmp/torcc3
# mkdir -p ${HIDDEN_SERVER_DIR}
# chmod 700 ${HIDDEN_SERVER_DIR}

# echo "VirtualAddrNetworkIPv4 10.192.0.0/10
# AutomapHostsOnResolve 1
# TransPort 127.0.0.1:9040
# DNSPort 127.0.0.1:5353
# HiddenServiceDir ${HIDDEN_SERVER_DIR}
# HiddenServicePort 80 127.0.0.1:80
# HiddenServicePort 22 127.0.0.1:22
# HiddenServicePort 443 127.0.0.1:443
# " > ${TORCC}

# sudo chown ${tor_user} ${TORCC}
# sudo chown -R ${tor_user} ${HIDDEN_SERVER_DIR}
# sudo chown -R ${tor_user} ${HIDDEN_SERVER_DIR}

# sudo -u ${tor_user} tor -f ${TORCC} &

# echo "HIDDEN_SERVER_DIR: ${HIDDEN_SERVER_DIR}"
# (cd ${HIDDEN_SERVER_DIR} && sleep 3s && cat hostname)


##
## 加载远程脚本
##
## 先写死

# python3 ./bin/gitrun.py

# node ./dist/main --help

# sleep infinity
# echo "-- setup iptables end  --"