# -*- coding: utf-8 -*-
"""
Created on Sun May 04 08:46:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br
"""
# To enrich the active ingredients in HealDB with drug-related information, 
# this script explores RxNorm’s public REST API using the RxCUI (RxNorm Concept 
# Unique Identifier) already linked to the database. 
# The RxNorm Concept Unique Identifier (RxCUI) refers to distinct drug concepts such as:
# IN (Ingredient), PIN (Precise Ingredient), SCD (Semantic Clinical Drug), 
# SBD (Semantic Branded Drug), GPCK (Generic Pack), BPCK (Branded Pack), 
# BN (Brand Name), SCDC (Semantic Clinical Dose Component), and 
# SBDC (Semantic Branded Dose Component).
# 
# Outputs a structured JSON file including:
# - id_active_ingredient
# - nm_active_ingredient
# - cd_rxcui
# - preferred_name
# - tty (IN-Ingredient, PIN-Precise Ingredient and others)
# - status
# - status_date
# - synonyms
# - clinical_presentations
# - branded presentations



import requests
import json
import time
from config import PATHS, APIS_USE_CASES

RXNORM_API = APIS_USE_CASES["rxnorm"]

# Retrieves basic properties from RxCUI ((name, tty and status)
def get_rxcui_properties(rxcui):
    url = RXNORM_API["property_url"].format(rxcui=rxcui)
    rxcui_property = {
        "preferred_name": None,
        "tty": None,
        "status": None,
        "status_date": None
    }
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("properties", {})
            rxcui_property["preferred_name"] = data.get("name")
            rxcui_property["tty"] = data.get("tty")
            rxcui_property["status"] = data.get("status")
            rxcui_property["status_date"] = data.get("statusDate")
    except Exception as e:
        print (f"Error retrieving properties from RxCUI {rxcui}, {e}")
            
    return rxcui_property

# Retrieves synonyms from RxCUI
def get_rxcui_synonyms(rxcui):
    url = RXNORM_API["synonym_url"].format(rxcui=rxcui)
    rxcui_synonym = []
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            names = response.json().get("propConceptGroup", {}).get("propConcept", [])
            for item in names:
                if "propValue" in item:
                    rxcui_synonym.append(item["propValue"])
        
    except Exception as e:
        print (f"Error retrieving synonyms from RxCUI {rxcui}, {e}")
            
    return rxcui_synonym

# Retrieves RxCUI entities for the specified term types (TTYs).
# Used to obtain clinical presentations (e.g., SCD) and branded presentations 
# (e.g., SBD, BPCK, SBDF, SBDC), including strength and dosage form.
 
def get_rxcui_entities(rxcui, types):
    rxcui_related = []

    for tty in types:
        url = RXNORM_API["related_url"].format(rxcui=rxcui) + f"?tty={tty}"
        #print(f"rxcui = {rxcui} | tty = {tty} | url = {url}")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                groups = data.get("relatedGroup", {}).get("conceptGroup", [])
                for group in groups:
                    concepts = group.get("conceptProperties", [])
                    for concept in concepts:
                        name = concept.get("name")
                        if name:
                            rxcui_related.append(name)
        except Exception as e:
            print(f"Error retrieving entities from RxCUI {rxcui}, tty {tty}: {e}")

        time.sleep(0.2)  # evita sobrecarga na API

    return rxcui_related



# Main function that enriches active ingredients from HealDB using RxNorm data.
# Retrieved data are name, tty, status, synonym, clinical and branded presentations.
# Results are exported to a JSON file.

def rxnorm_export_enrichment(cnx, cursor):
    sql_command = (
        "SELECT DISTINCT b.id_active_ingredient, a.nm_active_ingredient, b.cd_ext_id "
        "FROM hd_active_ingredient a "
        "INNER JOIN hd_active_ingredient_ext_id b " 
        "ON a.id_active_ingredient = b.id_active_ingredient "
        "WHERE b.tp_ext_id = 'RXCUI' "
    )
    cursor.execute(sql_command)
    rows = cursor.fetchall()

    # Optional: limit rows for testing
    #rows = rows[:5]

    json_output = []

    print("Starting active ingredient enrichment with RxNorm data\n")

    for row in rows:
        id_active_ingredient = str(row[0])
        nm_active_ingredient = row[1]
        rxcui = row[2]

        print(f"Processing {id_active_ingredient} - {nm_active_ingredient} (RxCUI {rxcui})")

        properties = get_rxcui_properties(rxcui)
        synonyms = get_rxcui_synonyms(rxcui)
        clinical = get_rxcui_entities(rxcui, types=["SCD"])      # retrieves clinical entity
        branded = get_rxcui_entities(rxcui, types=["SBD", "BPCK", "SBDF", "SBDC"]) # retrievs  branded entity
        

        rxnorm_data = {
            "id_active_ingredient": id_active_ingredient,
            "nm_active_ingredient": nm_active_ingredient,
            "cd_rxcui": rxcui,
            "preferred_name": properties.get("preferred_name"),
            "tty": properties.get("tty"),
            "status": properties.get("status"),
            "status_date": properties.get("status_date"),
            "synonyms": synonyms,
            "clinical_presentations": clinical,
            "branded_presentations": branded
        }

        json_output.append(rxnorm_data)

        time.sleep(0.5)

    # Save to JSON file
    output_rxnorm_path = f"{PATHS['output_rxnorm']}/rxnorm_enrichment_healdb.json"
    with open(output_rxnorm_path, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=4, ensure_ascii=False)

    print(f"\nExport completed: {output_rxnorm_path}")
    
    
    return