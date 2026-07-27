can you help me with the task below?
- We need to discover together our lab environment.
- I've put the sandbox `<Ip> web0x05.hbtn` into `/etc/hosts` and I can access the sandbox through vpn (ping ok).
- Let's proceed step by step, give me only one command at once and explain the parameters and what are we going to learn from it.
- I'll then execute the command and provide you with the output, and we will analyze it together.

## 0. Oops! We forget that endpoint for testing purpose

Your mission is to determine which subdomain contains a web application with an insecure file upload feature.
This task requires you to methodically explore each subdomain, looking for any interfaces or functionalities that allow file uploads.
Identifying the correct subdomain sets the stage for deeper vulnerability analysis in subsequent tasks.

- Main Domain: http://web0x05.hbtn
- Example:
  ```
  $ cat 0-target.txt
  up3l0d3r.web0x05.hbtn
  ```

**Useful Instructions**

1. Consider using automated tools like subdomain enumeration tools or web crawlers to quickly identify which subdomains host web applications with upload features.
2. For each subdomain that hosts an upload feature, manually inspect the page and attempt a benign file upload (e.g., a simple text file) to understand how the application processes uploads.
3. Keep detailed notes on your findings for each subdomain, including the types of upload features found and any immediate indicators of potential vulnerabilities.



## 1. Some filters are only client-sided !

Having identified the vulnerable subdomain, your next challenge is to bypass the client-side file type filtering mechanism of the web application's upload feature.
Your success in uploading a restricted file type will reveal a hidden Flag ⛳️ as proof of your accomplishment.

- Target Endpoint: http://[vuln-subdomain].web0x05.hbtn/task1

You will need to use this php command to read the flag: <?php readfile('FLAG_1.txt') ?>
FLAG will only be generated if you upload a php file!

**Useful Instructions**

1. Use browser developer tools to inspect the upload form and any JavaScript code that validates file types. Look for patterns or keywords it checks against.
2. Consider using tools like Burp Suite to intercept and modify the upload request, changing the file name or MIME type to bypass client-side checks.
3. Explore different ways to initiate the file upload (e.g., drag-and-drop functionality) that might not trigger client-side validation as expected.
4. Pay attention to any error messages or feedback from the server after attempting an upload. These messages can offer clues for refining your bypass technique.


## 2. Special Characters are so special !

After successfully navigating past the client-side restrictions, you're faced with a more formidable challenge: bypassing the server-side validation that scrutinizes the file formats being uploaded.

This task requires you to cleverly use special characters in the file name to deceive the server-side checks, allowing you to upload a file type that is normally restricted.
Successfully uploading such a file will unveil a hidden `Flag` ⛳️.


Target Endpoint: http://[vuln-subdomain].web0x05.hbtn/task2

You will need to use this php command to read the flag: `<?php readfile('FLAG_2.txt') ?>`, FLAG will only be generated if you upload a php file!

**Useful Instructions**

1. Investigate how the server processes file names and extensions. Some servers might strip or ignore certain special characters, altering the file name after processing.
2. Experiment with adding special characters like spaces, dots, or null bytes (`%00`) in the file extension. For example, attempting to upload a file named `payload.php.jpg` might be blocked, but `payload.php%00.jpg` could bypass the filter if the server improperly handles null bytes.
3. Utilize tools like Burp Suite to intercept and modify your upload requests, carefully crafting the file names with special characters to test the server's validation logic.
4. Keep an eye on the server's response to each upload attempt. A successful bypass might not always be explicitly confirmed by the application’s UI. Check for any changes in behavior or new functionalities accessible after your upload.

