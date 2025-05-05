# -*- coding: utf-8 -*-
"""
Created on Sun Mar 03 19:08;50 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script links external identifiers from KEGG (PubChem CIDs and ChEBI IDs) 
# to active ingredients in HealDB. It uses KEGG Compound and KEGG Drug 
# identifiers previously obtained via Wikidata, queries the KEGG API,
# and inserts the related IDs to enhance interoperability with other 
# biomedical data sources and ontologies.



import requests
from config import URLS_EXTERNAL_IDS
from src.interoperability.external_ids_insert import insert_external_id

# KEGG API Base URL
KEGG_API_URL = URLS_EXTERNAL_IDS["kegg_api_url"]

def get_related_ids_from_kegg(kegg_id):
   # Get all PubChem CIDs and a single ChEBI ID from KEGG
    pubchem_cids = []
    chebi = None
    
    response = requests.get(KEGG_API_URL.format(kegg_id))

    if response.status_code == 200:
        text = response.text
        pubchem_cid_set = set()  # Use a set to avoid duplicates
        chebi = None

        for line in text.split('\n'):
            if "PubChem" in line:
                pubchem_cid_set.add(line.split()[-1])  # Store all PubChem CIDs
            elif "ChEBI" in line and chebi is None:
                chebi = line.split()[-1]  # Keep only the first ChEBI ID

        pubchem_cids = list(pubchem_cid_set)
    else:
        print(f"KEGG API Error: {response.status_code} for KEGG ID: {kegg_id}")
    
    return pubchem_cids, chebi


def link_kegg_related_ids_to_active_ing(cnx, cursor):
    # Link KEGG external IDs to active ingredients in HealDB 
    
    try:
        # Remove KEGG IDs from the external IDs table
        sql_command = (
            "DElETE from healdb.hd_active_ingredient_ext_id "
            "   WHERE fl_origin_ext_id = 'KEGG' "
            "     OR tp_ext_id like 'KEGG%' "
            )
        cursor.execute(sql_command)
        cnx.commit()

        # Fetch KEGG_COMP from hd_wrk_wikidata_ext_id
        sql_command = (
            "SELECT DISTINCT a.id_active_ingredient, w.cd_ext_id, w.tp_ext_id "
            "FROM hd_wrk_wikidata_ext_id w "
            ",hd_active_ingredient_ext_id a "
            "WHERE a.cd_ext_id = w.cd_rxcui "
            "AND   w.tp_ext_id = 'KEGG_COMP' "
            "AND   a.tp_ext_id = 'RXCUI' "
        )
        cursor.execute(sql_command)
        active_ingredients = cursor.fetchall()

        if not active_ingredients:
            print("No active ingredients found with KEGG IDs.")
            return

        print(f"Processing {len(active_ingredients)} KEGG ids...")

        for id_active_ingredient, kegg_id, tp_ext_id in active_ingredients:
            # Fetch related IDs from KEGG API
            pubchem_cids, chebi = get_related_ids_from_kegg(kegg_id)
            
            print (f"Processing id_active_ingredient {id_active_ingredient}, kegg_id: {kegg_id}")

            # Insert KEGG_ID (source: Wikidata)
            insert_external_id(cursor, cnx, id_active_ingredient, tp_ext_id, kegg_id, "WIKIDATA")

            # Insert all PubChem CIDs
            for pubchem_cid in pubchem_cids:
                insert_external_id(cursor, cnx, id_active_ingredient, "PUBCHEM_CID", pubchem_cid, "KEGG")

            # Insert ChEBI (if found)
            if chebi:
                insert_external_id(cursor, cnx, id_active_ingredient, "CHEBI", chebi, "KEGG")

        print("Success - KEGG-related external IDs linked.")

    except Exception as e:
        print(f"Error linking external IDs: {e}")
    return