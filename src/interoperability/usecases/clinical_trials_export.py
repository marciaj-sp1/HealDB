# -*- coding: utf-8 -*-
"""
Created on Fri May 16 19:18:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script retrieves clinical trial data related to active ingredients using 
# the ClinicalTrials.gov API v2.
# The information collected includes:
# - NCT ID: Unique identifier for each clinical trial
# - Study Title: Brief description of the clinical study
# - Clinical Conditions: Medical conditions targeted by the study
# - Interventions: Treatments or therapies tested in the study
# - Outcomes: Reported outcome measures, such as changes in clinical metrics
#
# The output is structured as both a CSV and JSON file that includes:
# - id_active_ingredient: Unique identifier for the active ingredient in HealDB
# - nm_active_ingredient: Scientific name of the active ingredient
# - clinical_trials: A list of clinical trials associated with the ingredient:
#   - cd_nct: Clinical trial identifier
#   - ds_title: Study title
#   - ds_conditions: Clinical conditions associated with the trial
#   - ds_interventions: Interventions or treatments tested in the trial
#   - ds_outcomes: Reported outcome measures
#
# Data is inserted into 'hd_wrk_clinical_trials' with intermediate commits 
# for data integrity.
# A delay of 5 seconds is applied between requests to manage API rate limits.

import requests
import json
import csv
import time
import os
from config import PATHS, APIS_USE_CASES

# Load Clinical Trials API configuration
CLIN_URL = APIS_USE_CASES["clinicaltrials"]

# Define delay in seconds
REQUEST_DELAY = 5.0

# Query ClinicalTrials.gov by intervention (Active Ingredient name)
def query_clinical_trials(active_ingredient_name):
    params = {
        "query.intr": active_ingredient_name,
        "fields": "protocolSection.identificationModule.nctId,protocolSection.identificationModule.briefTitle,protocolSection.conditionsModule.conditions,protocolSection.armsInterventionsModule.interventions.name,resultsSection.outcomeMeasuresModule.outcomeMeasures.title",
        "format": "json",
        "pageSize": 10
    }
    url = CLIN_URL["base_url"]
    response = requests.get(url, params=params)
    response_json = []
    if response.status_code == 200:
        response_json = response.json().get("studies", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
    return response_json

# Export clinical trial data for active ingredients
def clinical_trials_export(cnx, cursor):
    try:
        # Select active ingredients that have not been processed yet
        sql_command = (
            "SELECT a.id_active_ingredient, b.nm_active_ingredient_eng "
            "FROM hd_active_ingredient a "
            "JOIN hd_translate_eng_active_ing b " 
            "ON a.id_active_ingredient = b.id_active_ingredient "
            "LEFT JOIN hd_wrk_clinical_trials ct "
            "ON a.id_active_ingredient = ct.id_active_ingredient "
            "WHERE ct.id_active_ingredient IS NULL "
            "ORDER BY a.id_active_ingredient"
        )
        cursor.execute(sql_command)
        rows = cursor.fetchall()

        for row in rows:
            id_active_ingredient = row[0]
            nm_active_ingredient_eng = row[1]

            print(f"Processing {id_active_ingredient} - {nm_active_ingredient_eng}...")
            trials = query_clinical_trials(nm_active_ingredient_eng)
            time.sleep(REQUEST_DELAY)

            # Insert only complete records into the working table
            for trial in trials:
                nct_id = trial.get("protocolSection", {}).get("identificationModule", {}).get("nctId")
                title = trial.get("protocolSection", {}).get("identificationModule", {}).get("briefTitle")
                conditions = ", ".join(trial.get("protocolSection", {}).get("conditionsModule", {}).get("conditions", []))
                interventions = ", ".join([i.get("name", "") for i in trial.get("protocolSection", {}).get("armsInterventionsModule", {}).get("interventions", [])])
                outcomes = ", ".join([om.get("title", "") for om in trial.get("resultsSection", {}).get("outcomeMeasuresModule", {}).get("outcomeMeasures", [])])

                if nct_id and title and outcomes:
                    # Check if the record already exists
                    register = (id_active_ingredient, nct_id)
                    sql_command = (
                        "SELECT 1 FROM hd_wrk_clinical_trials "
                        "WHERE id_active_ingredient = %s AND cd_nct = %s"
                    )
                    cursor.execute (sql_command, register)
                    exists = cursor.fetchone()

                    if not exists:
                        register =  (id_active_ingredient, nct_id, title, 
                                     conditions, interventions, outcomes)
                        sql_command = (
                            "INSERT INTO hd_wrk_clinical_trials "
                            "(id_active_ingredient, cd_nct, ds_title, "
                            "ds_conditions, ds_interventions, ds_outcomes) "
                            "VALUES (%s, %s, %s, %s, %s, %s)"
                        )
                        cursor.execute (sql_command, register)
                        cnx.commit()

    except Exception as e:
        print(f"Error during processing: {e}")

    finally:
        # Generate CSV Output regardless of errors
        output_dir = PATHS["output_clinical"]
        csv_output_path = os.path.join(output_dir, "clinical_trials_healdb.csv")
        json_output_path = os.path.join(output_dir, "clinical_trials_healdb.json")
        
        sql_command = (
            "SELECT ct.id_active_ingredient, ai.nm_active_ingredient, "
            "ct.cd_nct, ct.ds_title, ct.ds_conditions, ct.ds_interventions, " 
            "ct.ds_outcomes "
            "FROM hd_wrk_clinical_trials ct "
            "JOIN hd_active_ingredient ai " 
            "ON ct.id_active_ingredient = ai.id_active_ingredient "
        )
        cursor.execute (sql_command)
        rows = cursor.fetchall()

        # Generate CSV Output
        with open(csv_output_path, "w", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id_active_ingredient", "nm_active_ingredient", 
                             "cd_nct", "ds_title", "ds_conditions", 
                             "ds_interventions", "ds_outcomes"])
            for row in rows:
                writer.writerow(row)

        # Generate JSON Output
        json_data = {}
        for row in rows:
            id_active_ingredient = row[0]
            nm_active_ingredient = row[1]
            cd_nct = row[2]
            ds_title = row[3]
            ds_conditions = row[4]
            ds_interventions = row[5]
            ds_outcomes = row[6]

            if id_active_ingredient not in json_data:
                json_data[id_active_ingredient] = {
                    "id_active_ingredient": id_active_ingredient,
                    "nm_active_ingredient": nm_active_ingredient,
                    "clinical_trials": []
                }

            json_data[id_active_ingredient]["clinical_trials"].append({
                "cd_nct": cd_nct,
                "ds_title": ds_title,
                "ds_conditions": ds_conditions,
                "ds_interventions": ds_interventions,
                "ds_outcomes": ds_outcomes
            })

        # Convert the structured JSON data to a list for final output
        json_output = list(json_data.values())

        with open(json_output_path, "w", encoding="utf-8") as jsonfile:
            json.dump(json_output, jsonfile, indent=4, ensure_ascii=False)

        print(f"CSV and JSON exports completed: {csv_output_path}, {json_output_path}")
        
    return