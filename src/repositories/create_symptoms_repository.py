# -*- coding: utf-8 -*-
"""
Created on Sun Nov  17 13:14:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Create a symptoms repository using hierarchical data from the BIREME/MeSH 
# controlled vocabulary. This vocabulary, widely used for indexing and 
# retrieving biomedical information, provides structured symptom data 
# that is processed and inserted into a hierarchical format for use in 
# health-related applications.

import csv
from config import PATHS

def create_symptoms_repository(cnx, cursor):
    # Symptoms file to be imported
    try:
        csv_file = PATHS["symptoms_csv"]

        # Clear existing data
        try:
            cursor.execute("TRUNCATE TABLE healdb.hd_wrk_symptom;")
            cursor.execute("DELETE FROM healdb.hd_symptom;")
            cursor.execute("ALTER TABLE healdb.hd_symptom AUTO_INCREMENT = 1;")
            cnx.commit()
        except Exception as e:
            print(f"Error clearing existing data: {e}")
            return

        # Load the symptoms file in CSV format
        print('Processing SYMPTOMS')
        try:
            with open(csv_file, "r") as file:
                csv_reader = csv.reader(file, delimiter=';')
                next(csv_reader)  # Skip header

                for row in csv_reader:
                    try:
                        # Create a record with the corresponding columns
                        cd_1 = None if row[0] == '' else row[0]
                        cd_2 = None if row[1] == '' else row[1]
                        cd_3 = None if row[2] == '' else row[2]
                        cd_4 = None if row[3] == '' else row[3]
                        cd_5 = None if row[4] == '' else row[4]
                        cd_6 = None if row[5] == '' else row[5]
                        cd_7 = None if row[6] == '' else row[6]
                        cd_8 = None if row[7] == '' else row[7]
                        cd_9 = None if row[8] == '' else row[8]
                        cd_10 = None if row[9] == '' else row[9]
                        ds_symptom = row[10]

                        register = (cd_1, cd_2, cd_3, cd_4, cd_5, cd_6, cd_7, cd_8, cd_9, cd_10, ds_symptom)

                        # Build the insert query
                        sql_command = (
                            "INSERT INTO healdb.hd_wrk_symptom "
                            "(cd_1, cd_2, cd_3, cd_4, cd_5, cd_6, cd_7, cd_8, "
                            " cd_9, cd_10, ds_symptom) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        )
                        cursor.execute(sql_command, register)

                    except Exception as e:
                        print(f"Error processing row {row}: {e}")
                cnx.commit()
        except Exception as e:
            print(f"Error reading symptoms CSV: {e}")
            return

        # Transform symptoms into a hierarchical structure (tree-like)
        try:
            sql_command = (
                "INSERT INTO healdb.hd_symptom "
                "(cd_symptom_full, ds_symptom, cd_symptom_full_parent) "
                "SELECT "
                "CASE "
                " WHEN cd_10 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7,'.',cd_8,'.',cd_9,'.',cd_10) "
                " WHEN cd_9 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7,'.',cd_8,'.',cd_9) "
                " WHEN cd_8 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7,'.',cd_8) "
                " WHEN cd_7 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7) "
                " WHEN cd_6 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6) "
                " WHEN cd_5 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5) "
                " WHEN cd_4 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4) "
                " WHEN cd_3 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3) "
                " WHEN cd_2 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2) "
                " WHEN cd_1 IS NOT NULL THEN cd_1 "
                " END AS cod, "
                "ds_symptom, "
                "CASE "
                " WHEN cd_10 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7,'.',cd_8,'.',cd_9) "
                " WHEN cd_9 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7,'.',cd_8) "
                " WHEN cd_8 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6,'.',cd_7) "
                " WHEN cd_7 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5,'.',cd_6) "
                " WHEN cd_6 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4,'.',cd_5) "
                " WHEN cd_5 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3,'.',cd_4) "
                " WHEN cd_4 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2,'.',cd_3) "
                " WHEN cd_3 IS NOT NULL THEN CONCAT(cd_1,'.',cd_2) "
                " WHEN cd_2 IS NOT NULL THEN cd_1 "
                " ELSE '' "
                " END AS cod_pai "
                "FROM healdb.hd_wrk_symptom"
            )
            cursor.execute(sql_command)
            cnx.commit()
        except Exception as e:
            print(f"Error transforming symptoms into hierarchy: {e}")
            return

        print("Symptoms processed successfully!")
    except Exception as e:
        print(f"Error creating symptoms repository: {e}")
    return
