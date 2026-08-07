# RetailMax Corporation – Security Policy Program Review & Gap Analysis

**Prepared for:** RetailMax Corporation – Executive Leadership & Information Security Steering Committee

**Prepared by:** [Consultant Name], Security Consultant – [Consulting Firm]

**Engagement:** Security Policy Program Assessment (PCI-DSS, ISO 27001, SOC 2 Type II readiness)

| Document Control | Detail |
|------------------|--------|
| Document title | Security Policy Program Review & Gap Analysis |
| Version | 1.0 |
| Status | Final – for management review |
| Classification | Confidential |
| Author | [Consultant Name] |
| Approved by | [CISO / Sponsor Name] |
| Approval date | [YYYY-MM-DD] |
| Issue date | [YYYY-MM-DD] |
| Next review date | [Approval date + 12 months] |
| Questions / contact | security-governance@retailmax.example – [Consultant email] |

---

## 1. Executive Summary

RetailMax Corporation is pursuing three concurrent assurance objectives – **PCI-DSS certification** (it stores, processes, and transmits cardholder data), **ISO 27001 certification**, and a **SOC 2 Type II audit**. This assessment reviews the company's current security policy program against those frameworks, measures the maturity of existing policies, and lays out a prioritized, time-bound plan to reach audit readiness.

**Current state.** RetailMax maintains three active policies – Information Security, Password, and Acceptable Use – and is missing three foundational policies: **Incident Response, Data Classification, and Access Control**. The existing policies are all materially out of date (2019–2021), predating current versions of the target frameworks, and none show evidence of the monitoring, formal review cadence, or version control the frameworks expect.

**Key findings.**

- **Three critical policy gaps.** The absence of Incident Response, Data Classification, and Access Control policies blocks certification against all three frameworks. PCI-DSS in particular requires a documented and tested incident response plan (Req. 12.10), data classification and retention practices (Req. 3 / 9.5), and least-privilege access control (Req. 7). These are not optional.
- **Existing policies are stale.** All three active policies pre-date PCI-DSS v4.0 (mandatory since 31 March 2024) and were not written to the ISO 27001:2022 control set. They require substantive rewrites, not just re-dating.
- **Weak program governance.** There is no consistent version control, no documented owner and review cycle, no evidence of communication/acknowledgement tracking, and no measurement of policy effectiveness. This is the difference between "we have a document" and "we operate a control."
- **Maturity is low but not zero.** The three active policies sit at maturity **Level 1–2** (documented but inconsistently followed and unmeasured). No existing policy reaches Level 3 (defined, communicated, and followed).

**Overall readiness.** RetailMax is **not currently ready** for any of the three certifications. However, the gaps are well understood and addressable within a **12-month program**. The recommended approach front-loads the three missing critical policies and a governance framework in the first quarter, refreshes existing policies in the second quarter, and spends the back half of the year on implementation, evidence collection, and continuous-improvement mechanisms – the exact operating history a SOC 2 **Type II** audit requires.

**Recommended investment focus.** The highest-value early actions are (1) stand up a policy governance framework (owners, version control, review cadence, approval workflow), (2) author the three missing critical policies, and (3) refresh the three stale policies to the current framework versions. Everything else builds on those foundations.

---

## 2. Part A – Gap Analysis Against PCI-DSS

The table below maps RetailMax's policy inventory against the relevant PCI-DSS v4.0 requirement areas. "Gap severity" reflects impact on certification: **Critical** = certification blocker; **High** = significant finding likely; **Medium** = remediation needed but not blocking.

| PCI-DSS Req. Area | Requirement (summary) | Governing Policy Needed | RetailMax Current State | Gap Severity | Gap Description |
|---|---|---|---|---|---|
| Req. 1 & 2 | Secure network, firewall configuration, no vendor defaults | Information Security Policy | Active (2019) | High | Policy exists but pre-dates v4.0; network security standards likely incomplete and unmapped to current requirements. |
| Req. 3 | Protect stored account data; retention & disposal | Data Classification Policy | **Missing** | Critical | No data classification or retention policy. Cannot demonstrate how cardholder data is identified, minimized, retained, or securely disposed. |
| Req. 4 | Encrypt cardholder data in transit | Information Security Policy | Active (2019) | High | Encryption-in-transit standards not evidenced or dated to current requirements. |
| Req. 5 & 6 | Anti-malware; secure development; patch management | Information Security Policy | Active (2019) | Medium | Referenced at a high level but likely lacks current vulnerability-management and secure-SDLC specifics. |
| Req. 7 | Restrict access by business need-to-know (least privilege) | Access Control Policy | **Missing** | Critical | No access control policy. Cannot demonstrate least-privilege, role-based access, or need-to-know enforcement. |
| Req. 8 | Identify users & authenticate access (incl. MFA) | Password Policy | Active (2020) | High | Password policy exists but pre-dates v4.0 MFA and authentication requirements (e.g., 12-char minimums, MFA for all CDE access). Needs rewrite. |
| Req. 9 | Restrict physical access; media handling | Data Classification Policy / Info Sec Policy | **Missing** (classification) | Critical | Media handling and physical data protection depend on classification, which does not exist. |
| Req. 10 | Log and monitor all access | Information Security Policy / Access Control Policy | Partial / Missing | High | Logging/monitoring standards not evidenced; monitoring depends on access control policy that is missing. |
| Req. 11 | Test security of systems and networks | Information Security Policy | Active (2019) | Medium | Vulnerability scanning / pen-test cadence likely not documented to current standard. |
| Req. 12.1–12.9 | Maintain an information security policy; risk assessment; awareness; personnel & vendor management | Information Security Policy / Acceptable Use Policy | Active (2019 / 2021) | High | Umbrella policy is stale; annual review, formal risk assessment, and third-party management provisions likely absent. |
| Req. 12.10 | Incident response plan (documented & tested) | Incident Response Policy | **Missing** | Critical | No incident response policy or plan. This is an explicit, mandatory PCI-DSS requirement and a certification blocker. |
| Req. 12.6 | Security awareness program | Acceptable Use Policy | Active (2021) | Medium | AUP exists but awareness program formalization and acknowledgement tracking are likely missing. |

**Cross-framework note.** The three missing policies are equally material to ISO 27001:2022 (Annex A controls: A.5.24–A.5.30 incident management, A.5.9–A.5.13 asset/information classification, A.5.15–A.5.18 access control) and to the SOC 2 Common Criteria (CC6 logical/physical access, CC7 system operations & incident response). Closing the PCI-DSS gaps closes the bulk of the ISO 27001 and SOC 2 policy gaps simultaneously.

---

## 3. Part B – Policy Maturity Assessment

Each policy is scored on the 0–5 maturity scale defined in the task. Scores reflect the policy's documentation, communication, adherence, and measurement – not merely whether a file exists.

**Maturity scale reference:** 0 Non-existent · 1 Initial · 2 Developing · 3 Defined · 4 Managed · 5 Optimized

| Policy | Current Maturity | Rationale | Target Maturity (12 mo.) |
|---|---|---|---|
| Information Security Policy (2019) | **2 – Developing** | Documented and organization-wide, but stale (pre-v4.0), no evidence of consistent adherence, review cadence, or measurement. | 4 – Managed |
| Password Policy (2020) | **2 – Developing** | Documented, but pre-dates current MFA/authentication requirements; enforcement and monitoring not evidenced. | 4 – Managed |
| Acceptable Use Policy (2021) | **1 – Initial** | Documented but appears ad-hoc; no evidence of acknowledgement tracking, communication program, or enforcement follow-through. | 3 – Defined |
| Incident Response Policy | **0 – Non-existent** | No policy exists. | 4 – Managed (must be tested, per PCI Req. 12.10) |
| Data Classification Policy | **0 – Non-existent** | No policy exists. | 3 – Defined |
| Access Control Policy | **0 – Non-existent** | No policy exists. | 4 – Managed |

**Program-level maturity:** Weighted across the six policies, RetailMax's policy program currently sits at approximately **Level 1 (Initial)**. Certification readiness generally requires the program to operate at **Level 3 (Defined)** or above, with critical control areas (incident response, access control) demonstrating **Level 4 (Managed)** through monitoring and testing – a particular emphasis for SOC 2 Type II, which evaluates operating effectiveness over a period.

---

## 4. Part C – Prioritized Recommendations

Recommendations are ordered by risk-weighted priority. **Effort:** H = High, M = Medium, L = Low. **Timeline** is elapsed weeks from program start.

| Priority | Recommendation | Justification | Effort | Timeline |
|---|---|---|---|---|
| 1 | Establish a **policy governance framework** (assign policy owners, version control, standard template, approval workflow, annual review cadence, acknowledgement tracking). | Nothing else is auditable without governance. Underpins ISO 27001 Clause 5/7, PCI Req. 12.1, SOC 2 CC1/CC5. Prevents future staleness. | M | Weeks 1–3 |
| 2 | Author and approve the **Incident Response Policy** and supporting plan. | Mandatory PCI-DSS Req. 12.10; ISO A.5.24–A.5.28; SOC 2 CC7.3–7.5. Hard certification blocker. Also reduces real breach impact. | H | Weeks 2–6 |
| 3 | Author and approve the **Access Control Policy** (least privilege, RBAC, need-to-know, joiner/mover/leaver, periodic access review). | Mandatory PCI-DSS Req. 7; ISO A.5.15–A.5.18; SOC 2 CC6. Highest-risk control area for a card-processing retailer. | H | Weeks 3–8 |
| 4 | Author and approve the **Data Classification Policy** (classification tiers, handling rules, retention & secure disposal, cardholder-data flows). | Mandatory PCI-DSS Req. 3/9; ISO A.5.9–A.5.13; SOC 2 CC6.1. Enables data minimization and correct scoping of the CDE. | H | Weeks 4–9 |
| 5 | **Rewrite the Password Policy** to PCI-DSS v4.0 authentication standards (12-char minimum, MFA for all CDE and admin access, credential lifecycle). | Password policy is stale (2020) and pre-dates mandatory v4.0 MFA rules. PCI Req. 8; SOC 2 CC6.1. | M | Weeks 6–9 |
| 6 | **Refresh the Information Security Policy** to align with PCI-DSS v4.0, ISO 27001:2022 Annex A, and SOC 2 CC – including risk assessment, vendor management, and annual review. | Umbrella policy is 6 years old and unmapped to current control sets. PCI Req. 1–2, 4–6, 10–12; ISO Clause 5/6. | H | Weeks 7–12 |
| 7 | **Refresh the Acceptable Use Policy** and stand up a formal **security awareness program** with acknowledgement tracking. | AUP is ad-hoc (Level 1). PCI Req. 12.6; ISO A.6.3; SOC 2 CC1.4/CC2. Raises the weakest-scoring policy to Defined. | M | Weeks 10–14 |
| 8 | Implement **monitoring and metrics** for each policy (access reviews, IR test results, exception tracking, KPI dashboard). | Moves critical policies from Defined (L3) to Managed (L4). Required for SOC 2 Type II operating-effectiveness evidence. | M | Weeks 14–26 |
| 9 | Conduct a **tabletop incident response test** and a first **periodic access review** cycle; capture evidence. | PCI Req. 12.10 requires the IR plan to be tested; provides SOC 2 Type II evidence of operation. | M | Weeks 18–26 |
| 10 | Establish **continuous improvement** – internal audit, management review, corrective-action tracking (path to Level 5). | ISO 27001 Clause 9/10; SOC 2 CC4. Sustains readiness beyond initial certification. | L | Weeks 26–52 |

---

## 5. Part D – 12-Month Implementation Roadmap

The roadmap is organized into four quarterly phases. Each phase names its objectives, key deliverables, and the maturity outcome it targets.

### Phase 1 – Foundation & Critical Gaps (Months 1–3)

**Objective:** Stand up governance and close the three certification-blocking policy gaps.

- Establish the policy governance framework: owners, standard template, version control, approval workflow, review cadence (Rec. 1).
- Author, approve, and publish the **Incident Response Policy** (Rec. 2), **Access Control Policy** (Rec. 3), and **Data Classification Policy** (Rec. 4).
- Communicate new policies organization-wide; begin acknowledgement tracking.

**Outcome:** Missing policies move from Level 0 to Level 3 (Defined). Governance framework operational.

### Phase 2 – Refresh Existing Policies (Months 4–6)

**Objective:** Bring the three stale active policies up to current framework versions.

- Rewrite the **Password Policy** to PCI-DSS v4.0 (Rec. 5).
- Refresh the **Information Security Policy** to PCI-DSS v4.0 / ISO 27001:2022 / SOC 2 CC (Rec. 6).
- Refresh the **Acceptable Use Policy** and launch the security awareness program (Rec. 7).

**Outcome:** All six policies at Level 3 (Defined). Full policy set aligned to all three frameworks.

### Phase 3 – Operationalize, Monitor & Measure (Months 7–9)

**Objective:** Turn documented policies into operating, measurable controls.

- Implement monitoring and KPIs for each policy; build the compliance dashboard (Rec. 8).
- Run the first periodic access review cycle and conduct an incident response tabletop test; retain evidence (Rec. 9).
- Perform a mock/readiness assessment against PCI-DSS and ISO 27001; remediate findings.

**Outcome:** Critical policies (Incident Response, Access Control, Information Security, Password) reach Level 4 (Managed). Operating-effectiveness evidence accumulating for SOC 2 Type II.

### Phase 4 – Audit Readiness & Continuous Improvement (Months 10–12)

**Objective:** Achieve certification readiness and establish sustainable improvement.

- Conduct internal audit and management review; open and track corrective actions (Rec. 10).
- Complete evidence packages for PCI-DSS assessment, ISO 27001 Stage 1/2, and the SOC 2 Type II observation period.
- Engage the QSA / certification body / SOC 2 auditor for formal assessment.
- Establish the annual review and continuous-improvement cycle (path toward Level 5).

**Outcome:** Program operating at Level 4 with a defined improvement loop. RetailMax audit-ready for all three frameworks.

### Roadmap at a Glance

| Phase | Months | Focus | Key Deliverables | Maturity Target |
|---|---|---|---|---|
| 1 | 1–3 | Foundation & critical gaps | Governance framework; IR, Access Control, Data Classification policies | Missing policies → L3 |
| 2 | 4–6 | Refresh existing policies | Rewritten Password & InfoSec policies; refreshed AUP + awareness program | All policies → L3 |
| 3 | 7–9 | Operationalize & measure | Monitoring/KPIs; access review; IR tabletop test; mock assessment | Critical policies → L4 |
| 4 | 10–12 | Audit readiness & improvement | Internal audit; evidence packages; certification engagement; CI loop | Program at L4, CI established |

---

## 6. Assumptions, Constraints & Next Steps

**Assumptions.** The current-state inventory reflects the policies provided; no additional undocumented policies exist. Executive sponsorship and a named program owner (CISO or equivalent) are available. Subject-matter experts across IT, security, HR, and legal can be engaged as needed.

**Constraints.** Timelines assume dedicated resourcing for policy authoring and no major competing initiatives. Concurrent pursuit of three frameworks increases coordination effort but yields significant overlap savings, which this roadmap deliberately exploits.

**Immediate next steps (first 30 days).**
1. Appoint a program owner and confirm the executive sponsor.
2. Approve the policy governance framework and standard template.
3. Begin drafting the Incident Response Policy (highest-priority missing critical policy).
4. Schedule a program kickoff and align stakeholders on the 12-month plan.

---

## 7. Document Governance

| Field | Detail |
|---|---|
| Version | 1.0 |
| Author | [Consultant Name], [Consulting Firm] |
| Reviewed by | [Reviewer Name] |
| Approved by | [CISO / Sponsor Name] |
| Approval date | [YYYY-MM-DD] |
| Review cycle | Annual, or upon significant change to PCI-DSS, ISO 27001, or SOC 2 criteria |
| Next review date | [Approval date + 12 months] |
| Distribution | Executive Leadership, Information Security Steering Committee (Confidential) |
| Questions / contact | security-governance@retailmax.example – [Consultant email] |

### Version History

| Version | Date | Author | Summary of Changes |
|---|---|---|---|
| 0.1 | [YYYY-MM-DD] | [Consultant] | Initial draft |
| 1.0 | [YYYY-MM-DD] | [Consultant] | Final for management review |

---

*Prepared as part of the RetailMax security policy program assessment engagement. This document assesses policy program readiness and does not itself constitute certification against PCI-DSS, ISO 27001, or SOC 2.*
