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
# It stores the results in two tables: hd_int_med_disease_entity and 
# hd_int_med_disease_trait. 


import json


def process_disease_data_json(cnx, cursor):
    # Extract all information from the API response of AWS Amazon Comprehend Medical
    # and insert it into the table hd_int_med_disease_entity.
    
    try:
        # Clear existing data
        cursor.execute("TRUNCATE TABLE healdb.hd_int_med_disease_trait;")
        cursor.execute("DELETE FROM healdb.hd_int_med_disease_entity;")
        cnx.commit()
            
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
            print (f"Processing id_medication={id_medication}... ")
            #print (f"ds_api_response = {ds_api_response}")
            
            try:
                # Convert the JSON string to a dictionary
                response_dict = json.loads(ds_api_response)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for medication ID {id_medication}: {e}")
                continue
            
            # Iterate through the entities in the API response
            for entity in response_dict.get('Entities', []):
                ds_icd_aggreg = entity.get('Text')
                tp_entity = entity.get('Type')
                vl_entity_score = entity.get('Score')
                tp_category = entity.get('Category')
                nr_begin_offset = entity.get('BeginOffset')
                nr_end_offset = entity.get('EndOffset')
                ds_attributes = json.dumps(entity.get('Attributes', []))
                
                for icd10cm_attribute in entity.get('ICD10CMConcepts', []):
                    cd_icd_full = icd10cm_attribute.get('Code')
                    vl_score = icd10cm_attribute.get('Score')
                    ds_icd = icd10cm_attribute.get('Description')

                    # Main entity register
                    reg_entity = (
                        id_medication, cd_icd_full, ds_icd,
                        vl_score, ds_icd_aggreg, vl_entity_score,
                        tp_category, nr_begin_offset, nr_end_offset,
                        tp_entity, ds_attributes
                    )

                    sql_command = (
                        "INSERT INTO healdb.hd_int_med_disease_entity "
                        "(id_medication, cd_icd_full, ds_icd, vl_score, "
                        "ds_icd_aggreg, vl_entity_score, tp_category, "
                        "nr_begin_offset, nr_end_offset, tp_entity, "
                        "ds_attributes) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE "
                        "ds_icd = VALUES(ds_icd), "
                        "vl_score = VALUES(vl_score), "
                        "ds_icd_aggreg = VALUES(ds_icd_aggreg), "
                        "vl_entity_score = VALUES(vl_entity_score), "
                        "tp_category = VALUES(tp_category), "
                        "nr_begin_offset = VALUES(nr_begin_offset), "
                        "nr_end_offset = VALUES(nr_end_offset), "
                        "tp_entity = VALUES(tp_entity), "
                        "ds_attributes = VALUES(ds_attributes)"
                    )

                    try:
                        cursor.execute(sql_command, reg_entity)
                        cnx.commit()
                    except Exception as e:
                        print(f"Error inserting entity for id_medication={id_medication}, ICD={cd_icd_full}: {e}")
                        continue

                    # Traits registers (if exists)
                    for trait in entity.get('Traits', []):
                        nm_trait = trait.get('Name')
                        vl_trait_score = trait.get('Score')
                        #print ("nm_trait = ", nm_trait)
                        #print ("vl_trait_score = ", vl_trait_score)

                        reg_trait = (id_medication, cd_icd_full, nm_trait, vl_trait_score)
                        sql_command = (
                            "INSERT INTO healdb.hd_int_med_disease_trait "
                            "(id_medication, cd_icd_full, nm_trait, vl_trait_score) "
                            "VALUES (%s, %s, %s, %s) "
                            "ON DUPLICATE KEY UPDATE vl_trait_score = VALUES(vl_trait_score)"
                        )

                        try:
                            cursor.execute(sql_command, reg_trait)
                            cnx.commit()
                        except Exception as e:
                            print(f"Error inserting trait for id_medication={id_medication}, ICD={cd_icd_full}, trait={nm_trait}: {e}")
    except Exception as e:
        print(f"Error fetching data from `hd_int_med_disease_api_response`: {e}")
    return
