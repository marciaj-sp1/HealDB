# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 16:47:51 2024

@author: User
"""

import requests
from bs4 import BeautifulSoup

# Function to fetch the introductory content of the Wikipedia page
def fetch_wikipedia_intro(title):
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
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract the pages from the response
    pages = data['query']['pages']
    page = next(iter(pages.values()))
    
    # Check for redirection and print the redirection details if available
    if 'redirects' in data['query']:
        redirect_from = data['query']['redirects'][0]['from']
        redirect_to = data['query']['redirects'][0]['to']
        print(f"Requested: {redirect_from} was redirected to: {redirect_to}")
    
    return page.get('extract', 'No introduction found.')

# Function to fetch sections of the Wikipedia page
def fetch_wikipedia_sections(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": title,
        "prop": "sections",
        "redirects": 1  # Follow redirects
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data['parse']['sections']

# Function to fetch specific section content
def fetch_wikipedia_section_content(title, section_name):
    # Fetch sections to identify the correct index for the section_name
    sections = fetch_wikipedia_sections(title)
    section_index = None
    
    # Find section index based on section name
    for section in sections:
        # Adjust to find the section even if the names do not exactly match
        if section_name.lower() in section['line'].lower() or section_name.lower().replace(" ", "") in section['line'].lower().replace(" ", ""):
            section_index = section['index']
            break
    
    # If section is not found, return a message
    if not section_index:
        return f"Section '{section_name}' not found for {title}."
    
    # Fetch content of the specific section
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": title,
        "prop": "text",
        "section": section_index
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Extract section content
    try:
        content = data['parse']['text']['*']
        # Clean HTML tags from the content
        content = clean_html_tags(content)
        return content
    except KeyError:
        return "No content found for this section."

# Function to clean HTML tags from the fetched content
def clean_html_tags(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text()

# Example usage
#medication_name = "Leuprorelin"  # Replace with the specific medication name
medication_name = "Ibuprofen"

# Fetch and display the introduction of the medication
intro_content = fetch_wikipedia_intro(medication_name)
print("Introduction:", intro_content)

# Fetch and display specific sections
print("Mechanism of action:", fetch_wikipedia_section_content(medication_name, "Mechanism of action"))
print("Contraindications:", fetch_wikipedia_section_content(medication_name, "Contraindications"))
print("Pharmacodynamics:", fetch_wikipedia_section_content(medication_name, "Pharmacodynamics"))
print("Chemical Structure:", fetch_wikipedia_section_content(medication_name, "Chemical Structure"))
print("Approval history:", fetch_wikipedia_section_content(medication_name, "Approval history"))
print("Side effects:", fetch_wikipedia_section_content(medication_name, "Side effects"))
