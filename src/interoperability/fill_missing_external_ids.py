# -*- coding: utf-8 -*-
"""
Created on Sun Mar 04 13:22:00 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script fills in missing external identifiers (CAS, ATC, SNOMEDCT, 
# UNII_CODE, CHEBI) in the HealDB external ID table by using matching RXCUI 
# values found in the Wikidata working table. Only IDs not already present 
# in the database are inserted.


def fill_missing_external_ids(cnx, cursor):
    # Populate the external ids table using some IDs from wikidata working table
    try:
        sql_command = '''
            INSERT INTO healdb.hd_active_ingredient_ext_id 
            (id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id) 
            SELECT DISTINCT 
                a.id_active_ingredient, 
                w.tp_ext_id, 
                w.cd_ext_id, 
                'WIKIDATA'
            FROM hd_wrk_wikidata_ext_id w
            JOIN hd_active_ingredient_ext_id a  
            ON a.cd_ext_id = w.cd_rxcui  
            AND a.tp_ext_id = 'RXCUI'
            WHERE w.tp_ext_id IN ('ATC', 'SNOMEDCT', 'UNII_CODE', 'CHEBI')
            AND NOT EXISTS (
                SELECT 1
                FROM hd_active_ingredient_ext_id a1
                WHERE a1.id_active_ingredient = a.id_active_ingredient
                AND a1.tp_ext_id = w.tp_ext_id
                AND a1.cd_ext_id = w.cd_ext_id
            )
        '''
        
        cursor.execute(sql_command)
        cnx.commit()
        
        sql_command = '''
            INSERT INTO healdb.hd_active_ingredient_ext_id
            (id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id)
            SELECT 
                id_active_ingredient,
                tp_ext_id,
                cd_ext_id,
                'WIKIDATA'
            FROM (
                SELECT 
                    a.id_active_ingredient,
                    w.tp_ext_id,
                    w.cd_ext_id,
                    ROW_NUMBER() OVER (PARTITION BY a.id_active_ingredient ORDER BY w.cd_ext_id) AS rn
                FROM hd_wrk_wikidata_ext_id w
                JOIN hd_active_ingredient_ext_id a  
                    ON a.cd_ext_id = w.cd_rxcui  
                    AND a.tp_ext_id = 'RXCUI'
                WHERE w.tp_ext_id = 'CAS'
                AND NOT EXISTS (
                    SELECT 1
                    FROM hd_active_ingredient_ext_id a1
                    WHERE a1.id_active_ingredient = a.id_active_ingredient
                    AND a1.tp_ext_id = 'CAS'
                )
            ) AS ranked
            WHERE rn = 1;
            '''

        cursor.execute(sql_command)
        cnx.commit()

    except Exception as e:
        print(f"Error processing External IDs: {e}")
    return
