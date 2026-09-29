# Task 2: Risk Analysis

**Scenario:** Unauthenticated remote code execution (RCE) on a web server. Asset value = **$500,000**; exposure factor (EF) = **80%**; annual rate of occurrence (ARO) = **0.2**.

## CVSS v3.1 Base score

The vulnerability description does not specify every CVSS property. This worked answer assumes that an attacker can reach the web service across a network, exploitation needs no special preconditions or victim action, and successful code execution can fully compromise the vulnerable server. The impact remains within the web server's security authority. If the actual vulnerability has constraints or different consequences, its CVSS metrics and score should be adjusted.

| CVSS metric | Your value | Justification |
| :--- | :--- | :--- |
| Attack Vector (N/A/L/P) | **N** (Network) | The web server can be attacked remotely over a network. |
| Attack Complexity (L/H) | **L** (Low) | No special conditions beyond reaching the vulnerable service are specified. |
| Privileges Required (N/L/H) | **N** (None) | The RCE is explicitly unauthenticated. |
| User Interaction (N/R) | **N** (None) | The attacker can trigger exploitation without another user's action, as assumed here. |
| Scope (U/C) | **U** (Unchanged) | The assumed impact is within the vulnerable server's security authority; code execution alone does not establish a scope change. |
| Confidentiality (N/L/H) | **H** (High) | Full server compromise could expose all information accessible to the web server. |
| Integrity (N/L/H) | **H** (High) | The attacker could alter data and software accessible to the web server. |
| Availability (N/L/H) | **H** (High) | The attacker could stop or disrupt the web service. |
| **CVSS Score** | **9.8 / 10 (Base)** | Calculated from the vector below. |
| **Severity** | **Critical** | CVSS v3.1 labels scores from 9.0 to 10.0 Critical. |

**Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`

### Score calculation

Using the CVSS v3.1 metric weights and formulas:

1. Impact subscore: `ISS = 1 − (1 − 0.56)^3 = 0.914816`.
2. With unchanged scope: `Impact = 6.42 × ISS = 5.87311872`.
3. Exploitability: `8.22 × 0.85 × 0.77 × 0.85 × 0.85 = 3.887042775`.
4. Base score: `Roundup(min(Impact + Exploitability, 10)) = Roundup(9.760161495) = 9.8`. Here `Roundup` means rounding upward to one decimal place, as specified by CVSS v3.1.

## Financial analysis

| Financial metric | Calculation | Result |
| :--- | :--- | ---: |
| **SLE** (single loss expectancy) | `$500,000 × 0.80` | **$400,000 per event** |
| **ALE** (annual loss expectancy) | `$400,000 × 0.2` | **$80,000 per year** |

An ARO of 0.2 means an average of 0.2 occurrences per year under the scenario's estimate. ALE is an expected annual loss, not a forecast that $80,000 is lost each year. The CVSS score describes technical severity and is separate from this financial estimate.

**Source for CVSS equations, metric weights, and severity bands:** [FIRST, CVSS v3.1 Specification Document](https://www.first.org/cvss/v3-1/specification-document).
