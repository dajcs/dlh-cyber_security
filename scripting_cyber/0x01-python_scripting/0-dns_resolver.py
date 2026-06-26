#!/usr/bin/env python3
"""
Basic DNS Resolver
using Python's socket library
"""

import socket

def resolve_domain_to_ipv4(domain_name):
    """
    Resolves a domain name to its IPv4 address.
    
    Args:
        domain_name (str): The domain name to resolve.
        
    Returns:
        str: The resolved IPv4 address.
        None: If the domain name cannot be resolved (socket.gaierror).
        str: Error message for any other exceptions
    """
    try:
        ipv4_address = socket.gethostbyname(domain_name)
        return ipv4_address
    except socket.gaierror:
        return None
    except Exception as e:
        return f"Unexpected error: {e}"