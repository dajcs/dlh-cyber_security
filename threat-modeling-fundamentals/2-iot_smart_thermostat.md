# Threat Model: IoT Smart Thermostat

**System under analysis:** A Wi-Fi-connected smart thermostat that controls home HVAC, collects temperature data, receives commands from a mobile app, and updates its firmware over-the-air (OTA).

**Why IoT is different:** Unlike a web app that lives entirely inside a controlled data center, this device is a physical object sitting in an untrusted environment (someone's wall), running on constrained hardware, often deployed for a decade with little maintenance. The attacker can hold the device in their hands, and the "endpoint" is now a target rather than a browser you don't control. That changes the threat landscape substantially.

---

## 1. IoT-Specific Threats (that don't typically apply to web apps)

These threats arise from the physical, hardware, and lifecycle characteristics of IoT devices — dimensions a purely server-side web application doesn't have.

**1. Physical tampering and hardware attacks.**
A web server lives in a locked data center; a thermostat lives on a wall accessible to anyone in the home (guests, tenants, cleaners, a landlord, a previous owner). An attacker can physically open the device, probe its circuit board, access debug ports (JTAG/UART), desolder and read flash memory chips, or attach a logic analyzer. This class of attack simply has no equivalent for a cloud-hosted web app.

**2. Weak, default, or hardcoded credentials.**
IoT devices are notorious for shipping with default passwords (admin/admin) or credentials/keys baked into the firmware image that are identical across every unit. If one device is dumped and its hardcoded key extracted, that key may unlock every device of that model in the world. Web apps generally provision unique per-user secrets server-side; mass-produced identical device secrets are an IoT-specific failure mode (the Mirai botnet exploited exactly this).

**3. Unencrypted or weakly-encrypted local communications.**
Constrained devices often skip TLS to save resources, or use it improperly (no certificate validation). Traffic between the thermostat, the local Wi-Fi, the mobile app, and the cloud may travel in cleartext or over weak protocols, letting an attacker on the same network sniff commands, temperature data, and control messages. Home networks are far less controlled than a data-center backbone.

**4. Insecure OTA firmware updates.**
The ability to push new firmware is powerful and dangerous. If updates aren't signed and verified, an attacker can push malicious firmware and gain persistent, low-level control of the device. Firmware is the whole software stack (not just an app layer), so a firmware compromise is total and durable — this attack surface doesn't exist for a browser-based web client.

**5. Long lifecycle, no patching, and abandonment.**
Thermostats are installed and forgotten for 10+ years. Vendors may stop issuing security patches, leaving known vulnerabilities permanently unaddressed on live devices. Users rarely update IoT firmware manually, and devices may never be rebooted. Web apps are centrally patched by the operator in minutes; a fleet of unpatched embedded devices in the field is a distinctly IoT problem.

**Additional IoT-specific threats worth noting:**

- **Insecure device provisioning / onboarding:** The initial Wi-Fi setup (often via an open AP or Bluetooth pairing) can leak Wi-Fi credentials or let an attacker hijack the pairing.
- **Botnet conscription:** Compromised devices are mass-recruited into DDoS botnets — the device's value to an attacker is its network position, not its data.
- **Physical safety impact:** Because the device controls HVAC, a compromise has real-world physical consequences (see Section 2) — a purely digital web breach usually doesn't freeze someone's pipes.
- **Supply-chain / component trust:** Third-party chips, radios, and SDKs may carry backdoors or vulnerabilities baked in before the device ever ships.

---

## 2. Physical Access Attack Chain

Physical access is often game-over for embedded devices, because most of their defenses assume the attacker only reaches them over the network. Here is a representative attack chain and its consequences.

### Attack chain (step by step)

**Step 1 — Acquire and open the device.**
The attacker obtains a unit (their own, a returned/second-hand unit, or one pried off a wall) and opens the enclosure — typically trivial, held by clips or a few screws with no tamper-evident seals.

**Step 2 — Identify debug and test interfaces.**
On the exposed PCB, the attacker locates debug ports — **UART** (serial console), **JTAG/SWD** (chip debug/programming), and test pads. Manufacturers frequently leave these active in production for cost/convenience. A UART console often drops straight into a root shell or bootloader with no authentication.

**Step 3 — Extract firmware and secrets from memory.**
Using JTAG, a chip programmer, or by desoldering the flash/EEPROM and reading it in an external reader, the attacker dumps the entire firmware image and storage. From this they can recover: hardcoded credentials and API keys, Wi-Fi passwords stored in plaintext, cloud endpoints and protocols, encryption keys, and the update-signing scheme.

**Step 4 — Analyze and find vulnerabilities.**
Offline, the attacker reverse-engineers the firmware to understand the command protocol, discover bugs, and identify shared secrets. Because the firmware is often identical across all units, findings generalize to the entire product line.

**Step 5 — Manipulate hardware / firmware.**
The attacker modifies the firmware and reflashes it (if secure boot is absent), tampers with sensor inputs, or uses fault-injection/glitching to bypass checks. They can implant a persistent backdoor.

**Step 6 — Pivot and scale.**
With extracted keys and cloud endpoints, the attacker moves from one physical device to remote attacks against the vendor's fleet and cloud, or uses the recovered Wi-Fi credentials to pivot deeper into the victim's home network (the thermostat becomes a foothold onto laptops, NAS drives, cameras, etc.).

### Potential impacts

- **Full device compromise:** Persistent root control, backdoored firmware surviving reboots.
- **Credential and key theft:** Home Wi-Fi password, cloud API keys, and per-model shared secrets — enabling fleet-wide and network-wide attacks.
- **Home network pivot:** The thermostat becomes an entry point to every other device on the home network.
- **Privacy loss:** Temperature/occupancy patterns reveal when the home is empty — useful for physical burglary.
- **Physical/safety harm:** Malicious HVAC control can freeze pipes in winter, cause dangerous overheating, run up energy bills, or wear out equipment.
- **Fleet-wide compromise:** Because secrets are shared across units, breaking one device can yield attacks against all of them.

### Defenses that raise the cost of physical attacks

Disable or lock debug ports (JTAG/UART) in production; encrypt data and secrets at rest and store keys in a secure element / TPM rather than plain flash; use unique per-device keys (never shared); enable **secure boot** so only signed firmware runs; add tamper detection/evidence; and never store Wi-Fi credentials or keys in plaintext.

---

## 3. Secure OTA Update Design

OTA is the most security-sensitive feature on the device: it can replace the *entire* software stack remotely. Done wrong, it's a remote-code-execution channel to the whole fleet; done right, it's the mechanism that keeps devices patched for a decade. The design must guarantee that a device installs **only** firmware that is authentic, unmodified, current, and intended for it.

### Essential security requirements

**1. Code signing and integrity verification (authenticity).**
Every firmware image must be cryptographically signed by the vendor with a private key held in an offline/HSM-protected environment. The device verifies the signature against a public key baked into its trust store **before** installing. This ensures the image genuinely came from the vendor and was not modified. Pair the signature with a cryptographic hash check of the full image so any bit-flip or truncation is caught. *Without this, an attacker can push arbitrary malicious firmware — the single most important OTA control.*

**2. Secure boot (chain of trust).**
Signing the update only helps if the device also refuses to *run* unsigned code. Secure boot establishes a hardware-rooted chain of trust: an immutable boot ROM verifies the bootloader, which verifies the firmware, each stage checking the next's signature. This closes the gap where an attacker with physical access reflashes malicious firmware directly, bypassing the OTA path entirely.

**3. Encrypted and authenticated transport (confidentiality + MITM protection).**
Deliver updates over TLS 1.2+ with proper server certificate validation (ideally certificate pinning). This prevents an on-path attacker from tampering with the download, injecting a malicious image, or learning about vulnerabilities by inspecting the firmware contents. Encryption also protects any proprietary code in the image.

**4. Rollback / anti-downgrade protection (freshness).**
Attackers may try to install an older, legitimately-signed but *vulnerable* firmware version to re-open a patched hole. The device must track a monotonic version counter (or security epoch) and refuse to install any image older than what's currently running. This prevents "downgrade attacks" while still allowing controlled, vendor-authorized emergency rollbacks if designed carefully.

**5. Fail-safe installation with A/B partitions and atomic updates (availability/recovery).**
A failed or interrupted update must never brick the device. Use dual (A/B) firmware partitions: write the new image to the inactive slot, verify it, then atomically switch the boot pointer. If the new firmware fails to boot or pass a post-boot health check, the device automatically reverts to the known-good partition. This preserves availability — critical for a device controlling home heating.

**6. Device authentication and targeting.**
The update server should authenticate each device (unique per-device identity/certificate) so updates can be correctly targeted and so a rogue actor can't trivially pull firmware or spoof the fleet. This also prevents pushing the wrong hardware variant's image to a device.

### Putting it together — a secure OTA flow

1. Device authenticates to the update server over pinned TLS and reports its current signed version.
2. Server offers an update only if it is newer and matches the device's hardware variant.
3. Device downloads the encrypted image over TLS into the **inactive** A/B partition.
4. Device verifies the image's **signature** and **hash** against its embedded public key, and checks the version is **not a downgrade**.
5. Only on full success does the device atomically switch the boot pointer to the new partition.
6. **Secure boot** re-verifies the signature at next boot; a post-boot health check confirms the device is functional.
7. If verification, boot, or health check fails at any point, the device **automatically rolls back** to the known-good partition.

### OTA requirements summary

| Requirement | Protects against | CIA property |
|---|---|---|
| Code signing + hash verification | Malicious/forged firmware | Integrity, Authenticity |
| Secure boot | Running unsigned/reflashed code | Integrity |
| Encrypted + pinned transport (TLS) | MITM injection, eavesdropping | Confidentiality, Integrity |
| Anti-rollback / version counter | Downgrade to vulnerable versions | Integrity |
| A/B partitions + atomic update + health check | Bricking, failed updates | Availability |
| Per-device authentication | Fleet spoofing, mistargeted images | Authenticity |

Together, these ensure the device runs **only** firmware that is authentic (signed), unmodified (hash-verified), current (anti-rollback), confidentially delivered (TLS), and recoverable (A/B) — turning the most dangerous feature on the device into one of its strongest defenses.
