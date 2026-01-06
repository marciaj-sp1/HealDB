# -*- coding: utf-8 -*-
"""
Created on Sat Jan 03 15:20:00 2026

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script parses the Amazon Comprehend Medical output stored in
# `hd_int_med_disease_api_response.ds_api_response` and materializes the
# extracted clinical concepts into relational tables.
#
# For each medication, it iterates over the detected entities in the text and
# stores: (i) each ICD-10-CM concept suggested for an entity, including its code,
# description, confidence score, and the entity metadata (text span, type/category,
# offsets, and entity score); and (ii) all traits assigned to the entity (e.g.,
# NEGATION, HYPOTHETICAL, LOW_CONFIDENCE, PERTAINS_TO_FAMILY) along with their
# corresponding scores.
#
# The output is stored in two tables:
# - `hd_int_med_disease_entity_icd`: one row per (medication, entity occurrence, ICD code)
# - `hd_int_med_disease_entity_trait`: one row per (medication, entity occurrence, trait)
#
# These tables preserve the full set of extracted candidates and evidence,
# enabling downstream rules to select and deduplicate the clinically plausible
# medication–disease/symptom associations.



import json


def process_disease_data_json(cnx, cursor, truncate_before_load=True, batch_size=2000):
    try:
        if truncate_before_load:
            cursor.execute("TRUNCATE TABLE healdb.hd_int_med_disease_entity_icd;")
            cursor.execute("TRUNCATE TABLE healdb.hd_int_med_disease_entity_trait;")
            cnx.commit()

        print("Fetching data from `hd_int_med_disease_api_response`...")
        sql_command = (
            "SELECT id_medication, ds_api_response "
            "FROM healdb.hd_int_med_disease_api_response "
            "WHERE ds_api_response IS NOT NULL;"            
        )
        cursor.execute(sql_command)
        rows = cursor.fetchall()

        # --- Inserts ---------------------------------------------------------
        sql_command_entity_icd = (
            "INSERT INTO healdb.hd_int_med_disease_entity_icd ("
            "id_medication, nr_entity_id, ds_entity_text, tp_entity, ds_category, "
            "vl_entity_score, nr_begin_offset, nr_end_offset, ds_attributes, "
            "cd_icd_full, ds_icd, vl_icd_score"
            ") VALUES ("
            "%s,%s,%s,%s,%s,"
            "%s,%s,%s,%s,"
            "%s,%s,%s"
            ") "
            "ON DUPLICATE KEY UPDATE "
            "ds_entity_text=VALUES(ds_entity_text), "
            "tp_entity=VALUES(tp_entity), "
            "ds_category=VALUES(ds_category), "
            "vl_entity_score=VALUES(vl_entity_score), "
            "nr_begin_offset=VALUES(nr_begin_offset), "
            "nr_end_offset=VALUES(nr_end_offset), "
            "ds_attributes=VALUES(ds_attributes), "
            "ds_icd=VALUES(ds_icd), "
            "vl_icd_score=VALUES(vl_icd_score)"
        )

        sql_command_trait = (
            "INSERT INTO healdb.hd_int_med_disease_entity_trait ("
            "id_medication, nr_entity_id, nm_trait, vl_trait_score"
            ") VALUES (%s,%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE "
            "vl_trait_score=VALUES(vl_trait_score)"
        )

        batch_entity_icd = []
        batch_trait = []

        for (id_medication, ds_api_response) in rows:
            print(f"Processing id_medication={id_medication}...")

            # Keep EXACT behavior from your original script 2
            try:
                response_dict = json.loads(ds_api_response)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for medication ID {id_medication}: {e}")
                continue

            entities = response_dict.get("Entities", []) or []

            for idx, entity in enumerate(entities, start=1):
                # Entity occurrence identifier (prevents wrong deduplication)
                nr_entity_id = entity.get("Id")
                if nr_entity_id is None:
                    nr_entity_id = idx  # fallback (rare)

                ds_entity_text = entity.get("Text") or ""
                tp_entity = entity.get("Type")
                ds_category = entity.get("Category")
                vl_entity_score = entity.get("Score")
                nr_begin_offset = entity.get("BeginOffset")
                nr_end_offset = entity.get("EndOffset")

                # Keep attributes raw for traceability
                ds_attributes = json.dumps(entity.get("Attributes", []), ensure_ascii=False)

                # --- Traits: one row per trait (entity occurrence x trait) -----
                traits = entity.get("Traits", []) or []
                for tr in traits:
                    nm_trait = tr.get("Name")
                    if not nm_trait:
                        continue
                    vl_trait_score = tr.get("Score")
                    batch_trait.append((id_medication, nr_entity_id, nm_trait, vl_trait_score))

                # --- ICD concepts: one row per entity occurrence x ICD ----------
                for icd in (entity.get("ICD10CMConcepts", []) or []):
                    cd_icd_full = icd.get("Code")
                    if not cd_icd_full:
                        continue
                    ds_icd = icd.get("Description")
                    vl_icd_score = icd.get("Score")

                    batch_entity_icd.append((
                        id_medication, nr_entity_id, ds_entity_text, tp_entity, ds_category,
                        vl_entity_score, nr_begin_offset, nr_end_offset, ds_attributes,
                        cd_icd_full, ds_icd, vl_icd_score
                    ))

                # Flush if needed
                if len(batch_trait) >= batch_size:
                    cursor.executemany(sql_command_trait, batch_trait)
                    cnx.commit()
                    batch_trait.clear()

                if len(batch_entity_icd) >= batch_size:
                    cursor.executemany(sql_command_entity_icd, batch_entity_icd)
                    cnx.commit()
                    batch_entity_icd.clear()

        # Final flush
        if batch_trait:
            cursor.executemany(sql_command_trait, batch_trait)
            cnx.commit()

        if batch_entity_icd:
            cursor.executemany(sql_command_entity_icd, batch_entity_icd)
            cnx.commit()

        print("Done. Tables populated:")
        print(" - healdb.hd_int_med_disease_entity_icd")
        print(" - healdb.hd_int_med_disease_entity_trait")

    except Exception as e:
        print(f"Error processing `hd_int_med_disease_api_response`: {e}")

    return
