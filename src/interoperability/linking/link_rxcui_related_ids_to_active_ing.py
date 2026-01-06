# -*- coding: utf-8 -*-
"""
Created on Sun Mar 02 11:01:00 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Link RxNorm-related external identifiers (e.g., SNOMED CT, ATC, UNII) 
# to active ingredients using their RxCUI, enabling richer 
# interoperability across biomedical ontologies and databases.

import requests
import time
from config import URLS_EXTERNAL_IDS
from src.interoperability.external_ids_insert import (
    insert_external_id
)

# RXNorm API Base URL
RXNORM_PROPERTY_API_URL = URLS_EXTERNAL_IDS["rxnorm_property_api_url"]

# List of properties to retrieve from RxNorm
properties = ["SNOMEDCT", "ATC", "UNII_CODE"]

def get_rxcui_related_ids(rxcui):
    # Retrieves related external identifiers for a given RxCUI from the RxNorm API.
    # Handles multiple values for ATC and ensures data consistency.
    
    result = {}

    for prop in properties:
        url = RXNORM_PROPERTY_API_URL.format(rxcui, prop)
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("propConceptGroup", {}).get("propConcept", [])
            
            # Handle multiple values (especially ATC)
            if isinstance(data, list):
                values = [item["propValue"] for item in data if "propValue" in item]
            else:
                values = [data.get("propValue", "N/A")] if data else []

            # Store values in the result dictionary
            if not values:
               values = ["N/A"]
            result[prop] = values 
        else:
            result[prop] = ["API request error"]

        # Small delay to prevent API rate limits
        time.sleep(0.5)

    return result

def link_rxcui_related_ids_to_active_ing(cnx, cursor):
    # Links RxNorm-related external identifiers to active ingredients in the HealDB database.
    # Retrieves RxCUI values from the database, queries the RxNorm API, and inserts results.

    try:
        # Retrieve active ingredients that have an RxCUI
        sql_command = (
            "SELECT id_active_ingredient, cd_ext_id "
            "FROM healdb.hd_active_ingredient_ext_id "
            "WHERE tp_ext_id = 'RXCUI' "
        )
        cursor.execute(sql_command)
        list_rxcui = cursor.fetchall()

        for id_active_ingredient, cd_ext_id in list_rxcui:
            print(f"Processing Active Ingredient: {id_active_ingredient}, RxCUI: {cd_ext_id}")
            time.sleep(1)  # Wait 1 second before making API requests
            
            related_ids = get_rxcui_related_ids(cd_ext_id)
            
            for key, values in related_ids.items():
                for value in values:
                    if value and value != "N/A":
                        insert_external_id(cursor, cnx, id_active_ingredient, key, value, "RXNORM")

        print("Successfully linked RxCUI-related external IDs.")

    except Exception as e:
        print(f"Error linking RxCUI-related external IDs: {e}")
    return