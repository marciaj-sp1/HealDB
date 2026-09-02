# -*- coding: utf-8 -*-
"""
Created on Sun Jul 05 21:40:00 2026

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script validates the ChEBI identifiers (CHEBI) obtained from
# Wikidata by querying the ChEBI API. The ontology relationships are
# inspected to identify the preferred identifier representing the
# active ingredient. The validation result is stored in the
# Wikidata working table through the fl_preferred flag.

import time
import requests
from config import URLS_EXTERNAL_IDS

CHEBI_API = URLS_EXTERNAL_IDS["chebi_api_url"]


def get_chebi_information(chebi_id):

    try:

        response = requests.get(
            CHEBI_API.format(chebi_id),
            timeout=20
        )

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None


def is_preferred_chebi(data):

    if data is None:
        return False

    ontology = data.get("ontology_relations", {})

    incoming = ontology.get("incoming_relations", [])
    outgoing = ontology.get("outgoing_relations", [])

    for relation in incoming + outgoing:

        relation_type = relation.get("relation_type", "").lower()

        if relation_type in (
            "is tautomer of",
            "is conjugate acid of",
            "is conjugate base of"
        ):
            return False

    return True

def validate_wikidata_chebi(cnx, cursor):

    sql_command = (
        "UPDATE hd_wrk_wikidata_ext_id "
        "SET fl_preferred = NULL "
        "WHERE tp_ext_id = 'CHEBI'"
    )
    cursor.execute(sql_command)
    cnx.commit()

    sql_command = (
        "SELECT cd_rxcui, cd_ext_id "
        "FROM hd_wrk_wikidata_ext_id "
        "WHERE tp_ext_id = 'CHEBI' "
        "ORDER BY cd_rxcui, cd_ext_id"
    )
    cursor.execute(sql_command)

    rows = cursor.fetchall()
    total = len(rows)

    print(f"Processing {total} ChEBI identifiers...\n")

    for i, (healdb_rxcui, chebi_id) in enumerate(rows, start=1):

        chebi_data = get_chebi_information(chebi_id)

        flag = "Y" if is_preferred_chebi(chebi_data) else "N"

        sql_command = (
            "UPDATE hd_wrk_wikidata_ext_id "
            "SET fl_preferred = %s "
            "WHERE cd_rxcui = %s "
            "AND tp_ext_id = 'CHEBI' "
            "AND cd_ext_id = %s"
        )

        cursor.execute(
            sql_command,
            (flag, healdb_rxcui, chebi_id)
        )

        cnx.commit()

        print(
            f"[{i}/{total}] "
            f"RXCUI={healdb_rxcui} "
            f"CHEBI={chebi_id} "
            f"Name={chebi_data.get('name', 'N/A')} "
            f"Preferred={flag}"
        )   

        time.sleep(0.2)

    print("ChEBI validation completed.")

    return