# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 17:04:42 2024

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

def get_rxnorm_details(medication_name):
    base_url = "https://rxnav.nlm.nih.gov/REST"

    # 1. Get the RxCUI associated with the medication name
    rxcui_url = f"{base_url}/rxcui.json?name={medication_name}"
    rxcui_info = fetch_data(rxcui_url)
    rxcui = rxcui_info.get('idGroup', {}).get('rxnormId', ['No RxCUI found'])[0]
    print("1. RxCUI:", rxcui)

    if rxcui == 'No RxCUI found':
        return  # Stop further execution if no RxCUI is found

    # 2. Get available dosage forms
    forms_url = f"{base_url}/rxcui/{rxcui}/property.json?propName=FORM"
    forms_info = fetch_data(forms_url)
    forms = forms_info.get('propConceptGroup', {}).get('propConcept', [{'propValue': 'No forms found'}])
    print("2. Dosage Forms:", [form['propValue'] for form in forms])

    # 3. Get related codes like NDC or SNOMED
    related_url = f"{base_url}/rxcui/{rxcui}/related.json?tty=BN+SBD+SCD"
    related_info = fetch_data(related_url)
    related = related_info.get('relatedGroup', {}).get('conceptGroup', 'No related codes found')
    print("3. Related Codes:", related)

    # 4. Check availability or discontinuation status
    history_status_url = f"{base_url}/rxcui/{rxcui}/historystatus.json"
    history_status_info = fetch_data(history_status_url)
    history_status = history_status_info.get('historyStatus', 'No historical status found')
    print("4. Availability Status:", history_status)

    # 5. Get standardized dosages
    strength_url = f"{base_url}/rxcui/{rxcui}/property.json?propName=STRENGTH"
    strength_info = fetch_data(strength_url)
    strengths = strength_info.get('propConceptGroup', {}).get('propConcept', [{'propValue': 'No dosages found'}])
    print("5. Standardized Dosages:", [strength['propValue'] for strength in strengths])

# Example usage with a specific medication name
medication_name = "Ibuprofen"  # Replace with the specific medication name
get_rxnorm_details(medication_name)
