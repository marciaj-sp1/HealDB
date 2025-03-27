"""
Created on Wed Nov  20 11:33:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""
# This script translates drug interactions related to active ingredients 
# from English to Portuguese using the OpenAI GPT API and stores the results 
# in the HealDB database.


import pandas as pd
import requests
import json
from config import OPENAI_API

def insert_drug_interaction(cnx, cursor):
    # Inserts the active ingredient-related interactions translated into Portuguese
    # into the definitive table
    
    print("Starting insertion of drug interactions")
    # Disable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    # Truncate and reset the table
    cursor.execute("TRUNCATE TABLE healdb.hd_priv_drug_interaction_desc")
    cursor.execute("ALTER TABLE healdb.hd_priv_drug_interaction_desc AUTO_INCREMENT = 1")
    cursor.execute("TRUNCATE TABLE healdb.hd_drug_interaction")
    cursor.execute("ALTER TABLE healdb.hd_drug_interaction AUTO_INCREMENT = 1")

    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    print("After truncate table drug_interaction")
    # Batch size for batch insertion
    batch_size = 10000
    # SQL command for data selection
    sql_command = (
        "SELECT t.id_interaction, a.id_active_ingredient, " 
        "       a2.id_active_ingredient, t.ds_interaction_port "
        "FROM healdb.hd_priv_translate_port_drug_int t "
        "JOIN healdb.db_drug_interaction d ON d.id_interaction = " 
        "                                     t.id_interaction "
        "JOIN healdb.hd_priv_active_ingredient_drug a ON a.id_drug = d.id_drug "
        "JOIN healdb.hd_priv_active_ingredient_drug a2 ON a2.id_drug = " 
        "                                         d.id_drug_2"
    )
    
    # Execute the SQL query
    cursor.execute(sql_command)
   
    # Retrieve all query results
    results = cursor.fetchall()

    # Convert the results into a pandas DataFrame
    fields = ["id_interaction", "id_active_ingredient", 
              "id_active_ingredient_2", 
              "ds_interaction"]
    df_drug_interaction = pd.DataFrame(results, columns=fields)
   
    # Split the DataFrame into smaller batches
    batches = [df_drug_interaction[i:i+batch_size] 
               for i in range(0, len(df_drug_interaction), batch_size)]
    
    print("Starting batch insertion")
    # Insert each batch into the table
    for batch in batches:
        # Prepare values for the first table (3 columns)
        batch_values_table1 = [(row[0], row[1], row[2]) for row in batch.values]
    
        # Prepare values for the second table (4th column only)
        batch_values_table2 = [(row[3],) for row in batch.values]
        
        cursor.executemany(
            "INSERT INTO healdb.hd_drug_interaction "
            "(id_interaction, id_active_ingredient, id_active_ingredient_2) "
            "VALUES (%s, %s, %s)",
            batch_values_table1
        )
        cursor.executemany(
            "INSERT INTO healdb.hd_priv_drug_interaction_desc "
            "(ds_drug_interaction) "
            "VALUES (%s)",
            batch_values_table2  # Ensure only the description column is inserted
        )
        cnx.commit()  # Confirm changes to the database
    
    print("Completed insertion of drug interactions")
    return

def replace_var_by_active_ingredient(cnx, cursor):
    # Replaces the placeholder variables XXX and YYY with the Portuguese active ingredient
    # to complete the translation
    
    print("Starting replacement of placeholders with active ingredient names")
    
    sql_command = (
        " UPDATE healdb.hd_priv_translate_port_drug_int AS tpd "
        " JOIN db_drug_interaction AS d ON tpd.id_interaction = "
        "                                  d.id_interaction "
        " JOIN hd_priv_active_ingredient_drug AS ac ON d.id_drug = ac.id_drug " 
        " JOIN hd_active_ingredient AS a ON ac.id_active_ingredient =  "
        "                                a.id_active_ingredient "
        " JOIN hd_priv_active_ingredient_drug AS ac2 ON d.id_drug_2 = " 
        "                                        ac2.id_drug "
        " JOIN hd_active_ingredient AS a2 ON ac2.id_active_ingredient = "
        "                                 a2.id_active_ingredient "
        " SET tpd.ds_interaction_port = " 
        "                REPLACE(REPLACE(tpd.ds_interaction_var_port, "
        "   'XXX', CONCAT(UCASE(SUBSTRING(a.nm_active_ingredient, 1, 1)), "
        "   LCASE(SUBSTRING(a.nm_active_ingredient, 2)))), "
        "   'YYY', CONCAT(UCASE(SUBSTRING(a2.nm_active_ingredient, 1, 1)), "
        "   LCASE(SUBSTRING(a2.nm_active_ingredient, 2))));"
    )
    
    # Execute the SQL command with the values to be updated
    cursor.execute(sql_command)
        
    # Confirm the updates in the database
    cnx.commit()
    print("Completed replacement of placeholders with active ingredient names")
    return

def update_translate_drug_interaction(cnx, cursor, df_drug_interaction):
    # Updates the drug interaction table with the translation of the interaction
    # into Portuguese
    
    for index, row in df_drug_interaction.iterrows():
        reg = (row['ds_interaction_var_port'], 
               row['ds_interaction_var'])
        
        # SQL command to update the translation
        sql_command = (
            " UPDATE healdb.hd_priv_translate_port_drug_int "
            " SET ds_interaction_var_port = %s "
            " WHERE ds_interaction_var = %s"           
        )

        # Execute the SQL command with the values to be updated
        cursor.execute(sql_command, reg)

        # Confirm the updates in the database
        cnx.commit()
    return


def configure_openai_api():
    # Configure API settings for OpenAI GPT using centralized config
    headers = OPENAI_API["headers"]
    url = OPENAI_API["url"]
    model = OPENAI_API["model"]
    return headers, url, model



def translate_api_chatgpt(headers, url, model, ds_interaction_var):
    # Performs translation of drug interactions using the OpenAI GPT-4 model
    body_message = {
        "model": model,
        "messages": [{"role": "user", "content": 
                      f"traduzir para o português e retornar apenas a tradução: {ds_interaction_var}"}]
    }
    body_message = json.dumps(body_message)
    request_v = requests.post(url, headers=headers, data=body_message) 
    answer = request_v.json()
    output = answer["choices"][0]["message"]["content"]
    #print("eng =", ds_interaction_var)
    #print("port =", output)
    return output


def perform_drug_interaction_translation(cnx, cursor):
    # Translates drug interactions
    
    print("Starting translation of drug interactions")
    headers, url, model = configure_openai_api()
    sql_command = (
       "SELECT d.ds_interaction_var, COUNT(*) "
       "FROM healdb.hd_priv_translate_port_drug_int d "
       "WHERE d.ds_interaction_var_port IS NULL "
       "GROUP BY d.ds_interaction_var "
       "ORDER BY 2 DESC"       
    )
    cursor.execute(sql_command) 
    registers = cursor.fetchall()
    colunas = ["ds_interaction_var", "ds_interaction_var_port"]
    df_drug_interaction = pd.DataFrame(columns=colunas)
    count = 0
    for register in registers:
        ds_interaction_var = register[0]
        count_result = register[1]
        ds_interaction_var_port = translate_api_chatgpt(headers, url, model, ds_interaction_var)
        reg = (ds_interaction_var, ds_interaction_var_port)
        df_drug_interaction.loc[len(df_drug_interaction)] = reg
        count += count_result
        if count > 1000:
            count = 0
            update_translate_drug_interaction(cnx, cursor, df_drug_interaction)
            df_drug_interaction = pd.DataFrame(columns=colunas)
    if count != 0:
        update_translate_drug_interaction(cnx, cursor, df_drug_interaction)
    print("Completed translate of drug interaction")
    return


def insert_table_translate_drug_int(cnx, cursor):
    # Inserts drug interactions into the translation table for processing
    
    print("Starting insert drug interations into translation table")
    count_sql = "SELECT COUNT(*) FROM healdb.hd_priv_translate_port_drug_int"
    cursor.execute(count_sql)
    count_result = cursor.fetchone()
    
    if count_result[0] == 0:
        sql_command = (
        "SELECT DISTINCT i.id_interaction, "
        "    CONCAT(UCASE(SUBSTRING(d.nm_drug, 1, 1)), " 
        "    LCASE(SUBSTRING(d.nm_drug, 2))) AS nm_drug, "
        "    CONCAT(UCASE(SUBSTRING(d2.nm_drug, 1, 1)), " 
        "     LCASE(SUBSTRING(d2.nm_drug, 2))) AS nm_drug_2, "
        "    i.ds_interaction "
        "FROM db_drug_interaction i "
        "JOIN hd_priv_active_ingredient_drug a ON i.id_drug = a.id_drug " 
        "JOIN hd_priv_active_ingredient_drug a2 ON i.id_drug_2 = a2.id_drug "
        "JOIN db_drug d ON a.id_drug = d.id_drug "
        "JOIN db_drug d2 ON a2.id_drug = d2.id_drug "
        )
        cursor.execute(sql_command)
        registers = cursor.fetchall()
        for register in registers:
            id_interaction = register[0]
            nm_drug = register[1]
            nm_drug_2 = register[2]
            ds_interaction = register[3]
            
            # Ensure ds_interaction is converted to string
            if isinstance(ds_interaction, bytes):
                ds_interaction = ds_interaction.decode('utf-8')
                        
            ds_interaction_var = ds_interaction.replace(nm_drug,'XXX')
            ds_interaction_var = ds_interaction_var.replace(nm_drug_2, 'YYY')
            sql_command = (
                "INSERT INTO healdb.hd_priv_translate_port_drug_int "
                "(id_interaction, ds_interaction_var) "
                "VALUES (%s, %s)"
            )
            cursor.execute(sql_command, (id_interaction, ds_interaction_var))
            cnx.commit()
    else:
        print("There are already records in the table. No action is required.")
    print("Completed insert drug interactions into translation table")
    return


def translate_drug_interactions(cnx, cursor):
    # Main function to handle the translation of drug interactions
    
    # Step 1: Prepare the translation table with drug interactions
    insert_table_translate_drug_int(cnx, cursor)
    
    # Step 2: Translate interaction descriptions into Portuguese
    perform_drug_interaction_translation(cnx, cursor)
    
    # Step 3: Replace placeholders with translated active ingredient names
    replace_var_by_active_ingredient(cnx, cursor)
    
    # Step 4: Insert translated interactions into the final tables
    insert_drug_interaction(cnx, cursor)
    
    return
