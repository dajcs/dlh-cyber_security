# Threat Model: E-commerce Platform

**System under analysis:** E-commerce platform with React frontend, Node.js API backend, PostgreSQL database, and Stripe payment integration.

**Scope of user actions:**

| Action | Authentication |
|---|---|
| Browse products | Not required |
| Add items to cart | Not required |
| Checkout and pay | Required |
| View order history | Required |

---

## 1. STRIDE Threats for the Checkout Process

STRIDE is a mnemonic covering six threat categories: **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, and **E**levation of privilege. Below are three concrete threats to the checkout flow, drawn from different STRIDE categories.

### Threat 1 — Tampering: Client-side price manipulation

- **STRIDE category:** Tampering
- **Threat description:** The React frontend sends cart contents to the Node.js API at checkout, including item prices and quantities. If the backend trusts the price values submitted in the request body, an attacker can intercept or modify the request (via browser dev tools, a proxy like Burp Suite, or a crafted API call) and change a $500 item to $5.00, apply an unauthorized discount, or set a negative quantity to generate a credit.
- **Potential impact:** Direct financial loss on every fraudulent order, inventory loss, and corrupted order/revenue records. At scale this can be automated, multiplying the damage quickly.
- **Suggested mitigation:** Never trust price data from the client. The backend should treat the client request as a list of product IDs and quantities only, then re-derive every price server-side from the authoritative product catalog in PostgreSQL. Compute the order total on the server, validate quantities are positive integers within stock limits, and pass the server-calculated amount to Stripe. Optionally reconcile the charged amount against the recomputed total before capture.

### Threat 2 — Information Disclosure: Interception of payment/PII data

- **STRIDE category:** Information Disclosure
- **Threat description:** Checkout transmits sensitive data — billing details, shipping address, email, and payment tokens. If any leg of communication (browser → API, API → Stripe, or internal service calls) is unencrypted, uses weak TLS, or if card data is ever handled directly by the Node.js backend, an attacker on the network path (public Wi-Fi, compromised proxy, misconfigured load balancer) can capture it. Verbose error logging that records request bodies can also leak this data to logs.
- **Potential impact:** Exposure of customer PII and payment data, PCI-DSS violations, regulatory penalties (GDPR/PCI), fraud against customers, and reputational damage.
- **Suggested mitigation:** Enforce TLS 1.2+ everywhere with HSTS; redirect all HTTP to HTTPS. Use Stripe's client-side tokenization (Stripe Elements / Payment Element) so raw card numbers never touch your backend — the browser exchanges card data directly with Stripe for a token, and only the token reaches your API. This keeps you out of most PCI scope. Scrub sensitive fields from logs, and encrypt PII at rest in PostgreSQL.

### Threat 3 — Spoofing: Session hijacking / authenticating as another user

- **STRIDE category:** Spoofing
- **Threat description:** Checkout requires authentication. If session tokens (JWTs or session cookies) are weakly protected — stored in a way accessible to XSS, transmitted without `Secure`/`HttpOnly` flags, long-lived without rotation, or predictable — an attacker can steal or forge a token and impersonate a legitimate user, placing orders, using saved payment methods, or accessing their identity during checkout.
- **Potential impact:** Fraudulent purchases charged to a victim, theft of stored addresses/payment methods, and loss of accountability for who placed an order.
- **Suggested mitigation:** Use strong, random session identifiers or properly signed JWTs with short expiry and refresh rotation. Set cookies with `HttpOnly`, `Secure`, and `SameSite=Strict/Lax`. Mitigate XSS (the primary token-theft vector) with output encoding, a strict Content Security Policy, and input validation. Re-authenticate or require step-up verification (e.g., re-entering CVV or 3-D Secure) for high-value transactions.

### Bonus: mapping the remaining STRIDE categories

For completeness, the other three categories also apply to checkout:

- **Repudiation:** A user denies placing an order. Mitigate with tamper-evident audit logs, signed transaction records, and Stripe's payment receipts.
- **Denial of Service:** Automated bots flood the checkout/payment endpoint. Mitigate with rate limiting, CAPTCHA on suspicious traffic, and idempotency keys on payment requests.
- **Elevation of Privilege:** A regular user accesses admin-only order-management or refund functions. Mitigate with server-side role-based authorization checks on every endpoint.

---

## 2. Trust Boundaries

A trust boundary is any point where data or requests move between components that operate at different privilege or trust levels. Everything crossing a boundary must be authenticated, authorized, and validated. This system has several.

**Boundary 1 — User's browser (untrusted) ↔ Node.js API backend (trusted).**
This is the primary and most important boundary. The React frontend and everything in the browser is fully controllable by the user: they can read source, modify requests, disable client-side validation, and replay calls. All data arriving at the API must be treated as hostile and re-validated server-side (this is exactly why client-side price data cannot be trusted). Authentication and authorization are enforced here.

**Boundary 2 — Node.js API backend (trusted) ↔ PostgreSQL database (trusted, but distinct privilege zone).**
The application and the database are separate components, typically on separate hosts or network segments. The database holds the crown jewels (user records, orders, hashed credentials). Crossing this boundary safely requires parameterized queries (to prevent SQL injection), least-privilege database credentials (the app account should not have superuser or schema-drop rights), network segmentation so the DB is not internet-reachable, and encrypted connections.

**Boundary 3 — Node.js API backend ↔ Stripe (external third-party service).**
Data leaves your infrastructure entirely and travels to a third party over the internet. This boundary requires TLS, secure storage of the Stripe secret API key (in a secrets manager, never in source or client code), and verification of inbound Stripe webhooks using signature validation so an attacker cannot forge "payment succeeded" events.

**Additional boundaries worth noting:**

- **Anonymous zone ↔ authenticated zone:** Within the app itself, browsing and cart are unauthenticated, while checkout and order history require a logged-in identity. The transition from anonymous to authenticated (login) is a trust boundary where session establishment and authorization begin.
- **Internet ↔ internal network (perimeter):** The load balancer / API gateway / reverse proxy marks where public internet traffic enters your controlled infrastructure — a natural place for TLS termination, WAF rules, and rate limiting.

---

## 3. DREAD Rating: SQL Injection in Product Search

DREAD scores a threat across five factors, each rated 1–10, then averaged (or summed) for an overall risk rating. Here we assess **SQL injection in the product search functionality**, an unauthenticated feature that likely builds a query from user-supplied search terms.

| Factor | Score | Justification |
|---|---|---|
| **Damage** | 9 | A successful injection against PostgreSQL can dump the entire database — user accounts, hashed passwords, order history, PII — and potentially modify or delete data. If the DB account is over-privileged, it can escalate toward the OS. This is catastrophic damage. |
| **Reproducibility** | 9 | Once a working payload is found, it works reliably every time. The vulnerability is deterministic, requiring no special timing or race conditions. |
| **Exploitability** | 8 | Product search is unauthenticated and publicly reachable, so no credentials are needed. Injection is well-understood and automated tooling (e.g., sqlmap) can find and exploit it with modest skill. It's slightly below max only because modern ORMs/parameterization may already be partially in place, and detection may require some probing. |
| **Affected Users** | 10 | A full data breach exposes *every* registered user's data at once, not a single account. All customers are potentially affected, so this scores at the maximum. |
| **Discoverability** | 8 | Search is one of the most obvious, easily located features on any e-commerce site, and injectable search fields are a top target for both automated scanners and manual testers. Error-based leaks make it easy to confirm. Slightly below max since blind/boolean injection can take more effort to discover than error-based. |

**Overall DREAD score:** (9 + 9 + 8 + 10 + 8) / 5 = **44 / 50 → average 8.8 / 10**

**Rating: HIGH / Critical.** This combination of severe damage, mass user impact, high reproducibility, and an easily discoverable unauthenticated attack surface makes SQL injection in product search a top-priority risk.

**Primary mitigation:** Use parameterized queries / prepared statements (or a well-vetted ORM/query builder) for *all* database access — never concatenate user input into SQL strings. Apply strict input validation and allowlisting on search parameters, run the application under a least-privilege database account, and deploy a WAF as defense-in-depth. Ensure database errors are not returned verbatim to the client (to prevent error-based enumeration).

---

*Note on DREAD:* DREAD scoring is inherently subjective and different assessors may reasonably assign scores a point or two apart. Its value is in enabling consistent relative comparison of threats within the same organization, using a shared rubric — not in producing an objectively precise number.
