# -*- coding: utf-8 -*-
"""
Created on Fri May 30 15:07 2025

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""
# This script links medications with ICD-10-CM disease or symptom codes
# identified via Amazon Comprehend Medical (ACM) based on translated
# leaflet sections (indication + functionality). The goal is to populate
# `hd_medication_disease` with reliable associations between medications
# and ICD-classified conditions.
#
# Cutoff and Filtering Logic:
# 1. Only CIDs that exist in `hd_icd_category` or `hd_icd_subcategory` are accepted.
#
# 2. Both `vl_score` and `vl_entity_score` must be ≥ 0.6.
#
# 3. Traits that indicate uncertainty or irrelevance are excluded:
#    - "LOW_CONFIDENCE", "NEGATION", "PERTAINS_TO_FAMILY"
#    - "HYPOTHETICAL" is only accepted when its score ≤ 0.6.
#
# 4. The entity must have at least one of the following traits to be accepted:
#    - "DIAGNOSIS", "SYMPTOM", "SIGN", or accepted "HYPOTHETICAL".
#
# 5. Fallback rule is embedded: if score thresholds are met but traits are not aligned,
#   the entity is still excluded to ensure high precision.
#
# 6. The trait with the highest score is stored as `nm_trait_main`, along with its score.
#
# 7. `fl_low_confidence` is marked True if either score is < 0.7, even if accepted.
#
# This balance of confidence thresholds, trait filtering, and CID existence
# ensures high-quality links between medications and their associated diseases or symptoms.


def search_repository_icd(cursor, cd_icd_full_nodot):
    try:
        id_cat = id_group = id_subcat = None
        sql_command = (
            "SELECT id_group, id_cat FROM healdb.hd_icd_category WHERE cd_cat = %s"
        )
        cd_icd_cat = cd_icd_full_nodot[:3]
        cursor.execute(sql_command, (cd_icd_cat,))
        register = cursor.fetchone()
        if register:
            id_group, id_cat = register

        sql_command = (
            "SELECT c.id_group, s.id_cat, s.id_subcat "
            "FROM healdb.hd_icd_subcategory s "
            ",healdb.hd_icd_category c "
            "WHERE s.cd_subcat = %s "
            "and   s.id_cat = c.id_cat "
        )
        cursor.execute(sql_command, (cd_icd_full_nodot,))
        register = cursor.fetchone()
        if register:
            #id_subcat = register[0]
            id_group, id_cat, id_subcat = register
    except Exception as e:
        print(f"Error searching ICD repository for code {cd_icd_full_nodot}: {e}")

    return id_group, id_cat, id_subcat

def link_medications_with_diseases(cnx, cursor):
    try:
        print("Fetching data from hd_int_med_disease_entity and trait...")
        sql_command = (
            "SELECT e.id_medication, e.cd_icd_full, "
            "REPLACE(e.cd_icd_full, '.', '') AS cd_icd_full_nodot, "
            "e.vl_score, e.vl_entity_score, t.nm_trait, t.vl_trait_score "
            "FROM healdb.hd_int_med_disease_entity e "
            "LEFT JOIN healdb.hd_int_med_disease_trait t "
            "ON e.id_medication = t.id_medication AND e.cd_icd_full = t.cd_icd_full "
        )
        cursor.execute(sql_command)
        rows = cursor.fetchall()

        print("Creating medication_map dictionary...")
        medication_map = {}
        for row in rows:
            id_med = row[0]
            icd_full = row[1]
            icd_full_nodot = row[2]
            vl_score = row[3]
            vl_entity_score = row[4]
            trait = row[5]
            trait_score = row[6]

            key = (id_med, icd_full, icd_full_nodot)
            if key not in medication_map:
                medication_map[key] = {
                    'vl_score': vl_score,
                    'vl_entity_score': vl_entity_score,
                    'traits': []
                }
            if trait:
                medication_map[key]['traits'].append((trait, trait_score))

        print("Processing each medication-disease match...")
        for (id_med, icd_full, icd_full_nodot), values in medication_map.items():
            vl_score = values['vl_score']
            vl_entity_score = values['vl_entity_score']
            traits = values['traits']

            # Skip if CID does not exist in category or subcategory tables
            sql_check = (
                "SELECT EXISTS (SELECT 1 FROM healdb.hd_icd_category "
                "                WHERE cd_cat = %s) "
                "OR EXISTS (SELECT 1 FROM healdb.hd_icd_subcategory "
                "                WHERE cd_subcat = %s)"
            )
            cursor.execute(sql_check, (icd_full_nodot, icd_full_nodot))
            exists = cursor.fetchone()[0]
            # Check if the first three characters of the subcategory CID exist in the category table.
            # If so, use this CID to associate it with the medication.
            if not exists:
                if (len(icd_full_nodot) >=3):
                    icd_cat = icd_full_nodot[:3]
                    sql_check = (
                        "SELECT EXISTS (SELECT 1 FROM healdb.hd_icd_category "
                        "                WHERE cd_cat = %s) ")
                    cursor.execute(sql_check, (icd_cat,))
                    exists = cursor.fetchone()[0]
                    if not exists:
                       continue
                else:
                    continue
            # Trait filtering
            trait_names = {t[0] for t in traits}
            if trait_names & {"LOW_CONFIDENCE", "NEGATION", "PERTAINS_TO_FAMILY"}:
                continue
            if any(t[0] == "HYPOTHETICAL" and (t[1] or 0) > 0.65 for t in traits):
                continue

            # Secondary option: accepts SIGN or HYPOTHETICAL ≤ 0.6 if scores are high
            if vl_score >= 0.6 and vl_entity_score >= 0.6:
                valid_trait = any(
                    (t[0] in {"DIAGNOSIS", "SYMPTOM", "SIGN"} or
                     (t[0] == "HYPOTHETICAL" and (t[1] or 0) <= 0.6))
                    for t in traits
                )
                if not valid_trait:
                    continue
            else:
                continue

            # Select main trait
            nm_trait_main, vl_trait_score_main = (None, None)
            if traits:
                sorted_traits = sorted(traits, key=lambda x: x[1] or 0, reverse=True)
                nm_trait_main, vl_trait_score_main = sorted_traits[0]

            fl_low_confidence = vl_score < 0.7 or vl_entity_score < 0.7

            id_group, id_cat, id_subcat = search_repository_icd(cursor, icd_full_nodot)

            sql_insert = (
                "INSERT INTO healdb.hd_medication_disease "
                "(id_medication, cd_icd_full, id_icd_group, id_icd_cat, id_icd_subcat, "
                "vl_score, vl_entity_score, nm_trait_main, vl_trait_main_score, fl_low_confidence) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            )
            reg_insert = (
                id_med, icd_full, id_group, id_cat, id_subcat,
                vl_score, vl_entity_score, nm_trait_main, vl_trait_score_main, fl_low_confidence
            )

            cursor.execute(sql_insert, reg_insert)
            cnx.commit()
            print(f"Linked medication ID {id_med} with ICD {icd_full}")

    except Exception as e:
        print(f"Error in linking medications: {e}")
    return