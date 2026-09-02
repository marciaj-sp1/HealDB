# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 21:21:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br
"""

# Retrieves scientific publications for PubChem CIDs associated with active ingredients
# used in medications classified under the therapeutic class "antidepressant".
#
# This script uses the PubChemRDF REST interface to retrieve scientific references
# associated with chemical compounds via their PubChem CID.
#
# The relationship vocab:discussesAsDerivedByTextMining is used to retrieve PubChem
# references associated with each compound. The dcterms:identifier property is then
# used to obtain the corresponding PubMed identifier (PMID).
#
# Publication metadata (title, journal, date) are retrieved from PubMed using the
# NCBI Entrez E-Utilities API (esummary.fcgi).
#
# This approach enables access to PubChemRDF relationships without downloading and
# locally storing the complete RDF datasets.
#
# Outputs a structured JSON file including:
# - id_active_ingredient
# - nm_active_ingredient
# - cd_pubchem_cid
# - up to 3 scientific publications (PMID, title, journal, date)
# If no publications are found, the entry is excluded from the output.

import requests
import xml.etree.ElementTree as ET
import json
import time
from config import PATHS, APIS_USE_CASES


# Load PUBCHEM API configuration from the external configuration file
PUBCHEM_API = APIS_USE_CASES["pubchem"]

# PubChemRDF REST query endpoint
PUBCHEM_RDF_URL = PUBCHEM_API["rdf_query_url"]

# Retrieves PubChem reference IDs associated with a PubChem CID
def get_references_from_pubchem_cid(pubchem_cid):
    params = {
        "graph": "reference",
        "predicate": "vocab:discussesAsDerivedByTextMining",
        "object": f"compound:CID{pubchem_cid}",
        "format": "json"
    }

    try:
        response = requests.get(
            PUBCHEM_RDF_URL,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        content = response.json()
        references = []

        bindings = content.get("results", {}).get("bindings", [])

        for binding in bindings:
            subject = binding.get("subject", {}).get("value")

            if subject:
                reference_id = subject.rsplit("/", 1)[-1]
                references.append(reference_id)

        return references

    except Exception as e:
        print(
            f"Error retrieving references for "
            f"PubChem CID {pubchem_cid}: {e}"
        )
        return []


# Retrieves the PMID associated with a PubChem reference
def get_pmid_from_reference(reference_id):
    params = {
        "graph": "reference",
        "predicate": "dcterms:identifier",
        "subject": f"reference:{reference_id}",
        "format": "json"
    }

    try:
        response = requests.get(
            PUBCHEM_RDF_URL,
            params=params,
            timeout=30
        )
        response.raise_for_status()

        content = response.json()

        bindings = content.get("results", {}).get("bindings", [])

        for binding in bindings:
            identifier = binding.get("object", {}).get("value")

            if (
                identifier
                and "pubmed.ncbi.nlm.nih.gov/" in identifier
            ):
                pmid = (
                    identifier
                    .rstrip("/")
                    .rsplit("/", 1)[-1]
                )

                return pmid

    except Exception as e:
        print(
            f"Error retrieving PMID for "
            f"PubChem reference {reference_id}: {e}"
        )

    return None


# Retrieves PMIDs from PubChemRDF using PubChem CID
def get_pmids_from_pubchem_cid(pubchem_cid):
    references = get_references_from_pubchem_cid(pubchem_cid)

    if not references:
        return []

    pmids = []

    for reference_id in references:

        pmid = get_pmid_from_reference(reference_id)

        if pmid and pmid not in pmids:
            pmids.append(pmid)

        # Stop after retrieving three PubMed publications
        if len(pmids) == 3:
            break

        time.sleep(0.2)

    return pmids


# Retrieves publication details (title, journal, date) for a given PMID
def get_article_details(pmid):
    url = PUBCHEM_API["esummary_url"]
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        content = ET.fromstring(response.content)

        title = content.find(".//Item[@Name='Title']")
        source = content.find(".//Item[@Name='Source']")
        pub_date = content.find(".//Item[@Name='PubDate']")

        return {
            "pmid": pmid,
            "title": title.text if title is not None else "N/A",
            "journal": source.text if source is not None else "N/A",
            "date": pub_date.text if pub_date is not None else "N/A"
        }

    except Exception as e:
        return {
            "pmid": pmid,
            "title": "Error",
            "journal": str(e),
            "date": "N/A"
        }

    return


# Main function that queries the database and exports the enriched JSON
def pubchem_export_references(cnx, cursor):
    sql_command = (
        "SELECT DISTINCT "
        "       a.id_active_ingredient, "
        "       a.nm_active_ingredient, "
        "       e.cd_ext_id "
        " FROM hd_active_ingredient a "
        " JOIN hd_medication_active_ingredient m ON a.id_active_ingredient = m.id_active_ingredient "
        " JOIN hd_medication m1 ON m1.id_medication = m.id_medication "
        " JOIN hd_therapeutic_class t ON m1.id_therapeutic_class = t.id_therapeutic_class "
        " JOIN hd_active_ingredient_ext_id e ON e.id_active_ingredient = a.id_active_ingredient "
        "WHERE UPPER(t.ds_therapeutic_class) LIKE '%ANTIDEPRESSIVO%' "
        "  AND e.tp_ext_id = 'PUBCHEM_CID' "
    )

    cursor.execute(sql_command)
    rows = cursor.fetchall()

    # Limit to a maximum of 100 rows
    #rows = rows[:100]

    json_output = []

    print("Starting data extraction...\n")

    for row in rows:
        id_active_ingredient = str(row[0])
        nm_active_ingredient = row[1]
        pubchem_cid = str(row[2])

        print(f"PUBCHEM CID {pubchem_cid} - {nm_active_ingredient}")

        pmids = get_pmids_from_pubchem_cid(pubchem_cid)

        if not pmids:
            continue

        publications = []

        pmids = pmids[:3]

        for pmid in pmids:
            details = get_article_details(pmid)
            publications.append(details)
            time.sleep(0.4)

        json_output.append({
            "id_active_ingredient": id_active_ingredient,
            "nm_active_ingredient": nm_active_ingredient,
            "cd_pubchem_cid": pubchem_cid,
            "publications": publications
        })

    output_pubchem_ref_file = (
        f"{PATHS['output_pubchem']}/"
        "pubchem_reference_healdb.json"
    )

    with open(
        output_pubchem_ref_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            json_output,
            f,
            indent=4,
            ensure_ascii=False
        )

    print(f"\nExport completed: {output_pubchem_ref_file}")

    return