# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 23:08:19 2024

@author: User
"""

import requests

# Fetch available sections from the Wikipedia page
def fetch_wikipedia_sections(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": title,
        "prop": "sections",
        "redirects": 1
    }
    response = requests.get(url, params=params)
    data = response.json()
    sections = data.get('parse', {}).get('sections', [])
    return sections

# Fetch sections of the Cetuximab page
#sections = fetch_wikipedia_sections("Cetuximab")
#sections = fetch_wikipedia_sections("Ibuprofen")
#sections = fetch_wikipedia_sections("Lepirudin")
sections = fetch_wikipedia_sections("Leuprolide")


# Display available sections with their IDs
for section in sections:
    print(f"ID: {section['index']} - Title: {section['line']}")