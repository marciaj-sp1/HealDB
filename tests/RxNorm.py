# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 08:15:37 2024

@author: User
"""

import requests

def fetch_data(url):
    """Fetch data from the specified URL and handle errors gracefully."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()  # Attempt to parse the response as JSON
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - URL: {url}")
        return {}  # Return an empty dictionary if an error occurs
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err} - URL: {url}")
        return {}  # Return an empty dictionary if an error occurs
    except ValueError as json_err:
        print(f"JSON decode error: {json_err} - URL: {url}")
        return {}  # Return an empty dictionary if JSON parsing fails

def get_rxnorm_details(rxcui):
    base_url = "https://rxnav.nlm.nih.gov/REST"

    # 1. Get basic properties of the RXCUI
    properties_url = f"{base_url}/rxcui/{rxcui}/properties.json"
    properties_info = fetch_data(properties_url)
    properties = properties_info.get('properties', 'No basic info found')

    # 2. Get related concepts by type (including dosage forms)
    related_by_type_url = f"{base_url}/rxcui/{rxcui}/related.json?tty=SCD+SBD"
    related_info = fetch_data(related_by_type_url)
    related = related_info.get('relatedGroup', 'No related concepts found')

    # Extract dosage information from related concepts
    dosages = []
    if 'conceptGroup' in related:
        for group in related['conceptGroup']:
            if 'conceptProperties' in group:
                for concept in group['conceptProperties']:
                    name = concept.get('name', 'No name')
                    tty = concept.get('tty', 'No type')
                    if tty in ['SCD', 'SBD']:  # Only include clinical and branded drugs
                        dosages.append(name)

    # 3. Get all properties of the RXCUI
    all_properties_url = f"{base_url}/rxcui/{rxcui}/allProperties.json"
    all_properties_info = fetch_data(all_properties_url)
    all_properties = all_properties_info.get('allProperties', 'No detailed properties found')

    # 4. Get drug interactions if available
    interactions_url = f"{base_url}/interaction/list.json?rxcuis={rxcui}"
    interactions_info = fetch_data(interactions_url)
    interactions = interactions_info.get('interactionTypeGroup', 'No interactions found')

    # 5. Find related NDCs (National Drug Codes)
    related_ndcs_url = f"{base_url}/rxcui/{rxcui}/ndcs.json"
    related_ndcs_info = fetch_data(related_ndcs_url)
    related_ndcs = related_ndcs_info.get('ndcGroup', 'No related NDCs found')

    # 6. Get approximate matches for the RXCUI (useful for variations in spelling)
    approx_match_url = f"{base_url}/approximateTerm?term={rxcui}"
    approx_match_info = fetch_data(approx_match_url)
    approx_match = approx_match_info.get('approximateGroup', 'No approximate matches found')

    # 7. Get historical status and properties (if applicable)
    history_status_url = f"{base_url}/rxcui/{rxcui}/historystatus.json"
    history_status_info = fetch_data(history_status_url)
    history_status = history_status_info.get('historyStatus', 'No historical status found')

    # Print collected information
    print("1. Basic Properties:", properties)
    print("\n2. Related Concepts by Type:", related)
    print("\n3. Dosages Found:", dosages)
    print("\n4. All Properties:", all_properties)
    print("\n5. Drug Interactions:", interactions)
    print("\n6. Related NDCs:", related_ndcs)
    print("\n7. Approximate Matches:", approx_match)
    print("\n8. Historical Status:", history_status)

# Example usage with a specific RXCUI
rxcui = "5640"  # RXCUI for Ibuprofen
get_rxnorm_details(rxcui)
