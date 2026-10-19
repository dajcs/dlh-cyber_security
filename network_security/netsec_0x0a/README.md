# Pentest Networking

Start sandbox cyber_netsec_0x0a.

Get IP address of the target machine (10.42.96.24 in my case)

Put Ip in kali /etc/hosts file.

```bash
echo "10.42.96.24 targetmachine" >> /etc/hosts

# check hosts file
cat /etc/hosts | grep net0
# 10.42.96.24     net0x0a.hbtn
```

Start openvpn and check if you can ping the target machine.

```bash
alias | grep ^ov
# ovc='ps aux | grep [o]penvpn;ip route'
# ovi='sudo openvpn --config ~/sandbox.ovpn --daemon'
# ovkill='sudo pkill openvpn'


ovi
# 2026-10-19 08:26:08 DEPRECATED OPTION: --persist-key option ignored. Keys are now always persisted across restarts.

ovc
# root        4321  0.0  0.0  16192  9828 ?        Ss   08:26   0:00 openvpn --config /home/kali/sandbox.ovpn --daemon
# default via 10.0.2.2 dev eth0 proto dhcp src 10.0.2.15 metric 100
# 10.0.2.0/24 dev eth0 proto kernel scope link src 10.0.2.15 metric 100
# 10.8.0.0/24 dev tun0 proto kernel scope link src 10.8.0.2
# 10.42.0.0/16 via 10.8.0.1 dev tun0 metric 200
# 192.168.56.0/24 dev eth1 proto kernel scope link src 192.168.56.101 metric 101

ping net0x0a.hbtn
# PING net0x0a.hbtn (10.42.96.24) 56(84) bytes of data.
# 64 bytes from net0x0a.hbtn (10.42.96.24): icmp_seq=1 ttl=126 time=17.8 ms
# 64 bytes from net0x0a.hbtn (10.42.96.24): icmp_seq=2 ttl=126 time=15.8 ms
# 64 bytes from net0x0a.hbtn (10.42.96.24): icmp_seq=3 ttl=126 time=16.1 ms
```

Open Firefox and go to the target machine IP address [http://net0x0a.hbtn:5000/](http://net0x0a.hbtn:5000/)


## [M01 - Lobby Reconnaissance (Host Discovery)](./M01_Lobby_Reconnaissance_Summary.md)

## [M02 - IP Camera Takeover (IoT Exploitation)](./M02_IP_Camera_Takeover_Summary.md)

## [M03 - M03_WEP_WiFi_Crack_Summary.md](./M03_WEP_WiFi_Crack_Summary.md)

## [M04 - M04_EternalBlue_MS17-010_Summary.md](./M04_EternalBlue_MS17-010_Summary.md)


