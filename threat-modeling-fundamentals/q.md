Please provide the answer to the task below as a downloadable markdown file:

## 0. E-commerce Platform

You are threat modeling an e-commerce platform where users can:

- Browse products (no authentication required)
- Add items to cart (no authentication required)
- Checkout and pay (authentication required)
- View order history (authentication required)

The system architecture includes:

- React frontend
- Node.js API backend
- PostgreSQL database
- Stripe payment integration

Questions:

1. **Identify three STRIDE threats** for the checkout process. For each threat, specify:
   - STRIDE category
   - Threat description
   - Potential impact
   - Suggested mitigation
2. **What trust boundaries exist** in this system? Describe at least three.

3. **Rate the threat of SQL injection** in the product search functionality using DREAD (provide scores for each factor and justify them).

**Hints**:

- For STRIDE threats: Consider what happens if a user modifies the price in the frontend request, or if someone intercepts the payment data
- For trust boundaries: Think about where data crosses from untrusted (user browser) to trusted (your server) zones
- For DREAD scoring: Consider how easy it is to find the search functionality and how many users would be affected by a data breach



Please provide the answer to the task below as a downloadable markdown file:

## 1. Healthcare Mobile App

A healthcare mobile app allows patients to:
- View medical records
- Schedule appointments
- Message healthcare providers
- Receive prescription refills

The app uses:
- Mobile client (iOS/Android)
- REST API backend
- Cloud-hosted database
- Integration with hospital systems

**Questions**:

1. Which asset is most critical in this system? Explain your reasoning using the CIA Triad.
2. Apply STRIDE to the "message healthcare providers" feature. List at least four threats.
3. What security controls would you prioritize to protect patient data? List five controls in order of priority and explain why.

**Hints**:

- For critical assets: Think about HIPAA regulations - what data is most sensitive? Consider all three CIA components
- For STRIDE on messaging: Can someone pretend to be a doctor? Can messages be modified? Can someone deny sending a message?
- For security controls: Start with authentication, then think about encryption, access controls, and audit logging




Please provide the answer to the task below as a downloadable markdown file:

## 2. IoT Smart Thermostat

A smart thermostat device:
- Connects to home Wi-Fi
- Controls heating/cooling systems
- Collects temperature data
- Receives commands from mobile app
- Updates firmware over-the-air

**Questions**:

1. **Identify IoT-specific threats** that don't typically apply to web applications. List at least five.
2. **What happens if an attacker gains physical access** to the device? Describe the attack chain and potential impacts.
3. **Design security controls** for the OTA (Over-The-Air) update process. What are the essential security requirements?

**Hints**:

- For IoT-specific threats: Think about physical tampering, weak default credentials, unencrypted communications, firmware vulnerabilities
- For physical access: Consider debug ports, memory extraction, hardware manipulation
- For OTA security: Think about code signing, secure boot, encrypted channels, rollback protection



Please provide the answer to the task below as a downloadable markdown file:

## 3. Financial Trading Platform

A trading platform allows users to:
- View real-time stock prices
- Execute buy/sell orders
- Transfer funds between accounts
- Set up automated trading rules

System requirements:
- High availability (99.99% uptime)
- Low latency (<100ms for trades)
- Regulatory compliance (SEC, FINRA)

**Questions**:

1. Which CIA component is most critical for this system and why? Can security requirements conflict with performance requirements?
2. Threat model the "automated trading rules" feature. What are the top three risks and how would you mitigate them?
3. An attacker compromises a user account. What defense-in-depth controls should limit the damage? List at least five layers of security.

**Hints**:

- For CIA priority: In financial systems, which is worse - data leak, data modification, or system downtime? Consider regulatory requirements
- For automated trading risks: Think about logic flaws, race conditions, and unauthorized rule modifications
- For defense-in-depth: Consider transaction limits, anomaly detection, MFA, session management, and audit trails
