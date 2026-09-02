# -*- coding: utf-8 -*-
"""
Created on Sun Mar 03 19:08;50 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script links external identifiers from KEGG (PubChem CIDs and ChEBI IDs)
# to active ingredients in HealDB. It retrieves KEGG Compound identifiers
# previously obtained via Wikidata, queries the KEGG API to obtain PubChem
# Substance IDs (SIDs) and ChEBI IDs, converts PubChem SIDs into PubChem CIDs
# using the PubChem API, and stores the resulting external identifiers in
# HealDB to enhance interoperability with other biomedical data sources.


import requests
from config import URLS_EXTERNAL_IDS
from src.interoperability.linking.insert_external_id import insert_external_id

# KEGG API Base URL
KEGG_API_URL = URLS_EXTERNAL_IDS["kegg_api_url"]
PUBCHEM_SID_TO_CID_API = URLS_EXTERNAL_IDS["pubchem_sid_to_cid_api_url"]

def get_related_ids_from_kegg(kegg_id):
   # Get all PubChem CIDs and a single ChEBI ID from KEGG
    pubchem_sids = []
    chebi = None
    
    response = requests.get(KEGG_API_URL.format(kegg_id))

    if response.status_code == 200:
        text = response.text
        pubchem_sid_set = set()  # Use a set to avoid duplicates
        chebi = None

        for line in text.split('\n'):
            if "PubChem" in line:
                pubchem_sid_set.add(line.split()[-1])  # Store all PubChem SIDs
            elif "ChEBI" in line and chebi is None:
                chebi = line.split()[-1]  # Keep only the first ChEBI ID

        pubchem_sids = list(pubchem_sid_set)
    else:
        print(f"KEGG API Error: {response.status_code} for KEGG ID: {kegg_id}")
    
    return pubchem_sids, chebi

def get_pubchem_cid_from_sid(pubchem_sid):

    try:

        response = requests.get(
            PUBCHEM_SID_TO_CID_API.format(pubchem_sid),
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        information = (
            data
            .get("InformationList", {})
            .get("Information", [])
        )

        if information:

            cids = information[0].get("CID", [])

            if cids:
                return str(cids[0])

    except Exception:
        pass

    return None

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
        
        total = len(active_ingredients)

        print(f"Processing {total} KEGG identifiers...\n")

        if not active_ingredients:
            print("No active ingredients found with KEGG IDs.")
            return

        print(f"Processing {len(active_ingredients)} KEGG ids...")

        for i, (id_active_ingredient, kegg_id, tp_ext_id) in enumerate(
                active_ingredients, start=1):
            # Fetch related IDs from KEGG API
            pubchem_sids, chebi = get_related_ids_from_kegg(kegg_id)
            
            print(
                f"[{i}/{total}] "
                f"id_active_ingredient={id_active_ingredient} | "
                f"KEGG={kegg_id}"
            )

            # Insert KEGG_ID (source: Wikidata)
            insert_external_id(cursor, cnx, 
                               id_active_ingredient,
                               tp_ext_id, kegg_id, 
                               "WIKIDATA")
            
            # Insert all PubChem CIDs
            for pubchem_sid in pubchem_sids:
                pubchem_cid = get_pubchem_cid_from_sid(pubchem_sid)
                if pubchem_cid:
                    insert_external_id(cursor, cnx, 
                                       id_active_ingredient, 
                                       "PUBCHEM_CID", 
                                       pubchem_cid, 
                                       "KEGG")
                    
                print(f"    SID={pubchem_sid} -> CID={pubchem_cid}")

            # Insert ChEBI (if found)
            if chebi:
                insert_external_id(cursor, cnx, id_active_ingredient, "CHEBI", chebi, "KEGG")

        print("Success - KEGG-related external IDs linked.")

    except Exception as e:
        print(f"Error linking external IDs: {e}")
    return