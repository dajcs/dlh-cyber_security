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

