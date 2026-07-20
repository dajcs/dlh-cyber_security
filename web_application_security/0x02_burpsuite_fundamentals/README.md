# BurpSuite - Fundamentals


## Task 0. Getting Started with Burp Suite

### Step 0.1: Downloading and Installing Burp Suite

Kali already has Burp Suite.




### Start web0x02.hbtn

\Network Information\Ip: 10.42.105.161

```bash
# put ip in /etc/hosts
sudo vim /etc/hosts

# check
cat /etc/hosts | grep web0x02.hbtn
# 10.42.105.161   web0x02.hbtn
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
  # 2026-07-20 04:33:50 DEPRECATED OPTION: --persist-key option ignored. Keys are now always persisted across restarts. 

  ovc
  # root      905317  0.0  0.0  15876  9600 ?        Ss   04:33   0:00 openvpn --config /home/kali/sandbox.ovpn --daemon
  # default via 10.0.2.2 dev eth0 proto dhcp src 10.0.2.15 metric 100 
  # 10.0.2.0/24 dev eth0 proto kernel scope link src 10.0.2.15 metric 100 
  # 10.8.0.0/24 dev tun0 proto kernel scope link src 10.8.0.2 
  # 10.42.0.0/16 via 10.8.0.1 dev tun0 metric 200 
  ```

### Step 2: Starting up BurpSuite

**Method 1**: Proxy Setup and Certificate Installation
  - Upon opening Burp Suite, start a new project and navigate to the Proxy -> Options tab.(\\`Proxy`\\`Proxy Settings`)
  - Set the Burp Suite proxy to listen on `127.0.0.1:8080` or another port of your choice.
  - Configure your preferred web browser to route traffic through the Burp proxy by setting the HTTP proxy to `127.0.0.1` with the port you selected. (\Firefox \Settings \Search: proxy \ proxy settings \ Manual Proxy \ HTTP and HTTPS: `127.0.0.1:8080` \ OK)
  - With your browser configured, attempt to navigate to any HTTPS website. You'll be blocked by a security warning due to the browser not recognizing Burp's certificate.
  - Return to Burp Suite and navigate to Proxy -> Intercept. Ensure Intercept is off. Access http://burpsuite from your browser to download the CA certificate provided by Burp.  \
  **Alternatively**: Burp \Settings \ Proxy \ Export certificate
  - Install this certificate in your browser's certificate store to avoid further security warnings (\Firefox \Settings \Search: certif \ View certificates \ import `cacert.der` \ view `PortSwiggerCA.crt` installed)

**Method 2**: Open Browser
- Navigate to Proxy Tab.
- Click on Open Browser Button.
- Clarification: apparently Burp Suite has its own browser, there is \ Settings \ Tools \ Burp's Browser, but I need to find out where can be started this browser
- Found it, it is on start page upper right corner globe `🌐` icon


### Step 3: DNS Resolution Configuration

- Navigate to Project options -> Connections in Burp Suite and find the section titled Hostname Resolution Overrides.  \
**Alternatively**: Burp \ Settings \ Network \ Connections
- Add a new record with the hostname `web0x02.hbtn` and the IP address `10.42.105.161` provided by your container or virtual lab environment.

### Step 4: Discovering the `FLAG`

- Ensure your configured browser's proxy settings are directing traffic through Burp Suite.
- Visit https://web0x02.hbtn, allowing Burp Suite to intercept the request.
- After successfully accessing the site, navigate to Project options -> TLS in Burp Suite, then to Server TLS Certificate.
- Carefully examine the server certificate details presented by Burp Suite, looking for a Flag encapsulated within.


```bash
# when navigating to https://web0x02.hbtn this flag is displayed:
echo f8c4ca67589b6e27098d0a528cf3f1b2 > 0-flag.txt

# when examining Burp \ Settings \ Network \ TLS \ web0x02.hbtn \ Subject field has a flag-like string:
echo 92383e47a8806601622b2c98a761638f > 0-flag.txt

cat 0-flag.txt
```