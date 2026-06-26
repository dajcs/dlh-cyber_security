#!/usr/bin/env python3
"""
Download and format a web page's HTML content
using requests and BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup

def download_page(url):
    """
    Downloads the HTML content of a web page and formats it.
    
    Args:
        url (str): The URL of the web page to download.
        
    Returns:
        str: The formatted HTML content of the web page - if successful.
        str: Error message - if the download fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        
        # Use BeautifulSoup to format the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        formatted_html = soup.prettify()
        return formatted_html

    except requests.exceptions.RequestException as e:
        return f"Error downloading page: {e}"