# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br
"""

# This script retrieves detailed conservation information for medicinal plants classified as
# "PM" (Planta Medicinal) in the Brazilian Common Denomination (DCB) list, including:
#  - IUCN conservation status (category and year)
#  - Geographic distribution with origin and presence status
#  - Reported threats and habitats
#
# It uses the IUCN Red List API v4 and processes all active ingredients found in the HealDB database.
# Results are saved to JSON files.

import requests
import re
import time
import json
from config import PATHS, APIS_USE_CASES, CATEGORY_MEANINGS

IUCN_API = APIS_USE_CASES["iucn"]


def clean_name(name):
    # Remove " L." from end and keep only genus and species.
    name = re.sub(r"\\sL\\.$", "", name)
    words = name.lower().split()
    words_cleaned = " ".join(words[:2])
    return words_cleaned

def query_geographic ():
    print ("query geographic")
    url = IUCN_API["base_geo_url"]
    print ("url = ", url)
    headers = {"Authorization": f"Token {IUCN_API['token']}"}
    print (headers)
    response = requests.get(url, headers=headers, timeout=15)
    response_json = {}
    if response.status_code == 200:
        response_json = response.json()
    print ("status code = ", response.status_code)
    print("RESPONSE JSON:")
    print(json.dumps(response.json(), indent=2))
    return response_json

def query_taxa(genus, species):
    print ("query taxa")
    print ("genus = ", genus)
    print ("species = ", species)
    url = IUCN_API["base_tax_url"]
    print ("url = ", url)
    params = {"genus_name": genus, "species_name": species}
    headers = {"Authorization": f"Token {IUCN_API['token']}"}
    print (headers)
    response = requests.get(url, headers=headers, params=params, timeout=15)
    response_json = {}
    if response.status_code == 200:
        response_json = response.json()
    print ("status code = ", response.status_code)
    print("RESPONSE JSON:")
    print(json.dumps(response.json(), indent=2))
    return response_json


def query_assessment(assessment_id):
    url = f"{IUCN_API['base_assessment_url']}/{assessment_id}"
    headers = {"Authorization": f"Token {IUCN_API['token']}"}
    response = requests.get(url, headers=headers, timeout=15)
    print (headers)
    response_json = {}
    print (response.status)
    if response.status_code == 200:
        response_json = response.json()
    return response_json


def process_plants(plants, output_list):
    total = 0

    for plant in plants:
        plant_data = {"name": plant}
        print(f"Processing plant: {plant}")

        # Break into genus and species
        cleaned = clean_name(plant)
        parts = cleaned.split()
        if len(parts) != 2:
            continue
        genus, species = parts

        data_geo = query_geographic()
        print ("data geo = ", data_geo)

        tax_data = query_taxa(genus, species)
        if not tax_data.get("assessments"):
            print(f"No taxonomic data found for {plant}")
            continue

        for entry in tax_data["assessments"]:
            plant_data = {"name": plant}
            assessment_id = entry.get("assessment_id")
            if not assessment_id:
                continue

            # Store basic info
            plant_data.update({
                "scientific_name": tax_data.get("scientific_name"),
                "taxon_id": entry.get("sis_taxon_id"),
                "assessment_id": assessment_id,
                "category": entry.get("category"),
                "meaning": CATEGORY_MEANINGS.get(entry.get("category", ""), "Unknown status"),
                "year_assessed": entry.get("year_published"),
                "criteria": entry.get("criteria")
            })

            # Get detailed assessment
            assessment = query_assessment(assessment_id)
            if assessment:
                plant_data["population_trend"] = assessment.get("population_trend")
                plant_data["range"] = assessment.get("range")
                plant_data["habitats"] = assessment.get("habitats")
                plant_data["locations"] = assessment.get("locations")
                plant_data["threats"] = assessment.get("threats")
                plant_data["use_trade"] = assessment.get("use_trade")
                plant_data["conservation_actions"] = assessment.get("conservation_actions")

            output_list.append(plant_data)
            total += 1
            time.sleep(1.5)

    return total


def iucn_export_conservation_status(cnx, cursor):
    print("Starting IUCN Detailed Conservation Status processing...")

    sql_command = (
        "SELECT UPPER(h1.nm_active_ingredient) AS nm_active_ingredient "
        "FROM hd_active_ingredient h1 "
        "JOIN hd_dcb_list h2 ON TRIM(UPPER(h1.nm_active_ingredient)) = TRIM(UPPER(h2.nm_dcb)) "
        "JOIN hd_dcb_classification h3 ON h2.id_dcb_classification = h3.id_dcb_classification "
        "WHERE h3.tp_dcb_classification = 'PM' "
        "ORDER BY 1 "
        "LIMIT 1 "
    )

    cursor.execute(sql_command)
    raw_names = [row[0] for row in cursor.fetchall()]
    cleaned_names = [clean_name(name) for name in raw_names]

    output_data = []
    total_processed = process_plants(cleaned_names, output_data)

    output_iucn_path = f"{PATHS['output_data']}/iucn_conservation_healdb.json"
    with open(output_iucn_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"\nProcessed {total_processed} plants.")
    print(f"Output saved to {output_iucn_path}")
    return
