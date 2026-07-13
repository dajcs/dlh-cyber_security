# OWASP Top 10

- 1-xor_decoder.sh
- 2_flag.txt
















## Task1. (A2:2021) - Cryptographic Failures - Catch The Flag

- Turn back to the target machine `cyber_websec_0x01`
- Heads out to: A2 - Cryptographic Failures -> Encoding Failure.
- The goal is finding out the the login credentials in order to retreive the flag on sign in.
- Login page: `http://[MACHINE-IP]/a2/crypto_encoding_failure/`
- **Hints**:
  - Start with the profile page: `/a2/crypto_encoding_failure/profile`
  - Think about the headers of all Fetch/XHR made requests
  - Use the previous task to decrypt the password

start sandbox `cyber_websec_0x01`
- hostname: `web-0-218-230.cod-eu-west-3.hbtn.io`
- ip: `10.42.218.230`

start sandbox `ubuntu_2204`
- login to ubuntu_2204
```bash
ssh -p 13554 root@ssh.cod-eu-west-3.hbtn.io
# yes
# Password: c12d5f6296ce4d04b14be2d3798da563
```
