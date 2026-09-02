# -*- coding: utf-8 -*-
"""
Created on Sun Jul 05 17:35:00 2026

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script validates the PubChem Compound IDs (PUBCHEM_CID) obtained from
# Wikidata by querying the PubChem PUG View API. The returned RXCUI is compared
# with the HealDB RXCUI, and the validation result is stored in the
# Wikidata working table through the fl_preferred flag.

import time
import requests
from config import URLS_EXTERNAL_IDS

PUBCHEM_API = URLS_EXTERNAL_IDS["pubchem_pug_view_api_url"]

def search_toc_heading(node,heading):
    if isinstance(node,dict):
        if node.get("TOCHeading")==heading:
            return node
        for v in node.values():
            r=search_toc_heading(v,heading)
            if r:return r
    elif isinstance(node,list):
        for i in node:
            r=search_toc_heading(i,heading)
            if r:return r
    return None

def extract_rxcui(pubchem_json):
    node=search_toc_heading(pubchem_json,"RXCUI")
    if node is None:return None
    try:
        return node["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
    except:
        return None

def get_pubchem_rxcui(cid):
    try:
        r=requests.get(PUBCHEM_API.format(cid),timeout=20)
        if r.status_code!=200:return None
        return extract_rxcui(r.json())
    except:
        return None

def validate_wikidata_pubchem(cnx, cursor):

    sql_command = (
        "UPDATE hd_wrk_wikidata_ext_id "
        "SET fl_preferred = NULL "
        "WHERE tp_ext_id = 'PUBCHEM_CID'"
    )
    cursor.execute(sql_command)
    cnx.commit()

    sql_command = (
        "SELECT cd_rxcui, cd_ext_id "
        "FROM hd_wrk_wikidata_ext_id "
        "WHERE tp_ext_id = 'PUBCHEM_CID' "
        "ORDER BY cd_rxcui, cd_ext_id"
    )
    cursor.execute(sql_command)

    rows = cursor.fetchall()
    total = len(rows)

    print(f"Processing {total} PubChem identifiers...\n")

    for i, (healdb_rxcui, pubchem_cid) in enumerate(rows, start=1):

        rx = get_pubchem_rxcui(pubchem_cid)

        flag = "Y" if rx is not None and str(rx) == str(healdb_rxcui) else "N"

        sql_command = (
            "UPDATE hd_wrk_wikidata_ext_id "
            "SET fl_preferred = %s "
            "WHERE cd_rxcui = %s "
            "AND tp_ext_id = 'PUBCHEM_CID' "
            "AND cd_ext_id = %s"
        )

        cursor.execute(
            sql_command,
            (flag, healdb_rxcui, pubchem_cid)
        )

        cnx.commit()
        print(
            f"[{i}/{total}] "
            f"RXCUI={healdb_rxcui} "
            f"CID={pubchem_cid} "
            f"Preferred={flag}"
        )

        time.sleep(0.2)

    print("PubChem validation completed.")

    return