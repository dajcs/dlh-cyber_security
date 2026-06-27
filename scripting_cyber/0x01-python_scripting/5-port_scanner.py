#!/usr/bin/env python3
"""
Basic TCP port checker using Python's socket module

Main function:
    check_port(host: str, port: int) -> bool
"""

import socket


def check_port(host, port):
    """
    Check whether a TCP port is open on a host.

    Args:
        host (str): Hostname or IP address to scan.
                    Example: "scanme.nmap.org" or "45.33.32.156"

        port (int): TCP port number to check.
                    Example: 80, 443, 22

    Returns:
        bool:
            True  -> the TCP port is open
            False -> the TCP port is closed, filtered, unreachable,
                     or an error occurred
    """

    try:
        # socket.socket() creates a socket object.
        #   socket.AF_INET means IPv4.
        #   socket.SOCK_STREAM means TCP.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # timeout in sec (float or int)
        sock.settimeout(3.0)

        # try connecting to host:port
        # Return value:
        #   0 means connection succeeded, so the port is open.
        #   non-zero means connection failed, so the port is closed
        #   or unreachable.
        result = sock.connect_ex((host, port))

        # Always close the socket after the check.
        sock.close()

        # Return True when connection succeeded.
        return result == 0

    except Exception:
        # If anything unexpected happens, treat the port as closed
        # or unreachable.
        return False
