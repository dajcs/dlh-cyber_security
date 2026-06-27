#!/usr/bin/env python3
"""
Recursive internal-link web crawler
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl_website(start_url, max_depth=2):
    """
    Recursively crawl a website and discover internal links
    
    Args:
        start_url (str): The URL where crawling starts
        max_depth (int): Maximum recursion depth
                         e.g. depth 0 -> start page
                              depth 1 -> links on the start page
    
    Returns:
        set: URLs successfully visited from the same domain
             e.g.
             {
                 "https://google.com",
                 "https://google.com/preferences",
                 "https://google.com/advanced_search"
             }

             Returns an empty set if the starting URL is unreachable
    """

    visited = set()

    try:
        # urlparse(start_url) returns a ParseResult object.
        # .netloc is a str containing the domain part of the URL.
        #
        # Example:
        #   urlparse("https://google.com/search?q=test").netloc
        #   returns "google.com"
        start_domain = urlparse(start_url).netloc
    except Exception:
        # If parsing fails, return an empty set.
        return set()
    
    # If start_domain is an empty string, the URL is probably invalid.
    #
    # Example:
    #   urlparse("not-a-real-url").netloc
    #   returns ""
    if not start_domain:
        return set()
    
    def crawl(url, depth):
        """
        Inner recursive crawler function
        
        Args:
            url (str): Current URL to crawl
            depth (int): Current crawl depth

        Returns:
            None
            but modifies the outer visited set directly
        """

        # Stop recursion if current depth exceeds max_depth.
        if depth > max_depth:
            return
        
        # If this URL was already visited, skip it.
        if url in visited:
            return
        
        try: 
            # urlparse() returns a ParseResult object.
            # It decomposes the URL in parts like:
            #   scheme: "https"
            #   netloc: "google.com"
            #   path: "/search"
            #   query: ?"q=test"
            #   fragment: #"main-content"
            parsed_url = urlparse(url)

            # Only crawl URLs from the same domain as start_url.
            if parsed_url.netloc != start_domain:
                return

            # requests.get() visits the webpage
            # and returns a requests.models.Response object
            # response will have:
            #     response.status_code
            #     response.headers
            #     response.text
            #     response.content
            #     response.url
            #     response.cookies
            response = requests.get(url, timeout=5)

            # response.raise_for_status() is a method that
            # raises an HTTPError exception for bad status codes,
            # such as 404, 403, or 500.
            response.raise_for_status()

            # Add the current URL string to the visited set.
            # to store the crawl results in the outer `visited` set
            visited.add(url)

            # print for monitoring the crawl progress.
            print(f"depth: {depth}  url: {url:.123s}")

            # response.text is a str containing the HTML source code.
            # soup will be a BeautifulSoup object that can parse HTML code
            soup = BeautifulSoup(response.text, "html.parser")

            # soup.find_all("a", href=True) returns a list-like collection
            # of <a> tags that contain an href attribute.
            #
            # Each link is a BeautifulSoup Tag object.
            for link in soup.find_all("a", href=True):

                # href is a str containing the link target.
                #
                # Examples:
                #   "/about"
                #   "https://google.com/preferences"
                #   "#main-content"
                href = link.get("href")

                # urljoin() converts relative URLs to absolute URLs.
                #
                # Example:
                #   urljoin("https://google.com", "/about")
                #   returns "https://google.com/about"
                # Note:
                #   urljoin("https://google.com", "http://example.com")
                #   returns "http://example.com" - since that is already an absolute URL
                absolute_url = urljoin(url, href)

                # examining the new absolute_url
                parsed_link = urlparse(absolute_url)

                # Only recursively crawl links from the same domain.
                if parsed_link.netloc == start_domain:
                    # Recursive call:
                    # - absolute_url is the next URL to crawl
                    # - depth + 1 increases the crawl depth
                    crawl(absolute_url, depth + 1)

        except requests.exceptions.RequestException:
            # Catches request-related errors, including:
            #   - connection errors
            #   - timeout errors
            #   - invalid URL errors
            #   - HTTP errors from raise_for_status()
            return

        except Exception:
            # Catches any other unexpected error and skips that URL.
            return


    # Start recursive crawling from the initial URL at depth 0.
    crawl(start_url, 0)
    print("\n","=" * 50, "\n\n")

    # visited is a set[str] containing successfully crawled URLs.
    return visited
