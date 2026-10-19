# M01 | Lobby Reconnaissance: Lab Summary

**Mission:** M01 (LOW)  
**Environment:** ACME Corp, authorized penetration-testing lab  
**Kali IP:** `10.10.10.5`  
**Target subnet:** `192.168.0.0/24`  
**Primary infrastructure target:** `192.168.0.1` (`LOBBY-SW01.acme.corp`)  
**Status:** **Completed, flag captured**

## Objectives

1. Discover all live hosts in the lobby subnet.
2. Enumerate management services on infrastructure IPs `192.168.0.1` through `192.168.0.5` using TCP and UDP scanning.
3. Confirm an SNMP community string, walk the switch's MIB tree, and locate `ACME-CUSTOM-MIB::assetTag.0`.

---

## Step 1: Host discovery

### Command

```bash
sudo nmap -sn 192.168.0.0/24
```

### Parameters

| Parameter | Meaning |
|---|---|
| `sudo` | Run Nmap with privileges for low-level discovery probes. |
| `nmap` | Network scanning utility. |
| `-sn` | Host discovery only, without a port scan. Discovery probes vary with privileges and network topology. |
| `192.168.0.0/24` | Target the subnet, containing 256 addresses. |

### Response

```text
Starting Nmap 7.94 at 2024-03-15 09:12 EST
Initiating Ping Scan on 192.168.0.0/24 [256 hosts]
Scanning 256 hosts [4 ports/host]
Completed Ping Scan on 192.168.0.0/24 in 4.02s (12 hosts up)
Nmap scan report for 192.168.0.1
Nmap scan report for 192.168.0.2
Nmap scan report for 192.168.0.10
Nmap scan report for 192.168.0.11
Nmap scan report for 192.168.0.12
Nmap scan report for 192.168.0.15
Nmap scan report for 192.168.0.20
Nmap scan report for 192.168.0.21
Nmap scan report for 192.168.0.30
Nmap scan report for 192.168.0.40
Nmap scan report for 192.168.0.50
Nmap done: 256 IP addresses (12 hosts up) scanned in 4.23 seconds
[+] Step 1/3 complete! Proceed to step 2.
```

**Result:** Lab reports **12 active hosts**, as required.

**Output discrepancy:** The pasted discovery response explicitly lists **11 IPs**, although its summary says **12**. The missing twelfth IP cannot be identified from that output alone. The next scan confirms that `.3`, `.4` and `.5` respond, but these cannot be assumed to be the omitted discovery entry.

**Other clue:** `192.168.0.15` is labeled a Hikvision camera (identified by the lab as an M02 target).

---

## Step 2: Service and version enumeration

The lab required **one combined TCP SYN + UDP scan** with service-version detection and default scripts, restricted to infrastructure addresses `.1` to `.5`.

### Successful command

```bash
sudo nmap -sS -sU -sV -sC -p T:22,23,80,443,4786,U:161 192.168.0.1-5
```

### Parameters

| Parameter | Meaning |
|---|---|
| `-sS` | TCP SYN scan. |
| `-sU` | UDP scan. |
| `-sV` | Probe detected services to identify products and versions. |
| `-sC` | Run Nmap's default NSE scripts against the selected services. |
| `-p T:22,23,80,443,4786,U:161` | Scan TCP management ports 22, 23, 80, 443, 4786 and UDP port 161. |
| `192.168.0.1-5` | Target `192.168.0.1` through `192.168.0.5`. |

### Port reference

| Port | Service | Purpose / significance |
|---|---|---|
| `22/tcp` | SSH | Encrypted administrative access. |
| `23/tcp` | Telnet | Administrative access without transport encryption. |
| `80/tcp` | HTTP | Web-based management, unencrypted. |
| `443/tcp` | HTTPS | Web-based management with TLS. |
| `4786/tcp` | Cisco Smart Install | Cisco device deployment / management feature; requires security review if exposed. |
| `161/udp` | SNMP | Network-device monitoring and MIB queries. |

### Responses by host

#### `192.168.0.1` | `LOBBY-SW01.acme.corp`

```text
22/tcp    open  ssh            OpenSSH 7.4p1 Debian 10+deb9u7 (protocol 2.0)
23/tcp    open  telnet         Cisco IOS telnetd
80/tcp    open  http           Cisco IOS http config (HTML)
443/tcp   open  ssl/http       Cisco IOS HTTPS
4786/tcp  open  smart-install  Cisco Smart Install (SMI) -- CVE-2018-0171 risk
161/udp   open  snmp           SNMPv2c server (public)

snmp-info:
  enterprise: cisco
  sysContact: noc@acme.corp
  sysName: LOBBY-SW01
```

**Key findings:** Telnet is open; SNMPv2c accepts the `public` community; Smart Install port 4786 is open. The lab mentions **CVE-2018-0171 risk**, but an open port alone does **not** establish that the device is vulnerable.

#### `192.168.0.2` | `GW-LOBBY.acme.corp`

```text
22/tcp    open      ssh            Dropbear 2020.81 (edge router)
23/tcp    filtered  telnet
80/tcp    open      http           lighttpd 1.4.45
443/tcp   closed    https
4786/tcp  filtered  smart-install
161/udp   closed    snmp
```

#### `192.168.0.3` | `LOBBY-AP01.acme.corp`

```text
22/tcp    open    ssh        OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
23/tcp    closed  telnet
80/tcp    open    http       nginx 1.18.0 (AP captive portal)
443/tcp   open    ssl/http  nginx
4786/tcp  closed  smart-install
161/udp   closed  snmp
```

#### `192.168.0.4` | `LOBBY-PRINT01.acme.corp`

```text
22/tcp    closed  ssh
23/tcp    closed  telnet
80/tcp    open    http   HP HTTP Server; JetDirect
443/tcp   closed  https
4786/tcp  closed  smart-install
161/udp   closed  snmp
```

#### `192.168.0.5` | `LOBBY-NAS01.acme.corp`

```text
22/tcp    open    ssh        OpenSSH 7.9 (Synology DSM)
23/tcp    closed  telnet
80/tcp    open    http       nginx
443/tcp   open    ssl/http  nginx
4786/tcp  closed  smart-install
161/udp   closed  snmp
```

### Scan completion

```text
Nmap done: 5 IP addresses (5 hosts up) scanned in 18.94 seconds
[!] FINDING: 192.168.0.1 -- 23/tcp telnet open (cleartext management)
[!] FINDING: 192.168.0.1 -- 161/udp SNMP 'public' (no encryption)
[!] NOTE: 4786/tcp open on .1 -- audit Smart Install before exploitation class
[+] Step 2/3 complete! Proceed to step 3.
```

**Why the earlier commands were rejected:** The exercise's command validator expected the **TCP and UDP scanning options together**, with the relevant service/version flags and target scope. Separate TCP-only and UDP-only scans, or a generic default-port scan, did not satisfy that specific check.

---

## Step 3: SNMP community discovery and MIB enumeration

### 3A. Confirm the community string with `onesixtyone`

**Command typed:**

```bash
onesixtyone 192.168.0.1 public
```

**Parameters:**

| Argument | Meaning |
|---|---|
| `onesixtyone` | Utility for enumerating SNMP community strings. |
| `192.168.0.1` | SNMP host to query. |
| `public` | Community string supplied in the lab interaction. |

**Simulator response:**

```text
# onesixtyone -c /usr/share/doc/onesixtyone/dict.txt 192.168.0.1
Scanning 1 hosts using 375 community strings...
192.168.0.1 [public] Cisco IOS software, C2960 (C2960-UNIVERSALK9-M), Version 12.4(25e)
192.168.0.1:161 [public] -- community string CONFIRMED
[note] Use this community string with snmpwalk to enumerate the device.
flag captured: 66800c78ea0eb4515fd4df0aba022243
saved to ~/flags/flag0.txt
[+] Mission M01 complete: Lobby Reconnaissance
```

**Important simulator behavior:** Although the typed command was `onesixtyone 192.168.0.1 public`, the replay displayed a dictionary-based `onesixtyone -c ...` invocation. The simulator **captured and saved the flag at this point**, before the subsequent `snmpwalk` was submitted.

For reference, a conventional `onesixtyone` community dictionary scan uses:

```bash
onesixtyone -c /usr/share/doc/onesixtyone/dict.txt 192.168.0.1
```

### 3B. Walk the MIB with `snmpwalk`

**Command typed:**

```bash
snmpwalk -v2c -c public 192.168.0.1 .1
```

**Parameters:**

| Parameter | Meaning |
|---|---|
| `snmpwalk` | Traverse successive SNMP object identifiers (OIDs). |
| `-v2c` | Use SNMP version 2c. |
| `-c public` | Supply the read community string `public`. |
| `192.168.0.1` | Query the lobby Cisco switch. |
| `.1` | Start at the top of the numeric OID tree for a broad walk. |

**Response:** The simulator reported that Step 3 was already complete and replayed a stored SNMP walk. Its replay showed the effective command as `snmpwalk -v2c -c public 192.168.0.1`.

```text
SNMPv2-MIB::sysDescr.0 = STRING: ACME-LOBBY-SW01 Cisco C2960 Ver 12.4(25e)
SNMPv2-MIB::sysName.0 = STRING: LOBBY-SW01.acme.corp
SNMPv2-MIB::sysContact.0 = STRING: noc@acme.corp
SNMPv2-MIB::sysLocation.0 = STRING: ACME Corp HQ, Rack 4-U12
IF-MIB::ifNumber.0 = INTEGER: 48
IF-MIB::ifDescr.1 = STRING: GigabitEthernet0/1
IF-MIB::ifAlias.1 = STRING: Reception Desk 1 (192.168.0.10)
IF-MIB::ifDescr.2 = STRING: GigabitEthernet0/2
IF-MIB::ifAlias.2 = STRING: Reception Desk 2 (192.168.0.11)
IF-MIB::ifDescr.3 = STRING: GigabitEthernet0/3
IF-MIB::ifAlias.3 = STRING: IP-CAM Hikvision DS-2CD2143 (192.168.0.15)
IF-MIB::ifDescr.4 = STRING: GigabitEthernet0/4
IF-MIB::ifAlias.4 = STRING: Security DVR (192.168.0.21)
IF-MIB::ifDescr.5 = STRING: GigabitEthernet0/5
IF-MIB::ifAlias.5 = STRING: Wireless AP (192.168.0.30)
... (247 OIDs total) ...
IP-MIB::ipRouteDest.192.168.99.0 = IpAddress: 192.168.99.0
CISCO-VLAN-MIB::vlanTrunkPortEncapsulationType.1 = INTEGER: dot1Q(4)
ACME-CUSTOM-MIB::assetTag.0 = 66800c78ea0eb4515fd4df0aba022243
snmpwalk complete: 247 OIDs enumerated in 3.1 seconds
```

### Information recovered

| Item | Value / observation |
|---|---|
| Hostname | `LOBBY-SW01.acme.corp` |
| Hardware / OS | Cisco Catalyst 2960, IOS 12.4(25e) (as reported by the lab) |
| Administrative contact | `noc@acme.corp` |
| Physical location | ACME Corp HQ, Rack 4-U12 |
| Interface count reported | `48` |
| `GigabitEthernet0/1` | Reception Desk 1, `192.168.0.10` |
| `GigabitEthernet0/2` | Reception Desk 2, `192.168.0.11` |
| `GigabitEthernet0/3` | Hikvision IP camera, `192.168.0.15` |
| `GigabitEthernet0/4` | Security DVR, `192.168.0.21` |
| `GigabitEthernet0/5` | Wireless AP, `192.168.0.30` |
| Other network | Route destination `192.168.99.0`, labeled *hidden VLAN* by the lab; a route entry by itself does not confirm the VLAN ID or membership. |
| Trunk encapsulation | `dot1Q(4)` (802.1Q) |
| Custom asset-tag OID | `ACME-CUSTOM-MIB::assetTag.0` |

**Technical note:** SNMPv2c has **no built-in encryption** and relies on a community string for rudimentary access control. Therefore `public` is not an absence of authentication; it is a weak, shared community credential in this scenario.

---

## Flag and mission result

**Flag OID:**

```text
ACME-CUSTOM-MIB::assetTag.0
```

**Captured flag:**

```text
66800c78ea0eb4515fd4df0aba022243
```

**Local file reported by the simulator:**

```text
~/flags/flag0.txt
```

**Mission status:** `M01 complete: Lobby Reconnaissance`

---

## Command cheat sheet

```bash
# 1. Discover active hosts across the lobby subnet
sudo nmap -sn 192.168.0.0/24

# 2. Enumerate TCP + UDP management services on infrastructure hosts
sudo nmap -sS -sU -sV -sC -p T:22,23,80,443,4786,U:161 192.168.0.1-5

# 3. Confirm the SNMP community string (lab-entered command)
onesixtyone 192.168.0.1 public

# 4. Walk the SNMP MIB tree
snmpwalk -v2c -c public 192.168.0.1 .1

# 5. Read the discovered flag file locally
cat ~/flags/flag0.txt
```

## Main lessons

1. **Discovery before enumeration:** `-sn` identifies responding devices without scanning their ports.
2. **Match protocols to services:** SNMP normally uses UDP/161, so a TCP-only scan misses it.
3. **Service banners are evidence, not proof of exploitability:** A suspected CVE needs separate validation.
4. **SNMP can expose topology and operational details:** The walk revealed host identity, interface descriptions, connected assets and routing information.
5. **Treat command validators separately from real tool semantics:** In this lab, Step 2 required an exact combined-scan pattern, and Step 3 returned a replay after the flag was already marked captured.
