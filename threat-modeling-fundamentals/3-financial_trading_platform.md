# Threat Model: Financial Trading Platform

**System under analysis:** A trading platform where users view real-time prices, execute buy/sell orders, transfer funds, and configure automated trading rules — under strict requirements for high availability (99.99% uptime), low latency (<100ms per trade), and regulatory compliance (SEC, FINRA).

**Why this system is distinctive:** Money moves in real time and irreversibly, decisions are made by automation at machine speed, downtime directly costs money, and regulators impose hard requirements on record-keeping, fairness, and resilience. Security here must coexist with punishing latency and uptime targets — which sets up genuine trade-offs, addressed below.

---

## 1. Most Critical CIA Component (and the Security vs. Performance Tension)

### The most critical component is Integrity.

In most financial-trading contexts, **integrity** is the top priority — the guarantee that orders, balances, prices, and trading rules are accurate, authentic, and unaltered. Here's the reasoning, contrasted against the other two:

**Integrity — the highest stakes.**
A trading platform's entire value rests on transactions being correct and trustworthy. If an attacker can modify an order (change quantity, price, or ticker), alter an account balance, tamper with the price feed, or forge a fund transfer, the result is direct, often irreversible financial loss and a collapse of trust in the market. Trades settle and money moves in ways that are extremely hard to unwind. Regulators (SEC/FINRA) require accurate, tamper-evident books and records precisely because integrity failures are catastrophic and can constitute market manipulation or fraud. An integrity breach can also be *silent* — corrupting outcomes before anyone notices.

**Availability — a very close second (and arguably co-critical).**
This system explicitly demands 99.99% uptime and <100ms latency, which tells you availability is near the top. If the platform is down or lagging during volatile markets, users cannot exit positions, automated rules fail to fire, and losses mount by the second — plus there are regulatory and reputational consequences. In some real-time-trading framings availability even ties integrity for first place. It ranks just below integrity here because an outage, while damaging, is usually *recoverable and visible*, whereas a silent integrity breach corrupts the ground truth itself.

**Confidentiality — critical, but third.**
Financial data (positions, strategies, PII) is sensitive, and a leak causes real harm — front-running of strategies, privacy violations, regulatory penalties. But of the three, a confidentiality breach is generally less immediately catastrophic than having your balances rewritten or being unable to trade. It's ranked third *for this system*, not because it's unimportant, but because integrity and availability are existential here.

**Summary ordering for this platform: Integrity ≈ Availability > Confidentiality**, with integrity edging ahead because its failures are irreversible and can be invisible.

### Can security requirements conflict with performance requirements?

**Yes — directly, and this is one of the defining challenges of the system.** The <100ms latency and 99.99% availability targets sit in real tension with thorough security:

- **Every security check adds latency.** Cryptographic verification, deep authorization checks, fraud/anomaly scoring, input validation, and multi-step MFA all consume milliseconds. On a hot trade path, adding synchronous checks can blow the 100ms budget.
- **Encryption has overhead.** TLS handshakes and payload encryption cost CPU and time; naive implementations add measurable latency to every request.
- **Logging and audit trails cost I/O.** Comprehensive, synchronous audit logging (required for compliance) competes with the low-latency path.
- **Availability vs. lockdown.** Aggressive security responses — locking accounts on suspicion, rate-limiting, failing closed — can *reduce* availability and block legitimate high-frequency activity, conflicting with the uptime goal.

**How mature platforms resolve the tension (rather than choosing one):**

- **Tiered/asynchronous controls:** Do the minimum blocking checks synchronously on the trade path (authN, authorization, hard limits) and push heavier analysis (fraud scoring, anomaly detection, full audit writes) to asynchronous pipelines that can halt or reverse suspicious activity moments later.
- **Fail-safe defaults chosen deliberately:** Decide per-action whether to *fail closed* (funds transfers — favor integrity) or *fail open with monitoring* (price viewing — favor availability).
- **Hardware acceleration & session reuse:** TLS termination on optimized hardware, session resumption, and connection pooling shrink crypto overhead.
- **Defense in depth so no single check must be exhaustive:** Layered controls (Section 3) mean the hot path can stay lean while other layers catch what it skips.

The goal is not to sacrifice one for the other, but to place the right control at the right layer with the right latency budget.

---

## 2. Threat Model: "Automated Trading Rules" Feature

Automated rules let users define conditions ("if AAPL < $150, buy 100 shares") that the system executes without a human in the loop. This is powerful and uniquely dangerous: flaws execute at machine speed, repeatedly, with real money, before anyone can intervene. Below are the top three risks.

### Risk 1 — Unauthorized creation or modification of trading rules (Tampering / Spoofing)

**Threat:** An attacker who compromises an account, exploits a broken authorization check (IDOR), or intercepts an API call creates or alters automated rules — e.g., adding a rule that repeatedly buys a worthless stock the attacker is pumping, or sells the victim's holdings into the attacker's order. Because rules run autonomously, the damage compounds without the victim present.
**Impact:** Direct financial theft, market manipulation (pump-and-dump), drained accounts, regulatory violations.
**Mitigation:**
- Strong authentication (MFA) *and* step-up verification specifically for creating/modifying automated rules — treat rule changes as high-privilege actions.
- Strict server-side authorization on every rule operation (verify the rule belongs to the requesting user; prevent IDOR).
- Immutable audit logging of every rule create/edit/delete with who/when/what, and user notifications on any rule change.
- Optional "cool-down"/confirmation window before a newly created high-impact rule goes live.

### Risk 2 — Logic flaws and runaway/erroneous execution (Denial of Service / financial self-harm)

**Threat:** A poorly-bounded rule, a logic bug, or an edge case (e.g., a rule with no maximum, a feedback loop between two rules, or a reaction to a bad price tick) causes runaway execution — placing thousands of orders in seconds, draining funds, or moving the market. This is the automated analogue of the real-world "flash crash" and fat-finger incidents. It can be triggered accidentally or deliberately.
**Impact:** Catastrophic user losses in seconds, market disruption, platform instability, regulatory scrutiny, breached latency/availability SLOs under order-flood load.
**Mitigation:**
- Hard, server-enforced limits: max orders per rule per time window, max position size, max spend, price sanity bounds ("circuit breakers").
- Rate limiting and throttling on automated order submission, independent of the rule logic.
- Kill-switch: a system- and user-level ability to instantly disable automated trading.
- Validate rules against sane-value constraints at creation, and sandbox/back-test before activation.
- Guard against acting on anomalous market data (reject implausible price ticks feeding rule conditions).

### Risk 3 — Race conditions and concurrency exploits (Tampering via timing)

**Threat:** Automated rules and manual actions operate concurrently on the same account balance/positions. An attacker exploits a race condition — e.g., triggering many simultaneous rule executions or fund actions that each check the balance before any debits it (a time-of-check-to-time-of-use flaw), allowing spending or selling more than the account holds ("double-spend"). Low-latency, high-concurrency systems are especially prone to this.
**Impact:** Overdrawn accounts, phantom purchases, inconsistent ledger state, financial loss, integrity failure of the books.
**Mitigation:**
- Atomic transactions with proper database locking / serializable isolation on balance and position updates.
- Idempotency keys on order and transfer requests so retries/duplicates don't double-execute.
- Optimistic or pessimistic concurrency control on account state; reconcile continuously.
- Single authoritative ledger as the source of truth, with all debits/credits passing through it atomically.

---

## 3. Defense-in-Depth After Account Compromise

**Assumption:** The attacker has valid credentials and is logged in as a legitimate user. The goal of defense-in-depth is that no single failure (here, credential theft) leads to total loss — each subsequent layer independently limits the blast radius. These layers are ordered from the perimeter inward.

### Layer 1 — Step-up authentication (MFA) on sensitive actions
Even with a stolen password/session, the attacker should hit a second wall the moment they attempt anything dangerous — fund transfers, adding a withdrawal destination, large trades, or changing security settings. Require re-authentication or a fresh MFA challenge for these high-risk operations, not just at login. This alone stops most account-takeover cash-outs, because the attacker rarely controls the second factor.

### Layer 2 — Transaction limits and controls
Hard, server-enforced limits cap how much damage any authenticated session can do: daily/per-transaction transfer and trade limits, maximum position sizes, and velocity limits. New external withdrawal accounts should face a mandatory holding/cool-down period (e.g., 24–72 hours) before funds can be sent there — a simple control that defeats fast cash-out even after full takeover. Limits convert a catastrophic breach into a bounded, survivable one.

### Layer 3 — Real-time anomaly and fraud detection
Behavioral monitoring flags activity inconsistent with the user's normal pattern: a login from a new device/country, a sudden large transfer, unusual trading in unfamiliar instruments, or rule changes at odd hours. Detection can trigger graduated responses — additional verification, temporary holds, or session termination. Because it runs (largely asynchronously) alongside the trade path, it catches what the fast synchronous checks let through, without breaking the latency budget.

### Layer 4 — Session management and controls
Strong session hygiene limits how long and how freely a hijacked session remains useful: short session timeouts, idle-logout, secure token handling (`HttpOnly`/`Secure`/`SameSite` cookies, short-lived rotated tokens), binding sessions to device/context, concurrent-session detection, and the ability to remotely revoke all sessions. If the compromise is via a stolen session token, these controls shrink its lifespan and reach.

### Layer 5 — Comprehensive audit logging and alerting
Immutable, timestamped logs of every security-relevant action (logins, transfers, trades, rule changes, setting changes) provide detection, forensic reconstruction, non-repudiation, and the regulatory record SEC/FINRA require. Coupled with real-time user notifications ("a transfer was initiated," "a new device signed in"), logging turns the *user themselves* into a detection layer who can raise the alarm and enables the platform to reconstruct and reverse fraudulent activity.

### Layer 6 (bonus) — Authorization / least privilege and segmentation
Even a fully authenticated user should only reach their own data and only the functions their role permits (enforced server-side on every request), preventing a compromised account from pivoting into others' data or admin functions. Sensitive operations (fund movement) run through separately-authorized, tightly-scoped services.

### Defense-in-depth summary

| Layer | Control | Limits damage by… |
|---|---|---|
| 1 | Step-up MFA on sensitive actions | Blocking cash-out/high-risk actions despite stolen login |
| 2 | Transaction limits + withdrawal holds | Capping and delaying the maximum extractable loss |
| 3 | Real-time anomaly/fraud detection | Catching and halting abnormal behavior in near-real-time |
| 4 | Session management & revocation | Shrinking the lifespan and reach of a hijacked session |
| 5 | Audit logging + user alerts | Enabling detection, reversal, and accountability |
| 6 | Authorization / least privilege | Preventing lateral movement beyond the one account |

**The core principle:** a single compromised credential should be an *incident*, not a *catastrophe*. Each layer assumes the previous one may have failed, so the attacker must defeat all of them — while the user is alerted and the activity is capped, delayed, detected, and logged at every step.
