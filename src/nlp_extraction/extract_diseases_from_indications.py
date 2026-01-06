# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 11:59:00 2024

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Extract diseases and symptoms (ICD codes) from the medication leaflet 
# indications and functionality sections using the Amazon Comprehend Medical 
# API. The response is stored 
# in JSON format, and the ICD codes and scores are extracted from this JSON.

import json
import boto3
from config import AWS_CONFIG

# Configuration for Amazon Comprehend Medical client
comprehend_client = boto3.client(
    'comprehendmedical',
    region_name=AWS_CONFIG['region_name'],  # Use the region from config
    aws_access_key_id=AWS_CONFIG['aws_access_key_id'],  # Use access key from config
    aws_secret_access_key=AWS_CONFIG['aws_secret_access_key']  # Use secret key from config
)


def extract_diseases_from_indications(cnx, cursor):
    # Main function to process and extract diseases from indication text
    # using the Amazon Comprehend Medical tool.
    try:
        print("Fetching data from the table hd_translate_eng_leaflet_section...")
        # Fetch data from the translation table

        sql_command = """
            SELECT 
                t.id_medication,
                m.nm_medication,
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                      t.ds_indication_eng,
                      CONCAT(
                        '\\b',
                        REGEXP_REPLACE(
                          m.nm_medication,
                          '([\\\\\\\\.^$|()\\\\[\\\\]{}*+?\\\\-])',
                          '\\\\\\\\$1'
                          ),
                         '\\b'
                         ),
                         '<drug>',
                         1, 0, 'i'
                       ),
                       'with[[:space:]]+or[[:space:]]+without',
                       'regardless of',
                       1, 0, 'i'
                ) AS ds_indication_eng
            FROM healdb.hd_translate_eng_leaflet_section t
            JOIN healdb.hd_medication m
            ON m.id_medication = t.id_medication
            WHERE LENGTH(t.ds_indication_eng) > 10;
        """
        cursor.execute(sql_command)
        rows = cursor.fetchall()
        cont = 0
        for row in rows:
            # Access tuple elements using indices
            id_medication = row[0]  # First column: id_medication
            ds_indication_eng = row[2] # Third column: ds_indication_eng
            full_text = (
                "What this medication is indicated for:\n" +
                ds_indication_eng.strip() + "\n\n"  
                #+
                #"How this medication works:\n" +
                #ds_functionality_eng.strip()
            )   
            # Limit for 10.000 caracters
            full_text = full_text[:10000]
            print(f"Processing medication ID: {id_medication}")
            #print(f"Text for analysis: {full_text}")
            
            try:
                # Call Amazon Comprehend Medical API to infer ICD codes
                api_response = comprehend_client.infer_icd10_cm(Text=full_text)
                #print(f"API response for medication ID {id_medication}: {api_response}")
            except Exception as e:
                print(f"Error calling Amazon Comprehend Medical API for medication ID {id_medication}: {e}")
                continue

            # Convert the response to JSON format
            try:
                ds_api_response = json.dumps(api_response)
            except Exception as e:
                print(f"Error converting API response to JSON for medication ID {id_medication}: {e}")
                continue

            try:
                # Insert the response into the database
                sql_command = (
                    "INSERT INTO healdb.hd_int_med_disease_api_response "
                    "(id_medication, ds_text_submitted, ds_api_response) "
                    "VALUES (%s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE "
                    "ds_text_submitted = VALUES(ds_text_submitted), "
                    "ds_api_response = VALUES(ds_api_response)"
                )
                cursor.execute(sql_command, (id_medication, full_text, ds_api_response))
                cont += 1
                if (cont == 100):
                    cnx.commit()
                    cont = 0
                print(f"API response successfully stored for medication ID {id_medication}.")
            except Exception as e:
                print(f"Error storing API response in the database for medication ID {id_medication}: {e}")
                continue
        cnx.commit()
       
    except Exception as e:
        cnx.commit()
        print(f"Error processing indications: {e}")
    return
