# Content Discovery


## Task 0. Manual Discovery - Secrets in Plain Sight

Your goal is to uncover a hidden flag by thoroughly exploring the site's structure.

Use all available discovery methods, including analyzing files such as `robots.txt`, `sitemap.xml`, and `favicon.ico`

- Target Machine: `cyber_websec_0x04`
- Target Endpoint: `http://web0x04.hbtn/`
- [Dir Word List](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt)
- [WP Word List](https://github.com/test0001-star/0x04/blob/main/WP_Word_list.txt)
- start sandbox `cyber_websec_0x04`
  - Network Information  - Ip: `10.42.8.228`
  - add ip to `/etc/hosts`:
  ```bash
  sudo bash -c "echo '10.42.8.228  web0x04.hbtn' >> /etc/hosts"
  cat /etc/hosts
  ```
  - start vpn

### 0.1. Sitemap Exploration

Start by reviewing the sitemap located at `/sitemap.xml`. The sitemap may reveal unusual or hidden routes not linked from anywhere else on the site.

One of these routes contains your flag.

- Checking `http://web0x04.hbtn/sitemap.xml` there are quite a few links.
- downloading the `sitemap.xml`
```bash
curl -s http://web0x04.hbtn/sitemap.xml --output sitemap.xml

# extracting the links (47 in total) to a file
grep -oP '(?<=<loc>)[^<]+' sitemap.xml > sitemap_links.txt

# visiting every site and looking for the flag
while IFS= read -r url; do
  echo "[*] Checking $url"
  curl -fsSL "$url" | grep -iE 'flag|HTB\{[^}]+\}|[a-f0-9]{32}'
done < sitemap_links.txt
# [*] Checking http://web0x04.hbtn/macau-macau/
# curl: (22) The requested URL returned error: 500
# [*] Checking http://web0x04.hbtn/fort-de-france-martinique/
# curl: (22) The requested URL returned error: 500
# ...
# [*] Checking http://web0x04.hbtn/ta-holbie-malta/
# Congratulations! FLAG: 92383e47a8806601622b2c98a761638f
```


### 0.2. Additional Discovery

Investigate any common files such as `robots.txt` or `favicon.ico`, as they may contain further clues or hidden paths.


### 0.3. Useful Instructions

1. Start by navigating to `/robots.txt`. Look for any Disallow entries that might hint at hidden or restricted paths. These paths could lead to interesting or hidden resources.
2. Access `/sitemap.xml`. Sitemaps are used to help search engines index web content, but they may also reveal hidden resources. Find the resource that is not linked from anywhere else on the site to discover your flag.
3. Download the site's `favicon.ico` and analyze it using tools or online resources like the OWASP favicon database. By matching the favicon to known frameworks, you might uncover more information about the site.
4. Pay close attention to details in each file. Each file could contain direct paths or subtle hints that lead to the next step in your discovery process.
5. Utilize online tools for favicon analysis and comparison to help identify the framework and speed up your search for hidden resources.


```bash
curl http://web0x04.hbtn/robots.txt

# User-agent: *
# Disallow: /hidden-directory/
# Disallow: /wp-admin/
# 
# Sitemap: http://web0x04.hbtn/mpg-sitemap-switzerland-regions.xml
# Sitemap: http://web0x04.hbtn/mpg-sitemap-switzerland-places-index.xml
# Sitemap: http://web0x04.hbtn/mpg-sitemap-world-cities.xml
```

### 0.4. Save the Flag found in 0.1

```bash
echo 92383e47a8806601622b2c98a761638f > 0-flag.txt

cat 0-flag.txt

git add .
git commit -m "0-flag.txt"
git push
```



## 1. Manual Discovery - Headers, Headers, Always Check Headers

HTTP Headers often hide secrets 🤫.
In this task, you'll meticulously inspect HTTP response headers to unearth a hidden `Flag` ⛳️.  \
This requires a keen eye and an understanding of how developers might conceal information within the HTTP protocol.


### Useful Instructions

1. Utilize `curl`, browser developer tools, or similar tools to examine the complete set of HTTP response headers returned from the target endpoint.
2. Do not overlook non-standard headers; the flag may be tucked away within a custom or uncommon header field.
3. Be aware that servers can dynamically alter headers based on the request's nature. Vary your request type, user-agent, and other headers to provoke different responses.
4. Certain headers might appear only under specific circumstances (e.g., receiving error codes or when making requests with unique headers). Adjust your requests to explore these possibilities.


```bash
# first try
curl -I http://web0x04.hbtn/
# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Tue, 21 Jul 2026 10:52:08 GMT
# Content-Type: text/html; charset=UTF-8
# Connection: keep-alive
# X-Secret-Flag: d3cb5dd4bbe4410a51822ff2226508b4
# Link: <http://web0x04.hbtn/wp-json/>; rel="https://api.w.org/"
```

### Let's try our X-Secret-Flag

```bash
echo d3cb5dd4bbe4410a51822ff2226508b4 > 1-flag.txt

cat 1-flag.txt
```

```bash
git add .
git commit -m "1-flag.txt with push"
git push
```


## 2. The Buster Series - Initiating with Gobuster `dir mode`

Gobuster is a powerful tool designed to automate the process of content discovery.  \
It employs various modes, making it indispensable for the modern cybersecurity toolkit.  \
Your quest involves mastering Gobuster's modes to unearth hidden resources, subdomains, and much more.  \
We start our journey with an overview of the seven key modes Gobuster offers:

1. `dir`: A mode for classic directory brute-forcing.
2. `dns`: Brute-forces DNS subdomains.
3. `s3`: Enumerates open S3 buckets and checks for their existence and listings.
4. `gcs`: Searches for open Google Cloud Storage buckets.
5. `vhost`: Conducts brute-forcing of virtual hosts (vhosts), different from DNS subdomain searching.
6. `fuzz`: Undertakes basic fuzzing, pinpointing where a keyword (FUZZ) should be replaced.
7. `tftp`: Brute-forces TFTP file names.


This comprehensive feature set makes Gobuster adept at revealing the unseen parts of web applications and infrastructure.

Your first mission is to familiarize yourself with Gobuster's `dir` mode by conducting a directory brute-force attack against a target website.  \
You'll leverage this mode to discover hidden directories that will return a `Flag` ⛳️ as content with `Task #4` as Website title.


### Useful Instructions

1. Select a wordlist for the directory brute-forcing operation. You can use common wordlists provided by tools like `dirb` or `SecLists`.
2. Execute Gobuster in `dir` mode against the target website, specifying your chosen wordlist.
3. Analyze the output, focusing on HTTP status codes that indicate the presence of a directory (e.g., 200 OK, 403 Forbidden).
4. Document any interesting directories you discover, noting their paths and any content or functionality they reveal.

**Remember**:
- Experiment with different wordlists and options (e.g., specifying file extensions) to uncover as much as possible.
- Be mindful of the network and server load you're generating with your requests to ensure responsible use of the tool.


### Hints

1. There are two layers to find, and both can be discovered simultaneously.
2. The structure you're looking for is: web0x04//*.php.
3. Multiple endpoints follow the same format, each ending with .php.
4. Focus on fuzzing directories that lead to .php files—they hide what you need!



### 2.1 First Try - root scan

Starting with a root scan that tests both directory names and PHP filenames:

```bash
BASE='http://web0x04.hbtn'
WL='/usr/share/wordlists/dirb/common.txt'  # 4614 words

gobuster dir \
  -u "$BASE/" \
  -w "$WL" \
  -x php \
  -t 20 \
  -o gobuster-root.txt
```
- `-u` for the base URL
- `-w` for the wordlist
- `-x php` to test PHP extensions
- `-t 20` 20 threads

For every word such as admin, Gobuster effectively checks `/admin` and `/admin.php`

Checking the result saved in `gobuster-root.txt`:

```bash
cat gobuster-root.txt                                                           
# .htaccess            (Status: 200) [Size: 385]
# _                    (Status: 301) [Size: 0] [--> http://web0x04.hbtn/tour-to-the-beautiful-city-of-mpg_city-in-mpg_country/]
# 0                    (Status: 301) [Size: 0] [--> http://web0x04.hbtn/0/]
# admin                (Status: 302) [Size: 0] [--> http://web0x04.hbtn/wp-admin/]
# create               (Status: 301) [Size: 169] [--> http://web0x04.hbtn/create/]
# favicon.ico          (Status: 200) [Size: 1150]
# payment_gateway      (Status: 301) [Size: 169] [--> http://web0x04.hbtn/payment_gateway/]
# robots.txt           (Status: 200) [Size: 257]
# sitemap.xml          (Status: 200) [Size: 6860]
# wp-admin             (Status: 301) [Size: 169] [--> http://web0x04.hbtn/wp-admin/]
# wp-content           (Status: 301) [Size: 169] [--> http://web0x04.hbtn/wp-content/]
# wp-includes          (Status: 301) [Size: 169] [--> http://web0x04.hbtn/wp-includes/]
# wp-config.php        (Status: 200) [Size: 0]
# wp-cron.php          (Status: 200) [Size: 0]
# wp-links-opml.php    (Status: 200) [Size: 251]
# wp-load.php          (Status: 200) [Size: 0]
# wp-login.php         (Status: 200) [Size: 4123]
# wp-mail.php          (Status: 403) [Size: 2501]
# wp-settings.php      (Status: 500) [Size: 0]
# wp-signup.php        (Status: 302) [Size: 0] [--> http://web0x04.hbtn/wp-login.php?action=register]
# xmlrpc.php           (Status: 405) [Size: 42]
```

Most of the directories found are common WordPress directories, but directories `0`, `create` 
and `payment_gateway` might need further investigation with second gobuster run to find the filename.

After a half-a-day of unsuccessful busting attempts with different wordlists I've discovered that
in the very beginning of this task list it has been metioned a [WP Word List](https://github.com/test0001-star/0x04/blob/main/WP_Word_list.txt)
This contains common .php filenames (294) and I've downloaded it in the current directory as `common.php.txt`

Let's check the `create/` directory:

```bash
gobuster dir \
  -u "http://web0x04.hbtn/create/" \
  -w "common.php.txt" \
  -t 20 \
  -o gobuster-create.txt


# ===============================================================
# Gobuster v3.8.2
# by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
# ===============================================================
# [+] Url:                     http://web0x04.hbtn/create/
# [+] Method:                  GET
# [+] Threads:                 20
# [+] Wordlist:                common.php.txt
# [+] Negative Status codes:   404
# [+] User Agent:              gobuster/3.8.2
# [+] Timeout:                 10s
# ===============================================================
# Starting gobuster in directory enumeration mode
# ===============================================================
# hiddenflag.php       (Status: 200) [Size: 84]
# Progress: 294 / 294 (100.00%)
# ===============================================================
# Finished
# ===============================================================

```

> Lessons learned: no matter how big is your wordlist, if it doesn't contain the `hiddenflag` word you won't make it.  \
` ¯\_(ツ)_/¯ `

The `hiddenflag.php` sounds promising, let's have a visit to
[http://web0x04.hbtn/create/hiddenflag.php](http://web0x04.hbtn/create/hiddenflag.php)

```bash
curl http://web0x04.hbtn/create/hiddenflag.php

# Flag found! Congratulations. Here is your flag:  50a99edc175c95e7cfb9a8a56a2dc3de
```

### Save the flag

```bash
echo 50a99edc175c95e7cfb9a8a56a2dc3de > 2-flag.txt

cat 2-flag.txt

git add .
git commit -m "2-flag.txt"
git push
```

Nope, this wasn't the solution :-(

Double checking if we have another flag under `payment_gateway`:

```bash
gobuster dir \
  -u "http://web0x04.hbtn/payment_gateway/" \
  -w "common.php.txt" \
  -t 20 \
  -o gobuster-payment_gateway.txt

# hiddenflag.php       (Status: 200) [Size: 84]
```

```bash
curl http://web0x04.hbtn/payment_gateway/hiddenflag.php

# Flag found! Congratulations. Here is your flag:  50a99edc175c95e7cfb9a8a56a2dc3de  

# checking if there is a difference between the two flags
cat 2-flag.txt 
# 50a99edc175c95e7cfb9a8a56a2dc3de

```

The two flags are identical.

Double checking the **Repo**:
  - GitHub repository: `dlh-cyber_security`
  - Directory: `web_application_security/0x04_content_discovery`
  - **File**: **`4-flag.txt`**

It turns out we were navigating under a false flag.

```bash
mv 2-flag.txt 4-flag.txt

git add .
git commit -m "four-flag.txt"
git push
```


## 3. The Buster Series - Unveiling Hidden Subdomains `dns mode`

This powerful feature is designed for DNS subdomain enumeration,
allowing you to uncover hidden or unlinked subdomains which could expose additional facets of the target's online presence or infrastructure vulnerabilities.  \
Unlock the secrets of DNS by performing a zone transfer to uncover hidden records.  \
You’ll use advanced DNS querying techniques to reveal alternative DNS records that may not be easily discoverable through standard methods.  \
You'll leverage this mode to discover hidden subdomain that will return a `Flag` ⛳️ as content with `Task #5` as Website title.
- Target Machine: `cyber_websec_0x04`
- Target Domain: `web0x04.hbtn`
- start sandbox `cyber_websec_0x04`
  - Network Information  - Ip: `10.42.8.228`
  - add ip to `/etc/hosts`:
  ```bash
  sudo bash -c "echo '10.42.8.228  web0x04.hbtn' >> /etc/hosts"
  cat /etc/hosts
  ```
  - start vpn

- `dns_wordlist.txt`:
  ```
  lakeinsurveyor
  lakekindred
  lakelandcenter.place
  lakelandledger.fl
  lakemary.place
  lakemaryprep.learning
  lakemaster.blog
  lake-Michigan
  sub
  lakemonsters
  lakenozori.web
  lakeoconeeacademy
  db
  lake-of-the-ozarks
  lakeofthetorches
  lakeorion
  ns1
  lakeoswegoor
  ```

Let's prepare this `dns_wordlist.txt`:

```bash
cat > dns_wordlist.txt <<'EOF'
lakeinsurveyor
lakekindred
lakelandcenter.place
lakelandledger.fl
lakemary.place
lakemaryprep.learning
lakemaster.blog
lake-Michigan
sub
lakemonsters
lakenozori.web
lakeoconeeacademy
db
lake-of-the-ozarks
lakeofthetorches
lakeorion
ns1
lakeoswegoor
EOF

wc -l dns_wordlist.txt
# 18 dns_wordlist.txt

cat dns_wordlist.txt
```

### Useful Instructions
1. Choose a wordlist tailored for DNS subdomain brute-forcing. The `SecLists` project offers comprehensive lists suited for this purpose.
2. Use Gobuster in `dns` mode to enumerate subdomains for the target domain.
3. Pay careful attention to the output, particularly any discovered subdomains. These entries can reveal development, staging, or other sensitive environments related to the target.
4. Record the subdomains found, noting any that were previously unknown or particularly interesting in terms of security or functionality.

**Remember**:

- Utilizing a high thread count with `-t` can speed up the scan but ensure it's within reasonable limits to avoid network or service disruption.
- Some discovered subdomains may not be immediately accessible or resolve to public IP addresses, necessitating further investigation or different attack vectors.
5. Use the appropriate DNS query tools to attempt retrieving the DNS zone file for the target domain. Some DNS record types might contain hidden or valuable information.
6. Once you’ve performed the zone transfer, examine all returned records carefully. Look for any entries that seem out of the ordinary or contain unusual data.

**Hints**:

* DNS Query Tools: Make sure to use tools specifically designed for DNS queries. Some tools are capable of requesting entire zone files, which can contain valuable information.
* Record Types: Don’t just look at the common records like `A` or `CNAME`. Pay special attention to `TXT` and `SOA` records, as these may contain more than just technical data.
* Filtering the Results: Large zone files can be overwhelming. Use filtering methods to focus on records that contain descriptive information.
* Understanding Zone Transfers: Look up how DNS zone transfers work and why certain records are included in a transfer. Some zones may have hidden content that is not immediately obvious.


### Step 1 — Confirm reachability

```bash
ping -c 3 web0x04.hbtn
# PING web0x04.hbtn (10.42.8.228) 56(84) bytes of data.
# 64 bytes from web0x04.hbtn (10.42.8.228): icmp_seq=1 ttl=126 time=125 ms
# 64 bytes from web0x04.hbtn (10.42.8.228): icmp_seq=2 ttl=126 time=31.2 ms
# 64 bytes from web0x04.hbtn (10.42.8.228): icmp_seq=3 ttl=126 time=20.3 ms
# 
# --- web0x04.hbtn ping statistics ---
# 3 packets transmitted, 3 received, 0% packet loss, time 2002ms
# rtt min/avg/max/mdev = 20.287/58.889/125.231/47.119 ms
```

### Step 2 — Query the target's DNS server directly

```bash
dig @web0x04.hbtn web0x04.hbtn SOA +short
# <Empty output>
```

- `dig` — Domain Information Groper, the standard tool for DNS queries. Far more informative than `nslookup` for this kind of work.
- `@web0x04.hbtn` — the `@` tells dig which DNS server to send the query to. If the lab runs its own DNS, this is how we reach it.
- `web0x04.hbtn` — the name we're asking about (the domain/zone itself).
- `SOA` — the record type. **Start Of Authority** is the record every zone must have; it names the **primary nameserver** and **admin** contact for the zone. Asking for it is a clean way to confirm "yes, this server is authoritative for this zone."
- `+short` — trims the output to just the answer, no verbose headers. Good for a quick confirmation.

**Possible outputs and how to read them:**

- **An SOA line appears** — something like `web0x04.hbtn. root.web0x04.hbtn. 1 ...`. This confirms the target is a working DNS server that's authoritative for our zone. That's exactly what we want: it means both Gobuster `dns` mode and a zone transfer are viable. The first field also tells us the **primary nameserver name**, which is useful context.
- **Empty output** — the server answered but returned no SOA. Unusual for a zone that exists; we'd investigate with a fuller (non-+short) query.
- `connection timed out; no servers could be reached` — nothing is listening for DNS on that box, or it's filtering port 53. If that happens, we'd reconsider whether DNS lives elsewhere.
- `REFUSED` / `SERVFAIL` — a server is there but declined the query; we'd probe further.


### Step 3 — Repeat the query without +short to see the full response


```bash
dig @web0x04.hbtn web0x04.hbtn SOA       

# ; <<>> DiG 9.20.22-1-Debian <<>> @web0x04.hbtn web0x04.hbtn SOA
# ; (1 server found)
# ;; global options: +cmd
# ;; Got answer:
# ;; ->>HEADER<<- opcode: QUERY, status: REFUSED, id: 44339
# ;; flags: qr rd; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
# ;; WARNING: recursion requested but not available
# 
# ;; OPT PSEUDOSECTION:
# ; EDNS: version: 0, flags:; udp: 1232
# ; COOKIE: 2d2e48f10723e32d010000006a60ac9f59d334703719563d (good)
# ; EDE: 18 (Prohibited)
# ;; QUESTION SECTION:
# ;web0x04.hbtn.                  IN      SOA
# 
# ;; Query time: 16 msec
# ;; SERVER: 10.42.8.228#53(web0x04.hbtn) (UDP)
# ;; WHEN: Wed Jul 22 07:42:22 EDT 2026
# ;; MSG SIZE  rcvd: 75
```

- The status: field in the `;; ->>HEADER<<-` line. This is the single most important thing:
  - `NOERROR` — the server processed the query fine. If the answer section is still empty, the zone may exist but the query needs adjusting, or the record lives under a different name.
  - `NXDOMAIN` — the server says this name doesn't exist. Would suggest the zone isn't what we think.
  - `REFUSED` — the server exists but won't answer us for this zone (sometimes a hint about access-control config).
  - `SERVFAIL` — the server broke trying to answer.

- `;; ANSWER SECTION:` — if an SOA is present, it'll be listed here with the primary nameserver and admin contact.
- `;; AUTHORITY SECTION:` — even when the answer is empty, this often reveals the authoritative nameserver(s) for the zone — valuable for aiming the later zone transfer.
- `;; SERVER:` confirms which IP dig actually queried, so we can be sure it hit `10.42.8.228` and not some fallback resolver.


### Our lab DNS setup:

- `status: REFUSED` plus `EDE: 18 (Prohibited)`. That Extended DNS Error code 18 literally means "Prohibited" — the server has an access-control policy (ACL) that blocks ordinary queries for this zone. It's not broken and it's not unreachable; it's deliberately refusing standard lookups.

Gobuster's `dns` mode works by doing a normal A-record lookup for each wordlist entry. If the server refuses ordinary queries like it just refused our SOA, brute-forcing would get refused for every single entry — a dead end.

The smart move is to test the zone transfer, because the ACL that blocks queries often doesn't cover AXFR.


### Step 4 — Attempt the zone transfer (AXFR)

```bash
dig @web0x04.hbtn web0x04.hbtn AXFR

# ; <<>> DiG 9.20.22-1-Debian <<>> @web0x04.hbtn web0x04.hbtn AXFR
# ; (1 server found)
# ;; global options: +cmd
# ; Transfer failed.
```
- `@web0x04.hbtn` — again, direct the request straight at the target's DNS server (`10.42.8.228`), not local PC resolver.
- `web0x04.hbtn` — the zone we want transferred.
- `AXFR` — **Asynchronous Full Zone Transfer**. This is a special request type meant for a secondary/slave nameserver to pull a complete copy of a zone from the primary. It returns every record in the zone at once — A, CNAME, TXT, SOA, NS, the lot. It's meant to be restricted to trusted servers; when it's left open to anyone, it hands an attacker the entire DNS map of the target. `dig` automatically uses TCP for this (zone transfers don't fit in a single UDP packet).


**The transfer failed** — but before we call this path dead, let's think about why. A very common reason AXFR fails on the domain name is that the transfer ACL is keyed to a **specific nameserver name**, not to `web0x04.hbtn` as a bare zone. In other words, the server may only honor a transfer request that's framed correctly, and it may only allow it from/for the host listed in its `NS` records.

We hit a wall asking the server about itself (`SOA` was `REFUSED`). But `NS` records are sometimes readable even when other query types are locked down, and knowing the authoritative nameserver's *name* gives us another host to aim at. So the next logical step is to ask the server which nameserver is authoritative for this zone.


### Step 5 — Find the zone's nameserver(s)

```bash
dig @web0x04.hbtn web0x04.hbtn NS

# ; <<>> DiG 9.20.22-1-Debian <<>> @web0x04.hbtn web0x04.hbtn NS
# ; (1 server found)
# ;; global options: +cmd
# ;; Got answer:
# ;; ->>HEADER<<- opcode: QUERY, status: REFUSED, id: 60395
# ;; flags: qr rd; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
# ;; WARNING: recursion requested but not available
# 
# ;; OPT PSEUDOSECTION:
# ; EDNS: version: 0, flags:; udp: 1232
# ; COOKIE: a88dfb1b75773968010000006a60b61b0784c82c141f51da (good)
# ; EDE: 18 (Prohibited)
# ;; QUESTION SECTION:
# ;web0x04.hbtn.                  IN      NS
# 
# ;; Query time: 28 msec
# ;; SERVER: 10.42.8.228#53(web0x04.hbtn) (UDP)
# ;; WHEN: Wed Jul 22 08:22:52 EDT 2026
# ;; MSG SIZE  rcvd: 75
```
- `NS` — the **Name Server** record type. Every zone lists one or more NS records naming the servers that are authoritative for it. This is different from the SOA query we tried — different record type, and the server's ACL may treat it differently.

**Answer**:

Same `REFUSED` / `EDE 18 (Prohibited)` — so the server is blanket-refusing metadata queries about the zone (SOA, NS, both prohibited). That's a strong, consistent signal: this box refuses queries by *zone name*.

That pattern points to a specific, well-known cause. When a nameserver refuses `web0x04.hbtn` but is genuinely serving DNS on port 53 (which it is — we're getting clean, fast responses, just refusals), the usual explanation is that **the ACL is scoped to the zone name**, and the query framing matters. There are two things worth checking before we conclude the transfer path is closed, and the task's own materials hint at both:

1. The wordlist includes `ns1` and `db`. `ns1` is almost certainly the authoritative nameserver's hostname, and the transfer ACL may be keyed to allow AXFR only when you request the zone the way the primary expects.
2. AXFR is a different operation from a standard query, and some servers that refuse `SOA`/`NS` lookups still permit `AXFR` — but only when pointed at the right server name rather than an alias.

Since resolving `ns1` by asking this server will likely just get refused again, the cleaner move is to go back to the AXFR but make dig show us *everything* about the attempt — including any server message explaining the refusal. The bare `; Transfer failed.` earlier hid the underlying status code.


### Step 6 — Retry the zone transfer with full diagnostics

```bash
dig @web0x04.hbtn web0x04.hbtn AXFR +noshort +comments +stats

# ; <<>> DiG 9.20.22-1-Debian <<>> @web0x04.hbtn web0x04.hbtn AXFR +noshort +comments +stats
# ; (1 server found)
# ;; global options: +cmd
# ;; Got answer:
# ;; ->>HEADER<<- opcode: QUERY, status: NOTAUTH, id: 25642
# ;; flags: qr; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1
# 
# ;; OPT PSEUDOSECTION:
# ; EDNS: version: 0, flags:; udp: 1232
# ; COOKIE: 3e21443e4bdf2655010000006a60b936bb257a7c8064086b (good)
# ; Transfer failed.
```
- `+comments` — force dig to print the header and comment lines even for AXFR (which normally suppresses them). This is what surfaces the actual `status:` behind "Transfer failed" — was it `REFUSED`, `NOTAUTH`, a TCP error, etc.
- `+stats` — print the query statistics footer (server queried, time, message size). Confirms it genuinely tried TCP against `10.42.8.228#53`.
- `+noshort` — ensure we're not in any abbreviated mode; show the complete exchange.

**Anser**:

`status: NOTAUTH`  \
That's a different error from the `REFUSED` we kept getting. `NOTAUTH` on an AXFR means: *"I am not authoritative for the zone name you asked me to transfer."* The server isn't refusing us by policy here — it's saying we asked for the **wrong zone name**. It doesn't serve `web0x04.hbtn` as a zone; it serves something else.

Lessons learned:

- `SOA web0x04.hbtn` → REFUSED
- `NS web0x04.hbtn` → REFUSED
- `AXFR web0x04.hbtn` → **NOTAUTH**

The server is authoritative for some zone, just not the one we named. `web0x04.hbtn` is the name we use to reach the box (via `/etc/hosts`), but the DNS zone it actually hosts is probably a parent domain — most likely **`hbtn`** itself. The subdomains in these labs typically live under the top-level lab zone.

So a possible fix is to attempt the transfer against the parent zone name.


### Step 7 — Attempt the zone transfer against the parent zone `hbtn`

```bash
dig @web0x04.hbtn hbtn AXFR +comments +stats


; <<>> DiG 9.20.22-1-Debian <<>> @web0x04.hbtn hbtn AXFR +comments +stats
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOTAUTH, id: 6913
;; flags: qr; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; COOKIE: d0c9cc26dc241583010000006a60bbc58ccad4ba84c96c22 (good)
; Transfer failed.
```

**Answer**:

`status: NOTAUTH`


We've spent a while probing zone names and it makes sense to switch tools and see whether Gobuster's approach gets traction.

One honest caveat so the result isn't confusing: Gobuster's `dns` mode works by doing ordinary A-record lookups for each wordlist entry (`lakeorion.web0x04.hbtn`, etc.). Those are exactly the kind of standard queries the server hit us with `REFUSED` / `Prohibited` on earlier. So there's a real chance Gobuster reports nothing found — not because the subdomains don't exist, but because the server refuses the lookups. That's still useful information: it confirms which path is open. And it's possible the ACL treats hostname lookups differently from the zone-metadata queries we tried, so it's genuinely worth a shot. Let's run it.


### Step 8 — Run Gobuster in dns mode

```bash
gobuster dns \
  --domain web0x04.hbtn \
  --resolver web0x04.hbtn \
  --wordlist dns_wordlist.txt \
  --threads 10 \

# ===============================================================
# Gobuster v3.8.2
# by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
# ===============================================================
# [+] Domain:     web0x04.hbtn
# [+] Threads:    10
# [+] Resolver:   web0x04.hbtn
# [+] Timeout:    1s
# [+] Wordlist:   dns_wordlist.txt
# ===============================================================
# Starting gobuster in DNS enumeration mode
# ===============================================================
# [ERROR] error on word lakelandledger.fl: lookup lakelandledger.fl.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeinsurveyor: lookup lakeinsurveyor.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakemary.place: lookup lakemary.place.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakelandcenter.place: lookup lakelandcenter.place.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word sub: lookup sub.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakekindred: lookup lakekindred.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakemaryprep.learning: lookup lakemaryprep.learning.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakemonsters: lookup lakemonsters.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lake-Michigan: lookup lake-Michigan.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
db.web0x04.hbtn 6.19.0.21
# [ERROR] error on word lakemaster.blog: lookup lakemaster.blog.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakenozori.web: lookup lakenozori.web.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeofthetorches: lookup lakeofthetorches.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word ns1: lookup ns1.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lake-of-the-ozarks: lookup lake-of-the-ozarks.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeoconeeacademy: lookup lakeoconeeacademy.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeorion: lookup lakeorion.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeoswegoor: lookup lakeoswegoor.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# Progress: 18 / 18 (100.00%)
# ===============================================================
# Finished
# ===============================================================
```

This is a breakthrough. Two things to note:

1. **We got a real hit**:
   ```bash
   db.web0x04.hbtn 6.19.0.21
   ```
2. **The errors reveal why almost everything else failed — and it's not an ACL**.
   ```bash
   lookup ...web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
   ```
   The `[fd17:625c:f037:2::3]` is an **IPv6 address** — and it is not our target. Gobuster's `--resolver web0x04.hbtn` got resolved to an IPv6 address (probably your system's default DNS resolver picked up from `/etc/resolv.conf`), and queries were being sent there, not to `10.42.8.228`. Those queries "misbehave" because that resolver isn't authoritative for the lab zone. The one success (`db`) likely slipped through on a path that did reach the right server.  \
   In short: Gobuster wasn't reliably talking to our target at all. The earlier `REFUSED` theory was overstated — the real problem this run is that the resolver wasn't pinned to the target's IP. Let's fix that by giving Gobuster the **IP and port explicitly**, so there's no name-resolution ambiguity.


### Step 9 — Re-run Gobuster with the resolver pinned to the target IP

```bash
gobuster dns --domain web0x04.hbtn --resolver 10.42.8.228:53 --wordlist dns_wordlist.txt --threads 5
# ===============================================================
# Gobuster v3.8.2
# by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
# ===============================================================
# [+] Domain:     web0x04.hbtn
# [+] Threads:    5
# [+] Resolver:   10.42.8.228:53
# [+] Timeout:    1s
# [+] Wordlist:   dns_wordlist.txt
# ===============================================================
# Starting gobuster in DNS enumeration mode
# ===============================================================
# [ERROR] error on word lakemary.place: lookup lakemary.place.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakelandcenter.place: lookup lakelandcenter.place.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakekindred: lookup lakekindred.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakelandledger.fl: lookup lakelandledger.fl.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeinsurveyor: lookup lakeinsurveyor.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakemaryprep.learning: lookup lakemaryprep.learning.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakemonsters: lookup lakemonsters.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lake-Michigan: lookup lake-Michigan.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word sub: lookup sub.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakemaster.blog: lookup lakemaster.blog.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
db.web0x04.hbtn 6.19.0.21
# [ERROR] error on word lakenozori.web: lookup lakenozori.web.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lake-of-the-ozarks: lookup lake-of-the-ozarks.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeoconeeacademy: lookup lakeoconeeacademy.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeofthetorches: lookup lakeofthetorches.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeorion: lookup lakeorion.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word ns1: lookup ns1.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# [ERROR] error on word lakeoswegoor: lookup lakeoswegoor.web0x04.hbtn. on [fd17:625c:f037:2::3]:53: server misbehaving
# Progress: 18 / 18 (100.00%)
# ===============================================================
# Finished
# ===============================================================


# still IPv6 resolver, let's check /etc/resolv.conf
cat /etc/resolv.conf
# # Generated by NetworkManager
# search fritz.box
# nameserver 10.0.2.3
# nameserver fd17:625c:f037:2::3


# and let's check /etc/hosts
cat /etc/hosts
# 127.0.0.1       localhost
# 127.0.1.1       kali
# ::1             localhost ip6-localhost ip6-loopback
# ff02::1         ip6-allnodes
# ff02::2         ip6-allrouters
# 
# # 10.42.181.227 web0x01.hbtn
# # 10.42.105.161 web0x02.hbtn
# 
# 10.42.8.228  web0x04.hbtn
```

Giving to Gobuster `--resolver 10.42.8.228:53` still didn't fixed invoking the IPv6 resolver.

- We set `--resolver 10.42.8.228:53` ✓ (Gobuster even confirms it in the header)
- But the errors still say on `[fd17:625c:f037:2::3]:53` — which is precisely the IPv6 `nameserver` line in the local `/etc/resolv.conf`.

So Gobuster **ignored our resolver for most words and fell back to the system resolver**. This is a known quirk: when a wordlist entry itself contains a dot (`lakemary.place`, `lakelandledger.fl`, `lakemaryprep.learning`, `lakenozori.web`), and for certain lookup paths, Gobuster's resolver hands the query off to the OS resolver, which then uses `resolv.conf` — hitting that IPv6 server that knows nothing about the lab zone → "server misbehaving."

Rather than keep fighting Gobuster's fallback behavior, the cleanest fix is to **temporarily neutralize the IPv6 resolver** so nothing can fall back to it. Then every query has only one place to go: our target.


### Step 10 — Temporarily comment out the IPv6 resolver, then re-run

```bash
cat /etc/resolv.conf
# # Generated by NetworkManager
# search fritz.box
# nameserver 10.0.2.3
# nameserver fd17:625c:f037:2::3


sudo sed -i.bak 's/^nameserver fd17:625c:f037:2::3/#&/' /etc/resolv.conf && cat /etc/resolv.conf

# # Generated by NetworkManager
# search fritz.box
# nameserver 10.0.2.3
# #nameserver fd17:625c:f037:2::3
```


### Step 11 — Re-run Gobuster with the clean resolver setup

```bash
gobuster dns --domain web0x04.hbtn --resolver 10.42.8.228:53 --wordlist dns_wordlist.txt --threads 5           
# ===============================================================
# Gobuster v3.8.2
# by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
# ===============================================================
# [+] Domain:     web0x04.hbtn
# [+] Threads:    5
# [+] Resolver:   10.42.8.228:53
# [+] Timeout:    1s
# [+] Wordlist:   dns_wordlist.txt
# ===============================================================
# Starting gobuster in DNS enumeration mode
# ===============================================================
# [ERROR] error on word lakelandcenter.place: lookup lakelandcenter.place.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakeinsurveyor: lookup lakeinsurveyor.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakelandledger.fl: lookup lakelandledger.fl.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakekindred: lookup lakekindred.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakemary.place: lookup lakemary.place.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakemaryprep.learning: lookup lakemaryprep.learning.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word sub: lookup sub.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakemaster.blog: lookup lakemaster.blog.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lake-Michigan: lookup lake-Michigan.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakemonsters: lookup lakemonsters.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
db.web0x04.hbtn 6.19.0.21
# [ERROR] error on word lakeoconeeacademy: lookup lakeoconeeacademy.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakeofthetorches: lookup lakeofthetorches.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lake-of-the-ozarks: lookup lake-of-the-ozarks.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakenozori.web: lookup lakenozori.web.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakeorion: lookup lakeorion.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word lakeoswegoor: lookup lakeoswegoor.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# [ERROR] error on word ns1: lookup ns1.web0x04.hbtn. on 10.0.2.3:53: server misbehaving
# Progress: 18 / 18 (100.00%)
# ===============================================================
# Finished
# ===============================================================

cat /etc/resolv.conf
# Generated by NetworkManager
search fritz.box
nameserver 10.0.2.3
#nameserver fd17:625c:f037:2::3
```

The errors moved — they now say on `10.0.2.3:53` instead of the IPv6 address. That confirms two things:

1. **Gobuster is ignoring our `--resolver` for these words entirely** and using the OS resolver (`resolv.conf`). We proved it by commenting out the IPv6 line — the errors dutifully followed to the next nameserver in the resolv.conf: `10.0.2.3`. So `--resolver 10.42.8.228:53` is not being honored for the failing lookups. This is a real Gobuster behavior/bug in this version, not something we're misconfiguring.
2. `db.web0x04.hbtn → 6.19.0.21` resolved correctly every single time. Three runs, same clean hit. That's a genuine, confirmed subdomain — and notably, the query that does work is going to the right place, while the failing ones leak to the OS resolver.

Rather than keep wrestling it, let's **bypass Gobuster and do the enumeration with `dig` directly**, which we already know sends queries exactly where we tell it (we saw earlier `dig @web0x04.hbtn` hit `10.42.8.228#53` correctly). A tiny shell loop does the same brute-force, but with a resolver we fully control — no fallback, no leakage.


### Step 12 — Brute-force the subdomains with a dig loop

```bash
while read -r sub; do
  ip=$(dig +short @10.42.8.228 "${sub}.web0x04.hbtn" A)
  [ -n "$ip" ] && echo "FOUND: ${sub}.web0x04.hbtn -> ${ip}"
done < dns_wordlist.txt
# FOUND: db.web0x04.hbtn -> 6.19.0.21
```

**This happens in the script:**:
- `while read -r sub; do ... done < dns_wordlist.txt` — reads the wordlist one line at a time into the variable `sub`. `-r` prevents backslash mangling.
- `dig +short @10.42.8.228 "${sub}.web0x04.hbtn" A` — for each word, ask the **target's DNS server directly** (`@10.42.8.228` — literal IP, zero ambiguity, no OS-resolver fallback possible) for the **A** record of `word.web0x04.hbtn`. `+short` prints just the IP if it exists, nothing if it doesn't.
- `ip=$(...)` — capture that result.
- `[ -n "$ip" ] && echo "FOUND: ..."` — only print when the result is non-empty, i.e. only for subdomains that actually resolve. This filters out all the non-existent ones silently.


**Result**:

- `db` is the only host in our wordlist that exists in the zone
- The IP `6.19.0.21` is a bit unusual — it's a public-range address, not the `10.42.x.x` lab range. The task even warned: *"Some discovered subdomains may not resolve to public IP addresses, necessitating further investigation."*  \
That `db` record may be a decoy, or it may point somewhere we can't directly reach. Either way, the flag task says the target page has `Task #5` **as the website title** and a `Flag` **as content** — so what matters is which host serves that page, not just which names resolve.

The most direct way to find out: actually request the page. Since `db.web0x04.hbtn` resolves to `6.19.0.21` (which we may not be able to reach), but the service we care about is almost certainly on the box we can reach (`10.42.8.228`), the cleanest test is to ask that server for the db vhost by setting the Host header explicitly.


### Step 13 — Fetch the db subdomain's page and check its title

```bash
curl -v -H "Host: db.web0x04.hbtn" http://10.42.8.228/
# *   Trying 10.42.8.228:80...
# * Established connection to 10.42.8.228 (10.42.8.228 port 80) from 10.8.0.2 port 51794 
# * using HTTP/1.x
# > GET / HTTP/1.1
# > Host: db.web0x04.hbtn
# > User-Agent: curl/8.19.0
# > Accept: */*
# > 
# * Request completely sent off
# < HTTP/1.1 404 Not Found
# < Server: nginx/1.22.1
# < Date: Wed, 22 Jul 2026 14:13:11 GMT
# < Content-Type: text/html
# < Content-Length: 153
# < Connection: keep-alive
# < 
# <html>
# <head><title>404 Not Found</title></head>
# <body>
# <center><h1>404 Not Found</h1></center>
# <hr><center>nginx/1.22.1</center>
# </body>
# </html>
# * Connection #0 to host 10.42.8.228:80 left intact
```

Useful result, even though it's a 404. Let's read it carefully rather than move on:

- We *reached an nginx web server* on `10.42.8.228:80` and got a valid HTTP response. So there is a webserver here.
- The `Host: db.web0x04.hbtn` vhost returned **404 Not Found** — but note this is nginx's default 404, not a custom page. That tells us nginx has no server block matching `db.web0x04.hbtn`, so it fell through to a default that serves nothing. In other words, db resolves in DNS but isn't configured as a website on this box.


### Step 14 — Query TXT/ANY on the known-good host to test what's readable

```bash
dig @10.42.8.228 db.web0x04.hbtn ANY +noall +answer +additional
# db.web0x04.hbtn.        604800  IN      A       6.19.0.21
# db.web0x04.hbtn.        604800  IN      SOA     ns1.web0x04.hbtn. admin.web0x04.hbtn. 1 604800 86400 2419200 604800
# db.web0x04.hbtn.        604800  IN      NS      ns1.web0x04.hbtn.
```

- `@10.42.8.228` — query the target server directly by IP (the path we've verified works).
- `db.web0x04.hbtn` — a name we **know** the server answers for. Using a known-good name isolates "does ANY/TXT work" from "does this name exist."
- `ANY` — ask for all record types the server will return for this name in one go: A, TXT, CNAME, etc. On servers that don't restrict it, ANY is a quick way to surface TXT records that might carry descriptive hints (exactly what the task's hints point to).
- `+noall +answer +additional` — show only the answer and additional sections, no header noise. The additional section sometimes carries extra records (like the target of a CNAME) that hint at other hostnames.

**Answer**:

1. **The authoritative nameserver is `ns1.web0x04.hbtn`** — and the SOA is served under `db.web0x04.hbtn`. This is unusual and telling: it strongly implies the zone the server is authoritative for is literally **`db.web0x04.hbtn`**, not `web0x04.hbtn`. That's why every AXFR we tried returned `NOTAUTH` — the real zone name has the `db.` prefix. The wordlist entry `db` wasn't a host to browse; it was pointing at the zone name all along.
2. The SOA/NS are readable here, so the refusal really was apex-only for `web0x04.hbtn`.

So the zone we should transfer is `db.web0x04.hbtn`. Let's do exactly that.


### Step 15 — Zone transfer against the real zone db.web0x04.hbtn

```bash
dig @10.42.8.228 db.web0x04.hbtn AXFR       

# ; <<>> DiG 9.20.22-1-Debian <<>> @10.42.8.228 db.web0x04.hbtn AXFR
# ; (1 server found)
# ;; global options: +cmd
# db.web0x04.hbtn.        604800  IN      SOA     ns1.web0x04.hbtn. admin.web0x04.hbtn. 1 604800 86400 2419200 604800
# db.web0x04.hbtn.        604800  IN      A       6.19.0.21
# db.web0x04.hbtn.        604800  IN      NS      ns1.web0x04.hbtn.
# lakemaryprep.learning.db.web0x04.hbtn. 604800 IN TXT "Holberton Sec Lab - FLAG: 7397b6974da78407f55de711eb04f194"
# lakemaryprep.learning.db.web0x04.hbtn. 604800 IN A 127.0.0.1
# ns1.db.web0x04.hbtn.    604800  IN      A       127.0.0.1
# db.web0x04.hbtn.        604800  IN      SOA     ns1.web0x04.hbtn. admin.web0x04.hbtn. 1 604800 86400 2419200 604800
# ;; Query time: 19 msec
# ;; SERVER: 10.42.8.228#53(10.42.8.228) (TCP)
# ;; WHEN: Wed Jul 22 10:33:11 EDT 2026
# ;; XFR size: 7 records (messages 1, bytes 328)
```

### Step 16 - Save the Flag

```bash
echo 7397b6974da78407f55de711eb04f194 > 5-flag.txt

cat 5-flag.txt

git add .
git commit -m "5-flag.txt"
git push
```


## 4. FFuf Series - Subdomain Fuzzing Frenzy

Explore the web infrastructure by using ffuf to brute-force subdomains (virtual hosts) on the target server.
Discover hidden subdomains that might contain important information, such as a flag or access to alternative environments.

Target Domain: `web0x04.hbtn`

### Use `ffuf` tool

**Useful Instructions**

1. Wordlist Preparation:
        Use a wordlist tailored to subdomain enumeration. Make sure it includes common subdomains, environment names, and other relevant terms.
2. Fuzz Subdomains:
         Run `ffuf` to fuzz for potential subdomains of the target domain. Pay attention to the responses and any unusual or unexpected status codes.
3. Examine Responses:
         Analyze the output and investigate any discovered subdomains.
         Some may return useful content that could contain sensitive information, such as a flag or further clues for your reconnaissance.


**Hints**

* Look for subdomains that produce different or unexpected HTTP status codes.
* If you find an accessible subdomain, carefully inspect the content for any hidden information.
* Some subdomains might seem unimportant but can still contain critical clues or data.


### Step 1 — Locate a suitable SecLists subdomain wordlist

```bash
ls -la /usr/share/seclists/Discovery/DNS/ 2>/dev/null | grep -iE "subdomain|top1million|5000|110000"        
-rw-r--r-- 1 root root  1426217 Sep 19  2025 bitquark-subdomains-top100000.txt
-rw-r--r-- 1 root root 25319380 Sep 19  2025 bug-bounty-program-subdomains-trickest-inventory.txt
-rw-r--r-- 1 root root  8285473 Sep 19  2025 combined_subdomains.txt
-rw-r--r-- 1 root root   605423 Sep 19  2025 deepmagic.com-prefixes-top50000.txt
-rw-r--r-- 1 root root   155984 Sep 19  2025 italian-subdomains.txt
-rw-r--r-- 1 root root 51558245 Sep 19  2025 n0kovo_subdomains.txt
-rw-r--r-- 1 root root  5984338 Sep 19  2025 shubs-subdomains.txt
-rw-r--r-- 1 root root    55958 Sep 19  2025 subdomains-spanish.txt
-rw-r--r-- 1 root root  1115646 Sep 19  2025 subdomains-top1million-110000.txt
-rw-r--r-- 1 root root   148689 Sep 19  2025 subdomains-top1million-20000.txt
-rw-r--r-- 1 root root    33566 Sep 19  2025 subdomains-top1million-5000.txt
```

### Step 2 — Measure the baseline (bogus vhost) response

```bash
curl -s -o /dev/null -w "status=%{http_code} size=%{size_download}\n" -H "Host: definitelynotreal.web0x04.hbtn" http://10.42.8.228/

# status=404 size=153

```

**Inputs**:

- `curl -s` — silent (no progress meter).
- `-o /dev/null` — discard the actual page body; we only care about the metrics, not the HTML.
- `-w "status=%{http_code} size=%{size_download}\n"` — write-out format: print just the HTTP status code and the exact byte size of the response body. These two numbers are what ffuf filters on.
- `-H "Host: definitelynotreal.web0x04.hbtn"` — send a deliberately fake vhost. This forces nginx into its default/fallback response — precisely the baseline we want to characterize and later exclude.
- `http://10.42.8.228/` — the reachable target IP.


**Possible outputs and how to read them**:

- **`status=404 size=153`** (or similar) — this is what we expect from the earlier 404 we saw. That `153` is the magic number: we'll tell ffuf `-fs 153` (filter size 153) so it hides every response of that exact size, leaving only vhosts that behave differently. A real subdomain's page will have a different size and slip through the filter.
- **A redirect (`301`/`302`) or a different size** — then the baseline is different and we'd filter on that value instead. Either way, we now know the number to exclude.
- **`status=200`** for a fake host — would mean nginx serves a catch-all site for unknown hosts; we'd then filter on that size and watch for status/size deviations instead.


### Step 3 — Fuzz virtual hosts with ffuf

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -H "Host: FUZZ.web0x04.hbtn" \
     -u http://10.42.8.228/ \
     -fs 153 \
     -t 40

#         /'___\  /'___\           /'___\       
#        /\ \__/ /\ \__/  __  __  /\ \__/       
#        \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
#         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
#          \ \_\   \ \_\  \ \____/  \ \_\       
#           \/_/    \/_/   \/___/    \/_/       
# 
#        v2.1.0-dev
# ________________________________________________
# 
#  :: Method           : GET
#  :: URL              : http://10.42.8.228/
#  :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
#  :: Header           : Host: FUZZ.web0x04.hbtn
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
#  :: Filter           : Response size: 153
# ________________________________________________
# 
sub                     [Status: 200, Size: 56, Words: 3, Lines: 2, Duration: 74ms]
# :: Progress: [4989/4989] :: Job [1/1] :: 296 req/sec :: Duration: [0:00:18] :: Errors: 0 ::
```

We got a hit:
```bash
sub                     [Status: 200, Size: 56, Words: 3, Lines: 2, Duration: 74ms]
```


### Step 4 — Fetch the sub vhost's content


```bash
curl -s -H "Host: sub.web0x04.hbtn" http://10.42.8.228/

# Congratulations! FLAG: c8ae24a662a495287194f61f4976b98e
```

### Step 5 - Save the flag

```bash
echo c8ae24a662a495287194f61f4976b98e > 6-flag.txt

cat 6-flag.txt

git add .
git commit -m "6-flag.txt"
git push
```