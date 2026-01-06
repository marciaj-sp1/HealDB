# -*- coding: utf-8 -*-
"""
Created on Sun Mar 02 11:01:00 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script link the cas number external id to active ingredients to enable 
# searches in other medical sources and ontologies


def link_cas_from_dcb_to_active_ing_ext_id(cnx, cursor):
    # Get CAS numbers from DCB list.

    try:
        print("Linking CAS numbers from DCB list...")

        sql_command = (
            "INSERT INTO healdb.hd_active_ingredient_ext_id "
            "(id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id) "
            "SELECT act.id_active_ingredient, 'CAS', dcb.nr_cas, 'DCB' "
            "FROM healdb.hd_active_ingredient act "
            "INNER JOIN healdb.hd_dcb_list dcb "
            "    ON TRIM(UPPER(CASE "
            "                 WHEN INSTR(UPPER(act.nm_active_ingredient), '(PORT.') > 0 THEN "
            "                   SUBSTR(UPPER(act.nm_active_ingredient), 1, "
            "                   INSTR(UPPER(act.nm_active_ingredient), '(PORT.') - 1) "
            "                ELSE "
            "                   UPPER(act.nm_active_ingredient) "
            "           END "
            "           ) "
            "      ) = TRIM(UPPER(dcb.nm_dcb)) "
            "WHERE dcb.nr_cas IS NOT NULL "
            "AND dcb.nr_cas NOT LIKE '[Ref%' " 
            "AND NOT EXISTS (SELECT 1 FROM healdb.hd_active_ingredient_ext_id ext "
            "                WHERE ext.id_active_ingredient = act.id_active_ingredient "
            "                  AND ext.tp_ext_id = 'CAS' "
            "               ) "
        )

        cursor.execute(sql_command)
        cnx.commit()

        print("CAS numbers successfully linked to hd_active_ingredient_ext_id from DCB list!")

    except Exception as e:
        print(f"Error while linking CAS numbers from DCB: {e}")
    return

def link_cas_to_active_ing(cnx, cursor):
    # Link the cas number to active ingredients

    try:
        # Truncate table hd_active_ingredient_ext_id if needed
        cursor.execute("TRUNCATE TABLE healdb.hd_active_ingredient_ext_id;")
        #cursor.execute("DELETE FROM healdb.hd_active_ingredient_ext_id where tp_ext_id = 'CAS'")
        cnx.commit()

        # Step 1: Link CAS from DCB List
        link_cas_from_dcb_to_active_ing_ext_id(cnx, cursor)


        print("Success - link cas number.")

    except Exception as e:
        print(f"Error linking cas number: {e}")
    return
