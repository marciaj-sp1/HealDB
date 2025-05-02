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
# This script uses the NCBI Entrez E-Utilities API (elink.fcgi) to retrieve PubMed publications
# that are directly linked to chemical compounds via their PubChem CID.
# PubChem itself does not store publication content, but only provide link to
# PubMed. 
# The elink.fcgi endpoint is the official and efficient way to navigate these cross-database
# relationships maintained by NCBI (e.g., from PubChem Compound to PubMed).
#
# Outputs a structured JSON file including:
# - id_active_ingredient
# - nm_active_ingredient
# - cd_pubchem_cid
# - up to 3 scientific publications (PMID, title, journal, date), the most recent
# If no publications are found, the entry is excluded from the output.

import requests
import xml.etree.ElementTree as ET
import json
import time
from config import PATHS

# Retrieves PMIDs from PubChem using the elink API
def get_pmids_from_pubchem_cid(pubchem_cid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"
    params = {
        "dbfrom": "pccompound",
        "id": pubchem_cid,
        "db": "pubmed"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        content = ET.fromstring(response.content)
        pmids = []
        for link in content.findall(".//LinkSetDb/Link"):
            id_node = link.find("Id")
            if id_node is not None and id_node.text:
                pmids.append(id_node.text)
        return pmids
    except Exception as e:
        print(f"Error for Pubchem CID {pubchem_cid}: {e}")
        return []

# Retrieves publication details (title, journal, date) for a given PMID
def get_article_details(pmid):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml"
    }
    try:
        print ("antes da chamada da api, pmid = ", pmid)
        response = requests.get(url, params=params, timeout=10)
        content = ET.fromstring(response.content)
        print ("após a chamada da api")
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
    
# Sort publications by date (descending) and keep only the top 3
def parse_date(pub):
    try:
        parts = pub["date"].split()
        year = int(parts[0])
        month = parts[1] if len(parts) > 1 else "Jan"
        month_map = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        return (year, month_map.get(month, 1))
    except:
        return (0, 1)


# Main function that queries the database and exports the enriched JSON
def export_pubchem_ref_with_details(cnx, cursor):
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
    rows = rows[:10]

    json_output = []

    print("Starting data extraction...\n")

    for row in rows:
        id_active_ingredient = str(row[0])
        nm_active_ingredient = row[1]
        pubchem_cid = str(row[2])

        print(f"PUBCHEM CID {pubchem_cid} - {nm_active_ingredient}")
        pmids = get_pmids_from_pubchem_cid(pubchem_cid)
        print ("pmids = ", pmids)

        if not pmids:
            continue

        publications = []
        for pmid in pmids:
            details = get_article_details(pmid)
            publications.append(details)
            time.sleep(0.4)
            
               
        # Sort the publications by parsed date in descending order 
        # and keep the 3 most recent
        sorted_publications = sorted(publications, key=parse_date, reverse=True)
        publications = sorted_publications[:3]   
        print ("publications after sorted = ", publications)

        json_output.append({
            "id_active_ingredient": id_active_ingredient,
            "nm_active_ingredient": nm_active_ingredient,
            "cd_pubchem_cid": pubchem_cid,
            "publications": publications
        })

    output_pubchem_ref_file = f"{PATHS['output_pubchem']}/pubchem_reference_detailed.json"
    with open(output_pubchem_ref_file, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=4, ensure_ascii=False)

    print("\nExport completed:")
    print("- pubchem_reference_detailed.json")

    return
