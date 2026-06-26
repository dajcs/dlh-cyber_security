#!/usr/bin/env python3
"""
Retrieve HTTP response headers from a website using requests
"""

import requests


def get_http_headers(url):
    """
    Retrieve HTTP reponse headers from a website
    
    Args:
        url (str): The URL to request

    Returns:
        dict: A dictionary containing the status code and headers
              Format: {'status_code": int, 'headers": dict}
        None: If the request fails
    """
    try:
        response = requests.get(url)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers)
        }
    
    except requests.exceptions.RequestException:
        return None