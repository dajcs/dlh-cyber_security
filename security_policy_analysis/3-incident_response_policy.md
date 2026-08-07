# Incident Response Policy

**GlobalTech Manufacturing**

---

## Document Control

| Field | Detail |
|-------|--------|
| **Document Title** | Incident Response Policy |
| **Document ID** | GTM-SEC-IRP-001 |
| **Version** | 1.0 |
| **Classification** | Internal – Confidential |
| **Status** | Approved |
| **Owner** | Chief Information Security Officer (CISO) |
| **Author** | Information Security Office |
| **Approved By** | Executive Leadership Team |
| **Approval Date** | 07 August 2026 |
| **Effective Date** | 01 September 2026 |
| **Last Reviewed** | 07 August 2026 |
| **Next Review Date** | 07 August 2027 (annually, or after any Critical incident) |
| **Applies To** | All GlobalTech Manufacturing entities across all 5 countries |

### Version History

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | 15 June 2026 | Information Security Office | Initial draft |
| 0.9 | 20 July 2026 | Information Security Office | Incorporated Legal and OT engineering review comments |
| 1.0 | 07 August 2026 | Information Security Office | Final approved version |

### Contact for Questions

| Purpose | Contact | Detail |
|---------|---------|--------|
| Policy questions | Information Security Office | security-policy@globaltech-mfg.example |
| **Report an incident (24/7)** | Security Operations Center (SOC) | soc@globaltech-mfg.example / +1-800-555-0140 |
| Data protection / GDPR | Data Protection Officer (DPO) | dpo@globaltech-mfg.example |

---

## 1. Purpose

The purpose of this policy is to establish a consistent, organization-wide framework for identifying, responding to, containing, and recovering from information security incidents at GlobalTech Manufacturing.

Because GlobalTech operates manufacturing facilities that combine traditional IT systems with Internet of Things (IoT) and Operational Technology (OT) environments, security incidents can affect not only data confidentiality but also production continuity and personnel safety. This policy is designed to:

- Minimize the impact of security incidents on people, operations, data, and reputation.
- Ensure incidents are handled in a structured way aligned with the **NIST incident response lifecycle** (Preparation → Detection & Analysis → Containment, Eradication & Recovery → Post-Incident Activity).
- Meet obligations under **ISO/IEC 27001**, the **EU General Data Protection Regulation (GDPR)**, and applicable industry-specific and national regulations across the countries in which we operate.
- Preserve evidence so incidents can be investigated properly and, where necessary, support legal or regulatory action.
- Ensure the right people are informed at the right time.

---

## 2. Scope

This policy applies to:

- **All personnel** – full-time and part-time employees, contractors, temporary staff, interns, and third parties acting on behalf of GlobalTech Manufacturing.
- **All locations** – every GlobalTech site across the 5 countries of operation, including corporate offices, manufacturing plants, and remote workers.
- **All information systems and assets**, including:
  - Corporate IT (email, file storage, ERP, HR, finance, cloud services).
  - **OT and IoT systems** – industrial control systems (ICS), SCADA, programmable logic controllers (PLCs), plant sensors, connected machinery, and building/safety systems.
  - Networks, endpoints, mobile devices, and removable media.
  - Data in all forms (electronic and physical), including personal data subject to GDPR.
- **All security incidents and suspected incidents**, regardless of whether they originate internally or externally, or whether they were accidental or malicious.

**Out of scope:** Routine IT service disruptions with no security dimension (e.g., a printer outage) are handled through standard IT service management, unless they are later found to have a security cause.

---

## 3. Policy Statement

GlobalTech Manufacturing is committed to protecting the confidentiality, integrity, and availability of its information and operational systems, and to safeguarding the personal data entrusted to it.

It is the policy of GlobalTech that:

1. **All security incidents will be reported promptly.** Every individual within scope has a duty to report suspected or confirmed incidents to the Security Operations Center (SOC) without delay.
2. **Incidents will be managed through a formal, repeatable process** based on the NIST lifecycle and coordinated by a designated Incident Response Team (IRT).
3. **Incidents will be classified by severity** and handled within defined response times.
4. **Safety takes priority.** Where an OT/IoT incident could endanger personnel or physical safety, protective and safety measures take precedence over evidence preservation and system availability.
5. **Legal and regulatory obligations will be met**, including GDPR breach notification to the relevant supervisory authority within 72 hours of becoming aware of a qualifying personal data breach, and notification of affected individuals where required.
6. **Evidence will be preserved** using sound chain-of-custody practices to support investigation and potential legal or disciplinary action.
7. **Every significant incident will be followed by a lessons-learned review** to drive continuous improvement, consistent with ISO/IEC 27001.
8. **This policy will be tested** through periodic exercises and reviewed at least annually.

Non-compliance with this policy may increase organizational risk and is subject to enforcement as described in Section 12.

---

## 4. Incident Classification

Incidents are assigned one of four severity levels. Severity drives the response time, the level of resources committed, and who is notified. The **Incident Response Manager** owns the final severity decision and may re-classify an incident as more information becomes available.

**Response Time** below refers to the target time to acknowledge the incident and begin an active, resourced response – not the time to full resolution.

### Incident Classification Matrix

| Severity | Description | Response Time (to begin response) | Examples |
|----------|-------------|-----------------------------------|----------|
| **Critical** | Incident causing, or imminently threatening, severe harm to safety, major production, large-scale data loss, or the organization as a whole. Widespread impact with no immediate workaround. | **Within 15 minutes**, 24/7. Immediate escalation to Executive Sponsor. | Ransomware spreading across plant networks; compromise or manipulation of OT/ICS/SCADA affecting production or personnel safety; confirmed large-scale breach of personal data (GDPR-reportable); full outage of a critical manufacturing site. |
| **High** | Serious incident with significant impact to a business unit, site, or sensitive data set, but contained or with a partial workaround. | **Within 1 hour**, 24/7. | Confirmed malware on multiple corporate endpoints; compromise of a privileged account; targeted phishing leading to credential theft; suspected exfiltration of confidential IP or a limited set of personal data; single production line disruption from a security event. |
| **Medium** | Incident with limited or localized impact, affecting a small number of users or systems, with no confirmed data loss. | **Within 4 business hours.** | Isolated malware infection on one endpoint (contained); repeated failed intrusion attempts against a service; policy violation such as unauthorized software; loss of a single encrypted device with no evidence of access. |
| **Low** | Minor event or near-miss with negligible impact; often informational or a precursor requiring monitoring. | **Within 1 business day.** | Single blocked phishing email reported by a user; minor misconfiguration with no exposure; spam; low-risk vulnerability identified during scanning. |

> **Note on IoT/OT:** Any incident that could affect physical safety, environmental controls, or continuous production processes is treated as **at least High**, and as **Critical** where safety or major production is at risk – regardless of the volume of data involved.

---

## 5. Incident Response Team (Roles & Responsibilities)

The Incident Response Team (IRT) is a cross-functional group activated according to incident severity. Not all roles are engaged for every incident; Low and Medium incidents may be handled by the SOC and IT with escalation as needed.

| Role | Core Responsibilities |
|------|----------------------|
| **Incident Response Manager (IRM)** | Owns the end-to-end response; declares and classifies incidents; coordinates the IRT; makes containment/eradication decisions; maintains the incident record; authorizes escalation and stand-down; primary point of accountability. |
| **Security Analysts** | Perform detection triage, technical investigation, forensic analysis, and threat hunting; execute containment and eradication actions; collect and preserve evidence; document technical timeline and indicators of compromise (IOCs). |
| **IT Support / Infrastructure** | Provide system, network, and application support; implement isolation, patching, rebuilds, and restoration from backups; validate that recovered systems function correctly; support OT/IT segmentation actions. |
| **OT/Plant Engineering** *(GlobalTech-specific)* | Advise on safe handling of ICS/SCADA/PLC systems; ensure that response actions do not endanger safety or production; execute OT-side containment in coordination with the IRM. |
| **Legal Counsel** | Advise on legal obligations, liability, contractual duties, and preservation of privilege; guide regulatory notification decisions; oversee handling of law-enforcement engagement. |
| **Data Protection Officer (DPO)** | Assess whether a personal data breach is notifiable under GDPR; manage the 72-hour supervisory-authority notification and any data-subject notifications; liaise with supervisory authorities. |
| **Communications / PR** | Own internal and external messaging; draft holding statements and approved communications; manage media and reputational aspects; ensure a single, consistent voice. |
| **Executive Sponsor** | Senior leader (e.g., CISO or CIO) providing authority, resources, and decision-making for High/Critical incidents; approves major actions (e.g., taking a plant offline); briefs the executive team and board. |
| **HR** *(engaged as needed)* | Supports incidents involving insiders or personnel-related matters; advises on disciplinary process. |

An up-to-date IRT contact roster (with 24/7 details and named deputies) is maintained by the Information Security Office and stored in a location accessible even if primary systems are unavailable.

---

## 6. Detection and Reporting

### 6.1 How incidents are detected

Incidents may be detected through:

- **Automated monitoring** – SIEM alerts, endpoint detection and response (EDR), intrusion detection/prevention systems, firewall and network monitoring, and dedicated **OT/IoT monitoring** for anomalies in industrial networks.
- **Human reporting** – employees, contractors, or third parties noticing something unusual.
- **Third-party notification** – vendors, partners, customers, threat-intelligence feeds, or law enforcement.
- **Routine activity** – vulnerability scans, audits, and log reviews.

### 6.2 How to report an incident

Anyone who suspects or observes a security incident must report it **immediately**, and **must not attempt to investigate or "fix" it themselves**, as this can destroy evidence or worsen impact.

Report to the **Security Operations Center (SOC)**, available 24/7:

- **Email:** soc@globaltech-mfg.example
- **Phone (urgent / suspected Critical or High):** +1-800-555-0140
- **Self-service portal:** the "Report a Security Incident" form on the intranet

For any incident that may affect **plant safety or production**, also alert the local plant supervisor or control room immediately.

Reporting in good faith is encouraged and protected; no one will be penalized for raising a genuine concern that turns out to be a false alarm.

### 6.3 What information to collect

When reporting, provide as much of the following as is known – but do **not** delay reporting to gather details:

- Reporter name, contact details, and location/site.
- Date and time the issue was noticed.
- What was observed (systems, applications, or equipment affected).
- Any error messages, unusual behavior, or suspicious communications.
- Whether personal data or OT/production systems may be involved.
- Actions already taken, if any.

### 6.4 Initial assessment procedures

On receipt, the SOC will:

1. Log the report and assign a unique incident reference number.
2. Perform initial triage to confirm whether it is a genuine security incident.
3. Assign a **provisional severity** using the Classification Matrix (Section 4).
4. Notify the **Incident Response Manager**, who confirms classification and activates the appropriate level of IRT.
5. Begin the incident timeline and open the incident record.

---

## 7. Response Procedures

All response actions follow the NIST lifecycle and are documented in the incident record. For OT/IoT systems, **safety and coordination with OT/Plant Engineering are mandatory before any containment action.**

### 7.1 Containment

- **Short-term containment:** Rapidly limit spread and damage – e.g., isolating affected endpoints from the network, disabling compromised accounts, blocking malicious IPs/domains, or segmenting affected OT zones. Aim to stop the bleeding without destroying evidence.
- **Evidence preservation:** Before wiping or rebuilding, capture forensic images, memory, and relevant logs (see Section 8). Where safety requires immediate action, prioritize safety and document what could not be preserved.
- **Long-term containment:** Apply more durable measures to keep systems stable while a full fix is prepared – e.g., temporary patches, hardened firewall rules, enhanced monitoring, or standing up clean rebuilt systems in isolation.

### 7.2 Eradication

- **Root cause analysis:** Identify how the incident occurred and the full extent of compromise (all affected systems, accounts, and data).
- **Threat removal:** Remove malware, unauthorized access, malicious artifacts, and compromised credentials; close the exploited vulnerabilities; rebuild systems from known-good sources where integrity is in doubt.
- **Validation:** Confirm that the threat is fully removed and the environment is clean before moving to recovery – e.g., re-scanning, verifying IOCs are absent, and confirming no persistence mechanisms remain.

### 7.3 Recovery

- **System restoration:** Return affected systems to normal operation from validated, clean backups or rebuilt systems, in a prioritized order that reflects business and safety criticality.
- **Testing:** Verify that restored systems function correctly and securely before returning them to production; for OT, confirm safe operation with Plant Engineering.
- **Monitoring:** Apply heightened monitoring for a defined period after recovery to ensure the threat does not recur and the incident is truly resolved.

The **Incident Response Manager** formally declares the incident closed once recovery is confirmed and monitoring shows stable, clean operation.

---

## 8. Communication Plan

Communication during an incident is coordinated by the **Incident Response Manager** together with **Communications/PR**, **Legal**, and the **DPO**. All external communications must be approved before release to ensure accuracy, legal soundness, and a single consistent message.

### Communication / Notification Matrix

| Stakeholder | When to Notify | Method |
|-------------|----------------|--------|
| **Executive Management** | Immediately for **Critical**; within 1 hour for **High**; summary reporting for Medium/Low. | Phone call / secure message from IRM to Executive Sponsor, followed by written brief. |
| **Legal** | As soon as an incident may have legal, contractual, or regulatory implications, or involves personal data, IP theft, or law enforcement. | Direct contact (phone/secure email) to Legal Counsel; engaged in IRT bridge. |
| **Regulators** (e.g., GDPR supervisory authority; industry regulators) | Where a personal data breach is likely to result in risk to individuals: **within 72 hours** of becoming aware. Industry/national regulators per applicable local requirements. | Formal notification led by the **DPO** with Legal, via each authority's official channel. |
| **Affected Users / Data Subjects** | Where a breach is likely to result in **high risk** to individuals, or where otherwise legally or contractually required – without undue delay. | Approved written notice (email/letter) from Communications, coordinated with DPO and Legal. |
| **Employees (internal)** | As needed to protect the organization and give safe instructions (e.g., "do not open X," "line 3 is offline"). | Intranet, email, or plant announcements via Communications. |
| **Customers / Partners** | Where their data or services are affected, or as required by contract. | Approved communication via account management, coordinated with Legal and Communications. |
| **Law Enforcement** | For criminal activity, where advised by Legal/Executive Sponsor. | Via Legal Counsel / designated liaison. |

> **GDPR reminder:** The 72-hour clock starts when GlobalTech becomes *aware* of a personal data breach, not when it is fully resolved. The DPO must be engaged early for any incident involving personal data.

---

## 9. Evidence Handling

Proper evidence handling ensures investigations are credible and that evidence is admissible if needed for legal, regulatory, or disciplinary purposes.

### 9.1 Chain of custody

- Every item of evidence (disk images, memory captures, logs, physical devices, media) must have a documented chain of custody recording: what it is, when and where it was collected, by whom, and every subsequent transfer or access.
- Evidence is handled only by authorized personnel (typically Security Analysts) and stored in secure, access-controlled locations or evidence repositories.

### 9.2 Evidence preservation

- Wherever feasible, work from **forensic copies**, leaving originals untouched.
- Capture volatile data (memory, active connections) before powering down systems where investigation requires it.
- Apply write-protection and integrity checks (e.g., cryptographic hashes) to preserve and verify integrity.
- Retain evidence for the period required by legal, regulatory, and internal retention requirements; do not destroy evidence while an investigation or legal matter is active.
- For **OT/IoT**, coordinate collection with Plant Engineering so that evidence gathering does not create safety or production risk.

### 9.3 Documentation requirements

- Maintain a complete, time-stamped incident timeline of events, observations, decisions, and actions.
- Record who authorized each significant action.
- Store all incident documentation securely, with access limited to the IRT and other authorized parties, respecting legal privilege where advised by Legal Counsel.

---

## 10. Post-Incident Activities

### 10.1 Lessons-learned process

For all High and Critical incidents (and any Medium/Low incident where valuable lessons exist), a **post-incident review** is held, ideally within **10 business days** of closure. The review, facilitated by the Incident Response Manager, covers:

- What happened, and the timeline of detection and response.
- What worked well and what did not.
- Root cause and contributing factors.
- Whether response times and communications met this policy's targets.
- Concrete, owned, time-bound improvement actions (technical controls, process, training, policy updates).

Improvement actions are tracked to completion and feed into GlobalTech's ISO/IEC 27001 continual-improvement process.

### 10.2 Report requirements

Each significant incident produces a formal **Incident Report** (template in Section 11) that includes the incident summary, classification, timeline, impact, response actions, root cause, regulatory/notification outcomes, and lessons learned. Reports are stored in the incident register and shared with the Executive Sponsor and, where relevant, Legal and the DPO.

Metrics (number of incidents, severity distribution, mean time to detect and respond) are reported to management periodically to inform risk decisions and investment.

---

## 11. Incident Report Template

> Complete one report per significant incident. Store in the incident register (reference: GTM-SEC-IRP register).

```
INCIDENT REPORT – GlobalTech Manufacturing
Classification: Internal – Confidential

1. INCIDENT IDENTIFICATION
   Incident Reference No.:
   Report Date:
   Report Author:
   Incident Response Manager:
   Current Status:            (Open / Contained / Eradicated / Recovered / Closed)
   Final Severity:            (Critical / High / Medium / Low)

2. SUMMARY
   Brief plain-language description of what happened:

3. DISCOVERY & CLASSIFICATION
   How detected:
   Date/time detected:
   Date/time reported to SOC:
   Provisional severity / Final severity:
   Site(s) / systems affected (IT / OT / IoT):
   Personal data involved?    (Yes / No – if yes, engage DPO)

4. TIMELINE OF EVENTS
   Date/Time | Event / Action | Performed by
   ----------|----------------|-------------

5. IMPACT ASSESSMENT
   Systems / production impact:
   Data impact (type, volume, sensitivity):
   Safety / OT impact:
   Business / financial / reputational impact:

6. RESPONSE ACTIONS
   Containment (short-term / long-term):
   Eradication (root cause / threat removal / validation):
   Recovery (restoration / testing / monitoring):

7. EVIDENCE
   Evidence collected:
   Chain-of-custody reference:
   Storage location:

8. COMMUNICATIONS & NOTIFICATIONS
   Internal stakeholders notified (who / when):
   Regulators notified?       (Authority / date / reference)
   Data subjects notified?     (Yes / No / N/A – date)
   Others (customers, law enforcement):

9. ROOT CAUSE
   Root cause:
   Contributing factors:

10. LESSONS LEARNED & ACTIONS
    What worked well:
    What to improve:
    Improvement actions (Action | Owner | Due date | Status):

11. APPROVAL
    Prepared by:                 Date:
    Reviewed by (IRM):           Date:
    Approved by (Exec Sponsor):  Date:
```

---

## 12. Enforcement

- Compliance with this policy is **mandatory** for all individuals within scope.
- Failure to report a known incident, interference with an investigation, or negligent handling of an incident may result in disciplinary action up to and including termination of employment or contract, and, where applicable, legal action – in accordance with local law and HR procedures.
- Deliberate concealment of an incident is treated as a serious violation.
- The **CISO** is responsible for enforcing this policy; **line managers** are responsible for ensuring their teams understand and follow it.
- Exceptions must be formally requested and approved in writing by the CISO and documented with a defined expiry date.

---

## 13. Review and Maintenance

This policy is reviewed **at least annually**, and additionally after any Critical incident, significant organizational change, or material change in legal or regulatory requirements. The Information Security Office owns the review; changes are approved by the Executive Leadership Team and recorded in the Version History.

---

## 14. Related Documents

- Information Security Policy (GTM-SEC-001)
- Data Protection & GDPR Policy
- Business Continuity & Disaster Recovery Plan
- OT/ICS Security Standard
- Acceptable Use Policy
- Data Classification & Handling Policy

---

*This document is the property of GlobalTech Manufacturing and is classified Internal – Confidential. Unauthorized distribution is prohibited. For questions, contact the Information Security Office at security-policy@globaltech-mfg.example.*
