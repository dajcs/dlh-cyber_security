# Server-Side Request Forgery

## [Task 0. Unlocking security, one exploit at a time!](./task0.md)
## [Task 1. Is our security a fortress or a sieve? Let's SSRF and find out!](./task1.md)
## [Task 2. Exploit SSRF to breach our security!](./task2.md)
## [Task 3. New security layers in town! Let's break 'em in and see if they hold up!](./task3.md)
## [Task 4. Let's see if our invoice generator spills the beans and lets you into the admin zone!](./task4.md)



## SSRF Challenge Series — Summary (Tasks 0–4)

| Task | Filter Strength | Bypass Technique |
|------|-----------------|-------------------|
| **0** | None — `articleApi` fetched the user-supplied URL with no validation at all. | Pointed `articleApi` directly at `http://127.0.0.1:3000/admin/list-of-items`, reading the internal admin page straight from the raw SSRF response. |
| **1** | Blocklist on the literal string `127.0.0.1`. | Supplied the **decimal IP representation** (`2130706433`) — same address, different encoding, which the blocklist didn't normalize before comparing. |
| **2** | Blocklist extended to reject decimal/IP-literal hosts entirely (allowlist-like hostname check). | Found the **real internal hostname** (`discount.newshop.tn`) leaked in the default form value, then simply changed the *path* from `check-reduction` to `/admin/list-of-items` — the host passed validation, but nothing checked where the path led. |
| **3** | Strict hostname allowlist: only the exact public-facing domain (`web0x08.hbtn`) is accepted; IP literals, decimal, userinfo (`@`) tricks, and substring spoofing all correctly rejected. | **SSRF via Open Redirect**: pointed `articleApi` at the app's own "Next Product" redirect feature (which lives on the whitelisted host, so it passes the filter), and that feature's `path` parameter — a totally unvalidated open redirect — sent the actual internal fetch to `127.0.0.1:8080/admin`. The filter validated the *entry* URL, not where it ultimately redirected. |
| **4** | No network allowlist at all for this feature — the "protection" was architectural isolation (PDF rendering happens in a separate process/container), not input validation. | **HTML injection → SSRF via PDF renderer**: the `handle` (Customer name) field was inserted unescaped into the invoice HTML before conversion by `wkhtmltopdf`. Injecting `<iframe src="http://127.0.0.1/admin/list-of-items">` made the *renderer itself* issue the internal request and paint the result directly into the output PDF — no HTTP response reflection needed at all. |

### Key takeaway

Every "fix" in this series patched the **previous** bypass but validated the wrong thing: a literal string, a single encoding, or only the *first hop* of a request. None of them validated what actually mattered — **the real destination of the final network connection** — and none of them considered that user input can reach the network in ways other than the one obvious parameter. The lesson compounds across all five tasks: SSRF defenses built as string blocklists/allowlists on a single input field are inherently incomplete. Robust protection requires enforcing destination restrictions at the network layer (egress rules, not string matching), disabling automatic redirect-following for any SSRF-prone fetch, and treating *every* code path that can trigger an outbound request — including "unrelated" features like template rendering, PDF/image generation, or webhooks — as part of the same attack surface.
