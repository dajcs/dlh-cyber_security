# Content Discovery


## Task 0. Manual Discovery - Secrets in Plain Sight

Your goal is to uncover a hidden flag by thoroughly exploring the site's structure.

Use all available discovery methods, including analyzing files such as `robots.txt`, `sitemap.xml`, and `favicon.ico`

- Target Machine: `cyber_websec_0x04`
- Target Endpoint: `http://web0x04.hbtn/`
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
```

### Double-check

The correction check failed at `Check 0` - this means even the directory/README.md wasn't found.

- GitHub repository: dlh-cyber_security
- Directory: web_application_security/0x04_content_discovery
- File: 0-flag.txt

```bash
ls -l ~/dlh-cyber_security/web_application_security/0x04_content_discovery/README.md
-rw-rw-r-- 1 kali kali 3287 Jul 21 06:25 /home/kali/dlh-cyber_security/web_application_security/0x04_content_discovery/README.md

ls -l ~/dlh-cyber_security/web_application_security/0x04_content_discovery/0-flag.txt
-rw-rw-r-- 1 kali kali 33 Jul 21 06:22 /home/kali/dlh-cyber_security/web_application_security/0x04_content_discovery/0-flag.txt

```
