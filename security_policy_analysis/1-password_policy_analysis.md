# Security Policy Analysis & Rewrite



## Part A: Missing Components

The sample policy is only five lines long and omits nearly every element expected of a formal policy document. The table below lists each missing component and why it matters.

| Missing Component | Why It's Important |
|-------------------|--------------------|
| **Policy ID / unique identifier** | Without an identifier (e.g., POL-SEC-001) the policy cannot be referenced, indexed, tracked in a register, or cited by other documents. |
| **Version number** | No version means no way to know whether a reader is looking at the current, superseded, or draft version. Change management becomes impossible. |
| **Effective Date** | Staff cannot tell when the policy became binding. This undermines enforceability and audit defensibility. |
| **Review Date** | Policies must be periodically reviewed. Without a scheduled review date, the policy silently becomes stale and non-compliant with governance standards. |
| **Policy Owner** | No accountable owner means no one is responsible for keeping the policy accurate, answering questions, or approving exceptions. |
| **Approved By / approval authority** | Without documented approval from management, the policy has no formal authority and cannot be enforced as a management directive. |
| **Classification** | No handling label (e.g., Internal, Confidential) leaves distribution and storage requirements undefined. |
| **Purpose statement** | The policy never states *why* it exists or what objective it serves, so staff cannot understand its intent or apply it to edge cases. |
| **Scope / applicability** | It is unclear whether the policy covers contractors, vendors, or only "employees," and which systems and accounts are in scope. |
| **Specific, measurable policy statements** | "Use good passwords" is not a requirement. There are no measurable rules (length, complexity, rotation, MFA, storage) that can be implemented or verified. |
| **Roles and responsibilities** | Beyond a vague "IT will handle security stuff," no roles, duties, or accountability are defined for management, IT, or users. |
| **Compliance / monitoring** | There is no description of how compliance is monitored, reported, or audited, so the policy cannot be measured or evidenced. |
| **Enforcement section** | No consequences are defined for non-compliance, so the policy is unenforceable and carries no weight. |
| **Exceptions process** | There is no defined path for requesting, justifying, approving, or time-boxing exceptions, so deviations happen informally and untracked. |
| **Definitions** | Terms like "good passwords," "security stuff," and "problems" are undefined, leaving interpretation to each reader. |
| **Related documents** | No links to related standards, procedures, or frameworks (e.g., access control policy, NIST guidance), so the policy stands in isolation. |
| **Revision history** | There is no record of changes over time, defeating auditability and version traceability. |
| **Reporting contact / channel** | "Report problems to someone" gives no name, email, ticket queue, or method, so incidents may never be reported. |
| **Acknowledgment** | There is no mechanism for users to confirm they have read and agree to comply, which is often a compliance and legal requirement. |

---

## Part B: Weaknesses

The following weaknesses concern the *language and requirements* of the existing policy (distinct from the structural omissions in Part A). At least five are required; several are provided.

| Weakness | Problem | Impact |
|----------|---------|--------|
| "All employees **should** use good passwords." | "Should" is advisory, not mandatory; "good" is subjective and undefined; scope is limited to "employees." | Requirement is unenforceable and open to interpretation. Contractors and vendors appear excluded, leaving gaps attackers can exploit. |
| "use **good passwords**" | No measurable criteria — no minimum length, complexity, uniqueness, rotation, MFA, or prohibited-password rules. | Users choose weak, guessable passwords. There is no objective standard to test, audit, or enforce against. |
| "**Don't share** them." | States a rule but provides no detail on storage, password managers, service/shared accounts, or consequences of sharing. | Ambiguity leads to unsafe workarounds (spreadsheets, sticky notes, shared logins). No accountability when sharing occurs. |
| "**IT will handle security stuff.**" | Vague, informal, and undefined; "security stuff" assigns no concrete duties and no accountability to any named role. | Responsibilities fall through the cracks; no one owns monitoring, enforcement, or user support. Not auditable. |
| "Report problems to **someone**." | No named contact, email address, phone number, ticketing system, or escalation path is provided. | Incidents go unreported or are reported to the wrong place, delaying response and increasing damage. |
| "Updated: **Sometime last year**." | No real date, version number, author, or approval. Not verifiable version control. | Impossible to confirm currency or authority of the document. Fails audit and governance requirements. |
| No stated **consequences** anywhere in the document | The policy lists expectations but attaches no enforcement or disciplinary outcome to violations. | Without consequences, the policy is effectively optional and provides no deterrent. |

---

## Part C: Rewritten Password Policy

The following is a complete rewrite using the organization's policy template. Bracketed values (e.g., dates, owner names) should be finalized by the policy owner before publication.

---

# Password Policy

## Document Control

| Field | Value |
|-------|-------|
| Policy ID | POL-SEC-001 |
| Version | 1.0 |
| Effective Date | 2026-09-01 |
| Review Date | 2027-09-01 |
| Policy Owner | Chief Information Security Officer (CISO) |
| Approved By | [Name/Role — e.g., Chief Executive Officer] |
| Classification | Internal |

---

## 1. Purpose

This policy establishes the minimum requirements for the creation, use, protection, and management of passwords and related authentication credentials across the organization. Its objective is to reduce the risk of unauthorized access, credential compromise, and data breaches by ensuring that all account credentials meet a consistent, verifiable security standard and are protected throughout their lifecycle.

---

## 2. Scope

### 2.1 Applicability

This policy applies to:

- [x] All employees
- [x] Contractors and consultants
- [x] Third-party vendors with access to organizational systems
- [x] Any other individual granted access to organizational systems, applications, or data

### 2.2 Systems/Assets Covered

- All user, administrative, and service accounts
- Corporate workstations, laptops, and mobile devices
- Email, collaboration, and cloud (SaaS) applications
- Servers, databases, network devices, and infrastructure
- Remote access systems (VPN, remote desktop) and multi-factor authentication (MFA) systems

### 2.3 Exclusions

- Personal accounts not used for organizational business
- Guest network access that provides no access to internal systems or data
- Systems explicitly covered by a separate, formally approved authentication standard (documented via the exception process in Section 7)

---

## 3. Policy Statements

### 3.1 Password Construction and Strength

All passwords must meet defined strength requirements to resist guessing and brute-force attacks.

**Requirements:**
- Minimum length of 14 characters for standard user accounts and 16 characters for privileged/administrative accounts.
- Passwords must not contain the user's name, username, email address, or organization name.
- Passwords must not be reused from the user's previous 10 passwords.
- Passwords must be checked against a list of known-breached and common passwords, which are prohibited.
- Passphrases (multiple unrelated words) are encouraged as a strong, memorable alternative.

### 3.2 Password Protection and Handling

Credentials must be kept confidential and protected from disclosure at all times.

**Requirements:**
- Passwords must never be shared with any other person, including IT staff, managers, or the help desk.
- Passwords must not be written down in plaintext, stored in unprotected files, or sent by email, chat, or SMS.
- Passwords must be stored only in an organization-approved password manager.
- Users must not reuse organizational passwords for personal accounts, and vice versa.
- Any suspected credential compromise must be reported immediately (see Section 6.2) and the affected password changed.

### 3.3 Multi-Factor Authentication and Account Management

Passwords alone are not sufficient; additional controls apply to sensitive access.

**Requirements:**
- Multi-factor authentication (MFA) must be enabled for all remote access, email, cloud administrative consoles, and privileged accounts.
- Accounts must lock after 5 consecutive failed login attempts and remain locked for at least 15 minutes or until reset by the help desk.
- Passwords must be changed immediately upon known or suspected compromise; routine forced rotation is not required unless a compromise is indicated.
- Default vendor passwords must be changed before any system is placed into production.
- Service and shared accounts must have a documented owner, use a unique credential, and be reviewed at least quarterly.

---

## 4. Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Executive Management** | Approve the policy, allocate resources, and demonstrate commitment to secure authentication practices. |
| **IT Security Team** | Implement and maintain password controls and MFA, monitor compliance, investigate incidents, and report violations. |
| **IT Help Desk** | Support password resets, account unlocks, and password manager onboarding following verified identity checks. |
| **Department Managers** | Ensure team compliance, support training, and promptly report suspected issues or departing-staff access changes. |
| **All Employees / Users** | Comply with this policy, protect their credentials, complete required training, and report suspected incidents immediately. |
| **Policy Owner (CISO)** | Maintain the policy, approve exceptions, and ensure timely review and updates. |

---

## 5. Compliance

### 5.1 Monitoring

Compliance is monitored through automated password-strength enforcement at account creation and change, breached-password screening, MFA enrollment reporting, and periodic reviews of privileged and service accounts.

### 5.2 Reporting

The IT Security Team reports compliance metrics (e.g., MFA coverage, accounts failing strength checks, exception counts) to Executive Management on a quarterly basis and following any significant credential-related incident.

### 5.3 Auditing

An audit of password and authentication controls is conducted at least annually, and after any major system change or breach, to verify that technical controls enforce the requirements in Section 3.

---

## 6. Enforcement

### 6.1 Violations

Violations of this policy may result in:

- Verbal warning
- Written warning
- Suspension of access privileges
- Disciplinary action up to and including termination
- Legal action where applicable

### 6.2 Reporting Violations

Report suspected violations, lost or shared credentials, or account compromise immediately to the IT Security Team at **security@[organization].com** or via the IT Service Desk ticketing system. For urgent incidents outside business hours, contact the on-call security line at **[phone number]**.

---

## 7. Exceptions

### 7.1 Exception Process

Exceptions to this policy require:

1. Written request to the Policy Owner (CISO) or Security Committee
2. Business justification
3. Risk assessment
4. Compensating controls (if applicable)
5. Formal approval and documentation

### 7.2 Exception Duration

All exceptions must have a defined end date and be reviewed quarterly.

---

## 8. Definitions

| Term | Definition |
|------|------------|
| **Credential** | Any secret used to authenticate identity, including passwords, passphrases, PINs, and authentication tokens. |
| **Multi-Factor Authentication (MFA)** | An authentication method requiring two or more independent factors (e.g., a password plus a one-time code or hardware token). |
| **Privileged Account** | An account with elevated permissions, such as administrator, root, or service accounts with system-wide access. |
| **Password Manager** | An organization-approved application that securely stores and generates unique passwords. |
| **Passphrase** | A password composed of multiple unrelated words, providing high strength while remaining memorable. |

---

## 9. Related Documents

- Access Control Policy
- Acceptable Use Policy
- Information Security Standard
- Incident Response Procedure
- NIST SP 800-63B, Digital Identity Guidelines (external reference)

---

## 10. Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-09-01 | @anemet | Initial release |

---

## 11. Acknowledgment

By accessing company systems, all users acknowledge they have read, understood, and agree to comply with this policy.

**For formal acknowledgment tracking, use the company's policy acknowledgment system.**

---

*End of Policy Document*
