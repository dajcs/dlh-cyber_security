# Risk Fundamentals Exercise

## Scenario

**Risk:** SQL injection vulnerability in customer database

- **Asset Value (AV):** $2,000,000
- **Exposure Factor (EF):** 40% = 0.40
- **Annual Rate of Occurrence (ARO):** 0.3

---

## Calculations

### 1. Single Loss Expectancy (SLE)

Formula:

`SLE = Asset Value × Exposure Factor`

Calculation:

`SLE = $2,000,000 × 0.40`

`SLE = $800,000`

So, the estimated loss from one successful SQL injection incident is **$800,000**.

### 2. Annual Loss Expectancy (ALE)

Formula:

`ALE = SLE × Annual Rate of Occurrence`

Calculation:

`ALE = $800,000 × 0.3`

`ALE = $240,000`

So, the expected annualized loss from this risk is **$240,000 per year**.

---

## Qualitative Assessment

### Threat

The threat is an **attacker exploiting SQL injection to gain unauthorized access to the customer database**.

### Vulnerability

The vulnerability is **insufficient input validation / use of unsafe SQL queries that allow attacker-controlled input to be interpreted as SQL commands**.

### Likelihood

**Medium**

Reasoning: an ARO of `0.3` means the event is expected, statistically, about **0.3 times per year**, or roughly **once every 3.33 years**:

`1 ÷ 0.3 ≈ 3.33 years`

That suggests a meaningful but not extremely frequent occurrence, so **Medium** is a reasonable qualitative classification.

### Impact

**High**

Reasoning: the asset value is $2,000,000 and the exposure factor is 40%, producing an estimated single-event loss of $800,000. A compromise of customer records can also affect confidentiality, operations, and reputation, so the impact is reasonably classified as **High**.

### Risk Level

Using the supplied matrix:

- **Likelihood:** Medium
- **Impact:** High
- **Matrix result:** **High**

### Treatment

**Mitigate**

Reasoning: SQL injection is a remediable technical vulnerability. Appropriate controls such as parameterized queries, prepared statements, server-side input validation, least-privilege database permissions, secure coding practices, and application security testing can materially reduce the likelihood of exploitation.

---

## Completed Risk Assessment Table

| **Component**                                  | **Your Answer** |
| :--------------------------------------------- | :-------------- |
| **Threat**                                     | Attacker exploiting SQL injection to gain unauthorized access to the customer database |
| **Vulnerability**                              | Insufficient input validation / unsafe SQL queries that allow attacker-controlled input to execute as SQL |
| **Likelihood** (Low/Medium/High)               | Medium |
| **Impact** (Low/Medium/High)                   | High |
| **Risk Level** (use matrix)                    | High |
| **SLE** (Asset × EF)                           | $800,000 |
| **ALE** (SLE × ARO)                            | $240,000 per year |
| **Treatment** (Mitigate/Transfer/Accept/Avoid) | Mitigate |

---

## Risk Matrix:

|                             | **Low Impact** | **Medium** | **High** |
| :-------------------------- | :------------- | :--------- | :------- |
| **High Likelihood**         | Medium         | High       | Critical |
| **Medium Likelihood**       | Low            | Medium     | High     |
| **Low Likelihood**          | Low            | Low        | Medium   |

---

## Quick Check

`SLE = $2,000,000 × 40% = $800,000`

`ALE = $800,000 × 0.3 = $240,000/year`

`Medium Likelihood + High Impact = High Risk`
