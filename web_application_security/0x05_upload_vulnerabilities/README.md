# Upload Vulnerabilities



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

### Start sandbox

- start `cyber_websec_0x05` sandbox
- \Network information: ip: `10.42.220.203`
- put ip in `/etc/hosts` file: `
  ```bash
  sudo bash -c "echo '10.42.220.203  web0x05.hbtn' >> /etc/hosts"
  cat /etc/hosts
  ```
  - start vpn

```
sudo
