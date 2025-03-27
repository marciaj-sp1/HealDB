# -*- coding: utf-8 -*-
"""
Created on Mon Nov  19 08:25:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Validate the translation of active ingredients in two steps:
# 1. Verify the match of the automatically translated term in the DrugBank tables, 
#    specifically related to drugs, synonyms, and product ingredients.
# 2. Confirm the match of the manually translated term in the same tables.

# Note: Before executing this script, a manual step is required. Data must be 
# copied from the translation table to the working translation table to allow 
# for review and, if necessary, the addition of manual corrections to the translations.
# Specifically, data is copied from `healdb.hd_translate_eng_active_ing` to 
# `healdb.hd_wrk_translate_eng_active_ing` with the original translations.

# During this manual process, translations are reviewed, and new translations 
# are added if the originals are deemed incorrect. The reviewed translation is 
# stored in the field `nm_active_ingredient_eng_review`. 

# In the validation process, the origin flag (`fl_orig`) is updated as follows: 
# - `DRU` if the term matches a drug, 
# - `SYN` if it matches a synonym, and 
# - `PIN` if it matches a product ingredient. 
# At the same time, the corresponding drug is identified and recorded.

# The table `hd_wrk_translate_eng_active_ingredient` is integral to this process 
# as it helps update the translation table with the reviewed translations, ensuring 
# a final and accurate translation of the active ingredient.


def link_active_ingredient_drug(cnx, cursor):
    # Associates active ingredients with drugs in the DrugBank database
    print("Associating active ingredient with DrugBank drugs")

    sql_command = "TRUNCATE TABLE healdb.hd_priv_active_ingredient_drug"
    cursor.execute(sql_command)
    cnx.commit()

    sql_command = (
        "INSERT INTO healdb.hd_priv_active_ingredient_drug (id_active_ingredient, id_drug) "
        "SELECT id_active_ingredient, id_drug "
        "FROM healdb.hd_translate_eng_active_ing "
        "WHERE id_drug IS NOT NULL"
    )
    cursor.execute(sql_command)
    cnx.commit()
    return

def update_final_translate(cnx, cursor):
    # Updates the final English translation of active ingredients
    print("Updating the final English translation")
    sql_command = (
        "UPDATE healdb.hd_translate_eng_active_ing "
        "SET nm_active_ingredient_eng = "
        "UPPER(COALESCE(nm_active_ingredient_eng_review, nm_active_ingredient_eng_ini))"
    )
    cursor.execute(sql_command)
    cnx.commit()
    return

def update_origin_translate_eng(cnx, cursor, id_active_ingredient, fl_orig, id_drug):
    # Updates the origin of the translated termprint
    
    sql_command = (
        "UPDATE healdb.hd_translate_eng_active_ing "
        "SET fl_orig = %s, id_drug = %s "
        "WHERE id_active_ingredient = %s"
    )
    reg = (fl_orig, id_drug, id_active_ingredient)
    cursor.execute(sql_command, reg)
    cnx.commit()
    return

def search_db_product_ingredient(cnx, cursor, nm_active_ingredient_eng_ini):
    # Searches for the term in the product ingredients table
    sql_command = (
        "SELECT MIN(p.id_drug) "
        "FROM healdb.db_product_ingredient p, healdb.db_drug d "
        "WHERE UPPER(p.nm_product_ingredient) = %s "
        "AND d.id_drug = p.id_drug"
    )
    cursor.execute(sql_command, (nm_active_ingredient_eng_ini,))
    result = cursor.fetchone()
    return result[0] if result else None

def search_db_synonym(cnx, cursor, nm_active_ingredient_eng_ini):
    # Searches for the term in the synonyms table
    sql_command = (
        "SELECT MIN(s.id_drug) "
        "FROM healdb.db_synonym s, healdb.db_drug d "
        "WHERE UPPER(s.nm_synonym) = %s "
        "AND d.id_drug = s.id_drug"
    )
    cursor.execute(sql_command, (nm_active_ingredient_eng_ini,))
    result = cursor.fetchone()
    return result[0] if result else None

def search_db_drug(cnx, cursor, nm_active_ingredient_eng_ini):
    # Searches for the term in the drugs table
    sql_command = (
        "SELECT MIN(id_drug) "
        "FROM healdb.db_drug "
        "WHERE UPPER(nm_drug) = %s"
    )
    cursor.execute(sql_command, (nm_active_ingredient_eng_ini,))
    result = cursor.fetchone()
    return result[0] if result else None

def search_update_origin(cnx, cursor, id_active_ingredient, nm_active_ingredient_eng):
    # Searches for the translated term in DrugBank tables and updates the origin
    id_drug = search_db_drug(cnx, cursor, nm_active_ingredient_eng)
    
    if id_drug is None:
        id_drug = search_db_synonym(cnx, cursor, nm_active_ingredient_eng)
        if id_drug is None:
            id_drug = search_db_product_ingredient(cnx, cursor, nm_active_ingredient_eng)
            if id_drug is not None:
                update_origin_translate_eng(cnx, cursor, id_active_ingredient, "PIN", id_drug)
        else:
            update_origin_translate_eng(cnx, cursor, id_active_ingredient, "SYN", id_drug)
    else:
        update_origin_translate_eng(cnx, cursor, id_active_ingredient, "DRU", id_drug)
    return

def update_manual_validate_translate(cnx, cursor):
    # Updates manually reviewed translations and searches for their origin
    print("Updating manually reviewed translations")

    sql_command = (
        "UPDATE healdb.hd_translate_eng_active_ing t "
        "SET t.nm_active_ingredient_eng_review = "
        "(SELECT a.nm_active_ingredient_eng_review "
        "FROM healdb.hd_wrk_translate_eng_active_ing a "
        "WHERE a.id_active_ingredient = t.id_active_ingredient) "
        "WHERE t.fl_orig IS NULL"
    )
    cursor.execute(sql_command)
    cnx.commit()

    sql_command = "SELECT * FROM healdb.hd_translate_eng_active_ing WHERE fl_orig IS NULL"
    cursor.execute(sql_command)
    registers = cursor.fetchall()

    for register in registers:
        id_active_ingredient = register[0]
        nm_active_ingredient_eng_review = register[3]
        search_update_origin(cnx, cursor, id_active_ingredient, nm_active_ingredient_eng_review)
    return

def automatic_validate_translate_act_ing(cnx, cursor):
    # Automatically validates the translation of active ingredients
    print("Automatic validation of active ingredient translations")

    sql_command = (
        "UPDATE healdb.hd_translate_eng_active_ing "
        "SET fl_orig = NULL, nm_active_ingredient_eng_review = NULL, id_drug = NULL "
    )
    cursor.execute(sql_command)
    cnx.commit()
    
    sql_command = "SELECT * FROM healdb.hd_translate_eng_active_ing"
    cursor.execute(sql_command)
    registers = cursor.fetchall()
    for register in registers:
        id_active_ingredient = register[0]
        nm_active_ingredient_eng_ini = register[2]
        search_update_origin(cnx, cursor, id_active_ingredient, nm_active_ingredient_eng_ini)
    return

def validate_translation_and_link_active_ing(cnx, cursor):
    
    # Validates active ingredient translations and links them to DrugBank drugs
    
        
    # Step 1: Perform automatic validation of the translation by checking 
    # matches in DrugBank tables and update the origin flag and drug ID if found.
    automatic_validate_translate_act_ing(cnx, cursor)
    
    # Step 2: Update the translation table with manually reviewed translations.
    update_manual_validate_translate(cnx, cursor)
    
    # Step 3: Finalize the translation by selecting the manually reviewed translation 
    # or the initial automatic translation if no review exists.
    update_final_translate(cnx, cursor)
    
    # Step 4: Link active ingredients to DrugBank drugs using the final translation.
    link_active_ingredient_drug(cnx, cursor)
    
    return
