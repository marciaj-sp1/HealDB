# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 08:40:03 2024

@author: User
"""

import requests

# Define a função para buscar o conteúdo completo da Wikipedia, incluindo redirecionamentos
def fetch_full_wikipedia_content(title):
    # Define the API endpoint and initial parameters
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "redirects": 1  # This parameter allows the API to follow redirects
    }

    # Make the request to the API
    response = requests.get(url, params=params)
    data = response.json()

    # Extract the first page from the response
    pages = data['query']['pages']
    page = next(iter(pages.values()))

    # Check if there were any redirects
    if 'redirects' in data['query']:
        redirect_from = data['query']['redirects'][0]['from']
        redirect_to = data['query']['redirects'][0]['to']
        print(f"Requested: {redirect_from} was redirected to: {redirect_to}")
    else:
        print(f"Requested: {title} (No redirection)")

    # Check if the page has content or if it's a redirection
    if 'revisions' in page:
        # If revisions are found, extract the full content
        full_content = page['revisions'][0]['*']
        return full_content
    else:
        return "No content found or the page does not exist."

# Use the function to fetch the full content with the title "Lepirudin" (Example)
#result = fetch_full_wikipedia_content("Leuprolide")
#result = fetch_full_wikipedia_content("Ibuprofen")
#result = fetch_full_wikipedia_content("Lepirudin")
result = fetch_full_wikipedia_content("Cetuximab")
#result = fetch_full_wikipedia_content("Dornase_alfa")
print(result)
