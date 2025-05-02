# -*- coding: utf-8 -*-
"""
Created on Mon Mar 03 13:17:00 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script fetches and stores external IDs found in Wikidata  
# using RXCUI as the input data. These IDs will be used to fill  
# in missing external identifiers, enabling links to other  
# medical sources and ontologies.


import time
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON, POST
from config import URLS_EXTERNAL_IDS

# Wikidata SPARQL Endpoint
WIKIDATA_SPARQL_URL = URLS_EXTERNAL_IDS["wikidata_sparql_url"]

def fetch_active_ingredient_rxcui(cnx, cursor):
    # Fetch all the active ingredients in HealDB with RXCUI available

    sql_command = (
        "SELECT distinct cd_ext_id as rxcui "
        "FROM healdb.hd_active_ingredient_ext_id "
        "WHERE tp_ext_id = 'RXCUI' "
    )
    
    cursor.execute(sql_command)
    results = cursor.fetchall()
        
    return pd.DataFrame(results, columns=["rxcui"])

def fetch_wikidata_ids(rxcui_list):
    # Fetches external IDs from Wikidata in batches of 500 RXCUIs

    sparql = SPARQLWrapper(WIKIDATA_SPARQL_URL)
    sparql.setMethod(POST)  # Use POST method for larger queries
    
    # Builds the SPARQL query with an IN filter for RXCU
    rxcui_filter = ", ".join(f'"{rxcui}"' for rxcui in rxcui_list)

    sparql_command = (
            "PREFIX wdt: <http://www.wikidata.org/prop/direct/> "
            "PREFIX wd: <http://www.wikidata.org/entity/> "
            "SELECT ?rxcui ?compound ?cas_number ?drugbank_id ?pubchem_cid ?chebi_id ?snomed_ct ?atc ?unii_code ?kegg_compound ?kegg_drug "
            " WHERE { "
            "   ?compound wdt:P3345 ?rxcui. "
            "   FILTER (?rxcui IN (" + rxcui_filter + "))  "      
            "   OPTIONAL { ?compound wdt:P231 ?cas_number. } "    
            "   OPTIONAL { ?compound wdt:P715 ?drugbank_id. } "   
            "   OPTIONAL { ?compound wdt:P662 ?pubchem_cid. } "   
            "   OPTIONAL { ?compound wdt:P683 ?chebi_id. } "      
            "   OPTIONAL { ?compound wdt:P5806 ?snomed_ct. } "    
            "   OPTIONAL { ?compound wdt:P267 ?atc. } "           
            "   OPTIONAL { ?compound wdt:P652 ?unii_code. } "     
            "   OPTIONAL { ?compound wdt:P665 ?kegg_compound. } " 
            "   OPTIONAL { ?compound wdt:P1268 ?kegg_drug. } "    
            "} "
    )
    sparql.setQuery(sparql_command)
    sparql.setReturnFormat(JSON)

    try:
        response = sparql.query().convert()
        query_results = response["results"]["bindings"]

        extracted_data = []
        for entry in query_results:
            record = {
                "rxcui": entry["rxcui"]["value"] if "rxcui" in entry else None,
                "cas_number": entry["cas_number"]["value"] if "cas_number" in entry else None,
                "drugbank_id": entry["drugbank_id"]["value"] if "drugbank_id" in entry else None,
                "pubchem_cid": entry["pubchem_cid"]["value"] if "pubchem_cid" in entry else None,
                "chebi_id": entry["chebi_id"]["value"] if "chebi_id" in entry else None,
                "snomed_ct": entry["snomed_ct"]["value"] if "snomed_ct" in entry else None,
                "atc": entry["atc"]["value"] if "atc" in entry else None,
                "unii_code": entry["unii_code"]["value"] if "unii_code" in entry else None,
                "kegg_compound": entry["kegg_compound"]["value"] if "kegg_compound" in entry else None,
                "kegg_drug": entry["kegg_drug"]["value"] if "kegg_drug" in entry else None,
                "ds_url_wikidata": entry["compound"]["value"] if "compound" in entry else None  # URL do item no Wikidata
            }
            extracted_data.append(record)
            
        return pd.DataFrame(extracted_data)

    except Exception as e:
        print(f"Error querying Wikidata: {e}")
    return pd.DataFrame()

def link_wikidata_ids_to_stg(cnx, cursor):
    # Processes active ingredients and stores them in a Wikidata working table
    # Fetches active ingredients with RXCUI
    df_rxcui = fetch_active_ingredient_rxcui(cnx, cursor)

    if df_rxcui.empty:
        print("# No active ingredients with RXCUI found in the table.")
        return

    print(f"Processing {len(df_rxcui)} rxcui codes in batches of 100...")

    # Clears the working table before inserting new data
    cursor.execute("TRUNCATE TABLE healdb.hd_wrk_wikidata_ext_id")
    cnx.commit()

    batch_size = 100
    total_inserted = 0

    for i in range(0, len(df_rxcui), batch_size):
        batch = df_rxcui.iloc[i:i+batch_size]
        df_wikidata = fetch_wikidata_ids(batch["rxcui"].tolist())  # Busca pelo RXCUI
        
        if not df_wikidata.empty:
            # Links using RXCUI as the key
            df_merged = batch.merge(df_wikidata, left_on="rxcui", right_on="rxcui", how="left")
            
            # Insert the data in the working table
            sql_command = (
                "INSERT INTO healdb.hd_wrk_wikidata_ext_id "
                "(cd_rxcui, tp_ext_id, cd_ext_id, ds_url_wikidata) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE ds_url_wikidata = VALUES(ds_url_wikidata) "
            )
            #Query hd_type_ext_id to obtain the valid list of external ids types 
            cursor.execute("SELECT tp_ext_id FROM healdb.hd_type_ext_id;")
            valid_tp_ext_ids = {row[0] for row in cursor.fetchall()}
            
            values = set()
            for _, row in df_merged.iterrows():
                for col, tp_ext_id in [
                    ("cas_number", "CAS"), 
                    ("drugbank_id", "DRUGBANK"), 
                    ("pubchem_cid", "PUBCHEM_CID"), 
                    ("chebi_id", "CHEBI"), 
                    ("snomed_ct", "SNOMEDCT"), 
                    ("atc", "ATC"), 
                    ("unii_code", "UNII_CODE")
                ]:
                    if pd.notnull(row[col]) and tp_ext_id in valid_tp_ext_ids:
                        values.add((
                            row["rxcui"], 
                            tp_ext_id, 
                            row[col], 
                            row["ds_url_wikidata"]  
                        ))

                if pd.notnull(row["kegg_compound"]):  
                    if row["kegg_compound"].startswith("C") and "KEGG_COMP" in valid_tp_ext_ids:  
                        values.add((row["rxcui"], "KEGG_COMP", row["kegg_compound"], row["ds_url_wikidata"]))
                    elif row["kegg_compound"].startswith("D") and "KEGG_DRUG" in valid_tp_ext_ids:  
                        values.add((row["rxcui"], "KEGG_DRUG", row["kegg_compound"], row["ds_url_wikidata"]))

                if pd.notnull(row["kegg_drug"]) and "KEGG_DRUG" in valid_tp_ext_ids:  
                    values.add((row["rxcui"], "KEGG_DRUG", row["kegg_drug"], row["ds_url_wikidata"]))
            values = list(values)
            if values:
                cursor.executemany(sql_command, values)
                cnx.commit()
                total_inserted += len(values)

        print(f"Batch {i//batch_size + 1}/{len(df_rxcui)//batch_size + 1} processed.")
        time.sleep(2)  # Prevent Error 429

    print(f"Data inserted in the table hd_wrk_wikidata_ext_id: {total_inserted} records.")

    return
