# -*- coding: utf-8 -*-
"""
Created on Sat Jan 03 15:20:00 2026

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Applies the article cutoff policy over ACM outputs to create medication–disease associations.
#
# Inputs (already populated):
# - healdb.hd_int_med_disease_entity_icd   : exploded ICD-10-CM concepts per entity occurrence (entity × ICD10CMConcepts)
# - healdb.hd_int_med_disease_entity_trait : exploded traits per entity occurrence (entity × traits)
#
# Outputs:
# 1) healdb.hd_int_med_disease_cutoff_audit
# - one row per entity occurrence (top-ranked ICD-10-CM concept),
#   including: entity metadata, ICD-10-CM score level (LOW/MEDIUM/HIGH),
#   trait flags (e.g., NEGATION), pass/fail flags for each filtering rule,
#   and the ICD-10 mapping (exact subcategory match or 3-character category 
#   fallback).
#
# 2) healdb.hd_medication_disease
# - final medication–ICD-10 associations after:
#   (i) keeping only DX_NAME entities,
#   (ii) removing entities flagged with NEGATION,
#   (iii) applying an Entity.Score threshold,
#   (iv) selecting the top-ranked ICD-10-CM concept per entity,
#   (v) mapping ICD-10-CM to the HealDB ICD-10 repository (subcategory or category fallback),
#   (vi) aggregating by medication and removing duplicates,
#   (vii) keeping only MEDIUM and HIGH ICD score levels.


def link_medications_with_diseases(
    cnx,
    cursor,
    entity_score_min=0.70,
    icd_medium_min=0.30,
    icd_high_min=0.60,
    truncate_audit=True,
    truncate_final=True
):
    try:
        # Use session variables for readability in the SQL
        cursor.execute("SET @entity_score_min = %s", (float(entity_score_min),))
        cursor.execute("SET @icd_medium_min  = %s", (float(icd_medium_min),))
        cursor.execute("SET @icd_high_min    = %s", (float(icd_high_min),))
        cnx.commit()

        if truncate_audit:
            cursor.execute("TRUNCATE TABLE healdb.hd_int_med_disease_cutoff_audit;")
            cnx.commit()

        if truncate_final:
            cursor.execute("TRUNCATE TABLE healdb.hd_medication_disease;")
            cnx.commit()

        # ---------------------------------------------------------------------
        # 1) AUDIT TABLE 
        #    Selects the top ICD-10-CM concept per entity, computes the flags 
        #    and score level, maps it to the HealDB ICD-10 repository (exact 
        #    subcategory match or category fallback), and stores everything as 
        #    one auditable row per entity.
        # ---------------------------------------------------------------------
        sql_audit = """
        INSERT INTO healdb.hd_int_med_disease_cutoff_audit
       (
        id_medication, nr_entity_id,
        ds_entity_text, tp_entity, ds_category, vl_entity_score,
        nr_begin_offset, nr_end_offset, ds_attributes,
        cd_icd10cm_full, cd_icd10cm_nodot, ds_icd10cm, vl_icd10cm_score, tp_icd10cm_score_level,
        fl_negation, nm_trait_main, vl_trait_main_score,
        cd_icd10_nodot, tp_icd10_map,
        id_icd_group, id_icd_cat, id_icd_subcat,
        fl_pass_dx_name, fl_pass_negation, fl_pass_entity_score, fl_pass_all_pre
       )
        WITH
        -- 1) Rank ICD concepts per entity and keep top-1 
        top_icd AS (         
          SELECT
            e.*,
            ROW_NUMBER() OVER (
              PARTITION BY e.id_medication, e.nr_entity_id
              ORDER BY e.vl_icd_score DESC, e.cd_icd_full
            ) AS rn
          FROM healdb.hd_int_med_disease_entity_icd e
        ),
        -- 2) Keep only the top-1 ranked ICD per entity 
        entity_top AS (       
          SELECT              
            id_medication,
            nr_entity_id,
            ds_entity_text,
            tp_entity,
            ds_category,
            vl_entity_score,
            nr_begin_offset,
            nr_end_offset,
            ds_attributes,
            cd_icd_full,
            ds_icd,
            vl_icd_score
          FROM top_icd
          WHERE rn = 1
        ),
        -- 3) Flag the negation trait, if it exists 
        trait_flags AS (
          SELECT
            id_medication,
            nr_entity_id,
            MAX(CASE WHEN nm_trait = 'NEGATION' THEN 1 ELSE 0 END) AS fl_negation
          FROM healdb.hd_int_med_disease_entity_trait
          GROUP BY id_medication, nr_entity_id
        ),
        -- 4) Search the trait with the highest score - only for audit, not for cutoff 
        main_trait AS (
          SELECT
            id_medication,
            nr_entity_id,
            SUBSTRING_INDEX(
              GROUP_CONCAT(nm_trait ORDER BY COALESCE(vl_trait_score, 0) DESC, nm_trait SEPARATOR ','),
              ',', 1
            ) AS nm_trait_main,
            MAX(COALESCE(vl_trait_score, 0)) AS vl_trait_main_score
          FROM healdb.hd_int_med_disease_entity_trait
          GROUP BY id_medication, nr_entity_id
        ),
        -- 5) Map the ICD-10-CM to the ICD-10 
        --    mapped - prepare to use cat from subcat or only cat (when no subcat exact) 
        --    map_join - code mapping between ICD-10-CM and ICD-10  
        mapped AS (
          SELECT
            t.*,
            REPLACE(t.cd_icd_full, '.', '') AS cd_icd10cm_nodot,
            LEFT(REPLACE(t.cd_icd_full, '.', ''), 3) AS cd_cat3
          FROM entity_top t
        ),
        map_join AS (
          SELECT
            m.*,

            -- exact match subcategory (ICD-10 repository)
            s.id_subcat,
            s.id_cat AS id_cat_from_subcat,
            s.cd_subcat AS cd_subcat_match,

            -- category of subcategory (for group id)
            csub.id_group AS id_group_from_subcat,

            -- fallback category by 3 chars
            c3.id_cat   AS id_cat_from_cat3,
            c3.id_group AS id_group_from_cat3,
            c3.cd_cat   AS cd_cat3_match,

            -- choose ICD-10 code used by HealDB + ids (final choice)
            CASE
              WHEN s.id_subcat IS NOT NULL THEN s.cd_subcat
              WHEN c3.id_cat  IS NOT NULL THEN c3.cd_cat
              ELSE NULL
            END AS cd_icd10_nodot,

            -- classify the type of matching
            CASE
              WHEN s.id_subcat IS NOT NULL THEN 'SUBCAT_EXACT'
              WHEN c3.id_cat  IS NOT NULL THEN 'CAT3_FALLBACK'
              ELSE 'NO_MAP'
            END AS tp_icd10_map,

            -- define the final IDs
            COALESCE(csub.id_group, c3.id_group) AS id_icd_group,
            COALESCE(s.id_cat,     c3.id_cat)    AS id_icd_cat,
            s.id_subcat                          AS id_icd_subcat

          FROM mapped m
          LEFT JOIN healdb.hd_icd_subcategory s   /* exact subcat match */
            ON s.cd_subcat = m.cd_icd10cm_nodot   
          LEFT JOIN healdb.hd_icd_category csub   /* category from subcat */
            ON csub.id_cat = s.id_cat
          LEFT JOIN healdb.hd_icd_category c3     /* fallback for category */
            ON c3.cd_cat = m.cd_cat3
        )
        
        -- 6) Insert everything calculated before into the audit table using map_join
        SELECT
          j.id_medication,
          j.nr_entity_id,
          j.ds_entity_text,
          j.tp_entity,
          j.ds_category,
          j.vl_entity_score,
          j.nr_begin_offset,
          j.nr_end_offset,
          j.ds_attributes,

          j.cd_icd_full AS cd_icd10cm_full,
          j.cd_icd10cm_nodot,
          j.ds_icd      AS ds_icd10cm,
          j.vl_icd_score AS vl_icd10cm_score,

          -- Classifies the top ICD score per entity into LOW/MEDIUM/HIGH
          CASE
            WHEN j.vl_icd_score >= @icd_high_min   THEN 'HIGH'
            WHEN j.vl_icd_score >= @icd_medium_min THEN 'MEDIUM'
            ELSE 'LOW'
          END AS tp_icd10cm_score_level,

          COALESCE(tf.fl_negation, 0) AS fl_negation,
          mt.nm_trait_main,
          mt.vl_trait_main_score,

          j.cd_icd10_nodot,
          j.tp_icd10_map,
          j.id_icd_group,
          j.id_icd_cat,
          j.id_icd_subcat,
          
          -- Pass/fail flags for the cutoff
          -- fl_pass_all_pre indicates that the entity passed the article’s 
          -- pre-filters: it is DX_NAME; it is not flagged with NEGATION;
          -- Entity.Score is greater than or equal to the threshold.
          
          (j.tp_entity = 'DX_NAME') AS fl_pass_dx_name,
          (COALESCE(tf.fl_negation, 0) = 0) AS fl_pass_negation,
          (j.vl_entity_score >= @entity_score_min) AS fl_pass_entity_score,
          (
            (j.tp_entity = 'DX_NAME')
            AND (COALESCE(tf.fl_negation, 0) = 0)
            AND (j.vl_entity_score >= @entity_score_min)
          ) AS fl_pass_all_pre

        FROM map_join j
        LEFT JOIN trait_flags tf
          ON tf.id_medication = j.id_medication
         AND tf.nr_entity_id = j.nr_entity_id
        LEFT JOIN main_trait mt
          ON mt.id_medication = j.id_medication
         AND mt.nr_entity_id = j.nr_entity_id;
        """

        cursor.execute(sql_audit)
        cnx.commit()

        # ---------------------------------------------------------------------
        # 2) FINAL TABLE: dedup by (medication, ICD-10 mapped) + keep MEDIUM 
        #    and HIGH ICD score
        # ---------------------------------------------------------------------
        sql_final = """
        INSERT INTO healdb.hd_medication_disease
        (
         id_medication,
         cd_icd_full,
         id_icd_group,
         id_icd_cat,
         id_icd_subcat,
         vl_entity_score,
         vl_icd_score,
         tp_icd_score,
         nm_trait_main,
         vl_trait_main_score
        )
        WITH
        -- Select the lines that passed in the filter and has icd-10 not null
        -- (i.e. icd-10-cm successfully mapped to icd-10)
        eligible AS (
          SELECT
            a.id_medication,
            a.cd_icd10_nodot AS cd_icd10_final,
            a.id_icd_group,
            a.id_icd_cat,
            a.id_icd_subcat,
            a.vl_icd10cm_score,
            a.vl_entity_score,
            a.nm_trait_main,
            a.vl_trait_main_score
          FROM healdb.hd_int_med_disease_cutoff_audit a
          WHERE a.fl_pass_all_pre = 1
            AND a.cd_icd10_nodot IS NOT NULL
        ),
        -- Deduplicate repeated ICD-10 codes per medication by grouping on 
        -- (id_medication, cd_icd10_final) and keeping the best-scoring evidence
        dedup AS (
          SELECT
            id_medication,
            cd_icd10_final,

            MAX(vl_icd10cm_score) AS vl_icd_score,

            -- pick values from the row with the best ICD score (and best entity score as tie-breaker)
            SUBSTRING_INDEX(
              GROUP_CONCAT(vl_entity_score ORDER BY vl_icd10cm_score DESC, vl_entity_score DESC SEPARATOR ','),
              ',', 1
            ) AS vl_entity_score_best,

            SUBSTRING_INDEX(
              GROUP_CONCAT(nm_trait_main ORDER BY vl_icd10cm_score DESC, vl_entity_score DESC SEPARATOR ','),
              ',', 1
            ) AS nm_trait_main_best,

            SUBSTRING_INDEX(
              GROUP_CONCAT(COALESCE(vl_trait_main_score, 0) ORDER BY vl_icd10cm_score DESC, vl_entity_score DESC SEPARATOR ','),
              ',', 1
            ) AS vl_trait_main_score_best,

            MAX(id_icd_group)  AS id_icd_group,
            MAX(id_icd_cat)    AS id_icd_cat,
            MAX(id_icd_subcat) AS id_icd_subcat

          FROM eligible
          GROUP BY id_medication, cd_icd10_final
        ),
        --  After deduplication, it classifies the final pair score (vl_score) 
        -- into HIGH, MEDIUM, or LOW.
        icd_score_classified AS (
          SELECT
            *,
            CASE
              WHEN vl_icd_score >= @icd_high_min   THEN 'HIGH'
              WHEN vl_icd_score >= @icd_medium_min THEN 'MEDIUM'
              ELSE 'LOW'
            END AS tp_icd_score
          FROM dedup
        )
        -- Insert the final table by keeping only MEDIUM/HIGH pairs, 
        -- storing the mapped ICD-10 code, final scores, a MEDIUM 
        -- low-confidence flag, and main traits for documentation.

        SELECT
          id_medication,
          cd_icd10_final AS cd_icd_full,
          id_icd_group,
          id_icd_cat,
          id_icd_subcat,
          vl_entity_score_best AS vl_entity_score,
          vl_icd_score,
          tp_icd_score,
          nm_trait_main_best as nm_trait_main,
          vl_trait_main_score_best as vl_trait_main_score
        FROM icd_score_classified
        WHERE tp_icd_score IN ('MEDIUM','HIGH');
        """
        cursor.execute(sql_final)
        cnx.commit()

        print("OK: hd_int_med_disease_cutoff_audit filled (with ICD-10 mapping) and hd_medication_disease loaded (MEDIUM/HIGH).")

    except Exception as e:
        cnx.rollback()
        print(f"Error applying the cutoff policy and loading tables: {e}")
        raise
