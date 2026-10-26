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


Solution:
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
```


