# M07 | MongoDB No-Auth Data Breach

**Mission:** M07 // HIGH  
**Environment:** Browser-based simulated security lab  
**Target:** `10.0.2.15`  
**Service:** MongoDB 4.0.28 on TCP port `27017`  
**Weakness:** Missing Authentication for Critical Function (CWE-306)  
**Lab severity:** Critical, CVSS 10.0 (as reported by the simulator)  
**Status:** Completed, flag captured

## Executive summary

The exercise demonstrated how a MongoDB server with authentication disabled can expose its database metadata and contents to anyone who can reach its MongoDB port. The three stages were (1) discover and fingerprint MongoDB, (2) establish an unauthenticated shell session, and (3) inspect records, export the database contents, and locate the lab flag. The simulator reported that **284,492 customer records** were dumped, including plaintext Social Security numbers (SSNs) and payment-card data.

**Captured flag:** `c160b23374436bb938ac95a9f5bbf7ed`  
**Flag file reported by the lab:** `~/flags/flag6.txt`

> **Evidence distinction:** The results below reproduce the outputs and completion claims provided by the simulated lab. The full database dump and individual sensitive records were not supplied for separate verification. No customer PII is reproduced in this report.

## Step 1: Discovery, identify unauthenticated MongoDB

### Commands

Optional subnet discovery:

```bash
nmap -p 27017 --open 10.0.2.0/24
```

Targeted service detection and MongoDB enumeration:

```bash
nmap -sV -p 27017 --script mongodb-info 10.0.2.15
```

### Parameters

| Parameter | Meaning | Reason for use |
|---|---|---|
| `nmap` | Network scanner | Determine which hosts expose MongoDB's port. |
| `-sV` | Service/version detection | Fingerprint the service, including its version when possible. |
| `-p 27017` | Scan TCP port 27017 | Focus on MongoDB's default listener rather than scanning unrelated ports. |
| `--script mongodb-info` | Execute the MongoDB information NSE script | Request server metadata for identification and assessment. |
| `--open` | Display hosts with an open scanned port | Reduce subnet discovery output to likely MongoDB endpoints. |
| `10.0.2.0/24` | /24 subnet (256 addresses) | Find hosts exposing port 27017 in the lab network. |
| `10.0.2.15` | Target IP address | Assess the identified MongoDB instance. |

### Observed result

The simulator's command output reported:

```text
10.0.2.10 -- closed
10.0.2.15 -- OPEN -- MongoDB 4.0.28
mongodb-info: Authentication: DISABLED
Databases: admin, financials, logs, production, userdata
[+] Step 1/3 complete!
```

### Reasoning

A MongoDB service reachable on the network warrants an access-control check. Service discovery established the exposed port and MongoDB version. The simulator additionally reported that authentication was disabled and listed five databases. **A successful informational scan is not, by itself, universally sufficient to prove unrestricted data reads**; that risk was tested more directly in the next stages. The exact `Authentication: DISABLED` output is a lab-provided observation and is not guaranteed to appear in the real `mongodb-info` script's output on every server.

## Step 2: Connection, access without credentials

### Command

```bash
mongosh 10.0.2.15:27017
```

### Parameters

| Parameter | Meaning | Reason for use |
|---|---|---|
| `mongosh` | MongoDB interactive shell | Establish a session and issue database commands. |
| `10.0.2.15` | Host address | Connect to the exposed instance. |
| `:27017` | TCP port | Select MongoDB's listener. |
| No username/password arguments | No credentials provided | Test whether the server enforces authentication for the session and subsequent operations. |

### Enumeration commands (inside `mongosh`)

```javascript
show dbs
use production
show collections
```

| Command | Meaning | Reason for use |
|---|---|---|
| `show dbs` | List visible databases and sizes | Establish the database inventory. |
| `use production` | Select the `production` database | Choose a database context for subsequent commands. |
| `show collections` | List collections in the selected database | Understand the data structure without reading every document. |

### Observed result

The shell connected using MongoDB **4.0.28** and Mongosh **1.10.6** and displayed:

```text
Access control is not enabled for the database.
Read and write access to data and configuration is unrestricted
[note] No authentication required! Connected directly.
[+] Step 2/3 complete!
```

The five databases identified in the mission were `admin`, `financials`, `logs`, `production`, and `userdata`. The transcript shows successful connection and a server startup warning; it does **not** include actual `show dbs` or `show collections` output, so specific collection inventories are not asserted here.

### Reasoning

The server's own access-control warning and the no-credential connection confirmed the configuration finding. Database enumeration is a low-volume way to map exposure before examining records. A TCP connection alone does not prove all reads or writes will succeed; that conclusion depends on authorized operations succeeding, which the simulator reported in Step 3.

## Step 3: Inspect data, create a dump, capture the flag

### Commands

Inspect a small sample in the expected user database (inside `mongosh`):

```javascript
use userdata
show collections
db.users.find().limit(3).pretty()
```

Locate the lab canary/flag:

```javascript
use financials
db.metadata.find().pretty()
```

Create the complete backup from the **Kali terminal**, not from inside `mongosh`:

```bash
mongodump --host 10.0.2.15 --port 27017 --out /tmp/mongo_dump
```

### Parameters and operators

| Parameter / expression | Meaning | Reason for use |
|---|---|---|
| `db.users` | `users` collection in the selected database | Select the collection that may contain customer records. |
| `.find()` | Query documents in a collection | Examine stored field structure and values. |
| `.limit(3)` | Return no more than three documents | Sample records without printing the whole collection. |
| `.pretty()` | Request more readable output | Make document inspection easier. |
| `use financials` | Switch to `financials` | Access the database identified as containing the canary. |
| `db.metadata.find()` | Query documents in `metadata` | Locate the mission flag. |
| `mongodump` | MongoDB logical backup utility | Export accessible databases/collections to BSON files. |
| `--host 10.0.2.15` | Target database server | Identify the source of the backup. |
| `--port 27017` | MongoDB listener | Specify the source port. |
| `--out /tmp/mongo_dump` | Local backup directory | Choose where BSON and metadata files are written. |
| No authentication options | No credentials supplied | Test whether unrestricted export is possible. |

### Observed result

The simulator reported:

- **Flag captured:** `c160b23374436bb938ac95a9f5bbf7ed`
- **Flag file created:** `~/flags/flag6.txt`
- **Dumped records:** 284,492 customer records
- **Sensitive fields exposed:** plaintext SSNs and credit card numbers, according to the exercise
- **Completion:** Step 3 and mission completed

The mission description also mentioned weak MD5 password hashing, but no actual password hashes or query output were provided to substantiate the hashing claim independently.

### Reasoning

A bounded `find().limit(3)` query demonstrates document-level access and exposes unsafe field-storage choices while limiting terminal output. The `financials.metadata` query targets the simulator's breach-detection canary. Unlike an interactive query, `mongodump` reads and serializes available database contents to local BSON backup files; its reported success establishes that the consequences go beyond metadata exposure and include bulk data disclosure. **A full logical backup is not the same as a consistent point-in-time snapshot in every MongoDB topology/configuration.**

## Findings and impact

| Field | Finding |
|---|---|
| Primary weakness | **CWE-306: Missing Authentication for Critical Function** |
| Root cause | MongoDB access control disabled |
| Network exposure | TCP `27017` reachable in the lab subnet |
| Affected host/version | `10.0.2.15`, MongoDB `4.0.28` |
| Databases identified | `admin`, `financials`, `logs`, `production`, `userdata` |
| Confidentiality impact | Unauthenticated reads and reported bulk export of customer data |
| Integrity/availability risk | Server warning states write access and configuration access are unrestricted |
| Sensitive data | SSNs and card numbers reported in plaintext |
| Severity | **Critical; lab-assigned CVSS 10.0** |
| CVE | No specific CVE assigned for this configuration error |
| Applicable standards | GDPR and PCI DSS considerations arise because of the data types and loss of access control; a formal compliance finding requires assessment against the relevant requirements and facts. |

**Key distinction:** CWE-306 identifies a **class of weakness**; it is not a CVE assigned to this particular deployment. The 10.0 score is the simulator's rating, not an independently calculated CVSS vector.

## Remediation and verification

1. **Enable access control** in `mongod.conf`:

   ```yaml
   security:
     authorization: enabled
   ```

   Provision appropriately scoped database users and credentials before enforcing the setting. For a replica set, configure the required internal-member authentication as well.

2. **Restrict network exposure.** For a MongoDB instance that should only accept local connections:

   ```yaml
   net:
     bindIp: 127.0.0.1
     port: 27017
   ```

   If remote application connectivity is required, bind only to necessary private interfaces and restrict TCP 27017 through firewalls/security groups. Binding to localhost is not appropriate for every legitimate deployment architecture.

3. **Protect sensitive fields.** Minimize SSN collection, encrypt sensitive personal data where retention is necessary, use payment tokens instead of retaining raw card data where possible, and follow PCI DSS storage rules. Do not store card verification codes after authorization.

4. **Fix password storage.** Replace any confirmed MD5 password hashes with a modern salted password-hashing algorithm, such as Argon2id, using a safe migration strategy.

5. **Harden and maintain the deployment.** Update unsupported MongoDB versions, use least-privilege accounts, audit database access, and monitor for anomalous exports.

6. **Verify the fix.** From a network location that should not have access, confirm port 27017 is blocked. Where the port is intentionally reachable, test that unauthenticated database enumeration and collection reads return authorization errors, while valid least-privilege application credentials still work.

## Mission conclusion

**All three steps completed successfully in the simulated lab.** Nmap identified MongoDB 4.0.28 and the lab reported disabled authentication; `mongosh` connected without credentials and surfaced an access-control warning; the final stage reported a full dump of 284,492 customer records and successful capture of the flag. The lesson is that **network reachability combined with missing authentication can turn a single database configuration mistake into a bulk data breach**, particularly when sensitive records are retained in plaintext.

