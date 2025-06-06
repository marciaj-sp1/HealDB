# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 03:12:00 2024

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Translate the content of the section "para que este medicamento é indicado" (indication) 
# and the section "como este medicamento funciona" (functionality) from 
# drug leaflets into English. The purpose of this translation is to enable the use of 
# English-language tools for extracting symptoms and diseases from medical texts.

import pandas as pd
import requests
import json
from config import OPENAI_API

def update_null_translation(cnx, cursor):
    # Updates empty translations that were mistakenly saved
    try:
        print("Starting the update of empty translations...")
        sql_command = (
            "UPDATE healdb.hd_translate_eng_leaflet_section t "
            "SET t.ds_indication_eng = '' "
            "WHERE length(t.ds_indication) <= 10"
        )
        cursor.execute(sql_command)
        cnx.commit()  # Commit the updates to the database
    except Exception as e:
        print(f"Error updating null translations: {e}")
    return


def update_translated_field(cnx, cursor, df_sec_text):
    # Updates the table with the translated indication and functionality text
    try:
        print("Starting the update of translated field text...")
        for index, row in df_sec_text.iterrows():
            reg = (row['ds_indication_eng'], 
                   row['ds_functionality_eng'],
                   row['id_medication'])

            # SQL command to update the ds_indication_eng field
            command_sql = (
                " UPDATE healdb.hd_translate_eng_leaflet_section "
                " SET ds_indication_eng = %s "
                "    ,ds_functionality_eng = %s "
                " WHERE id_medication = %s "
            )
            cursor.execute(command_sql, reg)  # Execute the SQL command
            cnx.commit()  # Commit the updates to the database
        print("Finished updating translated section text.")
    except Exception as e:
        print(f"Error updating translated fields: {e}")
    return


def configure_openai_api():
    # Configures OpenAI API settings using centralized configuration
    headers = OPENAI_API["headers"]
    url = OPENAI_API["url"]
    model = OPENAI_API["model"]
    return headers, url, model


def translate_api_chatgpt(headers, link, id_model, ds_field):
    try:
        if not ds_field or ds_field.strip() == "":
            return ""
        if len(ds_field) > 6000:  # 6000 caracters ≈ 1500 tokens
            ds_field = ds_field[:6000]
        
        #time.sleep(5)  # Used to avoid limit 

        body_message = {
            "model": id_model,
            "messages": [{"role": "user", "content": f"Translate to English and return only the translation: {ds_field}"}]
        }

        response = requests.post(link, headers=headers, data=json.dumps(body_message), timeout=60)

        if response.status_code != 200:
            print(f"API returned status {response.status_code}: {response.text}")
            return ""

        answer = response.json()

        if "choices" not in answer:
            print(f"Missing 'choices' in API response: {answer}")
            return ""

        return answer["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error translating with ChatGPT API: {e}")
        return ""

def translate_section(cnx, cursor):
    # Translates the leaflet sections using OpenAI API
    try:
        print("Starting leaflet indication translation...")
        headers, url, model = configure_openai_api()  # Configures OpenAI API

        sql_command = (
            "SELECT t.id_medication, t.ds_indication, t.ds_functionality "
            "FROM healdb.hd_translate_eng_leaflet_section t "
            "WHERE (length(t.ds_indication) != 0 "
            "AND (t.ds_indication_eng IS NULL OR t.ds_indication_eng = '')) OR "
            " (length(t.ds_functionality) != 0 "
            "AND (t.ds_functionality_eng IS NULL OR t.ds_functionality_eng = '')) "
            "ORDER BY 1 "
        )
        cursor.execute(sql_command)  # Fetch leaflet sections from the database
        registers = cursor.fetchall()

        colunas = ["id_medication", "ds_indication", "ds_indication_eng",
                   "ds_functionality", "ds_functionality_eng"]
        df_sec_text = pd.DataFrame(columns=colunas)  # Initialize a DataFrame

        print("Creating DataFrame for leaflet indications...")
        count = 0
        for register in registers:
            
            id_medication = register[0]
            ds_indication = register[1]
            ds_functionality = register[2]
            
            print (f"id_medication = {id_medication}")
            ds_indication_eng = translate_api_chatgpt(headers, url, model, ds_indication)

            ds_functionality_eng = translate_api_chatgpt(headers, url, model, 
                                                         ds_functionality)
    
            reg = (id_medication, ds_indication, ds_indication_eng,
                   ds_functionality, ds_functionality_eng)
            df_sec_text.loc[len(df_sec_text)] = reg
            count += 1

            update_translated_field (cnx, cursor, df_sec_text)  # Update translations in the database
            df_sec_text = pd.DataFrame(columns=colunas)

        if count != 0:
            print("Performing final update of translations...")
            update_translated_field(cnx, cursor, df_sec_text)

        print("Finished translating leaflet indications.")
    except Exception as e:
        print(f"Error during leaflet indication translation: {e}")
    return


def insert_table_translate_section(cnx, cursor):
    # Inserts leaflet indications and translations into the translation table
    try:
        print("Starting insert into hd_translate_eng_leaflet_section...")

        count_sql = "SELECT COUNT(*) FROM healdb.hd_translate_eng_leaflet_section"
        cursor.execute(count_sql)  # Check if the table already contains records
        count_result = cursor.fetchone()

        print(f"Records in table: {count_result[0]}")
        if count_result[0] == 0:
            command_sql = (
                "INSERT INTO healdb.hd_translate_eng_leaflet_section "
                "   (id_medication, ds_indication, ds_indication_eng, "
                "    ds_functionality, ds_functionality_eng) "
                " SELECT DISTINCT m.id_medication, m.ds_indication, '', "
                "                 m.ds_functionality, '' "
                " FROM hd_medication_drug_leaflet m "
            )
            cursor.execute(command_sql)  # Insert initial data into the table
            cnx.commit()
        else:
            print("Records already exist in the table. No action needed.")

        print("Finished inserting into hd_translate_eng_leaflet_section.")
    except Exception as e:
        print(f"Error inserting into hd_translate_eng_leaflet_section: {e}")
    return


def translate_leaflet_sections(cnx, cursor):
    # Main function to orchestrate the translation process
    insert_table_translate_section(cnx, cursor)  # Prepare the table
    translate_section(cnx, cursor) # Translate the indication and functionality
    update_null_translation(cnx, cursor)  # Update empty translations
    
    return
