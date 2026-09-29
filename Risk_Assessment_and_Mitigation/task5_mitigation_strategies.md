# Task 5 - Mitigation Strategies

## Scenario

**SecureBank** must protect its online banking platform from **SQL injection attacks**.

- **Budget:** $100,000
- **Timeline:** 90 days

## Defense-in-Depth Strategy

| **Layer** | **Control** | **Type** | **Cost** | **Priority** |
| :--- | :--- | :--- | ---: | :--- |
| **Network** | Deploy and tune a Web Application Firewall (WAF) with SQL injection detection/blocking rules and rate limiting | Tech | $20,000 | High |
| **Host** | Harden web/database servers, apply security patches, disable unnecessary services, and deploy host-based monitoring/EDR | Tech | $12,000 | Medium |
| **Application** | Remediate vulnerable code using parameterized queries/prepared statements, input validation, secure ORM usage, and SAST/DAST testing | Tech | $35,000 | Critical |
| **Data** | Enforce least-privilege database accounts, separate application/database roles, encrypt sensitive data, and improve database activity logging | Tech | $18,000 | High |
| **Administrative** | Secure coding training, SQL injection remediation standards, mandatory code review, and vulnerability management procedures | Admin | $10,000 | Medium |
| **TOTAL** |  |  | **$95,000** |  |

**Remaining contingency budget: $5,000**

## Why These Controls Work Together

SQL injection is primarily an **application-layer vulnerability**, so fixing the application code is the highest-priority control. Parameterized queries and prepared statements prevent user-controlled input from being interpreted as executable SQL.

The remaining controls provide additional layers of protection:

- The **WAF** can block common injection attempts before they reach the application.
- **Host hardening and monitoring** reduce the chance that a successful exploit leads to broader system compromise.
- **Database least privilege** limits the damage an attacker can cause if an injection vulnerability is exploited.
- **Administrative controls** reduce the probability that similar vulnerabilities are introduced again.

This approach follows the defense-in-depth principle: no single control is relied upon as the only security barrier.

## Implementation Timeline

| **Week** | **Action** |
| :--- | :--- |
| **1-2** | Perform SQL injection vulnerability assessment; deploy emergency WAF rules; patch internet-facing systems; identify vulnerable queries; review database privileges and logging. |
| **3-6** | Refactor vulnerable application code using parameterized queries/prepared statements; implement input validation; deploy SAST/DAST testing in the development pipeline; harden database accounts and access controls. |
| **7-12** | Complete remediation across the application; tune WAF and monitoring rules; conduct secure coding training; perform penetration testing and regression testing; verify logging, alerting, and least-privilege configuration. |

## Success Metric

**Zero exploitable SQL injection vulnerabilities in production at the end of the 90-day period, validated through SAST, DAST, and penetration testing, with 100% of database access using least-privilege service accounts and critical SQL injection alerts monitored through the WAF/SIEM.**

## Final Recommendation

SecureBank should prioritize **application-layer remediation first**, because eliminating vulnerable SQL queries directly addresses the root cause of SQL injection.

The proposed strategy costs **$95,000**, which remains within the **$100,000 budget**, leaving **$5,000 for contingency or additional testing**. The controls can reasonably be implemented within the **90-day timeline** while providing preventive, detective, and damage-limiting safeguards across multiple security layers.
