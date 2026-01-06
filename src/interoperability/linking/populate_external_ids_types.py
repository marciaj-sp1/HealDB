# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 21:20:00 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script populate the table with the types of external identifiers used 
# across various health data sources, such as DrugBank, PubChem, RxNorm, KEGG, 
# ChEBI, SNOMED CT, and others.


def populate_external_ids_types(cnx, cursor):
    # Check if there are external IDs stored in the table and insert them if the table is empty
    
    try:
        # Check if the table already contains data
        cursor.execute("SELECT COUNT(*) FROM healdb.hd_type_ext_id;")
        count = cursor.fetchone()[0]

        if count == 0:
            print("No external ID types found. Starting the insert step. ")

            # List of external ID types with short and long descriptions
            external_id_types = [
                ('CAS', 'CAS Number', 'Unique numerical identifier assigned by the Chemical Abstracts Service'),
                ('RXCUI', 'RxNorm CUI', 'Concept Unique Identifier from RxNorm for normalized drug names'),
                ('PUBCHEM_CID', 'PubChem Compound ID', 'Identifier for chemical compounds in PubChem Compound database'),
                ('KEGG_DRUG', 'KEGG Drug ID', 'Identifier for drugs in the KEGG Drug database'),
                ('KEGG_COMP', 'KEGG Compound ID', 'Identifier for chemical compounds in the KEGG Compound database'),
                ('DRUGBANK_ID', 'DrugBank ID', 'Unique identifier for drugs listed in the DrugBank database'),
                ('SNOMEDCT', 'SNOMED CT', 'Identifier from SNOMED Clinical Terms for medical concepts'),
                ('CHEBI', 'ChEBI ID', 'Identifier for chemical entities in the ChEBI database'),
                ('ATC', 'ATC Code', 'Anatomical Therapeutic Chemical Classification System code'),
                ('UNII_CODE', 'UNII Code', 'Unique Ingredient Identifier from the FDA for substances in drugs and biologics')
            ]

            # Insert each external ID type 
            for ext_id, short_desc, long_desc in external_id_types:
                sql_command = (
                    "INSERT INTO healdb.hd_type_ext_id (tp_ext_id, ds_short_type, ds_long_type) "
                    "VALUES (%s, %s, %s)"
                )
                register_ext_id = (ext_id, short_desc, long_desc)
                cursor.execute(sql_command, register_ext_id)
                cnx.commit()
                #print(f"Inserted {ext_id} - {short_desc}")

            print("External ID types successfully inserted.")
        else:
            print("External ID types already exist in the table.")

    except Exception as e:
        print(f"Error while inserting external ID types: {e}")
    return
