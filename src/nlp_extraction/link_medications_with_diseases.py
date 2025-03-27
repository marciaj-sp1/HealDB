# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 12:44:00 2024

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Insert ICD codes found by Amazon Comprehend Medical
# into the translated leaflet indication text. The data will then
# be stored in the final table, associating medications with diseases
# and symptoms represented by the ICD codes.

def search_repository_icd(cursor, cd_icd_full_nodot):
    # Searches for the category and subcategory IDs associated with the ICD code
    # without dots in the database.
    try:
        # Search for the category ID
        sql_command = (
            "SELECT id_cat "
            "FROM healdb.hd_icd_category "
            "WHERE cd_cat = %s"
        )
        cursor.execute(sql_command, (cd_icd_full_nodot,))
        register = cursor.fetchone()
        id_cat = register[0] if register else None

        # Search for the subcategory ID
        sql_command = (
            "SELECT id_subcat "
            "FROM healdb.hd_icd_subcategory "
            "WHERE cd_subcat = %s"
        )
        cursor.execute(sql_command, (cd_icd_full_nodot,))
        register = cursor.fetchone()
        id_subcat = register[0] if register else None

        return id_cat, id_subcat
    except Exception as e:
        print(f"Error while searching ICD repository for code {cd_icd_full_nodot}: {e}")
        return None, None


def link_medications_with_diseases(cnx, cursor):
    # Links medications with diseases and symptoms (ICD codes) by:
    # - Fetching data from the intermediate table.
    # - Filtering and selecting high-score ICD associations.
    # - Inserting the associations into the final table.
    try:
        print("Fetching data from the intermediate table `ht_int_med_disease_map`...")
        # Fetch data from the intermediate table
        sql_command = (
            "SELECT id_medication, "
            "cd_icd_full, "
            "replace(cd_icd_full,'.','') cd_icd_full_nodot, "
            "vl_score "
            "FROM healdb.ht_int_med_disease_map "
            "WHERE EXISTS (SELECT 1 FROM healdb.hd_icd_category "
            "              WHERE cd_cat = replace(cd_icd_full,'.','')) "
            "   OR EXISTS (SELECT 1 FROM healdb.hd_icd_subcategory "
            "             WHERE cd_subcat = replace(cd_icd_full,'.','')) "
        )
        cursor.execute(sql_command)
        rows = cursor.fetchall()

        # Organize data by medication ID
        medications = {}
        for row in rows:
            id_medication, cd_icd_full, cd_icd_full_nodot, vl_score = row

            if id_medication not in medications:
                medications[id_medication] = []
            medications[id_medication].append((cd_icd_full, cd_icd_full_nodot, vl_score))

        # Process each medication
        for id_medication, data in medications.items():
            try:
                # Filter scores > 0.7
                high_vl_scores = [item for item in data if item[2] > 0.7]

                # If high scores are <= 5, add 3 additional highest scores
                if len(high_vl_scores) <= 5:
                    sorted_data = sorted(data, key=lambda x: x[2], reverse=True)
                    additional_vl_scores = sorted_data[:3]
                    high_vl_scores = high_vl_scores + [
                        item for item in additional_vl_scores if item not in high_vl_scores
                    ]

                # Insert associations into the final table
                for cd_icd_full, cd_icd_full_nodot, vl_score in high_vl_scores:
                    try:
                        id_cat, id_subcat = search_repository_icd(cursor, cd_icd_full_nodot)
                        sql_command = (
                            "INSERT INTO healdb.hd_medication_disease "
                            "(id_medication, cd_icd_full, id_icd_group, "
                            "id_icd_cat, id_icd_subcat) "
                            "VALUES (%s, %s, %s, %s, %s)"
                        )
                        cursor.execute(
                            sql_command,
                            (id_medication, cd_icd_full, None, id_cat, id_subcat)
                        )
                        cnx.commit()
                        print(f"Inserted association for medication ID {id_medication} with ICD {cd_icd_full}.")
                    except Exception as e:
                        print(f"Error inserting association for medication ID {id_medication}, ICD {cd_icd_full}: {e}")
                        continue
            except Exception as e:
                print(f"Error processing medication ID {id_medication}: {e}")
                continue

    except Exception as e:
        print(f"Error fetching data from `ht_int_med_disease_map`: {e}")
    return
