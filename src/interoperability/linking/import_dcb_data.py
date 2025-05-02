# -*- coding: utf-8 -*-
"""
Created on Sat Nov  30 06:28:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br
"""

# Import and process Brazilian Common Denominations (DCB) data into the HealDB repository.
# 
# Process:
# 1. Load DCB data from an Excel file.
# 2. Map and insert classification types and their descriptions into the classification table.
# 3. Populate the DCB list table with information such as DCB numbers, names, CAS numbers, 
#    and classification history.


import pandas as pd
from config import PATHS

def update_dcb_classification_descriptions(cnx, cursor):
    
    # Updates the `ds_dcb_classification` column in the `hd_dcb_classification` table
    # with predefined descriptions for each classification type.
    
    try:
        print("Updating DCB classification descriptions...")

        # Define the mapping of `tp_dcb_classification` to `ds_dcb_classification`
        classification_descriptions = {
            "IFA": "Insumos Farmacêuticos Ativos",
            "INF": "Insumos Farmacêuticos Não Classificados",
            "BIO": "Produtos Biológicos",
            "EXA": "Excipientes e Adjuvantes",
            "HOM": "Homeopáticos",
            "PM": "Espécies Vegatais",
            "RAD": "Radiofármacos"
        }
  
        # Loop through the mapping and update each record in the table
        for tp_classification, ds_classification in classification_descriptions.items():
            sql_command = (
                "UPDATE healdb.hd_dcb_classification "
                "SET ds_dcb_classification = %s "
                "WHERE tp_dcb_classification = %s"
            )
            cursor.execute(sql_command, (ds_classification, tp_classification))

        # Commit the changes to the database
        cnx.commit()

        print("DCB classification descriptions updated successfully!")
    except Exception as e:
        print(f"Error updating DCB classification descriptions: {e}")
    return

def process_dcb_data(cnx, cursor):
    # Processes the DCB classification data and populates the tables `hd_dcb_classification`
    # and `hd_dcb_list`.
    
    try:
        # Load the DCB Excel file
        print("Loading DCB classification data...")
        df = pd.read_excel(PATHS["dcb_list"])

        # Truncate existing data in the target tables
        print("Clearing existing data in the target tables...")
       
        cursor.execute("TRUNCATE TABLE healdb.hd_dcb_list;")
        cursor.execute("DELETE FROM healdb.hd_dcb_classification;")
        cursor.execute("ALTER TABLE healdb.hd_dcb_classification AUTO_INCREMENT = 1;")
        cnx.commit()

        # Create a mapping for classifications
        classification_map = {}

        # Process classifications
        print("Processing DCB classifications...")
        for index, row in df.iterrows():
            # Skip the header (first row)
            if index == 0:
                continue

            # Extract data from the current row
            tp_classification = row[3]  # Assuming column 4 is the classification type
            ds_classification = None  # Placeholder if detailed descriptions are added later

            # Insert classifications if not already present
            if tp_classification not in classification_map:
                sql_command = (
                    "INSERT INTO healdb.hd_dcb_classification "
                    "(tp_dcb_classification, ds_dcb_classification) "
                    "VALUES (%s, %s)"
                )
                cursor.execute(sql_command, (tp_classification, ds_classification))
                cnx.commit()
                classification_map[tp_classification] = cursor.lastrowid

        # Update the classification descriptions
        update_dcb_classification_descriptions(cnx, cursor)

        # Process DCB list data
        print("Processing DCB list...")
        for index, row in df.iterrows():
            # Skip the header (first row)
            if index == 0:
                continue

            # Extract data from the current row
            nr_dcb = str(row[0]).zfill(5)  # Assuming column 0 is the DCB number
            nm_dcb = row[1]  # Assuming column 1 is the DCB name
            nr_cas = row[2] if not pd.isna(row[2]) else None  # Assuming column 2 is CAS number
            tp_classification = row[3]  # Assuming column 4 is the classification type
            id_dcb_classification = classification_map.get(tp_classification)
            ds_history = row[4] if not pd.isna(row[4]) else None  # Assuming column 5 is history

            # Insert into `hd_dcb_list`
            sql_command = (
                "INSERT INTO healdb.hd_dcb_list "
                "(nr_dcb, nm_dcb, nr_cas, id_dcb_classification, ds_history) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            cursor.execute(sql_command, (nr_dcb, nm_dcb, nr_cas, id_dcb_classification, ds_history))
            cnx.commit()

        print("DCB data processing completed successfully!")
    except Exception as e:
        print(f"Error processing DCB data: {e}")
    return


def import_dcb_data(cnx, cursor):
    
    # Process the dcb data into the database
    process_dcb_data(cnx, cursor)
    
    return