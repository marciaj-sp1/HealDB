# -*- coding: utf-8 -*-
"""
Created on Sun Mar 02 16:09:00 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Link RxNorm Concept Unique Identifiers (RXCUI) to active ingredients stored  
# in HealDB enabling interoperability with external biomedical ontologies and 
# databases.

import requests
import time
from config import URLS_EXTERNAL_IDS
from src.interoperability.external_ids_insert import (
    insert_external_id
)

# RXNorm API Base URL
RXNORM_API_URL = URLS_EXTERNAL_IDS["rxnorm_api_url"]


def get_rxcui(nm_active_ingredient_eng):
    # Search RxCUI using the active ingredient name
    rxcui = None  # valor padrão

    response = requests.get(RXNORM_API_URL.format(nm_active_ingredient_eng))

    if response.status_code == 200:
        data = response.json()
        id_group = data.get("idGroup", {})
        rxnorm_ids = id_group.get("rxnormId", [])
        
        if rxnorm_ids:
            rxcui = rxnorm_ids[0]
    else:
        print(f"RXNorm API Error: {response.status_code}")

    return rxcui



def link_rxcui_to_active_ing(cnx, cursor):
    # Link the rxcui external id to active ingredient, searching the following
    # source: RXNORM

    try:
        # Fetch active ingredients from HealDB
        sql_command = (
            "SELECT id_active_ingredient, nm_active_ingredient_eng "
            "FROM healdb.hd_translate_eng_active_ing "
            "WHERE nm_active_ingredient_eng IS NOT NULL "
        )
        cursor.execute(sql_command)
        active_ingredients = cursor.fetchall()

        for id_active_ingredient, nm_active_ingredient_eng in active_ingredients:
            # Step 3: Search RXCUI from RXNorm API
            print(f"Active ingredient: {id_active_ingredient} Name: {nm_active_ingredient_eng}")
            time.sleep(1)  # Wait 3 seconds before calling the API again
            rxcui = get_rxcui(nm_active_ingredient_eng)

            if rxcui:
                insert_external_id(cursor, cnx, id_active_ingredient, "RXCUI", rxcui, "RXNORM")
        print("Success - link rxcui external ids.")

    except Exception as e:
        print(f"Error linking rxcui external ids: {e}")
    return
