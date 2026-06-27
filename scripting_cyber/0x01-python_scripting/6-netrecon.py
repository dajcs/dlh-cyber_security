#!/usr/bin/env python3
"""
Basic network reconnaissance tool.

This script combines:
    - DNS reconnaissance
    - Web reconnaissance
    - TCP port checking

Functions:
    dns_recon(domain: str) -> dict
    web_recon(domain: str) -> dict
    port_scan(domain: str) -> dict
"""

import socket
import requests
from bs4 import BeautifulSoup

# the checker doesn't have dns.resolver :-(
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False




# ************************************************************
#                       dns_recon()
# ************************************************************

def dns_recon(domain):
    """
    Perform basic DNS reconnaissance.

    Args:
        domain (str): Target domain name.
                      Example: "google.com"

    Returns:
        dict: DNS information.
              Format:
              {
                  "ip_address": str or None,
                  "mx_records": list[str]
              }
    """

    # dns_info is a dict that stores the final DNS results.
    dns_info = {
        "ip_address": None,
        "mx_records": []
    }

    # ------------------------------------------------------------
    # Resolve domain to IPv4 address
    # ------------------------------------------------------------
    try:
        # socket.gethostbyname() returns a string containing an IPv4 address.
        #
        # Example:
        #   "216.58.211.206"
        ip_address = socket.gethostbyname(domain)
        dns_info["ip_address"] = ip_address

        print(f"IP Address: {ip_address}")

    except socket.gaierror:
        # socket.gaierror happens when DNS resolution fails.
        print("IP Address: Failed to resolve")

    except Exception as e:
        # Catch any other unexpected DNS-related error.
        print(f"IP Address: Error: {e}")


    # ------------------------------------------------------------
    # Retrieve MX records
    # ------------------------------------------------------------
    print("\nMX Records:")

    if DNS_AVAILABLE:
        try:
            # dns.resolver.resolve() returns an Answer object.
            # For MX records, each answer has:
            #   answer.preference -> int
            #   answer.exchange   -> DNS name/mail server
            mx_answers = dns.resolver.resolve(domain, "MX")

            for answer in mx_answers:
                # record is a str representation of the MX record.
                record = f"{answer.preference} {answer.exchange}"
                dns_info["mx_records"].append(record)
                print(f"  {record}")

        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.resolver.LifetimeTimeout,
        ):
            # Missing or unreachable MX records should not stop the script.
            print("  No MX records found")

        except Exception as e:
            print(f"  Error retrieving MX records: {e}")

    return dns_info



# ************************************************************
#                       web_recon()
# ************************************************************

def web_recon(domain):
    """
    Perform basic web reconnaissance.

    Args:
        domain (str): Target domain name.
                      Example: "google.com"

    Returns:
        dict: Web reconnaissance results.
              Format:
              {
                  "status_code": int or None,
                  "headers": dict,
                  "link_count": int
              }
    """

    # web_info is a dict storing the final results
    # containing HTTP status, headers, and link count.
    web_info = {
        "status_code": None,
        "headers": {},
        "link_count": 0
    }

    # Build a URL from the domain.
    url = f"https://{domain}"

    try:
        # response is a requests.Response object.
        # timeout expects int or float seconds.
        response = requests.get(url, timeout=5)

        # status_code is an int, for example 200, 301, 403, 404.
        web_info["status_code"] = response.status_code

        # response.headers is a dictionary-like object.
        # dict(response.headers) converts it to a normal dict.
        web_info["headers"] = dict(response.headers)

        print(f"\nStatus Code: {response.status_code}")

        # ------------------------------------------------------------
        # Display selected important headers
        # ------------------------------------------------------------
        print("\nImportant Headers:")

        important_headers = ["Server", "Content-Type"]

        for header in important_headers:
            if header in response.headers:
                print(f"  {header}: {response.headers[header]}")

        # ------------------------------------------------------------
        # Count links on the page
        # ------------------------------------------------------------

        # response.text is a str containing the HTML source code.
        # BeautifulSoup parses that HTML into a searchable object.
        soup = BeautifulSoup(response.text, "html.parser")

        # links is a list-like ResultSet of <a> tags with href attributes.
        links = soup.find_all("a", href=True)

        # link_count is an int.
        link_count = len(links)
        web_info["link_count"] = link_count

        print(f"\nTotal Links Found: {link_count}")

    except requests.exceptions.RequestException as e:
        # Handles connection errors, timeouts, invalid URLs, etc.
        print(f"\nWeb request failed: {e}")

    except Exception as e:
        # Keeps the script running even if parsing or another step fails.
        print(f"\nWeb reconnaissance error: {e}")

    return web_info



# ************************************************************
#                       port_scan()
# ************************************************************

def port_scan(domain):
    """
    Check common TCP ports on a target domain.

    Args:
        domain (str): Target domain name.
                      Example: "google.com"

    Returns:
        dict: Port scan results.
              Format:
              {
                  80: True,
                  443: True,
                  22: False
              }

              True means open.
              False means closed or unreachable.
    """

    # common_ports is a list[int].
    # Keeping it small for this beginner reconnaissance task.
    common_ports = [80, 443]

    # scan_results is a dict[int, bool].
    scan_results = {}

    print(f"\nScanning common ports on {domain}...")
    print("Open ports:")

    for port in common_ports:
        # port is an int.
        try:
            # Create an IPv4 TCP socket.
            #
            # socket.AF_INET     -> IPv4
            # socket.SOCK_STREAM -> TCP
            #
            # sock type: socket.socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

                # Prevent the connection attempt from hanging too long.
                # settimeout() expects int or float seconds.
                sock.settimeout(3.0)

                # connect_ex() expects a tuple[str, int]:
                #   (domain, port)
                #
                # result is an int:
                #   0 means the connection succeeded
                #   non-zero means failed, closed, or unreachable
                result = sock.connect_ex((domain, port))

                # is_open is a bool.
                is_open = result == 0
                scan_results[port] = is_open

                if is_open:
                    print(f"  Port {port}: OPEN")

        except Exception:
            # Any socket failure means this port is treated as closed.
            scan_results[port] = False

    # If no ports were open, make the output explicit.
    if not any(scan_results.values()):
        print("  No open common ports found")

    return scan_results