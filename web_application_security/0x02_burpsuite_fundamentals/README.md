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
# when examining Burp \ Settings \ Network \ TLS \ web0x02.hbtn \ Subject field has a flag-like string:
echo 92383e47a8806601622b2c98a761638f > 0-flag.txt

cat 0-flag.txt
```


## 1. Client-Side TLS Authentication with Burp Suite

This task involves navigating client-side TLS authentication—a critical aspect of ensuring secure connections between clients and servers.
Upon accessing `https://web0x02.hbtn`, you'll encounter a welcome screen offering a download link for a `.p12` certificate.  \
Your mission (should you accept ;-) is to correctly install this certificate within Burp Suite to authenticate and reveal hidden content guarded by TLS client authentication.

### Step 1.1: Downloading the PKCS#12 Certificate

- Visit `https://web0x02.hbtn` through your browser configured to use Burp Suite as its proxy.
- On the welcome screen, download the .p12 certificate provided via the download link. (Or Simply through: `https://web0x02.hbtn/static/web0x012.p12`)

### Step 1.2: Configuring Burp Suite with Client TLS Certificate

- With the `.p12` certificate downloaded, open Burp Suite and navigate to Proxy -> Options. (Burp \ Settings \ Network \ TLS \ Client TLS Certificates )
- Scroll down to the TLS section, then click on Client TLS Certificate.
- Ensure the "Override options" checkbox is selected.
- Click on `Add` to configure a new client certificate.
- In the `Destination Host` field, enter `web0x02.hbtn`.
- For `Certificate Type`, choose `"PKCS#12"` from the dropdown menu.
- Click `Select file` and browse to the location where you saved the downloaded `.p12` certificate.
- When prompted for a password, enter `holberton`, which is the password for the certificate.

### Step 1.3: Reloading the Page to Reveal Hidden Content

- After successfully configuring the client TLS certificate in Burp Suite, revisit `https://web0x02.hbtn` in your browser.
- If everything is configured correctly, upon reloading, you should bypass the initial welcome screen and gain access to a new page—a direct result of successful client-side TLS authentication.

```bash
# when navigating to https://web0x02.hbtn 
# FLAG {f8c4ca67589b6e27098d0a528cf3f1b2} is displayed
echo f8c4ca67589b6e27098d0a528cf3f1b2 > 1-flag.txt

cat 1-flag.txt
```


## 2. Modifying Page Responses to Reveal Hidden Information

In this task, you will delve deeper into the functionalities of Burp Suite, particularly focusing on manipulating web server responses.
By intercepting and altering responses, you'll learn how to modify web page content in real-time.
Your objective is to reveal a hidden `Flag` ⛳️ on the `/task2` page by spoofing the frontend through response modification.

### Step 2.1: Intercepting the Download Request

- Ensure Burp Suite is configured correctly with your browser's proxy settings.
- Visit `/task2` or click the "Continue" button from the previous task's page to navigate there.
- In Burp Suite, make sure Intercept is On in the Proxy -> Intercept tab.
- On the `/task2` page, click the "Download" button. Burp Suite should capture the outbound request to the web server.

### Step 2.2: Modifying the Server Response

- With the request captured, right click on request `HTTP	REQUEST	GET	https://web0x02.hbtn/api/task2/check_status`, then choose `Do intercept` -> `Response to this request` -- this is to enable capturing the response from server `web0x02.htbn` towards our browser
- press the orange `-> Forward` button to send our request to the server
- Burp captures the response:
  ```json
  {
  	"message": {
  		"payment_status": "unpaid",
  		"refresh_token": "dcb2f07331a8637ea23a1d43bfafeb70"
  	},
  	"success": false,
  	"username": "dajcs"
  }
  ```
- edit: `unpaid` -> `paid`, `"success": true`
- click orange `-> Forward` to forward the edited message back to our browser
- Burp captures the next request: `HTTP	REQUEST	GET	https://web0x02.hbtn/api/task2/flag`
- click orange `-> Forward` to get the flag in the browser


### Step 2.3: Revealing the Flag

- FLAG: 843d2d370de2621af2a9603e37a4a952

```bash
echo 843d2d370de2621af2a9603e37a4a952 > 2-flag.txt

echo 2-flag.txt
```


## 3. Exploring the Repeater Tool

Burp Suite's Repeater tool is pivotal for testing and tweaking requests without repeatedly interacting with the web application itself.
Your objective in this task is to utilize Repeater to guess login credentials on a page designed to mimic a router's login portal.
By examining the request details and making educated adjustments, you'll aim to gain unauthorized access and uncover a hidden `Flag` ⛳️.

### Step 3.1: Capturing the Login Request

- `Intercept Off`  \
  Navigate to `/task3` or continue from the previous task's page by clicking the "Continue" button.
- `Intercept On`
- On the `/task3` page, click the designated button to initiate a login request. Once the request is captured in Burp Suite, use the shortcut Ctrl + R (or right-click request `HTTP	REQUEST	POST	https://web0x02.hbtn/api/task3/signin` and select Send to Repeater) to send it to the Repeater tool.


### Step 3.2: Guessing Credentials with Repeater

- In the Repeater tab, you'll see the captured login request ready for modification. Based on the hint that the page uses default router credentials, attempt common combinations like `admin`/`admin`, `admin`/`password`, or similar.
- Pay attention to other fields in the request, such as role and remember me options. Altering these values could impact the server's response and might be necessary for successful authentication.

### Step 3.3: Uncovering the Flag

- Continue tweaking and resending your request as needed based on server responses until you successfully authenticate (`admin`, `Michelangelo`, `admin`, `1`)
```json
{
	"message": "Congratulation\nFLAG: 133d648ecb3a2abfdebf65ed4fc6f591",
	"success": true
}
```
```bash
echo 133d648ecb3a2abfdebf65ed4fc6f591 > 3-flag.txt

echo 3-flag.txt
```
