# -*- coding: utf-8 -*-
"""
Created on Sun Nov  17 09:00:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Create a structured repository of medications using external data sources, 
# specifically the DADOS_ABERTOS_MEDICAMENTOS dataset in CSV format from 
# DataVisa (ANVISA). The script processes medication records, including 
# therapeutic classes and regulatory categories, and stores the data in a 
# relational structure suitable for health data analysis and integration.

import csv
from config import PATHS
from datetime import datetime

def update_active_ingredient_medication(cnx, cursor):
    # Updates active ingredients in the medication table to standardize format.
    try:
        updates = [
            (
                "UPDATE healdb.hd_medication "
                "SET ds_active_ingredients = replace(ds_active_ingredients, 'CIANOCOBALAMINA 0 + 1%', 'CIANOCOBALAMINA')"
            ),
            (
                "UPDATE healdb.hd_medication "
                "SET ds_active_ingredients = replace(ds_active_ingredients, 'VACINA DENGUE 1 +  2 +  3 E 4 (ATENUADA)', "
                "'VACINA DENGUE 1 (ATENUADA) +  VACINA DENGUE 2 (ATENUADA) +  VACINA DENGUE 3 (ATENUADA) + VACINA DENGUE 4 (ATENUADA)')"
            ),
            (
                "UPDATE healdb.hd_medication "
                "SET ds_active_ingredients = replace(ds_active_ingredients,'VACINA ROTAVÍRUS HUMANO/BOVINO G1 +  G2 +  G3 +  G4 E P1A[8] (ATENUADA)', "
                "'VACINA ROTAVÍRUS HUMANO/BOVINO G1 (ATENUADA) +  VACINA ROTAVÍRUS HUMANO/BOVINO G2 (ATENUADA) +  VACINA ROTAVÍRUS HUMANO/BOVINO G3 (ATENUADA) + VACINA ROTAVÍRUS HUMANO/BOVINO G4 (ATENUADA) + VACINA ROTAVÍRUS HUMANO/BOVINO P1A[8] (ATENUADA)')"
            ),
            (
                "UPDATE healdb.hd_medication "
                "SET ds_active_ingredients = TRIM(TRAILING CHAR(0) FROM "
                "REVERSE(SUBSTRING(REVERSE(TRIM(TRAILING CHAR(0) FROM ds_active_ingredients)), 2, "
                "LENGTH(TRIM(TRAILING CHAR(0) FROM ds_active_ingredients))))) "
                "WHERE RIGHT(ds_active_ingredients, 1) = '+'"
            ),
        ]
        for sql_command in updates:
            cursor.execute(sql_command)
        cnx.commit()
    except Exception as e:
        print(f"Error updating active ingredients: {e}")
    return

def populate_tables_from_stg_medication(cnx, cursor):
    
    # Populate hd_company, hd_regulatory_category, hd_therapeutic_class,
    # and hd_medication tables using data from hd_wrk_medication.
    
    try:
        # Populate hd_company table
        print("Populating hd_company table...")
        sql_command = (
            "INSERT INTO healdb.hd_company "
            "(nr_cnpj_company, nm_company) "
            "SELECT DISTINCT nr_cnpj_company, nm_company "
            "FROM healdb.hd_wrk_medication "
            "WHERE nr_cnpj_company IS NOT NULL "
            "AND nm_company IS NOT NULL"
        )
        cursor.execute(sql_command)
        cnx.commit()
        
        # Populate hd_regulatory_category table
        print("Populating hd_regulatory_category table...")
        sql_command = (
            "INSERT INTO healdb.hd_regulatory_category "
            "(ds_regulatory_category) "
            "SELECT DISTINCT tp_regulatory_category "
            "FROM healdb.hd_wrk_medication "
            "WHERE tp_regulatory_category IS NOT NULL"
        )
        cursor.execute(sql_command)
        cnx.commit()

        # Populate hd_therapeutic_class table
        print("Populating hd_therapeutic_class table...")
        sql_command = (
            "INSERT INTO healdb.hd_therapeutic_class "
            "(ds_therapeutic_class) "
            "SELECT DISTINCT tp_therapeutic_class "
            "FROM healdb.hd_wrk_medication "
            "WHERE tp_therapeutic_class IS NOT NULL"
        )
        cursor.execute(sql_command)
        cnx.commit()

        # Populate hd_medication table
        print("Populating hd_medication table...")
        sql_command = (
            "INSERT INTO healdb.hd_medication "
            "(nr_register, nm_medication, id_regulatory_category, "
            "dt_expiration, id_therapeutic_class, id_company, "
            "fl_status, ds_active_ingredients) "
            "SELECT "
            "MAX(stg.nr_register) AS nr_register, "
            "stg.nm_medication, "
            "reg.id_regulatory_category, "
            "MAX(stg.dt_expiration) AS dt_expiration, "
            "ther.id_therapeutic_class, "
            "comp.id_company, "
            "stg.fl_status, "
            "stg.ds_active_ingredients "
            "FROM healdb.hd_wrk_medication stg "
            "LEFT JOIN healdb.hd_regulatory_category reg "
            "ON stg.tp_regulatory_category = reg.ds_regulatory_category "
            "LEFT JOIN healdb.hd_therapeutic_class ther "
            "ON stg.tp_therapeutic_class = ther.ds_therapeutic_class "
            "LEFT JOIN healdb.hd_company comp "
            "ON stg.nr_cnpj_company = comp.nr_cnpj_company "
            "GROUP BY "
            "stg.nm_medication, "
            "stg.tp_regulatory_category, "
            "stg.tp_therapeutic_class, "
            "stg.fl_status, "
            "stg.ds_active_ingredients, "
            "reg.id_regulatory_category, "
            "ther.id_therapeutic_class, "
            "comp.id_company"
            )   

        cursor.execute(sql_command)

        cnx.commit()

        print("All tables populated successfully!")
        
    except Exception as e:
        print(f"Error populating tables: {e}")

    return


def create_medications_repository(cnx, cursor):
    # Reads and processes medication data from an external source into the repository.
    print("Processing MEDICATIONS")

    try:
        csv_file = PATHS["medications_csv"]

        # Clear existing data
        try:
            cursor.execute("TRUNCATE TABLE healdb.hd_wrk_medication;")
            cursor.execute("DELETE FROM healdb.hd_medication;")
            cursor.execute("ALTER TABLE healdb.hd_medication AUTO_INCREMENT = 1;")
            cnx.commit()
        except Exception as e:
            print(f"Error clearing medication tables: {e}")
            return

        # Open and process the CSV file
        try:
            with open(csv_file, "r") as file:
                csv_reader = csv.reader(file, delimiter=";")
                next(csv_reader)  # Skip header

                for row in csv_reader:
                    try:
                        # Skip canceled medications
                        if row[9] == "CADUCO/CANCELADO":
                            continue

                        cnpj, company = row[8].split("-", 1)
                        register = (
                            row[4],  # nr_register
                            row[1],  # nm_medication
                            row[3],  # tp_regulatory_category
                            datetime.strptime(row[5], "%d/%m/%Y").strftime("%Y-%m-%d") if row[5] else None,
                            row[7],  # tp_therapeutic_class
                            cnpj.strip(),  # nr_cnpj_company
                            company.strip(),  # nm_company
                            row[9],  # fl_status
                            row[10] or row[1],  # ds_active_ingredients
                        )
                        sql_command = (
                            "INSERT INTO healdb.hd_wrk_medication "
                            "(nr_register, nm_medication, tp_regulatory_category, dt_expiration, "
                            "tp_therapeutic_class, nr_cnpj_company, nm_company, fl_status, ds_active_ingredients) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        )
                        cursor.execute(sql_command, register)
                    except Exception as e:
                        print(f"Error processing row {row}: {e}")

                cnx.commit()
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return

        # Update 3 incorrect company name
        sql_command = (
           "UPDATE healdb.hd_wrk_medication "
           "SET nm_company = CASE nr_cnpj_company "
           "    WHEN '46179008000168' THEN 'BRASTERAPICA INDUSTRIA FARMACEUTICA LTDA' "
           "    WHEN '55980684000127' THEN 'ADIUM S.A.' "
           "    WHEN '61072393000133' THEN 'PFIZER BRASIL LTDA' "
           "END "
           "WHERE nr_cnpj_company IN ('46179008000168', '55980684000127', '61072393000133')"
           )

        cursor.execute(sql_command)
        
        # Call the function to populate related tables
        populate_tables_from_stg_medication(cnx, cursor)        
        
        # Update active ingredients
        update_active_ingredient_medication(cnx, cursor)
        print("Medications processed successfully!")
    except Exception as e:
        print(f"Error during medication processing: {e}")
    return