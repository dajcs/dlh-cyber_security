# 0. Credits

```bash
┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x01_passive_reconnaissance]
└─$ shodan init jzaD4GVbF0mA0ogVDpilnGRLC1vGQu0c
Successfully initialized
                                                                            
┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x01_passive_reconnaissance]
└─$ shodan info                                 
Query credits available: 0
Scan credits available: 0
    
                                                                            
┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x01_passive_reconnaissance]
└─$ shodan domain holbertonschool.com

Error: Access denied (403 Forbidden)
┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x01_passive_reconnaissance]
```


# 1. Web Search

[https://www.shodan.io/search?query=holbertonschool.com](https://www.shodan.io/search?query=holbertonschool.com)

There are 4 IP addresses associated with the domain `holbertonschool.com` in the Shodan search results. All four results are hosted in **Paris, France** via **Amazon Data Services France**.

| IP Address | Hostname(s) | Scan Date & Time | HTTP Status / Title | Server Software | Additional Details |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **52.47.143.83** | `yriry2.holbertonschool.com`<br>`ec2-52-47-143-83...` | 2026-06-09<br>16:38:17 | **200 OK**<br>Holberton School Level2 Forum | `nginx` | **SSL Certificate:** Let's Encrypt<br>**SSL Versions:** TLSv1.2, TLSv1.3 |
| **35.180.27.154** | `ec2-35-180-27-154...` | 2026-05-26<br>08:22:00 | **301 Moved Permanently** | `nginx/1.18.0 (Ubuntu)` | **Redirect Location:**<br>`http://holbertonschool.com` |
| **52.47.143.83** | `ec2-52-47-143-83...` | 2026-05-20<br>10:48:40 | **301 Moved Permanently** | `nginx/1.21.6` | **Redirect Location:**<br>`https://yriry2.holbertonschool.com/` |
| **35.180.27.154** | `ec2-35-180-27-154...` | 2026-05-19<br>23:11:22 | **301 Moved Permanently** | `nginx/1.18.0 (Ubuntu)` | **Redirect Location:**<br>`http://holbertonschool.com` |

### General Scan Summary:
* **Target Query:** `holbertonschool.com`
* **Total Results:** 4
* **Top Ports Discovered:** Port 80 (2 results), Port 443 (2 results)

We're using this data to prepare a small file `ips.txt` that contains the IP addresses of the discovered hosts.

> **Note:** The IP addresses are repeated in the Shodan results, so it is enough to include them once in the `ips.txt` file.

```bash
echo "52.47.143.83" > ips.txt
echo "35.180.27.154" >> ips.txt
```

# 2. Free Shodan: the InternetDB API

`internetdb.shodan.io` is Shodan's free, unauthenticated API that returns open ports, hostnames, tags, CPEs (Customer Premises Equipment), and vulnerabilities for a given IP address. We can query this API using `curl` to retrieve information about the IP addresses we found in the previous step.

```bash
while read ip; do
    echo "=== $ip ==="
    curl -s "https://internetdb.shodan.io/$ip" | jq
    echo ""
done < ips.txt
```

### Result from 6-free_shodan.sh:

```bash
anemet@c2r6s4 ~/dlh-cyber_security/network_security/0x01_passive_reconnaissance
 % ./6-free_shodan.sh ips.txt 
=== 52.47.143.83 ===
{
  "cpes": [
    "cpe:/a:f5:nginx:1.21.6",
    "cpe:/a:f5:nginx"
  ],
  "hostnames": [
    "yriry2.holbertonschool.com",
    "ec2-52-47-143-83.eu-west-3.compute.amazonaws.com"
  ],
  "ip": "52.47.143.83",
  "ports": [
    80,
    443
  ],
  "tags": [
    "cloud",
    "eol-product"
  ],
  "vulns": [
    "CVE-2023-44487",
    "CVE-2025-23419"
  ]
}

=== 35.180.27.154 ===
{
  "cpes": [
    "cpe:/a:f5:nginx:1.18.0",
    "cpe:/o:canonical:ubuntu_linux",
    "cpe:/o:linux:linux_kernel"
  ],
  "hostnames": [
    "ec2-35-180-27-154.eu-west-3.compute.amazonaws.com"
  ],
  "ip": "35.180.27.154",
  "ports": [
    80
  ],
  "tags": [
    "eol-product",
    "cloud"
  ],
  "vulns": [
    "CVE-2025-23419",
    "CVE-2023-44487",
    "CVE-2021-23017",
    "CVE-2021-3618"
  ]
}

```

### Analysis of the Results:

Putting the available data into a table format for better readability:



| IP Address | Hostnames | Ports | CPEs (Software / OS) | Tags | Vulnerabilities |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **52.47.143.83** | `yriry2.holbertonschool.com`<br>`ec2-52-47-143-83.eu-west-3.compute.amazonaws.com` | `80`, `443` | `cpe:/a:f5:nginx:1.21.6`<br>`cpe:/a:f5:nginx` | `cloud`, `eol-product` | CVE-2023-44487<br>CVE-2025-23419 |
| **35.180.27.154** | `ec2-35-180-27-154.eu-west-3.compute.amazonaws.com` | `80` | `cpe:/a:f5:nginx:1.18.0`<br>`cpe:/o:canonical:ubuntu_linux`<br>`cpe:/o:linux:linux_kernel` | `eol-product`, `cloud` | CVE-2025-23419<br>CVE-2023-44487<br>CVE-2021-23017<br>CVE-2021-3618 |
