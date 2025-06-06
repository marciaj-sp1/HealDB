# -*- coding: utf-8 -*-
"""
Created on Sun Nov  17 10:30:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Create a disease repository using external data sources based on ICD-10 
# (International Classification of Diseases) in CSV format. The repository 
# organizes disease information into groups, categories, and subcategories, 
# and stores the data in structured tables for future use in health-related 
# applications and analyses.


import csv
from config import PATHS

def create_icd_group_rep(cnx, cursor):
    # Creating icd_group repository
    try:
        print('Processing ICD GROUP')
        csv_file = PATHS["icd_group_csv"]

        id_group = 0
        register_group = []

        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader)
            for row in csv_reader:
                cd_cat_ini = row[0]
                cd_cat_end = row[1]
                cat = row[0][0]
                catf = row[1][0]
                numini = int(''.join(filter(str.isdigit, cd_cat_ini)))
                numfin = int(''.join(filter(str.isdigit, cd_cat_end)))
                ds_group = row[2]
                ds_group_abbrev = row[3]

                i = numini
                if cat != catf:
                    numfin = 99

                id_group += 1

                # Build the insert query
                register = (id_group, ds_group, ds_group_abbrev, cd_cat_ini, cd_cat_end)
                sql_command = (
                    "INSERT INTO healdb.hd_icd_group "
                    "(id_group, ds_group, ds_group_abbrev, cd_cat_ini, cd_cat_end) "
                    "VALUES (%s, %s, %s, %s, %s)"
                )
                cursor.execute(sql_command, register)
                cnx.commit()

                repeat = True
                while repeat:
                    updated = False
                    while i <= numfin:
                        # Format the number with two digits
                        number_two_digits = str(i).zfill(2)
                        categ = cat + number_two_digits
                        # Check if the category already exists in the register_group
                        for w, row in enumerate(register_group):
                            if row[0] == categ:
                                register_group[w][1] = ds_group
                                register_group[w][2] = ds_group_abbrev
                                register_group[w][3] = id_group
                                updated = True
                                break
                        # If not updated, append the new category
                        if not updated:
                            register_group.append([categ, ds_group, ds_group_abbrev, id_group])
                        i += 1
                    
                    # Transition to the next letter if necessary
                    if cat != catf:
                        cat = chr(ord(cat) + 1)  # Move to the next letter
                        numini = 0
                        if cat == catf:
                            # Set numfin to the final number if it's the last letter
                            numfin = int(''.join(filter(str.isdigit, cd_cat_end)))
                        else:
                            # Default to 99 for intermediate letters
                            numfin = 99
                        i = numini  # Reset i to the starting number
                    else:
                        repeat = False
        return register_group
    except Exception as e:
        print(f"Error processing ICD GROUP: {e}")
        return []

def create_icd_category_rep(cnx, cursor, register_group):
    # Creating icd_category repository
    try:
        print('Processing ICD CATEGORY')
        csv_file = PATHS["icd_category_csv"]

        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader)
            for row in csv_reader:
                cd_cat = row[0]
                tp_classif = row[1]
                ds_cat = row[2]
                ds_cat_abbrev = row[3]
                cd_refer = row[4]
                cd_excluded = row[5]

                id_group = None
                for w, row in enumerate(register_group):
                    if row[0] == cd_cat:
                        id_group = register_group[w][3]
                        break

                # Build the insert query
                register = (id_group, cd_cat, ds_cat, ds_cat_abbrev, tp_classif, cd_refer, cd_excluded)
                sql_command = (
                    "INSERT INTO healdb.hd_icd_category "
                    "(id_group, cd_cat, ds_cat, ds_cat_abbrev, tp_classif, cd_refer, cd_excluded) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                )
                cursor.execute(sql_command, register)
                cnx.commit()
        return
    except Exception as e:
        print (register)
        print(f"Error processing ICD CATEGORY: {e}")
        return

def create_icd_subcategory_rep(cnx, cursor):
    # Creating icd_subcategory repository
    try:
        print('Processing ICD SUBCATEGORY')
        csv_file = PATHS["icd_subcategory_csv"]

        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file, delimiter=';')
            next(csv_reader)
            for row in csv_reader:
                cd_subcat = row[0]
                cd_cat = cd_subcat[:3]
                tp_classif = row[1]
                fl_restrgender = row[2]
                ds_subcat = row[4]
                ds_subcat_abbrev = row[5]
                cd_refer = row[6]
                cd_excluded = row[7]

                # Build the insert query
                register = (cd_subcat, ds_subcat, ds_subcat_abbrev, tp_classif, fl_restrgender, cd_refer, cd_excluded, cd_cat)
                sql_command = (
                    "INSERT INTO healdb.hd_icd_subcategory "
                    "(cd_subcat, id_cat, ds_subcat, ds_subcat_abbrev, tp_classif, fl_restrgender, cd_refer, cd_excluded) "
                    "SELECT %s, id_cat, %s, %s, %s, %s, %s, %s "
                    "FROM healdb.hd_icd_category "
                    "WHERE cd_cat = %s"
                )
                cursor.execute(sql_command, register)
                cnx.commit()
        return
    except Exception as e:
        print(f"Error processing ICD SUBCATEGORY: {e}")
        return

def create_diseases_repository(cnx, cursor):
    # Clear existing data
    try:
        cursor.execute("DELETE FROM healdb.hd_icd_subcategory;")
        cursor.execute("DELETE FROM healdb.hd_icd_category;")
        cursor.execute("DELETE FROM healdb.hd_icd_group;")
        cursor.execute("ALTER TABLE healdb.hd_icd_subcategory AUTO_INCREMENT = 1;")
        cursor.execute("ALTER TABLE healdb.hd_icd_category AUTO_INCREMENT = 1;")
        cnx.commit()

        # Process repository creation
        register_group = create_icd_group_rep(cnx, cursor)
        create_icd_category_rep(cnx, cursor, register_group)
        create_icd_subcategory_rep(cnx, cursor)
        return
    except Exception as e:
        print(f"Error creating disease repository: {e}")
        return
