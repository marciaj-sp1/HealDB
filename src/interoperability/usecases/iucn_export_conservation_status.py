# -*- coding: utf-8 -*-
"""
Created on Wed May 07 21:44:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br
"""

# This script retrieves data related to the conservation status of medicinal plants
# using the IUCN Red List API. It collects information such as:
# - Conservation category and description (e.g., Vulnerable, Least Concern)
# - Geographic locations where the plant is found
# - Identified threats to the plant
# - Extinction status (possibly extinct or possibly extinct in the wild)
# - Scope of the assessment (e.g., Global, Europe)

# The output is structured as a JSON file that includes:
# - id_active_ingredient or id_dcb
# - scientific name (normalized)
# - assessment data including category, locations, threats, and extinction status

import requests
import json
import time
import re
from config import PATHS, APIS_USE_CASES

# Load IUCN API configuration from the external configuration file
IUCN_API = APIS_USE_CASES["iucn"]

# Normalize scientific names by removing Unicode spaces, excess whitespace, 
# and authorship info
def normalize_name(name):

    # Cleans and standardizes the scientific name by removing special characters,
    # multiple spaces, and author information. It returns the first two words 
    # (genus and species).
    
    name = re.sub(r"[\u00A0\u200B]", " ", name).strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s*\(.*?\)$", "", name)
    words = re.findall(r"[a-zA-Z-]+", name)
    if len(words) >= 2:
        words_concat = " ".join(words[:2])
    else:
        words_concat = " ".join(words)
    return words_concat

# Retrieve taxonomic data for a given genus and species
def query_taxa(genus, species):
    try:
        url = IUCN_API["base_tax_url"]
        headers = {"Authorization": IUCN_API["token"]}
        params = {"genus_name": genus, "species_name": species}
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response_json = {}
        if response.status_code == 200:
           response_json = response.json()
    except Exception as e:
        print(f"Taxa query error for {genus} {species}: {e}")
    return response_json

# Retrieve assessment details for a specific assessment ID
def query_assessment(assessment_id):
    # Fetches assessment details from the IUCN API for a specific assessment_id.
    # Extracts and returns conservation category and description, geographic
    # locations, identified threats, scope of the assessment (e.g., Global, 
    # Europe), and extinction status.

    url = IUCN_API["base_assessment_url"].format(assessment_id=assessment_id)
    headers = {"Authorization": IUCN_API["token"]}

    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching assessment {assessment_id}: {response.status_code}")
            return {}, [], []

        data = response.json()
        locations = []
        threats = []
        dict_assess = {}

        # Extract conservation category and description
        category = data.get("red_list_category", {}).get("code", "Unknown")
        category_description = data.get("red_list_category", {}).get("description", {}).get("en", "Unknown")

        # Extract locations
        locations = [
            loc.get("description", {}).get("en", "Unknown")
            for loc in data.get("locations", [])
        ]

        # Extract threats
        threats = [
            thr.get("description", {}).get("en", "Unknown")
            for thr in data.get("threats", [])
        ]
        
        # Extract scope (e.g. Global, Europe)
        scopes = [
           scope.get("description", {}).get("en", "Unknown")
           for scope in data.get("scopes", [])
       ]

        # Extract extinction status
        possibly_extinct = data.get("possibly_extinct", False)
        possibly_extinct_in_the_wild = data.get("possibly_extinct_in_the_wild", False)

        dict_assess = {
             "category": category,
             "category_description": category_description,
             "possibly_extinct": possibly_extinct,
             "possibly_extinct_in_the_wild": possibly_extinct_in_the_wild
         } 
        
    except Exception as e:
        print(f"Exception fetching assessment {assessment_id}: {e}")
   
    return dict_assess, locations, threats, scopes


# Fetch IUCN data for a list of plant names and build the assessment structure
# to export to a JSON file
def fetch_iucn_data(names, data_map):
    
    results = {}

    for name in names:
        print(f"Processing: {name}")
        norm_name = normalize_name(name)
        parts = norm_name.split()

        if len(parts) != 2:
            results[norm_name] = {"name": norm_name, "error": "Invalid name format"}
            continue

        genus, species = parts
        entry = {"name": norm_name, "assessments": []}
        if norm_name in data_map:
           entry.update(data_map[norm_name])

        tax_data = query_taxa(genus, species)
        assessments = tax_data.get("assessments", [])
        if not assessments:
            entry["error"] = "No assessments found"
            results[norm_name] = entry
            continue

        for row in assessments:
           assessment_id = row.get("assessment_id")
            
           # Retrieving "locations" e "threats"  from the function query assessment function
           assessment_data, locations, threats, scopes = query_assessment(assessment_id)

           entry["assessments"].append({
               "scope": scopes,
               "year_published": str(row.get("year_published")),
               "assessment_id": assessment_id,
               "category": assessment_data.get("category", "Unknown"),
               "category_description": assessment_data.get("category_description", "Unknown"),
               "possibly_extinct": assessment_data.get("possibly_extinct", False),
               "possibly_extinct_in_the_wild": assessment_data.get("possibly_extinct_in_the_wild", False),
               "locations": locations,
               "threats": threats
               })
        time.sleep(1.5)

        results[norm_name] = entry

    return results

# Main function to query the database and process data for medicinal plants
# 1. Executes database queries to retrieve active ingredients from the 
#    Medicinal Plants category
# 2. Fetches IUCN conservation status
# 3. Generates a JSON output to DCB List and active ingredients from HealDB

def iucn_export_conservation_status(cnx, cursor):
    # Query for HealDB
    sql_command_healdb = (
       "SELECT  h1.id_active_ingredient, "
       "LOWER(TRIM(SUBSTRING_INDEX(h1.nm_active_ingredient, ' ', 2))) AS scientific_name "
       "FROM hd_active_ingredient h1 "
       "JOIN hd_dcb_list h2 " 
       "ON TRIM(UPPER(h1.nm_active_ingredient)) = TRIM(UPPER(h2.nm_dcb)) "
       "JOIN hd_dcb_classification h3 " 
       "ON h2.id_dcb_classification = h3.id_dcb_classification "
       "WHERE h3.tp_dcb_classification = 'PM' "
       "ORDER BY 2 "
       )

    # Query for DCB
    sql_command_dcb = (
       "SELECT hdl.id_dcb, "
       "hdl.nr_dcb, "
       "LOWER(TRIM(SUBSTRING_INDEX(hdl.nm_dcb, ' ', 2))) AS scientific_name "
       "FROM hd_dcb_list hdl "
       "JOIN hd_dcb_classification hdc "
       "ON hdl.id_dcb_classification = hdc.id_dcb_classification "
       "WHERE hdc.tp_dcb_classification = 'PM' "
       "ORDER BY 3 "
    )

    cursor.execute(sql_command_healdb)
    healdb_rows = cursor.fetchall()
    healdb_data = {}
    for row in healdb_rows:
        norm_name = normalize_name(row[1])
        healdb_data[norm_name] = {"id_active_ingredient": row[0]}
    healdb_names = list(healdb_data.keys())

    cursor.execute(sql_command_dcb)
    dcb_rows = cursor.fetchall()
    dcb_data = {}
    for row in dcb_rows:
        norm_name = normalize_name(row[2])
        dcb_data[norm_name] = {"id_dcb": row[0], "nr_dcb": row[1]}
    dcb_names = list(dcb_data.keys())

    # Process HealDB
    print ("HealDB data")
    healdb_results = fetch_iucn_data(healdb_names, healdb_data)

    # Process DCB
    print ("DCB data")
    dcb_results = fetch_iucn_data(dcb_names, dcb_data)

    # Save HealDB JSON
    healdb_output = PATHS["output_iucn"] + "/iucn_conservation_healdb.json"
    with open(healdb_output, "w", encoding="utf-8") as f:
        json.dump(healdb_results, f, indent=2, ensure_ascii=False)
        

    # Save DCB JSON
    dcb_output = PATHS["output_iucn"] + "/iucn_conservation_dcb.json"
    with open(dcb_output, "w", encoding="utf-8") as f:
        json.dump(dcb_results, f, indent=2, ensure_ascii=False)
        

    print(f"Saved HealDB output to: {healdb_output}")
    print(f"Saved DCB output to: {dcb_output}")

    return