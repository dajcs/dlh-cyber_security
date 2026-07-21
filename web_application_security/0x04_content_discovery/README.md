# Content Discovery


## Task 0. Manual Discovery - Secrets in Plain Sight

Your goal is to uncover a hidden flag by thoroughly exploring the site's structure.

Use all available discovery methods, including analyzing files such as `robots.txt`, `sitemap.xml`, and `favicon.ico`

- Target Machine: `cyber_websec_0x04`
- Target Endpoint: `http://web0x04.hbtn/`
- [Dir Word List](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt)
- [WP Word List](https://github.com/test0001-star/0x04/blob/main/WP_Word_list.txt)
- start sandbox `cyber_websec_0x04`
  - Network Information  - Ip: `10.42.19.152`
  - add ip to `/etc/hosts`:
  ```bash
  sudo bash -c "echo '10.42.19.152  web0x04.hbtn' > /etc/hosts"
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
This contains common .php filenames (294) and we dowloaded it in the current directory as `common.php.txt`

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

the `hiddenflag.php` sounds promising, let's have a visit to
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

- nope
- double checking the **Repo**:
  - GitHub repository: `dlh-cyber_security`
  - Directory: `web_application_security/0x04_content_discovery`
  - File: `4-flag.txt`

- another try

```bash
cp 2-flag.txt 4-flag.txt

git add .
git commit -m "4-flag.txt"
git push
```


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

cat 2-flag.txt 4-flag.txt
# 50a99edc175c95e7cfb9a8a56a2dc3de
# 50a99edc175c95e7cfb9a8a56a2dc3de


# turns out earlier I forgot to run the cp 2-flag.txt 4-flag.txt
git add .
git commit -m "2-flag.txt + 4-flag.txt"
git push
```