# -*- coding: utf-8 -*-
"""
Created on Mon Nov  18 23:30:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script provides functions to translate active ingredients from Portuguese to 
# English using the OpenAI API.

import pandas as pd
import json
import requests
from config import OPENAI_API

def copy_active_ingredients_to_translate(cnx, cursor):
    # Copy active ingredients from the main table to the translation table.
    print("Start copying active ingredients for translation")

    # SQL command to copy data from the main table to the translation table
    sql_command = (
        "INSERT INTO healdb.hd_translate_eng_active_ing "
        "(id_active_ingredient, nm_active_ingredient) "
        "SELECT id_active_ingredient, nm_active_ingredient "
        "FROM healdb.hd_active_ingredient"
    )

    # Execute the SQL command
    cursor.execute(sql_command)
    cnx.commit()
    print("Finished copying active ingredients")
    return

def update_translated_active_ingredients(cnx, cursor, df_active_ingredients):
    # Update the translation table with translated active ingredients in English.
    
    print("Updating translations in the database")

    # Iterate through the DataFrame and update each record
    for _, row in df_active_ingredients.iterrows():
        register = (row['nm_active_ingredient_eng_ini'], 
                    row['id_active_ingredient'])
        sql_command = (
            "UPDATE healdb.hd_translate_eng_active_ing "
            "SET nm_active_ingredient_eng_ini = UPPER(%s) "
            "WHERE id_active_ingredient = %s"
        )

        # Execute the SQL command for each record
        cursor.execute(sql_command, register)
    cnx.commit()
    print("Database updated with translations")
    return

def translate_with_gptmodel(headers, url, model, active_ingredient_port):
    # Translate a string using OpenAI's GPT model.
    
    body_message = {
        "model": model,
        "messages": [{"role": "user", "content": 
                      f"traduzir para o inglês e retornar apenas a tradução: {active_ingredient_port}"}]
    }

    try:
        # Send the request to the OpenAI API
        response = requests.post(url, headers=headers, data=json.dumps(body_message))
        response.raise_for_status()

        # Extract the translated text from the response
        translation = response.json()["choices"][0]["message"]["content"]
        #print ("port = ", active_ingredient_port)
        #print ("eng = ", translation)
        
        return translation.strip()

    except Exception as e:
        # Handle any exceptions that occur during the translation process
        print(f"Error translating {active_ingredient_port}: {e}")
        return 
    

def configure_openai_api():
    # Configure API settings for OpenAI GPT using centralized config
    headers = OPENAI_API["headers"]
    url = OPENAI_API["url"]
    model = OPENAI_API["model"]
    return headers, url, model

def translate_active_ingredients(cnx, cursor):
    # Translate active ingredients from Portuguese to English and update the database.
    
    print("Start translating active ingredients")
    
    # Copy active ingredients to translate to english
    copy_active_ingredients_to_translate(cnx, cursor)
    
    # Configure the OpenAI API
    headers, url, model = configure_openai_api()

    # SQL command to fetch active ingredients that need translation
    sql_command = (
        "SELECT id_active_ingredient, nm_active_ingredient "
        "FROM healdb.hd_translate_eng_active_ing "
        "WHERE nm_active_ingredient_eng_ini IS NULL"
    )

    # Execute the SQL command and fetch the results
    cursor.execute(sql_command)
    registers = cursor.fetchall()

    # Initialize a DataFrame to store translations
    columns = ["id_active_ingredient", "nm_active_ingredient", "nm_active_ingredient_eng_ini"]
    df_active_ingredients = pd.DataFrame(columns=columns)

    # Translate each register and store it in the DataFrame
    for register in registers:
        id_active_ingredient, nm_active_ingredient = register
        translation = translate_with_gptmodel(headers, url, model, nm_active_ingredient)
        #print ("id_active_ingredient = ", id_active_ingredient)
        # Append the translation to the DataFrame
        df_active_ingredients = pd.concat([
            df_active_ingredients,
            pd.DataFrame([{
                "id_active_ingredient": id_active_ingredient,
                "nm_active_ingredient": nm_active_ingredient,
                "nm_active_ingredient_eng_ini": translation
            }])
        ], ignore_index=True)

    # Update the database with the translated values
    update_translated_active_ingredients(cnx, cursor, df_active_ingredients)
    print("Finished translating active ingredients")
    return
