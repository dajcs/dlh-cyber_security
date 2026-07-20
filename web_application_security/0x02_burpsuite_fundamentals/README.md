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

## 4. The Intruder's Path to Hidden Profiles

Burp Suite's Intruder tool is engineered for automating customized attacks against web applications.
This task will have you utilize Intruder to discover hidden user profiles by automating requests with varying parameters.
Your mission is to find a specific profile ID that reveals a hidden `Flag` ⛳️ by systematically testing different ID values.


### Step 4.1: Capturing the Request

- `Intercept Off`  \
  Navigate to `/task4` or continue from the previous task's page by clicking the "Continue" button.
- `Intercept On`
- Click the "Refresh" button on the /task4 page to generate a request. Once captured, send it to `Intruder` by pressing `Ctrl + I` or manually via the context menu, right click on `HTTP	REQUEST	GET	https://web0x02.hbtn/api/task4/profile/58263966` then \ Send to Intruder


### Step 4.2: Setting Up and Executing an Intruder Attack

- Within the Intruder tab, make sure you are looking at tab `2` (tab `1` is just a generic example provided by Burp)
- the very first line is: `GET /api/task4/profile/58263966 HTTP/1.1`
- The user profile ID is `58263966`.
- highlight these numbers (58263966).
- Click the `Add §` button located just above the text box. The number should now look like this: `§58263966§`. This tells Burp Suite to inject the payloads into this specific spot.
- on the right side of the screen is the Payloads panel 
- Find the `Payload type` dropdown (currently it says `Simple list`). Click it and select `Numbers`.
- A new configuration area will appear below it for number ranges.
- In the From field, type your starting ID: `58263966`
- In the To field, type the starting ID plus 100: `58264066`
- In the Step field, type 1 (this tells it to count up one by one).

### Step 4.3: Attack

- Click the orange Start attack button at the top right of the window.
- A new window should pop up showing the attack progress.
- Instead the new window tells you that Burp community edition sucks.
- click ok
- keep an eye on the Status column in the Burp \ Logger. 
- Look for a request that returns a 200 status code instead of an error or redirect (status 403 in our case)
- Once you find a profile ID that yields a 200 response, note this ID (this profile bio contains the FLAG). It signifies access to a hidden or non-public user profile.
- my 200: `GET /api/task4/profile/58263996`


### Step 4.4: Retrieving the Flag

- Return to the original intercepted request in the Proxy -> Intercept tab.
- Replace the profile ID in the request with the ID discovered during the Intruder attack.
- Forward the modified request.
- The response should now render a hidden user profile page (Yosri, of course), unveiling the sought-after Flag.

```bash
# Congratulations!
# FLAG: d236fcff3c8cc0f7ed3184f17b65ff8d
echo d236fcff3c8cc0f7ed3184f17b65ff8d > 4-flag.txt

echo 4-flag.txt
```


## 5. Deciphering Tokens with Sequencer

Burp Suite's Sequencer tool is designed for testing the randomness of session tokens, cookies, and other critical data that should be unpredictable and resistant to guessing attacks.
In this exercise, you'll use Sequencer to analyze a specific cookie, hijack_session, to uncover patterns or weaknesses in how it's generated.
Ultimately, your analysis will lead you to a valid session cookie that reveals a hidden `Flag` ⛳️.

### Step 5.1: Capturing the Request

- `Intercept Off`  \
  Navigate to `/task5` or continue from the previous task's page by clicking the "Continue" button.
- `Intercept On`  \
  Click Reload to `/task5`.
- Once the page loads, capture this initial request and send it to the Repeater by pressing Ctrl + R or through the context menu.


### Step 5.2: Preparing for Sequencer Analysis

- In the Repeater tab, locate the `Cookie` header and remove the `hijack_session` value from the request.
- Right-click on the modified request and select "Send to Sequencer."


### Step 5.3: Configuring and Starting Sequencer

- In the Burp \ Sequencer tab, ensure the tool detects the `hijack_session` parameter for analysis (select Cookie: hijack_session=f88...)
- Before starting the live capture, enter Sequencer settings and adjust the "Throttle between requests (ms)" to 25 to regulate the pace of token generation without overwhelming the server and set number of threads to 1
- Close the settings and initiate the live capture of tokens. Aim to generate around 200 tokens before halting the capture.


### Step 5.4: Analyzing Token Pattern and Hijacking Session

- After stopping the capture, export or copy the tokens into your preferred text editor for analysis.
- Review the sequence of tokens to identify any discernible patterns or anomalies, such as skipped or repeating values.
- Locate a skipped cookie value—this represents a valid session that can be exploited.
```bash
f889bf9f-3189-4581-b854-cfdab56e02a8-178455888850
f889bf9f-3189-4581-b854-cfdab56e02a8-178455888855
# f889bf9f-3189-4581-b854-cfdab56e02a8-178455888860 <-missing
f889bf9f-3189-4581-b854-cfdab56e02a8-178455888865
f889bf9f-3189-4581-b854-cfdab56e02a8-178455888870
```

- Replace your current session cookie in the browser (using developer tools or a cookie management extension) with the identified valid hijack_session value.


### Step 5.5: Revealing the Flag

- Open your web browser and go to the /task5 page.
- Open your browser's Developer Tools (press F12 or right-click -> Inspect).
- Go to the Application tab (Chrome/Edge) or Storage tab (Firefox).
- On the left sidebar, expand Cookies and click on the website (https://web0x02.hbtn).
- Find the hijack_session cookie in the list. Double-click its current value and paste in the stolen token: f889bf9f-3189-4581-b854-cfdab56e02a8-178455888860
- Close the developer tools and Refresh the web page.
- Scratch the card!

```bash
# Congratulations!
# FLAG: 54abf5fc96a7d3f8a372c614d9197ffe
echo 54abf5fc96a7d3f8a372c614d9197ffe > 5-flag.txt

cat 5-flag.txt
```


## 6. `Decoder` Tab - Manipulating Base64 Encoded Bearer Tokens

In the final task of this series, you'll delve into the intricacies of Bearer Token manipulation.
By intercepting a request that includes a Bearer Token, you'll decode, modify, and re-encode the token to escalate privileges and reveal a hidden `Flag` ⛳️.
This task emphasizes the importance of secure token handling and validation by web applications.


### Step 6.1: Intercepting the Request

- `Intercept Off`  \
  Navigate to `/task6` or continue from the previous task's page by clicking the "Continue" button.
- `Intercept On`  \
- Click the "Check All" button on the /task6 page to generate a request.
- Intercept this request in Burp Suite.


### Step 6.2: Modifying the Bearer Token

- Locate the `Authorization` header in the intercepted request, which contains the Bearer Token.
- Right-click on the token and select "Send to Decoder" or navigate to the Decoder tab and paste the token there.


### Step 6.3: Decoding and Editing the Token

In the Decoder tab, follow these steps to decode and modify the token:
1. Decode the token from Base64.
2. Decompress the decoded data (GZIP).
3. You should now see a JSON object with an `"admin": false` value.
4. Edit the JSON to change `"admin": false` to `"admin": true`.
5. Compress the modified JSON using GZIP.
6. Encode the compressed data back to Base64.


### Step 6.4 Replacing the Modified Token

- Copy the newly encoded token.
- Return to the Proxy -> Intercept tab, and replace the original Bearer Token in the Authorization header with your modified token.
- Forward the request.


### Step 6.5: Revealing the Flag

- get the flag

```bash
# Congratulations!
# FLAG: 8b96e02115ec00089099138ee2959193
echo 8b96e02115ec00089099138ee2959193 > 6-flag.txt

cat 6-flag.txt
```