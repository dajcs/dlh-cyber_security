Here is the extracted content from the PDF, converted into a clean Markdown format:

# XSS

*For this project, we expect you to look at these concepts:*
* Client-Side Exploitation (/concepts/1539)

* **Novice**
* **By:** Youssef Belhadj
* **Weight:** 1
* Your score will be updated as you progress.
* Manual QA review must be done (request it when you are done with the project)

## Introduction

> "The most dangerous vulnerabilities are not the ones that crash systems, they're the ones that let attackers become the user." — Jeremiah Grossman

Welcome to the Client-Side Exploitation Layer. In previous modules, you learned how to protect user data and sanitize inputs. Now, you will learn to think like an attacker who does not need to hack the server, they hack the browser instead.

Before we start, make sure to:
* Carefully read the concept page Client-Side Exploitation (/rltoken/VxUeCB0QhugvB9utZ4SXgQ)

**How to use it:**
* **The Goal:** You are a penetration tester hired to exploit NexusShop. Your objective is to capture FLAGS by chaining XSS attacks.
* **The Process:** Do not guess. Follow the 7-Step Attack Loop (Probe → Context → Confirm → Execute) to methodically find vulnerabilities.
* **Troubleshooting:** If your payloads fail, consult the Common Failure Modes table before asking for help.

---

## Resources

**Read or Watch:**
* OWASP XSS Prevention Cheat Sheet (/rltoken/T0SwzPLipNE2s-SZ6_rckg)
* PortSwigger Web Security Academy - XSS (/rltoken/1wqZgnpYkSdG5xMUkA-RrA)
* LiveOverflow - XSS Explained (YouTube) (/rltoken/apmueP7_tSdGaeKplwP2ZA)
* Content Security Policy (CSP) - MDN (/rltoken/XExx8oP-G-gTfmOM7CHh1w)
* DOM-based XSS - OWASP (/rltoken/rrkaD9Ep4kRcBa_ePqF5Hw)

**Tools Documentation:**
* Browser Developer Tools (/rltoken/HkbZ7MwczvFYr1cmhetQ0g)
* Burp Suite - XSS Testing (/rltoken/ud_1CWgTeVfkCPJ_jWlQ-w)
* XSS Payload Lists (/rltoken/T099S3bXcQXkTd31UkBZ1Q)

**Reference Materials:**
* OWASP Testing Guide v4.2 - XSS (/rltoken/FZc5d6WjZOASZHy_WVNi5w)
* CWE-79: Improper Neutralization of Input During Web Page Generation (/rltoken/V7t5vjUwSWa0ecWFhjptHQ)
* HackerOne XSS Reports (Public) (/rltoken/d-mQIo6t6oYpmLqekbXduA)

---

## Learning Objectives
By the end of this project, you will be able to explain to anyone, **without the help of Google**:

**XSS Fundamentals**
* Differentiate between Reflected, Stored, and DOM-based Cross-Site Scripting.
* Explain how unsanitized input leads to code execution and why output encoding differs from input validation.

**Reflected XSS Techniques**
* **Reflected:** Break out of HTML attributes and JavaScript contexts using URL parameters and filter evasion.
* **Stored:** Persist malicious scripts in user-generated content to harvest credentials and log keystrokes.
* **DOM-based:** Identify and exploit client-side sources (e.g., `location.hash`, `postMessage`) and sinks (e.g., `innerHTML`, `eval`).

**Security Bypass Techniques**
* Evade filters using case manipulation, encoding schemes, and Unicode normalization.
* Bypass Content Security Policy (CSP) by exploiting misconfigurations like `unsafe-inline` and JSONP endpoints.

**Professional Skills**
* Document findings, calculate business impact, and recommend effective mitigations within a formal penetration test report.

---

## Requirements

### Environment
* Modern web browser with Developer Tools (Chrome/Firefox recommended)
* Access to the NexusShop application at `http://web0x0c.hbtn`
* Access to the C2 Dashboard at `http://web0x0c.hbtn/attacker`

### Info
**Target machine:** `cyber_websec_0x0c`
```bash
$ sudo bash -c "echo web0x0c.hbtn >> /etc/hosts"
```

### Technical Requirements
* All attacks must be performed against the NexusShop application
* You must capture evidence (screenshots, payloads) for your report
* Flags must be submitted exactly as found (case-sensitive)
* Use realistic payloads that demonstrate actual impact, not just `alert(1)`

### Professional Requirements
* Document each attack with: **Objective → Method → Evidence → Impact**
* Final report must include remediation recommendations for each vulnerability
* Analysis must demonstrate understanding of WHY each attack works, not just HOW

### Ethics & Scope
* Only attack the designated lab environment
* **All techniques learned here are illegal without explicit written authorization**

> **Hint:**
> Press `F12` and keep `Console` and `Network` ready.

---

## Tasks

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

