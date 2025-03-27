# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 03:12:00 2024

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Translate the content of the section "para que este medicamento é indicado" (indication) from 
# drug leaflets into English. The purpose of this translation is to enable the use of 
# English-language tools for extracting symptoms and diseases from medical texts.

import pandas as pd
import requests
import time
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


def update_translate_ds_indication(cnx, cursor, df_ind_text):
    # Updates the table with the translated indication text
    try:
        print("Starting the update of translated indication text...")
        for index, row in df_ind_text.iterrows():
            reg = (row['ds_indication_eng'], row['id_medication'])

            # SQL command to update the ds_indication_eng field
            command_sql = (
                " UPDATE healdb.hd_translate_eng_leaflet_section "
                " SET ds_indication_eng = %s "
                " WHERE id_medication = %s "
            )
            cursor.execute(command_sql, reg)  # Execute the SQL command
            cnx.commit()  # Commit the updates to the database
        print("Finished updating translated indication text.")
    except Exception as e:
        print(f"Error updating translated indications: {e}")
    return


def configure_openai_api():
    # Configures OpenAI API settings using centralized configuration
    headers = OPENAI_API["headers"]
    url = OPENAI_API["url"]
    model = OPENAI_API["model"]
    return headers, url, model


def translate_api_chatgpt(headers, link, id_model, ds_indication):
    # Sends a request to the OpenAI API to translate the indication text
    try:
        time.sleep(15)  # Adds a delay to avoid rate limits

        body_message = {
            "model": id_model,
            "messages": [{"role": "user", "content": 
                          f"traduzir para o inglês e retornar apenas a tradução {ds_indication}"}]
        }

        body_message = json.dumps(body_message)
        request_v = requests.post(link, headers=headers, data=body_message)
        answer = request_v.json()  # Extract the response in JSON format
        output = answer["choices"][0]["message"]["content"]
        return output
    except Exception as e:
        print(f"Error translating text using ChatGPT API: {e}")
        return ""


def translate_indication(cnx, cursor):
    # Translates the leaflet indications using OpenAI API
    try:
        print("Starting leaflet indication translation...")
        headers, url, model = configure_openai_api()  # Configures OpenAI API

        sql_command = (
            "SELECT t.id_medication, t.ds_indication "
            "FROM healdb.hd_translate_eng_leaflet_section t "
            "WHERE length(t.ds_indication) != 0 "
            "ORDER BY 1"
        )
        cursor.execute(sql_command)  # Fetch leaflet indications from the database
        registers = cursor.fetchall()

        colunas = ["id_medication", "ds_indication", "ds_indication_eng"]
        df_ind_text = pd.DataFrame(columns=colunas)  # Initialize a DataFrame

        print("Creating DataFrame for leaflet indications...")
        count = 0
        for register in registers:
            id_medication = register[0]
            ds_indication = register[1]
            print(f"id_medication: {id_medication}")
            print(f"ds_indication: {ds_indication}")

            ds_indication_eng = translate_api_chatgpt(headers, url, model, ds_indication)
            print(f"ds_indication_eng: {ds_indication_eng}")

            reg = (id_medication, ds_indication, ds_indication_eng)
            df_ind_text.loc[len(df_ind_text)] = reg
            count += 1

            update_translate_ds_indication(cnx, cursor, df_ind_text)  # Update translations in the database
            df_ind_text = pd.DataFrame(columns=colunas)

        if count != 0:
            print("Performing final update of translations...")
            update_translate_ds_indication(cnx, cursor, df_ind_text)

        print("Finished translating leaflet indications.")
    except Exception as e:
        print(f"Error during leaflet indication translation: {e}")
    return


def insert_table_translate_indication(cnx, cursor):
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
                "   (id_medication, ds_indication, ds_indication_eng) "
                " SELECT DISTINCT m.id_medication, m.ds_indication, '' "
                " FROM hd_medication_drug_leaflet m"
            )
            cursor.execute(command_sql)  # Insert initial data into the table
            cnx.commit()
        else:
            print("Records already exist in the table. No action needed.")

        print("Finished inserting into hd_translate_eng_leaflet_section.")
    except Exception as e:
        print(f"Error inserting into hd_translate_eng_leaflet_section: {e}")
    return


def translate_leaflet_indication(cnx, cursor):
    # Main function to orchestrate the translation process
    insert_table_translate_indication(cnx, cursor)  # Prepare the table
    translate_indication(cnx, cursor) # Translate the indication
    update_null_translation(cnx, cursor)  # Update empty translations
    
    return
