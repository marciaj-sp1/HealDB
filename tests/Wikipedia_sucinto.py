# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:57:14 2024

@author: User
"""

import requests

# Function to fetch content from Wikipedia using the extracts endpoint
def fetch_wikipedia_extract(title):
    # Define the API endpoint and parameters
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "redirects": 1  # Follow redirects
    }

    # Make the request to the Wikipedia API
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the first page from the response
    pages = data['query']['pages']
    page = next(iter(pages.values()))

    # Check if the page has extract content
    if 'extract' in page:
        extract_content = page['extract']
        return extract_content
    else:
        return "No extract found or the page does not exist."

# Example usage of the function
title = "Cetuximab"  # Replace with your desired Wikipedia page title
result = fetch_wikipedia_extract(title)
print(result)
