# Task 4 - Risk Assessment Methodologies

## Scenario

**GlobalTech** faces a data breach risk caused by **misconfigured cloud storage exposing 50,000 customer records**.

> **Note:** FAIR requires quantitative estimates. Since the scenario does not provide historical incident data, the values below are reasonable assumptions for the exercise.

## FAIR Analysis

| **FAIR Component** | **Your Estimate** | **Reasoning** |
| :--- | :--- | :--- |
| **Threat Event Frequency (TEF)** (events/year) | 4 events/year | Assume attackers, automated scanners, or accidental access attempts reach the exposed cloud storage approximately four times per year. |
| **Vulnerability** (0-1 probability) | 0.25 | Assume there is a 25% probability that a threat event results in an actual loss event because exploitation still depends on factors such as discovery, access permissions, and attacker intent. |
| **Loss Event Frequency (LEF)** (TEF × Vuln) | 1 event/year | 4 × 0.25 = **1 expected loss event per year**. |

## Loss Magnitude

| **Loss Category** | **Estimated Cost** |
| :--- | ---: |
| Response & Investigation | $150,000 |
| Notification costs ($5/record) | $250,000 |
| Regulatory fines | $500,000 |
| Reputation damage | $600,000 |
| **Total Loss Magnitude (LM)** | **$1,500,000** |

### Loss Magnitude Calculation

- Notification cost = **50,000 records × $5 = $250,000**
- Total Loss Magnitude = **$150,000 + $250,000 + $500,000 + $600,000**
- **Total Loss Magnitude = $1,500,000**

## Final Calculation

| **Final Calculation** | **Value** |
| :--- | ---: |
| LEF × LM = **Annualized Risk** | **$1,500,000/year** |

### Calculation

**Annualized Risk = Loss Event Frequency × Loss Magnitude**

**Annualized Risk = 1 × $1,500,000 = $1,500,000 per year**

## Risk Treatment Recommendation

**Mitigate the risk.**

GlobalTech should prioritize remediation of the cloud storage misconfiguration by enforcing secure access controls, removing public exposure, applying least-privilege permissions, enabling continuous cloud configuration monitoring, and implementing automated alerts for storage misconfigurations.

The FAIR estimate indicates an **annualized risk exposure of approximately $1.5 million**. This provides a quantitative basis for comparing the cost of security controls against the expected financial loss. If the proposed mitigation costs substantially less than the expected annualized loss and significantly reduces either the threat event frequency, vulnerability, or loss magnitude, the treatment is financially justified.
