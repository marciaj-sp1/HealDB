# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 15:02:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Create the repository of active ingredients by processing the medication records stored in the 
# medication table. The goal is to extract, normalize, and store active ingredients and 
# their associations with medications in structured MySQL tables for further use.

def create_activeingr_repository(cnx, cursor):
    # Create repository for active ingredients and their association with medications
    try:
        # Clear existing data from active ingredients tables
        try:
            cursor.execute("TRUNCATE TABLE healdb.hd_medication_active_ingredient;")
            cursor.execute("DELETE FROM healdb.hd_active_ingredient;")
            cursor.execute("ALTER TABLE healdb.hd_active_ingredient AUTO_INCREMENT = 1;")
            cnx.commit()
        except Exception as e:
            print(f"Error clearing active ingredient tables: {e}")
            return

        print("Creating active ingredient")

        # Select all records from the medication table
        try:
            sql_command = (
                "SELECT id_medication, ds_active_ingredients FROM healdb.hd_medication"
            )
            cursor.execute(sql_command)
            registers = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching medication records: {e}")
            return

        # Process each record to split active ingredients
        try:
            for register in registers:
                id_medication = register[0]
                ds_active_ingredients = register[1]

                list_active_ingredient = ds_active_ingredients.split('+')

                for nm_active_ingredient in list_active_ingredient:
                    nm_active_ingredient = nm_active_ingredient.strip()
                    if nm_active_ingredient:  # Ignore empty or whitespace entries
                        register_ingredient = (id_medication, nm_active_ingredient)
                        sql_command = (
                            "INSERT INTO healdb.hd_wrk_medication_active_ing "
                            "(id_medication, nm_active_ingredient) "
                            "VALUES (%s, %s)"
                        )
                        cursor.execute(sql_command, register_ingredient)

            cnx.commit()
        except Exception as e:
            print(f"Error processing active ingredients: {e}")
            return

        # Insert distinct active ingredients into the hd_active_ingredient table
        try:
            sql_command = (
                "INSERT INTO healdb.hd_active_ingredient "
                "(nm_active_ingredient) "
                "SELECT DISTINCT nm_active_ingredient "
                "FROM healdb.hd_wrk_medication_active_ing"
            )
            cursor.execute(sql_command)
            cnx.commit()
        except Exception as e:
            print(f"Error inserting into hd_active_ingredient table: {e}")
            return

        # Associate medications with active ingredients in the hd_medication_active_ingredient table
        try:
            sql_command = (
                "INSERT INTO healdb.hd_medication_active_ingredient "
                "(id_medication, id_active_ingredient) "
                "SELECT DISTINCT t.id_medication, a.id_active_ingredient "
                "FROM healdb.hd_wrk_medication_active_ing t "
                "JOIN healdb.hd_active_ingredient a "
                "ON t.nm_active_ingredient = a.nm_active_ingredient"
            )
            cursor.execute(sql_command)
            cnx.commit()
        except Exception as e:
            print(f"Error associating medications with active ingredients: {e}")
            return

        print("Active ingredient repository created successfully!")
    except Exception as e:
        print(f"Error in create_activeingr_repository: {e}")
    return
