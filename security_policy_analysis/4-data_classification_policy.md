# Data Classification Policy

**HealthPlus Medical Group**

---

## Document Control

| Field | Detail |
|-------|--------|
| Document Title | Data Classification Policy |
| Document Owner | Chief Information Security Officer (CISO) |
| Policy Number | HP-ISP-004 |
| Version | 1.0 |
| Status | Approved |
| Classification of this Document | INTERNAL |
| Effective Date | August 7, 2026 |
| Last Reviewed | August 7, 2026 |
| Next Review Date | August 7, 2027 (annually, or upon significant regulatory change) |
| Approved By | Information Governance Committee |

### Revision History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | July 15, 2026 | Security & Compliance Team | Initial draft |
| 0.9 | July 29, 2026 | CISO | Review edits, added Quick Reference Guide |
| 1.0 | August 7, 2026 | Information Governance Committee | Approved and published |

### Contact for Questions

For questions about this policy, data classification decisions, or to report a suspected misclassification or data incident:

- **Security & Compliance Team** – security@healthplusmedical.example
- **Privacy Officer (HIPAA/GDPR matters)** – privacy@healthplusmedical.example
- **Help Desk (day-to-day handling questions)** – helpdesk@healthplusmedical.example, ext. 4357
- **Suspected data breach (24/7)** – incident-response@healthplusmedical.example

---

## 1. Purpose

The purpose of this policy is to establish a consistent, organization-wide framework for classifying data based on its sensitivity and the harm that could result from its unauthorized disclosure, alteration, or loss. Proper classification ensures that HealthPlus Medical Group applies the right level of protection to the right information, protects patient and employee privacy, and meets its legal and regulatory obligations.

This policy exists to:

- Protect Protected Health Information (PHI), Personally Identifiable Information (PII), and other sensitive data from unauthorized access.
- Give every staff member a clear, simple way to know how to label, store, share, and dispose of information.
- Support compliance with HIPAA, the GDPR, and applicable state privacy laws.
- Reduce the risk of data breaches and the financial, legal, and reputational damage they cause.

## 2. Scope

This policy applies to:

- **All data** created, received, stored, processed, or transmitted by HealthPlus Medical Group, in any format – electronic, paper, or verbal.
- **All personnel**, including employees, contractors, temporary staff, volunteers, interns, business associates, and third-party vendors who access HealthPlus data or systems.
- **All systems and locations** where HealthPlus data resides, including on-premises servers, cloud services, laptops, mobile devices, removable media, email, and physical files.

This policy covers the six data types handled by HealthPlus: patient medical records (PHI), employee information (PII), financial data, research data, business operations data, and public marketing materials.

## 3. Policy Statement

HealthPlus Medical Group classifies all data into one of four levels – **PUBLIC**, **INTERNAL**, **CONFIDENTIAL**, or **RESTRICTED** – based on the sensitivity of the information and the potential impact of its unauthorized disclosure. Every piece of data must be classified, and the protections applied to it must match its classification level.

When data of different classifications is combined, the resulting collection must be protected at the **highest** classification level present. When classification is unclear, staff must treat the data as **CONFIDENTIAL** until the Security & Compliance Team confirms the correct level.

### 3.1 Classification Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **PUBLIC** | Information approved for public release. Disclosure causes no harm. | Marketing brochures, published website content, press releases, public health notices |
| **INTERNAL** | Information intended for internal use only. Disclosure would cause minor or no material harm. | Internal memos, org charts, staff directories, general policies, meeting minutes |
| **CONFIDENTIAL** | Sensitive information whose disclosure could cause harm to individuals or the organization. | Employee PII, financial data, contracts, non-public research data, vendor agreements |
| **RESTRICTED** | Highly sensitive information whose disclosure could cause severe damage, legal liability, or serious harm to individuals. | Patient medical records (PHI), authentication credentials, encryption keys, GDPR special-category data |

### 3.2 Handling Requirements Summary

The following table defines the minimum handling requirements for each classification level. Detailed rules for each control are in Sections 4 through 8.

| Requirement | Public | Internal | Confidential | Restricted |
|-------------|:------:|:--------:|:------------:|:----------:|
| Labeling | N | Y | Y | Y |
| Encryption at Rest | N | N | Y | Y |
| Encryption in Transit | N | Y | Y | Y |
| Access Control | Open / Anyone | All Staff (authenticated) | Role-Based, Need-to-Know | Strict Role-Based, Need-to-Know + MFA |

> **Note:** Although PUBLIC data does not require encryption or labeling, it must still be protected against unauthorized *modification*. Only authorized staff may alter or publish PUBLIC content.

## 4. Labeling

Labeling makes a document's sensitivity immediately visible so that everyone handling it applies the correct protections.

### 4.1 Requirements by Level

- **PUBLIC** – Labeling optional. May be marked "PUBLIC" for clarity but not required.
- **INTERNAL** – Must be labeled "INTERNAL."
- **CONFIDENTIAL** – Must be labeled "CONFIDENTIAL."
- **RESTRICTED** – Must be labeled "RESTRICTED." PHI must additionally be identifiable as protected health information.

### 4.2 How to Label

- **Electronic documents (Word, PDF, slides):** Place the classification label in the header or footer of every page (e.g., *"CONFIDENTIAL – HealthPlus Medical Group"*).
- **Emails:** Add the classification in the subject line prefix, e.g., `[RESTRICTED]` or `[INTERNAL]`.
- **File naming:** Include the level in the file name for CONFIDENTIAL and RESTRICTED files where practical, e.g., `2026-Budget_CONFIDENTIAL.xlsx`.
- **Physical documents:** Stamp or print the classification at the top of the first page and on folders/binders.
- **Databases and systems:** Data sets and fields containing CONFIDENTIAL or RESTRICTED data must be tagged in the system's data catalog.

## 5. Storage

Storage rules define where each type of data may and may not be kept.

### 5.1 Approved Locations

| Level | Approved Storage |
|-------|------------------|
| PUBLIC | Public website, approved marketing platforms, any internal storage |
| INTERNAL | Company-managed file shares, approved cloud collaboration tools (e.g., managed SharePoint/Google Workspace), company devices |
| CONFIDENTIAL | Access-controlled, encrypted company file shares and approved cloud storage with role-based permissions; encrypted company devices |
| RESTRICTED | Approved, encrypted, access-restricted systems only (e.g., the EHR/EMR system, HIPAA-compliant cloud environments under a signed Business Associate Agreement). Stored only where strictly necessary. |

### 5.2 Prohibited Locations (CONFIDENTIAL and RESTRICTED)

- Personal or unmanaged devices (personal laptops, phones, home computers not enrolled in device management).
- Personal cloud accounts (personal Google Drive, Dropbox, iCloud, etc.).
- Unencrypted USB drives, external hard drives, or removable media.
- Public or unsecured file-sharing services.
- Local desktop folders or "Downloads" folders not covered by managed encryption.
- Paper documents left unattended in unlocked areas.

RESTRICTED data (including all PHI) may only be stored in systems that meet HIPAA safeguards and, where personal data of EU residents is involved, GDPR requirements. Any cloud vendor handling PHI must have an executed Business Associate Agreement (BAA).

## 6. Transmission

Transmission rules govern how data may be sent by email, file transfer, or other means.

### 6.1 Email

- **PUBLIC / INTERNAL** – May be sent by standard company email. Internal data should not be forwarded to external parties without a business reason.
- **CONFIDENTIAL** – Must be sent using encrypted email (TLS in transit). External transmission requires the approved secure-email/encryption feature. Verify the recipient address before sending.
- **RESTRICTED (including PHI)** – Must be sent using the approved secure/encrypted email service or a secure portal. PHI must never be sent to personal email accounts. Include only the minimum necessary information. Never place PHI or credentials in an unencrypted email body or subject line.

### 6.2 File Transfer

- Use only company-approved, encrypted file-transfer tools and secure portals for CONFIDENTIAL and RESTRICTED data.
- All transmission of CONFIDENTIAL and RESTRICTED data must use encryption in transit (TLS 1.2+ or equivalent).
- Do not use personal messaging apps, consumer file-sharing links, or unencrypted FTP for CONFIDENTIAL or RESTRICTED data.
- External transfers of RESTRICTED data require a documented business need and, where a third party is involved, an appropriate agreement (BAA and/or Data Processing Agreement).

### 6.3 Verbal and Fax

- Discuss RESTRICTED/CONFIDENTIAL information only where it cannot be overheard.
- When faxing PHI, confirm the destination number and use a cover sheet with a confidentiality notice.

## 7. Disposal

Data must be disposed of securely when it is no longer needed, in line with retention schedules and legal requirements.

### 7.1 Paper Records

- **PUBLIC / INTERNAL** – Standard recycling is acceptable (INTERNAL may be recycled if it contains no personal data).
- **CONFIDENTIAL / RESTRICTED** – Must be cross-cut shredded or placed in locked, secure-shredding bins. Never placed in regular trash or open recycling.

### 7.2 Electronic Media and Devices

- **CONFIDENTIAL / RESTRICTED** – Media must be sanitized using approved methods (e.g., NIST SP 800-88 compliant wiping) before reuse. Devices that cannot be reliably wiped must be physically destroyed.
- Hard drives, SSDs, USB drives, and backup media containing CONFIDENTIAL or RESTRICTED data must be sanitized or destroyed by IT, with a record of destruction kept for RESTRICTED media.
- Deleting a file or emptying the recycle bin is **not** considered secure disposal.

### 7.3 Records and Certificates

For RESTRICTED data (especially PHI), retain a certificate or log of destruction as required by HIPAA and applicable state law.

## 8. Access Control

Access to data is granted on a **least-privilege** and **need-to-know** basis – staff receive only the access required to do their jobs.

### 8.1 Who May Access

| Level | Who May Access | How |
|-------|----------------|-----|
| PUBLIC | Anyone | No restriction |
| INTERNAL | All authenticated HealthPlus staff | Standard login |
| CONFIDENTIAL | Authorized staff by role and business need | Role-based access control (RBAC), unique login |
| RESTRICTED | Only specifically authorized staff with a documented need | RBAC + Multi-Factor Authentication (MFA); access logged and monitored |

### 8.2 How Access Is Managed

- Access is granted based on job role and approved by the data owner or manager.
- All users have unique accounts; shared or generic accounts are prohibited for CONFIDENTIAL and RESTRICTED data.
- MFA is required for access to all systems holding RESTRICTED data.
- Access to PHI and other RESTRICTED data is logged; logs are retained and reviewed for unusual activity.

### 8.3 Access Reviews

- Access rights to CONFIDENTIAL and RESTRICTED data are reviewed at least **quarterly** by data owners.
- Access is revoked promptly (same business day where possible) upon termination, role change, or end of contract.
- The "minimum necessary" standard under HIPAA applies to all PHI access decisions.

## 9. Roles & Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Information Governance Committee** | Owns and approves this policy; resolves classification disputes; oversees compliance. |
| **Chief Information Security Officer (CISO)** | Maintains the policy; oversees technical safeguards; leads incident response. |
| **Privacy Officer** | Ensures HIPAA, GDPR, and state-law compliance; manages data subject and patient rights requests. |
| **Data Owners** (department heads / system owners) | Assign classification to data in their area; approve access; conduct access reviews. |
| **IT / Security Team** | Implement encryption, access controls, secure storage, and secure disposal; monitor logs. |
| **Managers / Supervisors** | Ensure their teams are trained and follow this policy; request appropriate access for staff. |
| **All Staff, Contractors, and Vendors** | Correctly label, store, transmit, and dispose of data; complete required training; report suspected incidents immediately. |

## 10. Enforcement

Compliance with this policy is mandatory. Violations may result in disciplinary action up to and including termination of employment or contract, and may carry legal consequences.

- **Employees and contractors** who violate this policy are subject to HealthPlus's disciplinary procedures.
- **Vendors and business associates** who violate this policy may have contracts terminated and may be reported to authorities where required.
- Suspected or confirmed breaches of CONFIDENTIAL or RESTRICTED data – especially PHI – must be reported to the Security & Compliance Team immediately so that breach-notification obligations under HIPAA, GDPR, and state law can be met.
- Willful or negligent mishandling of PHI or PII may result in personal liability under applicable law.

Compliance is monitored through access logs, periodic audits, and access reviews. Managers are responsible for ensuring their teams understand and follow this policy.

## 11. Related Documents and Compliance References

- HIPAA Privacy and Security Rules (45 CFR Parts 160 and 164)
- EU General Data Protection Regulation (GDPR)
- Applicable state privacy and data breach notification laws
- HealthPlus Acceptable Use Policy, Incident Response Plan, Data Retention Schedule, and Encryption Standard

---

*This document is classified INTERNAL. Distribute only within HealthPlus Medical Group and to authorized parties.*
