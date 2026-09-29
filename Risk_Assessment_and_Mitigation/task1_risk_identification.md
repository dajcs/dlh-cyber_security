# Task 1 - Risk Identification

## Scenario

You are conducting a risk assessment for **SecureBank's online banking platform**, which serves **50,000 customers**.

The goal is to identify important assets, relevant threats, vulnerabilities that could be exploited or triggered, and clear risk statements describing the possible impact.

---

## Completed Risk Register

| **ID** | **Asset** | **Threat** | **Vulnerability** | **Risk Statement** |
| :----- | :-------- | :--------- | :---------------- | :----------------- |
| **R1** | Customer account and transaction data *(Information)* | Cyber attacker stealing sensitive data *(Adversarial)* | Weak input validation and insecure database queries | The **cyber attacker** exploiting **weak input validation and insecure database queries** in **customer account and transaction data systems** could cause **unauthorized disclosure or modification of customer information, financial loss, and regulatory penalties**. |
| **R2** | Online banking web application *(Software)* | Attacker gaining unauthorized account access *(Adversarial)* | Weak authentication controls, such as lack of multi-factor authentication or poor session management | The **attacker** exploiting **weak authentication and session controls** in the **online banking web application** could cause **account takeover, fraudulent transactions, and loss of customer trust**. |
| **R3** | Banking operations staff *(People)* | Employee accidentally exposing sensitive information *(Accidental)* | Insufficient security awareness and inadequate handling procedures for confidential data | The **employee error** exploiting **insufficient security awareness and weak data-handling procedures** among **banking operations staff** could cause **customer data exposure, privacy violations, and operational disruption**. |
| **R4** | Application and database servers *(Hardware)* | Server or storage hardware failure *(Structural)* | Lack of hardware redundancy and inadequate failover capability | The **hardware failure** exploiting **insufficient redundancy and failover capability** in **application and database servers** could cause **online banking outages, transaction delays, and loss of service availability**. |
| **R5** | Online banking availability and supporting infrastructure *(Services)* | Power outage, flood, fire, or other site disruption *(Environmental)* | Insufficient geographic redundancy and inadequate disaster recovery capability | The **environmental disruption** exploiting **insufficient geographic redundancy and disaster recovery capability** in **online banking services and supporting infrastructure** could cause **extended service outages and prevent customers from accessing banking services**. |

---

## Why These Risks Were Selected

The five entries cover several important parts of the banking platform rather than focusing only on cyberattacks.

- **Information:** Customer and transaction data are core banking assets and are highly sensitive.
- **Software:** The online banking application is directly exposed to customers and potentially to attackers.
- **People:** Human error remains a common source of security incidents.
- **Hardware:** The platform depends on reliable servers, storage, and infrastructure.
- **Services:** Availability itself is a critical asset because customers must be able to access banking functions.

The threats also span all four categories given in the exercise:

- **Adversarial:** R1 and R2
- **Accidental:** R3
- **Structural:** R4
- **Environmental:** R5

---

## Risk Statement Structure

Each risk statement follows the required pattern:

> The **[threat]** exploiting **[vulnerability]** in **[asset]** could cause **[impact]**.

This format is useful because it clearly links:

`Asset + Threat + Vulnerability -> Business Impact`

A strong risk statement should describe a possible business consequence, not just name a technical problem.

For example:

- Weak authentication by itself is a **vulnerability**.
- An attacker is the **threat**.
- The online banking application is the **asset**.
- Fraudulent transactions and account takeover are the **impacts**.

Together, these form the complete **risk**.
