# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 00:02:49 2024

@author: User
"""

import requests

# Function to fetch drug information by KEGG Drug ID
def fetch_drug_info(drug_id):
    url = f"http://rest.kegg.jp/get/{drug_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching drug information."

# Function to fetch related drugs by compound
def fetch_related_drugs(compound_id):
    url = f"http://rest.kegg.jp/link/drug/{compound_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching related drugs."

# Function to fetch compound information
def fetch_compound_info(compound_id):
    url = f"http://rest.kegg.jp/get/{compound_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Error fetching compound information."

# Example usage
drug_id = "D00109"  # Example Drug ID for Aspirin
compound_id = "C00047"  # Example Compound ID

# Fetch drug information
drug_info = fetch_drug_info(drug_id)
print(f"Drug Information for {drug_id}:\n", drug_info)

# Fetch related drugs
related_drugs = fetch_related_drugs(compound_id)
print(f"Related Drugs for {compound_id}:\n", related_drugs)

# Fetch compound information
compound_info = fetch_compound_info(compound_id)
print(f"Compound Information for {compound_id}:\n", compound_info)
