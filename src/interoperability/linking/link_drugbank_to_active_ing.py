# -*- coding: utf-8 -*-
"""
Created on Sun Jan 04 21:10:00 2026

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script aims to register, in `healdb.hd_active_ingredient_ext_id`, the
# DrugBank IDs obtained in a previous harmonization step (PT→EN translation and
# matching of active-ingredient names to DrugBank). It does not perform the
# harmonization; it only persists the resulting external identifier to support
# interoperability and downstream DrugBank-based analyses.


def link_drugbank_to_active_ing_ext_id(cnx, cursor):
    #  Persist DrugBank IDs as external identifiers for already-harmonized active ingredients.
    #  Preconditions: active ingredients have already been harmonized with 
    #  DrugBank (PT→EN + match); the mapping between active ingredients and 
    #  DrugBank entries is available in the mapping tables used by the query.

    
    try:
        print("Linking DRUGBANK_ID ...")

        sql_command = (
            "INSERT INTO healdb.hd_active_ingredient_ext_id "
            "(id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id) "
            "SELECT act.id_active_ingredient, 'DRUGBANK_ID', dru.id_drugbank, 'DRUGBANK' "
            "FROM healdb.hd_priv_active_ingredient_drug act "
            "INNER JOIN healdb.db_drug dru " 
            "   ON dru.id_drug = act.id_drug "
            "AND NOT EXISTS (SELECT 1 FROM healdb.hd_active_ingredient_ext_id ext "
            "                WHERE ext.id_active_ingredient = act.id_active_ingredient "
            "                  AND ext.tp_ext_id = 'DRUGBANK_ID' "
            "               ) "
        )

        cursor.execute(sql_command)
        cnx.commit()

        print("DRUGBANK ID successfully linked to hd_active_ingredient_ext_id!")

    except Exception as e:
        print(f"Error while linking DRUGBANK ID to active ingredient: {e}")
    return

def link_drugbank_to_active_ing(cnx, cursor):
    # Refresh DrugBank external identifiers in `hd_active_ingredient_ext_id`,
    # removing previous DRUGBANK rows (so the load can be re-run cleanly) and 
    # inserting again the identifiers based on the harmonized mappings.

    try:
        # Truncate table hd_active_ingredient_ext_id if needed
        #cursor.execute("TRUNCATE TABLE healdb.hd_active_ingredient_ext_id;")
        cursor.execute("DELETE FROM healdb.hd_active_ingredient_ext_id where tp_ext_id = 'DRUGBANK_ID'")
        cnx.commit()

        # Step 1: Link CAS from DCB List
        link_drugbank_to_active_ing_ext_id(cnx, cursor)


        print("Success - link drugbank id.")

    except Exception as e:
        print(f"Error linking drugbank id: {e}")
    return
