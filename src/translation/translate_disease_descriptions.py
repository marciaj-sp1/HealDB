# -*- coding: utf-8 -*-
"""
Created on Tue Jun  03 09:11:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Update ICD-10 disease descriptions in English using external CSV files.
# The script fills the fields ds_group_eng, ds_cat_eng, and ds_subcat_eng
# in the tables hd_icd_group, hd_icd_category, and hd_icd_subcategory.
# It uses WHO's 2008 official files as the reference source.
# Useful for multilingual support and international interoperability.
# The category and subcategory not found in the WHO´s files are translated
# using the gpt-4-0314 model. 

import csv
import json
import requests

from config import PATHS, OPENAI_API

def translate_with_gptmodel(headers, url, model, prompt, icd_desc_port):
    # Translate a string using OpenAI's GPT model.
    
    body_message = {
        "model": model,
        "messages": [{"role": "user", "content": prompt.format(text=icd_desc_port)}]
    }

    translation = ''
    try:
        # Send the request to the OpenAI API
        response = requests.post(url, headers=headers, data=json.dumps(body_message))
        response.raise_for_status()

        # Extract the translated text from the response
        translation = response.json()["choices"][0]["message"]["content"]
        translation = translation.strip()

    except Exception as e:
        # Handle any exceptions that occur during the translation process
        print(f"Error translating {icd_desc_port}: {e}")
    return translation

def configure_openai_api():
    # Configure API settings for OpenAI GPT using centralized config
    headers = OPENAI_API["headers"]
    url = OPENAI_API["url"]
    model = OPENAI_API["model"]
    return headers, url, model

def translate_missing_descriptions(cnx, cursor):
    # Translate ds_group
    print ("Translating ICD group description...")
    sql_command = (
        "SELECT id_group, cd_cat_ini, cd_cat_end, ds_group "
        "FROM healdb.hd_icd_group "
        "WHERE ds_group_eng IS NULL"
    )
    
    # Execute the SQL command and fetch the results
    cursor.execute(sql_command)
    registers = cursor.fetchall()

    # Configure the OpenAI API
    headers, url, model = configure_openai_api()
    cont = 0 
    for id_group, cd_cat_ini, cd_cat_end, ds_group in registers:
        try:
            prompt = f"Translate the following disease group description to English (keep it short): {ds_group}"
            ds_group_eng = translate_with_gptmodel(headers, url, model, prompt, ds_group)
            cursor.execute(
                "UPDATE healdb.hd_icd_group SET ds_group_eng = %s WHERE id_group = %s",
                (ds_group_eng, id_group)
            )
            cont+=1
            if cont == 100:
               cont=0
               cnx.commit()
        except Exception as e:
            print(f"Failed to translate group '{ds_group}': {e}")
            
    # Translate ds_cat
    print ("Translating ICD cat description...")
    sql_command = (
        "SELECT id_cat, cd_cat, ds_cat "
        "FROM healdb.hd_icd_category "
        "WHERE ds_cat_eng IS NULL"
    )
    # Execute the SQL command and fetch the results
    cursor.execute(sql_command)
    registers = cursor.fetchall()
    cont = 0
    for id_cat, cd_cat, ds_cat in registers:
        try:
            prompt = f"Translate the following disease category to English (short version): {ds_cat}"

            ds_cat_eng = translate_with_gptmodel(headers, url, model, prompt, ds_cat)
            cursor.execute(
                "UPDATE healdb.hd_icd_category SET ds_cat_eng = %s WHERE id_cat = %s",
                (ds_cat_eng, id_cat)
            )
            cont+=1
            if cont == 100:
               cont=0
               cnx.commit()
        except Exception as e:
            print(f"Failed to translate category '{ds_cat}': {e}")
    cnx.commit()

    # Translate ds_subcat based on ds_cat_eng
    sql_command = (
        "SELECT s.id_subcat, s.id_cat, s.cd_subcat, s.ds_subcat, c.ds_cat_eng "
        "FROM healdb.hd_icd_subcategory s "
        "JOIN healdb.hd_icd_category c ON s.id_cat = c.id_cat "
        "WHERE s.ds_subcat_eng IS NULL AND c.ds_cat_eng IS NOT NULL"
    )
    cursor.execute(sql_command)
    registers = cursor.fetchall()
    cont=0
    for id_subcat, id_cat, cd_subcat, ds_subcat, ds_cat_eng in registers:
        try:
            prompt = (
                f'Try to use the category translation "{ds_cat_eng}" and complete it with the following subcategory: "{ds_subcat}". '
                f'If that’s not possible, provide a full translation of the subcategory.'
            )
            ds_subcat_eng = translate_with_gptmodel(headers, url, model, prompt, ds_subcat)
            cursor.execute(
                "UPDATE healdb.hd_icd_subcategory SET ds_subcat_eng = %s WHERE id_subcat = %s AND id_cat = %s",
                (ds_subcat_eng, id_subcat, id_cat)
            )
            cont+=1
            if cont == 100:
               cont=0
               cnx.commit()
        except Exception as e:
            print(f"Failed to translate subcategory '{ds_subcat}': {e}")

    cnx.commit()
    return

def update_disease_descriptions_eng(cnx, cursor):
    # Updating english descriptions 
    # Updating the column: ds_group_eng (hd_icd_group)
    print ("Updating ICD group descriptions...")
    blocks_file      = PATHS["icd_group_eng_txt"]
    with open(blocks_file, "r") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            cd_cat_ini, cd_cat_end, ds_group_eng = row[0].strip(), row[1].strip(), row[3].strip()
            sql_command = (
                "UPDATE healdb.hd_icd_group "
                "     SET ds_group_eng = %s "
                "WHERE cd_cat_ini   = %s "
                "  AND cd_cat_end   = %s "
            )
            register = (ds_group_eng, cd_cat_ini, cd_cat_end)
            cursor.execute(sql_command, register)
            cnx.commit()

    # Updating the columns: ds_cat_eng e ds_subcat_eng (hd_icd_category e hd_icd_subcategory)
    print ("Updating ICD category and subcategory descriptions...")
    categories_file  = PATHS["icd_category_eng_txt"]

    with open(categories_file, "r") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            cd_icd = row[7].strip()
            ds_description  = row[8].strip()
            sql_command = (
                "UPDATE healdb.hd_icd_category "
                "SET ds_cat_eng = %s "
                "WHERE cd_cat   = %s"
            )
            register = (ds_description, cd_icd)
            
            cursor.execute(sql_command, register)
       
            sql_command = (
                "UPDATE healdb.hd_icd_subcategory "
                "SET ds_subcat_eng = %s "
                "WHERE cd_subcat   = %s "
            )
            cursor.execute(sql_command, register)
        cnx.commit()
    return

def translate_disease_descriptions(cnx, cursor):
    update_disease_descriptions_eng(cnx, cursor)
    translate_missing_descriptions(cnx, cursor)
    return
