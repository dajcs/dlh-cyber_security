# Threat Model: Healthcare Mobile App

**System under analysis:** A patient-facing healthcare mobile app for viewing medical records, scheduling appointments, messaging providers, and requesting prescription refills.

**Architecture:**

| Component | Role |
|---|---|
| Mobile client (iOS/Android) | Patient-facing app; untrusted, runs on user-controlled devices |
| REST API backend | Core application logic, authorization, business rules |
| Cloud-hosted database | Stores medical records, messages, appointments, credentials |
| Hospital system integrations | External EHR/clinical systems the app exchanges data with |

This is a HIPAA-regulated environment: the data involved is Protected Health Information (PHI), which raises the stakes for confidentiality, integrity, and availability alike.

---

## 1. Most Critical Asset (via the CIA Triad)

**The most critical asset is the patients' medical records (PHI) held in the cloud database and exchanged with hospital systems.**

Appointments, messages, and refill requests all matter, but they are ultimately spokes around this hub — they either reference, generate, or act upon the medical record. The record is where sensitivity, regulatory exposure, and irreversibility concentrate. Evaluating it against each leg of the CIA Triad shows why:

**Confidentiality — the dominant concern.**
Medical records contain some of the most sensitive personal data that exists: diagnoses, mental health notes, medications, lab results, and history. Under HIPAA, this is PHI, and unauthorized disclosure carries legal penalties, mandatory breach notification, and lasting harm to patients (discrimination, stigma, insurance and employment consequences). Unlike a leaked password, exposed medical history cannot be reset or rotated — the harm is permanent. This makes confidentiality the highest-weighted property for this asset.

**Integrity — safety-critical.**
If a medical record is altered — a wrong allergy, an incorrect medication, a modified lab value — a provider may make a clinical decision that directly harms or kills a patient. Integrity failures here are not merely financial or reputational; they are patient-safety events. This is a crucial distinction from the e-commerce context, where integrity failures mostly cost money.

**Availability — important, but recoverable.**
If the app is down, patients may be unable to view records or request refills, which can delay care and, for time-sensitive medications, cause real harm. Availability genuinely matters in healthcare. However, hospitals typically retain authoritative records in the primary EHR, so an app outage is usually a degradation rather than a total loss — making availability the least weighted of the three *for this specific asset*, though still significant.

**Conclusion:** The medical record is the crown jewel because a compromise damages all three CIA properties, two of them irreversibly (a confidentiality breach cannot be undone, and an integrity breach can cause physical harm before it is detected). Protecting it should anchor the entire security program.

---

## 2. STRIDE Applied to "Message Healthcare Providers"

The messaging feature lets patients and providers exchange clinical communication — a rich target because it carries PHI, drives clinical decisions, and involves identity on both ends. Below are threats across all six STRIDE categories (more than the four requested, for completeness).

### Spoofing
An attacker impersonates a healthcare provider to a patient — sending fake medical advice, phishing for more PHI, or instructing the patient to change medication — or impersonates a patient to extract another person's information from a provider. Weak authentication, stolen tokens, or no verification of provider identity all enable this.
**Impact:** Patients act on fraudulent medical instructions; PHI is disclosed to an imposter.
**Mitigation:** Strong mutual authentication (MFA), server-verified provider identity badges in the UI, short-lived signed session tokens, and clear in-app indicators of verified provider accounts.

### Tampering
Messages are altered in transit or at rest — for example, changing "take 1 tablet" to "take 10 tablets," or modifying which provider a message is attributed to. Achievable via a man-in-the-middle on weak transport or by writing directly to an unprotected datastore.
**Impact:** Dangerous clinical miscommunication; potential patient harm.
**Mitigation:** Enforce TLS 1.2+ for all traffic; store messages with integrity protection (e.g., signing/HMAC or a tamper-evident append-only log); validate and encode message content.

### Repudiation
A patient or provider denies having sent a message — for instance, a patient claims they never requested a medication change, or a provider denies giving advice that led to harm. Without reliable logging, disputes cannot be resolved and accountability is lost.
**Impact:** No accountability in clinical/legal disputes; failure to meet HIPAA audit requirements.
**Mitigation:** Immutable, timestamped audit logs of every message send/read event tied to authenticated identities; non-repudiation via server-side signed records.

### Information Disclosure
The message thread — full of PHI — is exposed to an unauthorized party through an insecure API endpoint (e.g., an ID that can be enumerated to read others' threads), unencrypted local storage on the device, over-permissive access, or logs that capture message bodies.
**Impact:** PHI breach, HIPAA violation, mandatory notification, patient harm.
**Mitigation:** Enforce authorization on every message read (verify the requester owns/participates in the thread — prevent IDOR); encrypt data at rest and in transit; encrypt local cache on-device; scrub message content from server logs.

### Denial of Service
An attacker floods the messaging endpoint or a single patient's thread with traffic, preventing legitimate clinical communication from getting through — potentially delaying urgent care.
**Impact:** Patients cannot reach providers when it matters; degraded care.
**Mitigation:** Rate limiting and throttling per account, input size limits, abuse detection, and autoscaling/queuing for resilience.

### Elevation of Privilege
A patient exploits a flaw to gain provider-level messaging capabilities (e.g., broadcasting to other patients, or reading provider-only fields), or a low-privilege staff account gains access to messages beyond its role.
**Impact:** Unauthorized mass access to PHI; ability to impersonate clinical authority.
**Mitigation:** Strict server-side role-based access control checked on every action; principle of least privilege; never rely on the client to enforce roles.

---

## 3. Top Five Security Controls (in priority order)

These controls are ordered to build a coherent defense: establish *who* the user is, then *protect the data* they touch, then *constrain what they can do*, then *observe and verify*, and finally *contain* the inevitable device-level exposure. Each layer assumes the ones above it.

### 1. Strong authentication with multi-factor authentication (MFA)
**Why first:** Every other control depends on knowing who the user is. If an attacker can log in as a patient or provider, encryption and access controls protect the data *for the attacker*. Healthcare accounts are high-value phishing targets, so passwords alone are insufficient. MFA (biometric or OTP) dramatically raises the cost of account takeover — the single most common breach vector. This directly counters the Spoofing threats from Section 2.

### 2. Encryption in transit and at rest
**Why second:** Once identity is established, the PHI itself must be unreadable to anyone who intercepts traffic or reaches the storage layer. Enforce TLS 1.2+ for all API traffic (defeating interception and tampering in transit) and strong encryption at rest for the cloud database and any on-device cache (defeating disclosure from a stolen backup, misconfigured bucket, or lost phone). This is effectively mandatory under HIPAA's Security Rule and protects confidentiality — the property we identified as most critical.

### 3. Authorization and access control (least privilege / RBAC)
**Why third:** Authentication proves *who* you are; authorization decides *what you may see and do*. Enforced server-side on every request, role-based access control ensures a patient can only reach their own records and messages (preventing IDOR/broken-object-level-authorization, a leading cause of health-data breaches) and that staff see only what their role requires. This counters Elevation of Privilege and Information Disclosure. It sits below encryption because it governs authorized users, whereas encryption also protects against unauthorized reach of the data itself.

### 4. Comprehensive audit logging and monitoring
**Why fourth:** You cannot prove compliance, detect an in-progress breach, or resolve a dispute without a reliable record of who accessed what and when. HIPAA specifically requires audit controls. Immutable, timestamped logs tied to authenticated identities provide non-repudiation (countering the Repudiation threat), enable anomaly detection (e.g., a provider account suddenly reading thousands of records), and support forensic response. It ranks below prevention controls because it detects and proves rather than blocks — but it is what turns the other controls into an accountable system.

### 5. Secure mobile client and data minimization on-device
**Why fifth:** The mobile client runs on untrusted, easily-lost hardware, so it's the hardest surface to fully control — hence last, after the server-side foundations are solid. Prioritize minimizing PHI stored on the device, encrypting any local cache, enforcing device-level protections (screen lock, jailbreak/root detection), using the secure keychain/keystore for tokens, applying certificate pinning to resist MITM, and enabling remote session revocation. This contains the damage when a phone is stolen or an app is tampered with, protecting the data at its most exposed edge.

---

### Priority summary

| # | Control | Primary CIA property | Key STRIDE threats addressed |
|---|---|---|---|
| 1 | Strong authentication + MFA | Confidentiality | Spoofing |
| 2 | Encryption in transit & at rest | Confidentiality, Integrity | Information Disclosure, Tampering |
| 3 | Authorization / RBAC (least privilege) | Confidentiality | Elevation of Privilege, Information Disclosure |
| 4 | Audit logging & monitoring | Integrity, accountability | Repudiation, (detection of all others) |
| 5 | Secure mobile client & data minimization | Confidentiality | Information Disclosure, Tampering |

Together these form a defense-in-depth posture: prevent unauthorized access (1, 3), protect the data even if perimeters fail (2, 5), and detect and prove what happens (4) — anchored on protecting the medical record, the system's most critical asset.
