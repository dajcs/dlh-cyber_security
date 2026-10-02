# Web Fundamentals


## Task 0 - Welcome



### Start cyber_websec_0x00

For some reason 2 servers have been opened ?!

#### server A
- Hostname: web-0-80-23.cod-eu-west-3.hbtn.io
- Local IP: 10.42.80.23

#### server B
- Hostname: web-0-173-56.cod-eu-west-3.hbtn.io
- Local IP: 10.42.173.56




```bash
# put ip in /etc/hosts
sudo vim /etc/hosts

# check
cat /etc/hosts | grep web0x00.*
# 10.42.80.23     web0x00.hbtn
# 10.42.173.56    web0x00b.hbtn
```

- start openvpn
- useful aliases in `.zshrc`
  ```bash
  ovi='sudo openvpn --config ~/sandbox.ovpn --daemon'
  ovc='ps aux | grep [o]penvpn;ip route'
  ovkill='sudo pkill openvpn'
  ```
- start openvpn
  ```bash
  ovc
  # default via 10.0.2.2 dev eth0 proto dhcp src 10.0.2.15 metric 100 
  # 10.0.2.0/24 dev eth0 proto kernel scope link src 10.0.2.15 metric 100 

  ovi
  # 2026-10-02 04:56:08 DEPRECATED OPTION: --persist-key option ignored. Keys are now always persisted across restarts. 

  ovc
  # root       27060  0.1  0.0  16060  9808 ?        Ss   04:56   0:00 openvpn --config /home/kali/sandbox.ovpn --daemon
  # default via 10.0.2.2 dev eth0 proto dhcp src 10.0.2.15 metric 100 
  # 10.0.2.0/24 dev eth0 proto kernel scope link src 10.0.2.15 metric 100 
  # 10.8.0.0/24 dev tun0 proto kernel scope link src 10.8.0.2 
  # 10.42.0.0/16 via 10.8.0.1 dev tun0 metric 200 
  ```
