# Threat Model: Cloud Storage Service (Advanced)

**System under analysis:** A cloud storage service offering file upload/download, file sharing between users, public link generation, file versioning, and both client-side and server-side encryption options.

**Why this is an advanced case:** The system is defined by *sharing* and *encryption* — two features that create rich, subtle attack surfaces. Public links deliberately punch holes in authentication; versioning multiplies the copies of sensitive data; and the coexistence of client-side and server-side encryption makes *key management* the pivotal security decision. Most real breaches of such systems come not from broken crypto but from misconfigured sharing and mishandled keys.

---

## 1. Attack Surface Map

The attack surface is the complete set of points where an attacker can attempt to interact with, inject into, or extract from the system. Below, each entry point is described and assigned a risk level, then ranked.

### Entry points

**A. Public link generation / sharing links — RISK: CRITICAL**
Public links are unauthenticated by design: anyone with the URL gets access. Risks include predictable/enumerable link tokens (guessing valid links), links leaking via referrer headers, browser history, chat logs, or search-engine indexing, links that never expire, links granting more access than intended (write instead of read), and no revocation. This is the highest-risk surface because it intentionally bypasses authentication and is the most common source of real-world cloud-storage data leaks.

**B. File upload endpoints — RISK: CRITICAL**
Uploads accept attacker-controlled content and are a classic injection point: malware/hosted-malware distribution, malicious file types, path-traversal in filenames (`../../`), zip bombs / decompression DoS, oversized uploads exhausting storage, XXE or macro payloads, and stored XSS via filenames or file content served inline. The server both stores and later serves this content, so a flaw here can pivot to other users.

**C. Authentication and session/account management flows — RISK: CRITICAL**
Login, registration, password reset, MFA, OAuth, token issuance, and session handling. Compromise here (credential stuffing, weak reset flows, session hijacking, token leakage) yields access to a user's entire file store. It's ranked critical because it's the gateway to everything and a perennial attacker favorite.

**D. API endpoints (download, file operations, sharing management) — RISK: HIGH**
The REST/GraphQL API driving all operations. Primary risks: broken object-level authorization / IDOR (requesting `file_id=123` you don't own), broken function-level authorization, mass-assignment, missing rate limits enabling enumeration, and inconsistent permission checks across the many endpoints. Large API surface = large attack surface.

**E. Encryption key management — RISK: CRITICAL**
Where keys are generated, stored, wrapped, and used (the focus of Section 2). If keys are exposed, all encryption is nullified. Ranked critical because it is the single point that determines whether "encrypted at rest" is real protection or a checkbox.

**F. File sharing permission model (user-to-user) — RISK: HIGH**
Granting/revoking access between authenticated users. Risks: privilege escalation via sharing, failure to revoke access (ex-collaborator retains a cached link/permission), confused-deputy problems, and shares that expose more versions/metadata than intended.

**G. File versioning subsystem — RISK: MEDIUM**
Version history can leak data thought to be deleted: an attacker (or an over-broad share) may access *prior* versions containing sensitive content the user believed they had removed. Access controls must apply to every version, not just the latest, and deletion must be reasoned about carefully.

**H. Admin interfaces / internal tooling — RISK: HIGH**
Admin panels, support tools, and internal APIs typically have broad access to user data. Risks: weak admin authentication, insider threat/abuse, over-privileged support staff, and admin endpoints exposed to the internet. Lower-frequency target but very high impact if breached.

**I. Third-party / storage-backend integrations — RISK: MEDIUM**
Underlying object storage (e.g., S3-style buckets), CDNs, and integrations. Misconfigured bucket permissions ("public bucket") are a top real-world breach cause; also SSRF reaching internal storage, and leaked backend credentials.

**J. Client applications (web/mobile/desktop sync) — RISK: MEDIUM**
Local key/token storage, insecure caching, sync-conflict handling, and (for client-side encryption) correctness of the client crypto implementation. Untrusted device environment.

### Ranked attack surface (highest risk first)

| Rank | Entry point | Risk level | Why |
|---|---|---|---|
| 1 | Public link generation / sharing links | **Critical** | Unauthenticated by design; #1 real-world leak vector |
| 2 | Encryption key management | **Critical** | Exposure nullifies all encryption at once |
| 3 | Authentication / account flows | **Critical** | Gateway to a user's entire store |
| 4 | File upload endpoints | **Critical** | Attacker-controlled content; injection & malware |
| 5 | API endpoints (IDOR/authz) | **High** | Broad surface; object-level authz failures |
| 6 | Admin interfaces / internal tooling | **High** | Broad data access; insider/abuse risk |
| 7 | User-to-user sharing permission model | **High** | Privilege escalation, failed revocation |
| 8 | Storage-backend / third-party integrations | **Medium** | Bucket misconfig, SSRF, leaked creds |
| 9 | File versioning subsystem | **Medium** | Leaks "deleted"/prior-version data |
| 10 | Client applications | **Medium** | Local secret storage; untrusted device |

**Top-level takeaway:** the four critical surfaces cluster around *access without proper authentication* (public links, auth flows) and *the things that make encryption meaningful* (key management) plus *untrusted input* (uploads). Harden these first.

---

## 2. Why Storing Encryption Keys in the Database Is Problematic

**The proposal:** store encryption keys in the same database as the data (or its metadata) "for convenience."

**The core problem — it defeats the purpose of encryption.** Encryption at rest exists to protect data when the storage layer is breached. If the keys live in the same database as the encrypted data, then a single database compromise hands the attacker **both the locked box and the key**. The encryption provides essentially no protection against the very scenario it was meant to defend against. This is the security equivalent of taping your house key to the front door.

Threat modeling makes the failure precise. Consider the primary breach scenario — an attacker gains read access to the database (via SQL injection, a leaked backup, a compromised DB credential, or a misconfigured instance):

- With keys stored **separately** (e.g., a dedicated KMS/HSM with independent access control): the attacker gets ciphertext only. The data stays protected. The breach is serious but contained.
- With keys stored **in the same database**: the attacker gets ciphertext **and** keys, decrypts everything, and walks away with all plaintext. The encryption bought nothing.

### STRIDE threats introduced

**Information Disclosure (the dominant one).**
Co-locating keys and data means any breach of that database is a total confidentiality failure — every user's files decryptable at once. It also collapses the blast radius protection: what should have been "attacker has unreadable ciphertext" becomes "attacker has all plaintext." Database backups, replicas, and logs now each become full-key exposures too.

**Tampering.**
An attacker (or malicious insider) with database access can not only read keys but *modify* them — rotating keys to lock users out (ransom), swapping in attacker-controlled keys, or corrupting keys to destroy data irrecoverably. Because keys and data share a trust boundary and access path, there's no independent control preventing key tampering by anyone who can reach the data.

**Elevation of Privilege.**
Any component or account with database access (application service accounts, DBAs, support tools, a compromised app via SQLi) now implicitly has *decryption* privilege over all data — far beyond what most of those principals should hold. Key access should be a separate, tightly-scoped privilege; merging it into DB access grants everyone who touches the DB the keys to everything.

**Repudiation.**
When keys live in the general-purpose database, key usage isn't independently logged the way a dedicated KMS logs every decrypt/encrypt operation. It becomes far harder to prove who accessed or used a key, weakening forensics and accountability after an incident.

**Spoofing / (weakened) integrity guarantees.**
If keys are also used to authenticate or sign, their exposure lets an attacker forge/impersonate operations that the crypto was supposed to make trustworthy.

### The correct pattern

- **Separate the keys from the data.** Use a dedicated **Key Management Service (KMS)** or **HSM** with its own access controls, audit logging, and network isolation — a distinct trust boundary from the data store.
- **Envelope encryption:** encrypt each file with a unique data-encryption key (DEK); encrypt (wrap) each DEK with a key-encryption key (KEK) that never leaves the KMS/HSM. The database may store only the *wrapped* DEK, which is useless without the KMS.
- **For maximum protection, prefer client-side encryption** where the provider never holds plaintext keys at all (zero-knowledge) — the strongest defense, at the cost of features like server-side search and recoverability.
- **Independent access control & audit** on keys, key rotation support, and least-privilege so that DB access does *not* imply key access.

**Bottom line:** storing keys with the data trades a small convenience for the elimination of the security property encryption was supposed to provide. Threat modeling shows it converts a survivable ciphertext breach into a total plaintext breach and introduces tampering, privilege-escalation, and accountability failures on top.

---

## 3. Risk Matrix — Top 5 Threats

**Method:** Each threat is scored on **Likelihood (1–5)** and **Impact (1–5)**; **Risk Score = Likelihood × Impact** (range 1–25). Risk level bands: **1–6 Low**, **7–12 Medium**, **13–18 High**, **19–25 Critical**. Scores are informed judgments for a typical deployment and should be tuned to a specific environment.

| # | Threat | Likelihood (1–5) | Impact (1–5) | Risk Score | Risk Level |
|---|---|:---:|:---:|:---:|:---:|
| 1 | **Data breach via encryption keys stored with data** — DB compromise yields keys + ciphertext, exposing all plaintext | 3 | 5 | **15** | High |
| 2 | **Public link exposure** — predictable/leaked/non-expiring links exposing private files | 5 | 4 | **20** | Critical |
| 3 | **Broken object-level authorization (IDOR)** on file/download API — accessing others' files by ID | 4 | 5 | **20** | Critical |
| 4 | **Account takeover** via credential stuffing / weak reset / session hijack | 4 | 5 | **20** | Critical |
| 5 | **Malicious file upload** — malware hosting, stored XSS, path traversal, or DoS via upload | 4 | 3 | **12** | Medium |

### Justification of scores

**1 — Keys stored with data (L3 × I5 = 15, High).**
*Likelihood 3:* This depends on a database breach occurring — a real but not everyday event, gated by other controls (moderate likelihood). *Impact 5:* If it happens, it's catastrophic and total — every user's files decrypted at once, encryption rendered worthless, mass regulatory/notification consequences. High impact drives the score even at moderate likelihood, which is exactly why Section 2 treats it so seriously.

**2 — Public link exposure (L5 × I4 = 20, Critical).**
*Likelihood 5:* Extremely common — links leak via referrers, chat, search indexing, and users routinely over-share; this is the most frequently realized cloud-storage threat. *Impact 4:* Serious confidentiality loss, but typically scoped to the files/folders shared rather than the entire platform, so just short of maximum. The very high likelihood makes this a top priority.

**3 — IDOR / broken authorization (L4 × I5 = 20, Critical).**
*Likelihood 4:* Broken object-level authorization is among the most prevalent API vulnerabilities and easy to introduce across a large endpoint surface. *Impact 5:* A single flaw can expose *any* user's files by iterating IDs — potentially the whole dataset — hence maximum impact.

**4 — Account takeover (L4 × I5 = 20, Critical).**
*Likelihood 4:* Credential stuffing and phishing are constant, high-volume threats against any consumer service; without strong MFA, success is common. *Impact 5:* Full access to a victim's entire file store, sharing, and versions — total compromise of that account. MFA is the control that most reduces the likelihood here.

**5 — Malicious file upload (L4 × I3 = 12, Medium).**
*Likelihood 4:* Upload endpoints are constantly probed and easy to attack. *Impact 3:* Real (malware distribution, stored XSS against other users, DoS) but generally more contained per-incident than a mass data breach, and mitigable with scanning, type/size limits, and safe serving (download-only, sandboxed domains). Nets out to Medium.

### Risk matrix (visual)

```
Impact
  5 |            IDOR(3)  Keys(1)
    |            ATO(4)
  4 |                    PublicLink(2)
  3 |            Upload(5)
  2 |
  1 |
    +----------------------------------
       1    2    3    4    5   Likelihood
```

### Prioritized remediation order

1. **Public links (20):** enforce cryptographically-random, unguessable tokens; mandatory expiration; scoped (read-only) permissions; revocation; `noindex`/no-referrer; optional passwords.
2. **IDOR / authorization (20):** enforce server-side object-level authorization on every request and every file *version*; deny-by-default; automated authz testing.
3. **Account takeover (20):** mandatory MFA, breached-password checks, rate limiting, hardened reset flows, session management.
4. **Key storage (15):** never co-locate keys and data — move to KMS/HSM with envelope encryption (Section 2); offer client-side/zero-knowledge encryption.
5. **Malicious upload (12):** malware scanning, strict type/size validation, filename sanitization, serve user content from an isolated domain as downloads.

**Note on method:** DREAD/likelihood-impact scoring is inherently subjective; its value is consistent *relative* prioritization within one organization using a shared rubric, not objective precision. The three 20-rated criticals — public links, IDOR, and account takeover — should be addressed first; together they represent the "access without proper authorization" theme that dominates real cloud-storage breaches.
