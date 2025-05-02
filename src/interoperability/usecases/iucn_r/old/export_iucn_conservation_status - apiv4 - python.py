# -*- coding: utf-8 -*-
"""
Created on Sun Dec 04 22:30:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br
"""

# This script retrieves conservation status, threats, and geographic 
# distribution data from the IUCN API for plant-based substances classified 
# as "PM" (Planta Medicinal) in the Brazilian Common Denomination (DCB) list, 
# including both active ingredients in the HealDB database and all 
# PM-classified DCB names.
#
# For each plant name, it queries the IUCN API to retrieve:
#  - Conservation status (e.g., endangered, vulnerable)
#  - Geographic distribution by country
#  - Reported environmental threats
#
# The result data is saved in two JSON files: one for active ingredients from 
# the medications from HealDB data base and the toher for general active
# ingredients in the DCB list. 
#

import requests
import urllib.parse
import re
import time
import json
from config import PATHS, APIS_USE_CASES, CATEGORY_MEANINGS

IUCN_API = APIS_USE_CASES["iucn"]

def clean_name(name):
    # Clean input name: remove ' L.' and keep only the first two words.
    
    name = re.sub(r'\sL\.$', '', name)  # Remove " L." at the end
    words = name.split()
    return " ".join(words[:2])  # Keep only the first two words


def query_country_data(plant_name):
    # Query IUCN API v4 for plant distribution by country.
    encoded_name = urllib.parse.quote(plant_name)
    url = f"{IUCN_API['base_country_url']}?name={encoded_name}"
    headers = {"Authorization": f"Token {IUCN_API['token']}"}
    print ("country url = ", url)
    response = requests.get(url, headers=headers, timeout=10)
    data_list = []
    if response.status_code == 200:
        data = response.json()
        data_list = data.get("result", [])
    return data_list

def query_threats(plant_name):
    # Query IUCN API v4 for plant threats.
    encoded_name = urllib.parse.quote(plant_name)
    url = f"{IUCN_API['base_threats_url']}?name={encoded_name}"
    headers = {"Authorization": f"Token {IUCN_API['token']}"}
    print ("threats url = ", url)
    response = requests.get(url, headers=headers, timeout=10)
    data_list = []
    if response.status_code == 200:
        data = response.json()
        data_list = data.get("result", [])
    return data_list

def query_conservation_status(plant_name):
    # Query IUCN API v4 for plant conservation status.
    encoded_name = urllib.parse.quote(plant_name)
    url = f"{IUCN_API['base_species_url']}?name={encoded_name}"
    headers = {"Authorization": f"Token {IUCN_API['token']}"}
    response = requests.get(url, headers=headers, timeout=10)
    print ("conservation url = ", url)
    data_dict = {}
    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            category = data["result"][0].get("category", "N/A")
            meaning = CATEGORY_MEANINGS.get(category, "Unknown status")
            data_dict = {"category": category, "meaning": meaning}
    return data_dict
def process_plants(plants, output_list):
    # Main function to process plants and save data

    total = 0
    count_data = 0
    count_status = 0
    for plant in plants:
        print(f"Processing: {plant}")
        plant_data = {"name": plant}
        print ("plant = ", plant)
        # Query country data
        country_data = query_country_data(plant)
        if country_data:
            plant_data["countries"] = country_data
        else:
            print(f"No country data found for {plant}")

        # Query threats
        threats_data = query_threats(plant)
        if threats_data:
            plant_data["threats"] = threats_data
        else:
            print(f"No threats found for {plant}")

        # Query conservation status
        conservation_status = query_conservation_status(plant)
        if conservation_status:
            plant_data["conservation_status"] = conservation_status
        else:
            print(f"No conservation status found for {plant}")
        total+=1
        if country_data or threats_data or conservation_status:
            count_data+=1
            output_list.append(plant_data)
        elif conservation_status:
            count_status+=1
        time.sleep(0.4)
    return total, count_data, count_status

def fetch_and_process_active_ingredients(cnx, cursor):
    # Fetch the active ingredients from the database, clean the names, and process the data
    # using the IUCN API.
    
    print("Searching active ingredients from the HealDB database")

    # SQL command to fetch active ingredients
    sql_command = (
        "SELECT UPPER(h1.nm_active_ingredient) AS nm_active_ingredient "
        "FROM hd_active_ingredient h1 "
        "JOIN hd_dcb_list h2 ON TRIM(UPPER(h1.nm_active_ingredient)) = TRIM(UPPER(h2.nm_dcb)) "
        "JOIN hd_dcb_classification h3 ON h2.id_dcb_classification = h3.id_dcb_classification "
        "WHERE h3.tp_dcb_classification = 'PM' "
        "ORDER BY 1 "
        "LIMIT 5 "
        )
    print (sql_command)
    # Execute the SQL command and fetch results
    cursor.execute(sql_command)
    active_ingredients = [row[0] for row in cursor.fetchall()]

    # Clean the names and process with the IUCN API
    cleaned_active_ingredients = [clean_name(name) for name in active_ingredients]

    print ("cleaned active ingredients", cleaned_active_ingredients)
    
    print(f"Fetched {len(cleaned_active_ingredients)} active ingredients.")
    return cleaned_active_ingredients


def fetch_and_process_dcb_names(cnx, cursor):
    
    # Fetch DCB names from the database, clean the names, and process the data
    # using the IUCN API.
    
    print("Fetching DCB names from the database...")

    # SQL command to fetch DCB names
    sql_command = (
        "SELECT UPPER(h1.nm_dcb) "
        "FROM hd_dcb_list h1 "
        "JOIN hd_dcb_classification h2 ON h1.id_dcb_classification = h2.id_dcb_classification "
        "WHERE h2.tp_dcb_classification = 'PM' "
        "ORDER BY 1 "
    )

    # Execute the SQL command and fetch results
    cursor.execute(sql_command)
    dcb_names = [row[0] for row in cursor.fetchall()]

    # Clean the names and process with the IUCN API
    cleaned_dcb_names = [clean_name(name) for name in dcb_names]

    print(f"Fetched {len(cleaned_dcb_names)} DCB names.")
    return cleaned_dcb_names

def export_iucn_conservation_status(cnx, cursor):
    # Main function to fetch data from the database, process with the IUCN API,
    # and save the results to JSON files.
    # This function extract the conservation status from medicinal plants
    # used as active ingredients to medications and also from medicinal plantas
    # found in all active ingredients from the DCB list.
    
    print("Starting IUCN Conservation Status processing...")

    # Fetch and process active ingredients and DCB names
    active_ingredients = fetch_and_process_active_ingredients(cnx, cursor)
    #dcb_names = fetch_and_process_dcb_names(cnx, cursor)

    # Initialize output lists
    output_active_ingredients = []
    #output_dcb = []

    # Process the plants using the IUCN API
    total_act, count_act, count_act_status = process_plants(active_ingredients, 
                                                            output_active_ingredients)
    #total_dcb, count_dcb, count_dcb_status = process_plants(dcb_names, output_dcb)

    # Add totals to the JSON output
    output_active_ingredients.append({
        "summary": {
            "total": total_act,
            "count_data": count_act,
            "count_status": count_act_status,
        }
    })

   # output_dcb.append({
   #     "summary": {
   #         "total": total_dcb,
   #         "count_data": count_dcb,
   #         "count_status": count_dcb_status,
   #     }
   # })

    # Save the results as JSON files
    output_active_ingredients_path = f"{PATHS['output_int_dir']}/export_iucn_conservation_active_ing.json"
    output_dcb_path = f"{PATHS['output_int_dir']}/export_iucn_conservation_dcb_list.json"

    with open(output_active_ingredients_path, "w", encoding="utf-8") as f:
        json.dump(output_active_ingredients, f, indent=4)

    #with open(output_dcb_path, "w", encoding="utf-8") as f:
    #   json.dump(output_dcb, f, indent=4)

    print(f"Conservation Active ingredients without status data: {count_act_status}")
    print(f"Conservation Active ingredients data saved to {output_active_ingredients_path}")
    #print(f"Conservation DCB names without status data: {count_dcb_status}")
    #print(f"Conservation DCB data saved to {output_dcb_path}")

    print(f"\nExport completed: {output_active_ingredients_path} and {output_dcb_path}")
    return