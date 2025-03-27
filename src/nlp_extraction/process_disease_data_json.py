# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 12:17:00 2024

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script processes the API response from Amazon Comprehend Medical.
# It extracts all the information, particularly the ICD (International
# Classification of Diseases) codes and their scores from the indication
# text. The extracted information will be used later to associate medications
# with diseases and symptoms represented by the ICD codes.

import json


def process_disease_data_json(cnx, cursor):
    # Extract all information from the API response of AWS Amazon Comprehend Medical
    # and insert it into the table `hd_int_med_disease_map`.
    try:
        # Clear existing data
        try:
            cursor.execute("TRUNCATE TABLE healdb.hd_int_med_disease_map;")
            cnx.commit()
        except Exception as e:
            print(f"Error clearing hd_int_med_disease_map: {e}")
            return
     
        print("Fetching data from the table `hd_int_med_disease_api_response`...")
        sql_command = (
            "SELECT id_medication, ds_api_response "
            "FROM healdb.hd_int_med_disease_api_response "
        )
        cursor.execute(sql_command)
        rows = cursor.fetchall()

        for row in rows:
            id_medication = row[0]
            ds_api_response = row[1]
            print ("id_medication = ", id_medication)
            print ("ds_api_response = ", ds_api_response)
            
            try:
                # Convert the JSON string to a dictionary
                response_dict = json.loads(ds_api_response)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for medication ID {id_medication}: {e}")
                continue
            
            # Iterate through the entities in the API response
            for entity in response_dict.get('Entities', []):
                try:
                    ds_icd_aggreg = entity.get('Text')
                    tp_entity = entity.get('Type')
                    vl_entity_score = entity.get('Score')
                    ds_traits = json.dumps(entity.get('Traits', []))
                    tp_category = entity.get('Category')
                    nr_begin_offset = entity.get('BeginOffset')
                    nr_end_offset = entity.get('EndOffset')
                    ds_attributes = json.dumps(entity.get('Attributes', []))

                    # Process each ICD10CM concept within the entity
                    for icd10cm_attribute in entity.get('ICD10CMConcepts', []):
                        cd_icd_full = icd10cm_attribute['Code']
                        vl_score = icd10cm_attribute['Score']
                        ds_icd = icd10cm_attribute['Description']

                        # Print the extracted data 
                        print("id_medication = ", id_medication)
                        print("cd_icd_full = ", cd_icd_full)
                        print("ds_icd = ", ds_icd)
                        print("vl_score = ", vl_score)
                        print("ds_icd_aggreg = ", ds_icd_aggreg)
                        print("vl_entity_score = ", vl_entity_score)
                        print("tp_category = ", tp_category)
                        print("nr_begin_offset = ", nr_begin_offset)
                        print("nr_end_offset = ", nr_end_offset)
                        print("tp_entity = ", tp_entity)
                        print("ds_traits = ", ds_traits)
                        print("ds_attributes = ", ds_attributes)

                        # Insert the data into the database table
                        sql_command = (
                            "INSERT INTO healdb.hd_int_med_disease_map "
                            "(id_medication, cd_icd_full, ds_icd, vl_score, "
                            "ds_icd_aggreg, vl_entity_score, tp_category, "
                            "nr_begin_offset, nr_end_offset, tp_entity, "
                            "ds_traits, ds_attributes) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                            "ON DUPLICATE KEY UPDATE "
                            "ds_icd = VALUES(ds_icd), "
                            "vl_score = VALUES(vl_score), "
                            "ds_icd_aggreg = VALUES(ds_icd_aggreg), "
                            "vl_entity_score = VALUES(vl_entity_score), "
                            "tp_category = VALUES(tp_category), "
                            "nr_begin_offset = VALUES(nr_begin_offset), "
                            "nr_end_offset = VALUES(nr_end_offset), "
                            "tp_entity = VALUES(tp_entity), "
                            "ds_traits = VALUES(ds_traits), "
                            "ds_attributes = VALUES(ds_attributes)"
                        )
                        try:
                            cursor.execute(
                                sql_command,
                                (
                                    id_medication, cd_icd_full, ds_icd,
                                    vl_score, ds_icd_aggreg, vl_entity_score,
                                    tp_category, nr_begin_offset, nr_end_offset,
                                    tp_entity, ds_traits, ds_attributes
                                )
                            )
                            cnx.commit()
                        except Exception as e:
                            print(f"Error inserting data for medication ID {id_medication}, ICD {cd_icd_full}: {e}")
                            continue
                except Exception as e:
                    print(f"Error processing entity for medication ID {id_medication}: {e}")
                    continue
    except Exception as e:
        print(f"Error fetching data from `hd_int_med_disease_api_response`: {e}")
    return
