# Password Policy

**SecureBank Financial Services**

---

## Document Control

| Field | Value |
|---|---|
| Policy ID | POL-SEC-002 |
| Version | 1.0 |
| Effective Date | 2026-08-07 |
| Review Date | 2027-08-07 |
| Policy Owner | Chief Information Security Officer (CISO) |
| Approved By | Information Security Steering Committee |
| Classification | Internal |

**Questions about this policy:** Contact the Information Security team at `security@securebank.example` or the IT Service Desk (ext. 4357).

---

## 1. Purpose

This policy establishes the requirements for creating, managing, storing, and protecting passwords and related authentication credentials across all SecureBank Financial Services systems. Passwords remain a primary control protecting customer financial data, banking transactions, and internal systems from unauthorized access.

The objectives of this policy are to:

- Ensure credentials are strong enough to resist guessing, brute-force, and credential-stuffing attacks.
- Reduce the risk of account compromise and unauthorized access to critical banking systems and cardholder data.
- Align authentication practices with **NIST SP 800-63B** (Digital Identity Guidelines) while satisfying the mandatory requirements of **PCI-DSS v4.0**, **Sarbanes-Oxley (SOX)**, and **FFIEC** authentication guidance.
- Provide clear, testable technical standards so that engineering and operations teams can configure systems consistently.

Where regulatory requirements and best-practice guidance differ, **the stricter control applies.**

---

## 2. Scope

### 2.1 Applicability

This policy applies to:

- [x] All employees
- [x] Contractors and consultants
- [x] Third-party vendors (with access to SecureBank systems or data)
- [x] Service, application, and machine accounts

It covers all credentials used to authenticate to SecureBank systems, including interactive user passwords, privileged/administrative passwords, service account credentials, API keys where used as authentication secrets, and any recovery or one-time credentials.

### 2.2 Systems / Assets Covered

| Tier | System | Criticality |
|---|---|---|
| 1 | Core banking system | Critical |
| 1 | Administrative and infrastructure systems (domain, PAM, cloud consoles) | Critical |
| 2 | Customer portal (internet-facing) | High |
| 2 | Systems within the Cardholder Data Environment (CDE) | High |
| 3 | Employee workstations and standard business applications | Moderate |
| 4 | Development / non-production environments | Moderate |

This policy also covers all networks, VPN and remote-access gateways, cloud services, databases, and any system that authenticates a SecureBank identity.

### 2.3 Exclusions

- Isolated laboratory or training systems that hold **no** production, customer, or cardholder data **and** have no network path to production may follow a documented alternate standard approved by the CISO.
- Third-party SaaS platforms where SecureBank cannot configure the authentication mechanism directly; these must instead be integrated with SecureBank Single Sign-On (SSO) so that this policy is enforced upstream, or covered by a documented exception (Section 7).

---

## 3. Policy Statements

### 3.1 Password Requirements

**Policy statement:** All passwords must meet minimum strength requirements appropriate to the system tier, favor length over forced complexity, and be screened against known-compromised and easily guessed values before acceptance.

**Requirements:**

- **Minimum length:**
  - Standard user and customer accounts: **at least 12 characters** (PCI-DSS v4.0 §8.3.6).
  - Privileged, administrative, and service accounts: **at least 16 characters** (see Section 3.5).
  - Systems must support passwords of **at least 64 characters** and must not truncate them.
- **Passphrases encouraged:** Users are encouraged to use long passphrases (e.g., four or more unrelated words). Length is the strongest defense and is preferred over character substitution tricks.
- **Character support:** All printable ASCII characters, spaces, and Unicode characters must be accepted. No character type may be forbidden.
- **Composition:** Passwords must contain **both letters and numbers** at minimum (PCI-DSS §8.3.6). Beyond this baseline, SecureBank does **not** impose additional forced-complexity rules (e.g., mandatory special-character positioning), consistent with NIST SP 800-63B, and instead relies on length plus blocklist screening.
- **Blocklist screening (prohibited passwords):** At the time a password is set or changed, it must be rejected if it is:
  - Present in a known breached-password corpus (e.g., Have I Been Pwned or an equivalent maintained list).
  - A common or dictionary word or a top-N common password.
  - Context-specific: contains the username, the person's name, `SecureBank`, the application name, or similar derivatives.
  - Sequential or repetitive (e.g., `123456`, `aaaaaa`, `qwerty`).
- **No password hints** and **no knowledge-based security questions** ("mother's maiden name," etc.) may be used as an authentication or recovery factor.
- **History:** The previous **12 passwords** must not be reused.

### 3.2 Password Management

**Policy statement:** Passwords must be changeable by the user through secure self-service, reset only after identity verification, and protected by throttling, lockout, and session controls.

**Requirements:**

- **Change procedure:** Users may change their password at any time via the self-service portal after authenticating. A change is **mandatory** whenever there is any evidence or suspicion of compromise.
- **Expiration / rotation:**
  - Where a password is the **only** authentication factor, it must be changed at least every **90 days** (PCI-DSS v4.0 §8.3.9 option 1).
  - Where **phishing-resistant MFA** and continuous account-posture monitoring are in place (§8.3.9 option 2), routine time-based expiration is **not** required, consistent with NIST guidance. Passwords are then changed only on evidence of compromise.
  - Privileged and service accounts follow the stricter rotation rules in Section 3.5.
- **Reset procedure:**
  - Self-service reset requires successful **MFA** verification.
  - Service-desk-assisted reset requires positive identity verification (e.g., callback plus knowledge only the user could have; never based on a static security question alone).
  - Temporary/reset passwords must be **randomly generated, single-use, unique per user, delivered over a secure channel, expire within 24 hours**, and force a password change at first login.
- **Account lockout:** After **no more than 10** consecutive failed attempts, the account is locked for a minimum of **30 minutes** or until an administrator verifies the user's identity and unlocks it (PCI-DSS v4.0 §8.3.4).
- **Rate limiting / throttling:** Authentication endpoints must throttle repeated failed attempts and defend against automated credential-stuffing (e.g., progressive delays, CAPTCHA on the customer portal, IP reputation controls).
- **Session timeout:** Idle sessions must re-authenticate after **15 minutes** of inactivity (PCI-DSS v4.0 §8.2.8). Critical-tier administrative sessions should use a shorter idle timeout where feasible.
- **First-use credentials:** Vendor default and initial passwords must be changed before a system is placed into service.

### 3.3 Multi-Factor Authentication (MFA)

**Policy statement:** MFA is required for all remote, administrative, and high-value access, and must use phishing-resistant methods for privileged and critical systems.

**Requirements:**

- **MFA is mandatory for:**
  - All remote access to the corporate network (VPN / remote gateways).
  - All access **into** the Cardholder Data Environment (PCI-DSS v4.0 §8.4.2).
  - All administrative / privileged access to any system (PCI-DSS v4.0 §8.4.1).
  - All console access to cloud management platforms.
  - Customer portal login for customers, and any access to the core banking system.
- **Approved methods (in order of preference):**
  1. **FIDO2 / WebAuthn hardware security keys or platform authenticators** – *required* (phishing-resistant) for privileged and critical-tier access.
  2. Authenticator apps generating TOTP, or push approval **with number matching**.
  3. **SMS / voice OTP** – permitted only as a fallback for lower-risk customer scenarios and **never** for privileged, administrative, or CDE access. NIST restricts SMS as a weaker ("restricted") authenticator; its use must be risk-assessed and documented.
- **MFA implementations** must resist replay and must not be bypassable (PCI-DSS v4.0 §8.5). All authentication factors must be verified before access is granted.
- **Enrollment and recovery** of MFA factors must themselves be protected (identity-proofed) so that account-recovery does not become the weak link.

### 3.4 Storage and Transmission

**Policy statement:** Passwords must never be stored or transmitted in a recoverable form; they must be salted and hashed with an approved algorithm and only ever transmitted over encrypted channels.

**Requirements:**

- **Hashing:** Stored passwords must be protected using a **memory-hard, salted, adaptive hashing function**:
  - **Preferred:** Argon2id.
  - **Acceptable:** bcrypt (work factor ≥ 12) or scrypt.
  - **Legacy-acceptable only where required for compatibility:** PBKDF2-HMAC-SHA-256 with a high iteration count and per-user salt.
- **Salting:** A unique, cryptographically random salt of at least 16 bytes must be applied per password. A system-wide secret ("pepper") stored separately from the database is recommended for internet-facing systems.
- **Prohibited storage:** Passwords must **never** be stored in plaintext, reversible/symmetric encryption, unsalted hashes, or fast general-purpose hashes (e.g., raw MD5/SHA-1/SHA-256). Passwords must never appear in application logs, error messages, monitoring tools, source code, or tickets.
- **Transmission:** All authentication traffic must use **TLS 1.2 or higher** (TLS 1.3 preferred). Passwords must never traverse the network in cleartext.
- **Password managers:** Use of the **approved enterprise password manager** is **required** for privileged and shared credentials and **strongly encouraged** for all employees. Storing corporate passwords in browsers, spreadsheets, plain text files, or personal/unapproved tools is prohibited.

### 3.5 Privileged and Service Accounts

**Policy statement:** Privileged, administrative, and machine accounts carry elevated risk and are subject to enhanced credential controls and centralized management through a Privileged Access Management (PAM) solution.

**Requirements:**

- **Enhanced credentials:** Minimum **16 characters**, unique per account, and **phishing-resistant MFA** for every interactive privileged login.
- **PAM enforcement:** All shared, administrative, and high-privilege credentials must be **vaulted in the approved PAM solution**, which provides:
  - **Check-out / check-in** workflows with approval where required.
  - **Just-in-time (JIT)** and least-privilege access rather than standing admin rights.
  - **Automatic credential rotation** after each use, or at minimum every **24 hours** for high-privilege accounts.
  - **Full session recording and audit logging** for privileged sessions.
- **No shared knowledge:** Administrators must not know or memorize vaulted privileged passwords; access is brokered by the PAM system.
- **Service / application accounts:** Must use non-interactive, unique credentials; be rotated on a defined schedule and immediately upon staff departure or suspected exposure; and, where supported, use certificates, managed identities, or secrets-manager–issued credentials instead of static passwords.
- **Break-glass accounts:** Emergency-access accounts must have long, complex, vaulted credentials; be alarmed on use; and be rotated immediately after each activation.
- **Separation of duties (SOX):** Privileged access to financial-reporting systems must be role-based, individually attributable (no anonymous shared logins), and periodically reviewed.

---

## 4. Roles and Responsibilities

| Role | Responsibilities |
|---|---|
| Executive Management | Approve policy, allocate resources, and demonstrate commitment to authentication security. |
| Information Security Steering Committee | Own and approve this policy; review exceptions and risk acceptances. |
| Chief Information Security Officer (CISO) | Policy owner; maintain the policy and its technical standards; oversee compliance. |
| IT Security Team | Implement and configure authentication controls, monitor for compromise, screen against breach lists, run the PAM and MFA platforms, and report violations. |
| IT Operations / Engineering | Configure systems to the technical standards in Appendix A; enforce hashing, lockout, and timeout settings. |
| Department Managers | Ensure their teams comply, report issues, and support training and enrollment. |
| Internal Audit | Independently test control effectiveness against PCI-DSS, SOX, and FFIEC obligations. |
| All Employees, Contractors, and Vendors | Comply with this policy, protect their credentials, use the approved password manager and MFA, and report suspected compromise immediately. |

---

## 5. Compliance

### 5.1 Monitoring

Compliance is monitored through automated and manual means, including: configuration scans of authentication settings against Appendix A, monitoring of failed-login and lockout events, detection of credential-stuffing patterns on the customer portal, alerting on privileged-account and break-glass use via the PAM solution, and periodic scanning of accounts against breach-corpus data.

### 5.2 Reporting

The IT Security team reports authentication metrics (MFA coverage, accounts failing standards, privileged-account rotation status, exception counts) to the Information Security Steering Committee at least **quarterly**, and reports material control failures to management and, where required, to regulators.

### 5.3 Auditing

Authentication controls are audited at least **annually** and as part of the **annual PCI-DSS assessment** and **SOX IT general controls** testing. Audits verify hashing configuration, MFA enforcement, lockout/timeout settings, password-history enforcement, and PAM effectiveness. Audit findings are tracked to remediation.

---

## 6. Enforcement

### 6.1 Violations

Violations of this policy may result in:

- Verbal warning
- Written warning
- Suspension of access privileges
- Disciplinary action up to and including termination
- Legal action where applicable (including for vendors and contractors, contractual penalties)

### 6.2 Reporting Violations

Report suspected violations, credential compromise, or lost/stolen MFA devices immediately to the **IT Service Desk (ext. 4357)** or the Information Security team at `security@securebank.example`. Suspected compromise of customer or cardholder data must be escalated per the Incident Response Plan without delay.

---

## 7. Exceptions

### 7.1 Exception Process

Exceptions to this policy require:

1. Written request to the **CISO / Information Security Steering Committee**.
2. Business justification.
3. Risk assessment.
4. Compensating controls (if applicable).
5. Formal approval and documentation.

Note: Requirements that are mandated by PCI-DSS, SOX, or FFIEC for in-scope systems are **not** eligible for exception; only the method of achieving compliance may be varied with approval.

### 7.2 Exception Duration

All exceptions must have a defined end date and be reviewed at least **quarterly**. Expired exceptions are automatically revoked.

---

## 8. Definitions

| Term | Definition |
|---|---|
| MFA (Multi-Factor Authentication) | Authentication using two or more independent factors: something you know, something you have, and/or something you are. |
| Phishing-resistant MFA | Authentication (e.g., FIDO2/WebAuthn) that is bound to the legitimate service and cannot be intercepted or replayed via a phishing proxy. |
| CDE (Cardholder Data Environment) | The people, processes, and technology that store, process, or transmit cardholder data, plus connected systems. |
| PAM (Privileged Access Management) | A system that vaults, brokers, rotates, and records the use of privileged credentials. |
| Salt | Unique random data added to a password before hashing so identical passwords produce different hashes. |
| Passphrase | A long password made of multiple words, favored for strength and memorability. |
| Credential stuffing | An attack that replays username/password pairs stolen from other breaches against SecureBank systems. |

---

## 9. Related Documents

- Information Security Policy (POL-SEC-001)
- Access Control Policy
- Acceptable Use Policy
- Incident Response Plan
- Privileged Access Management Standard
- NIST SP 800-63B – Digital Identity Guidelines (Authentication)
- PCI-DSS v4.0 – Requirement 8 (Identify Users and Authenticate Access)
- FFIEC Authentication and Access to Financial Institution Services and Systems
- Sarbanes-Oxley Act (SOX) – IT General Controls

---

## 10. Revision History

| Version | Date | Author | Description |
|---|---|---|---|
| 1.0 | 2026-08-07 | Information Security Team | Initial release |

---

## 11. Acknowledgment

By accessing company systems, all users acknowledge they have read, understood, and agree to comply with this policy.

**For formal acknowledgment tracking, use the company's policy acknowledgment system.**

---

# Appendix A – Technical Standards

The following standards are the enforceable configuration baseline. They are derived from the policy statements above and are what auditors and engineers should test against. Where a system cannot meet a value, a documented exception (Section 7) and compensating control are required.

## A.1 Password Requirements by System Tier

| Parameter | Standard User / Customer | CDE / Customer Portal | Privileged / Admin / Service |
|---|---|---|---|
| Minimum length | 12 | 12 | 16 |
| Maximum length accepted | ≥ 64 (no truncation) | ≥ 64 | ≥ 64 |
| Character set | All printable + Unicode + spaces | Same | Same |
| Composition minimum | Letters + numbers | Letters + numbers | Letters + numbers |
| Breach/dictionary screening | Required | Required | Required |
| Password history | 12 | 12 | 12 |
| Expiration (password-only) | ≤ 90 days | ≤ 90 days | ≤ 90 days / rotated by PAM |
| Expiration (with phishing-resistant MFA + monitoring) | Not required | Not required | Auto-rotated ≤ 24h |

## A.2 Lockout, Throttling, and Session Controls

| Control | Standard | Reference |
|---|---|---|
| Failed-attempt lockout threshold | ≤ 10 attempts | PCI-DSS §8.3.4 |
| Lockout duration | ≥ 30 min or admin unlock | PCI-DSS §8.3.4 |
| Idle session re-authentication | 15 min | PCI-DSS §8.2.8 |
| Automated attack defense | Progressive delay, CAPTCHA (portal), IP reputation | NIST SP 800-63B |
| Temporary/reset password validity | Single-use, ≤ 24h, force change at first login | – |

## A.3 MFA Standards

| Access type | MFA required | Minimum method |
|---|---|---|
| Customer portal (customers) | Yes | TOTP / push w/ number matching (SMS fallback only) |
| Remote / VPN access | Yes | TOTP or FIDO2 |
| CDE access | Yes | TOTP or FIDO2 (no SMS) |
| Administrative / privileged access | Yes | **FIDO2 / WebAuthn (phishing-resistant)** |
| Cloud management console | Yes | **FIDO2 / WebAuthn** |
| Core banking system | Yes | **FIDO2 / WebAuthn** |

## A.4 Storage and Transmission Standards

| Control | Standard |
|---|---|
| Hashing algorithm (preferred) | Argon2id |
| Hashing algorithm (acceptable) | bcrypt (work factor ≥ 12), scrypt |
| Hashing algorithm (legacy compat only) | PBKDF2-HMAC-SHA-256, high iteration count |
| Salt | Unique, random, ≥ 16 bytes per password |
| Pepper (internet-facing) | Recommended, stored separately |
| Prohibited storage | Plaintext, reversible encryption, unsalted or fast hashes (MD5/SHA-1/SHA-256 raw) |
| In logs / code / tickets | Never |
| Transport | TLS 1.2+ (TLS 1.3 preferred) |
| Enterprise password manager | Required for privileged/shared; encouraged for all |

## A.5 Privileged Account Standards

| Control | Standard |
|---|---|
| Minimum length | 16 |
| MFA | Phishing-resistant (FIDO2/WebAuthn), every login |
| Credential storage | Vaulted in PAM |
| Access model | Just-in-time, least privilege, check-out/check-in |
| Rotation | After each use, or ≤ 24h for high-privilege |
| Session recording | Required |
| Shared-password knowledge | Not permitted (brokered by PAM) |
| Service accounts | Unique, non-interactive, rotated on schedule and on staff departure; prefer certificates/managed identities |
| Break-glass accounts | Long, vaulted, alarmed on use, rotated immediately after activation |

## A.6 Regulatory Traceability

| Requirement area | PCI-DSS v4.0 | SOX (ITGC) | FFIEC | NIST SP 800-63B |
|---|---|---|---|---|
| Minimum length / composition | §8.3.6 | Access controls | Authentication strength | Length-focused, blocklist |
| Lockout / throttling | §8.3.4 | – | Layered security | Rate limiting |
| Session timeout | §8.2.8 | – | – | Reauthentication |
| Password expiration | §8.3.9 | – | – | No forced rotation w/o compromise |
| MFA | §8.4 – §8.5 | Privileged access | Authentication guidance | AAL2+ |
| Storage / hashing | §8.3.x | – | – | Salted, memory-hard hash |
| Privileged access | §7, §8 | Segregation of duties | Administrative controls | – |

*End of Policy Document*
