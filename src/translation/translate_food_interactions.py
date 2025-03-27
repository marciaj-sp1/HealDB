"""
Created on Wed Nov  20 17:18:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script translates food interactions related to active ingredients
# from English to Portuguese using the OpenAI GPT API and stores the results
# in the HealDB database.


import pandas as pd
import requests
import json
from config import OPENAI_API

def insert_food_interaction(cnx, cursor):
    # Inserts the active ingredient-related interactions translated into Portuguese
    # into the definitive table
    
    print("Starting insertion of food interactions")
    
    # Truncate and reset the table
    
    cursor.execute("TRUNCATE TABLE healdb.hd_priv_food_interaction")
    cursor.execute("ALTER TABLE healdb.hd_priv_food_interaction AUTO_INCREMENT = 1")
    
    # Insert data into the table
    sql_command = (
        "INSERT INTO healdb.hd_priv_food_interaction "
        "(id_interaction, id_active_ingredient, ds_food_interaction) "
        "SELECT t.id_interaction, a.id_active_ingredient, " 
        "       t.ds_interaction_port "
        "FROM healdb.hd_priv_translate_port_food_int t, "
        "     healdb.db_food_interaction df, "
        "     healdb.hd_priv_active_ingredient_drug a "
        "WHERE t.id_interaction = df.id_interaction "
        "  AND df.id_drug = a.id_drug "
        "  AND t.ds_interaction_port IS NOT NULL"
    )
    cursor.execute(sql_command)
    cnx.commit()
    
    print("Completed insertion of food interactions")
    return

def replace_var_by_active_ingredient(cnx, cursor):
    # Replaces placeholders (e.g., XXX) with active ingredient names in Portuguese
    
    print("Starting replacement of placeholders with active ingredient names")
    
    sql_command = (
        "UPDATE hd_priv_translate_port_food_int AS tpf "
        "JOIN db_food_interaction AS f ON tpf.id_interaction = f.id_interaction "
        "JOIN hd_priv_active_ingredient_drug AS ac ON f.id_drug = ac.id_drug " 
        "JOIN hd_active_ingredient AS a ON ac.id_active_ingredient = a.id_active_ingredient "
        "SET tpf.ds_interaction_port = "
        "REPLACE(tpf.ds_interaction_var_port, 'XXX', "
        "   CONCAT(UCASE(SUBSTRING(a.nm_active_ingredient, 1, 1)), "
        "   LCASE(SUBSTRING(a.nm_active_ingredient, 2))))"
    )
    cursor.execute(sql_command)
    cnx.commit()
    
    print("Completed replacement of placeholders with active ingredient names")
    return

def update_translate_food_interaction(cnx, cursor, df_food_interaction):
    # Updates the translated food interaction descriptions in the database
    
    for index, row in df_food_interaction.iterrows():
        reg = (row['ds_interaction_var_port'], row['ds_interaction_var'])
        sql_command = (
            "UPDATE healdb.hd_priv_translate_port_food_int "
            "SET ds_interaction_var_port = %s "
            "WHERE ds_interaction_var = %s"
        )
        cursor.execute(sql_command, reg)
        cnx.commit()
    return

def configure_openai_api():
    # Configure API settings for OpenAI GPT using centralized config
    headers = OPENAI_API["headers"]
    url = OPENAI_API["url"]
    model = OPENAI_API["model"]
    return headers, url, model


def translate_api_chatgpt(headers, url, model, ds_interaction_var):
    # Translates a food interaction description using OpenAI GPT API
    
    body_message = {
        "model": model,
        "messages": [{"role": "user", "content": 
                      f"Translate to Portuguese, only returning the translation, and translate 'St. John's Worth' as 'Erva de São João': {ds_interaction_var}"}]
    }
    body_message = json.dumps(body_message)
    request_v = requests.post(url, headers=headers, data=body_message)
    answer = request_v.json()
    output = answer["choices"][0]["message"]["content"]
    #print("eng =", ds_interaction_var)
    #print("port =", output)
    return output

def perform_food_interaction_translation(cnx, cursor):
    # Performs translation of food interactions
    
    print("Starting translation of food interactions")
    headers, url, model = configure_openai_api()
    sql_command = (
        "SELECT f.ds_interaction_var, COUNT(*) "
        "FROM healdb.hd_priv_translate_port_food_int f "
        "WHERE f.ds_interaction_var_port IS NULL "
        "GROUP BY f.ds_interaction_var "
        "ORDER BY 2 DESC"
    )
    cursor.execute(sql_command)
    registers = cursor.fetchall()
    fields = ["ds_interaction_var", "ds_interaction_var_port"]
    df_food_interaction = pd.DataFrame(columns=fields)
    count = 0
    for register in registers:
        ds_interaction_var = register[0]
        count_result = register[1]
        ds_interaction_var_port = translate_api_chatgpt(headers, url, model, ds_interaction_var)
        reg = (ds_interaction_var, ds_interaction_var_port)
        df_food_interaction.loc[len(df_food_interaction)] = reg
        count += count_result
        if count > 200:
            count = 0
            update_translate_food_interaction(cnx, cursor, df_food_interaction)
            df_food_interaction = pd.DataFrame(columns=fields)
    if count != 0:
        update_translate_food_interaction(cnx, cursor, df_food_interaction)
    print("Completed translation of food interactions")
    return

def insert_table_translate_food_int(cnx, cursor):
    # Inserts food interactions into the translation table for processing
    
    print("Starting insert food interactions into translation table")
    count_sql = "SELECT COUNT(*) FROM healdb.hd_priv_translate_port_food_int"
    cursor.execute(count_sql)
    count_result = cursor.fetchone()
    if count_result[0] == 0:
        sql_command = (
            "INSERT INTO healdb.hd_priv_translate_port_food_int "
            "(id_interaction, ds_interaction_var) "
            "SELECT DISTINCT i.id_interaction, "
            "   CASE "
            "       WHEN LOWER(i.ds_interaction) LIKE "
            "       CONCAT('%', LOWER(d.nm_drug), '%') "
            "   THEN CONCAT("
            "       LEFT(i.ds_interaction, INSTR(LOWER(i.ds_interaction), "
            "                                   LOWER(d.nm_drug)) - 1), 'XXX', "
            "       RIGHT(i.ds_interaction, LENGTH(i.ds_interaction) - "
            "               INSTR(LOWER(i.ds_interaction), LOWER(d.nm_drug)) "
            "               - LENGTH(d.nm_drug) + 1) "
            "   ) "
            "   ELSE i.ds_interaction "
            "   END AS ds_interaction "
            "FROM db_food_interaction i "
            "JOIN hd_priv_active_ingredient_drug a ON i.id_drug = a.id_drug "
            "JOIN hd_active_ingredient ac ON a.id_active_ingredient = ac.id_active_ingredient "
            "JOIN db_drug d ON a.id_drug = d.id_drug"
        )
        cursor.execute(sql_command)
        cnx.commit()
    else:
        print("There are already records in the table. No action is required.")
    print("Completed insert food interactions into translation table")
    return

def translate_food_interactions(cnx, cursor):
    # Main function to handle the translation of food interactions
    
    # Step 1: Prepare the translation table with food interactions
    insert_table_translate_food_int(cnx, cursor)
    
    # Step 2: Translate interaction descriptions into Portuguese
    perform_food_interaction_translation(cnx, cursor)
    
    # Step 3: Replace placeholders with translated active ingredient names
    replace_var_by_active_ingredient(cnx, cursor)
    
    # Step 4: Insert translated interactions into the final tables
    insert_food_interaction(cnx, cursor)
    
    return
