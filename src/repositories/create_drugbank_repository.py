# -*- coding: utf-8 -*-
"""
Created on Sun Nov  17 18:00:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Create a repository for DrugBank data provided in an XML file. This includes information about 
# drugs cataloged in DrugBank, such as synonyms, product ingredients (salt forms), drug interactions, 
# and food interactions. The attributes collected for each drug are: DrugBank identifier, 
#   name, description, and therapeutic indication.

from lxml import etree
import pandas as pd
from config import PATHS
from src.repositories.drugbank_inserts import (
    insert_db_drug,
    insert_db_food_interaction,
    insert_db_synonym,
    insert_db_product_ingredient,
    insert_db_drug_interaction,
    insert_db_drug_external_id,
)


def clear_drugbank_tables(cnx, cursor):
    # Clears existing data from DrugBank tables.
    print("Clearing existing DrugBank data")
    try:
        cursor.execute("TRUNCATE TABLE healdb.db_synonym;")
        cursor.execute("ALTER TABLE healdb.db_synonym AUTO_INCREMENT = 1;")
        cursor.execute("TRUNCATE TABLE healdb.db_product_ingredient;")
        cursor.execute("ALTER TABLE healdb.db_product_ingredient AUTO_INCREMENT = 1;")
        cursor.execute("DELETE FROM healdb.db_food_interaction;")
        cursor.execute("ALTER TABLE healdb.db_food_interaction AUTO_INCREMENT = 1;")
        cursor.execute("DELETE FROM healdb.db_drug_interaction;")
        cursor.execute("ALTER TABLE healdb.db_drug_interaction AUTO_INCREMENT = 1;")
        cursor.execute("TRUNCATE TABLE healdb.db_drug_external_id;")
        cursor.execute("DELETE FROM healdb.db_drug;")
        cursor.execute("ALTER TABLE healdb.db_drug AUTO_INCREMENT = 1;")
        cnx.commit()
    except Exception as e:
        print(f"Error clearing DrugBank tables: {e}")
        raise
    return

def read_process_drug_xml(tree, root, namespace):
    # Reads and processes the DrugBank XML, returning a DataFrame.
    
    print("Reading and Processing the DrugBank XML file")
    try:
        data_list = []
        id_drug = 0

        # Iterate through the 'drug' elements in the XML
        for drug in root.findall(".//db:drug", namespace):
            list_synonym = []
            list_product_ingredient = []
            list_food_interaction = []
            dict_drug_interaction = {}
            dict_external_ids = {}
            nm_drug = ''
            ds_drug = ''
            cas_number = ''

            # Find the drug name
            parent_drug = drug.getparent().tag if drug.getparent() is not None else None
            if parent_drug == '{http://www.drugbank.ca}drugbank':
      
                drugbank_id_xml = drug.find("db:drugbank-id", namespace)
                if drugbank_id_xml is not None and drugbank_id_xml.text:
                    id_drug += 1
                    id_drugbank = drugbank_id_xml.text
                    dict_external_ids["Drugbank Id"] = drugbank_id_xml.text
                
                drug_name_xml = drug.find("db:name", namespace)
                if drug_name_xml is not None and drug_name_xml.text:
                    nm_drug = drug_name_xml.text 
               
                # Find and print the drug description
                drug_desc_xml = drug.find("db:description", namespace)
                if drug_desc_xml is not None and drug_desc_xml.text:
                    ds_drug = drug_desc_xml.text
                    
                # Find cas-number
                drug_cas_xml = drug.find("db:cas-number", namespace)
                if drug_cas_xml is not None and drug_cas_xml.text:
                    cas_number = drug_cas_xml.text
                    dict_external_ids["CAS Number"] = drug_cas_xml.text

                     
                # Find indications
                drug_indication_xml =  drug.find("db:indication", namespace)
                if drug_indication_xml is not None and drug_indication_xml.text:
                    ds_drug_indication = drug_indication_xml.text
           
                # Find and print food interactions
                food_interactions = drug.findall(".//db:food-interaction", namespace)
                for interaction in food_interactions:
                    if interaction.text:
                        list_food_interaction.append(interaction.text)

                # Find and print drug interactions
                drug_interactions = drug.findall(".//db:drug-interaction", namespace)
                for interaction in drug_interactions:
                    drug_interaction_drugbank_id = interaction.find("db:drugbank-id", namespace)
                    desc_interaction = interaction.find("db:description", namespace)
                    if drug_interaction_drugbank_id is not None and drug_interaction_drugbank_id.text:
                            if desc_interaction is not None and desc_interaction.text:
                                dict_drug_interaction[drug_interaction_drugbank_id.text] = desc_interaction.text
               
     
               # Find and print synonyms
                synonym_elements = drug.findall(".//db:synonyms/db:synonym", namespace)
                for synonym in synonym_elements:
                    grandparent_synonym = synonym.getparent().getparent().tag
                    if grandparent_synonym == '{http://www.drugbank.ca}drug':
                        if synonym.text:
                            list_synonym.append(synonym.text)
                
                # Find and print product ingredients
                ingredient_elements = drug.findall(".//db:salts/db:salt", namespace)
                for ingredient in ingredient_elements:
                    ingredient_name = ingredient.find("db:name", namespace)
                    if ingredient_name is not None and ingredient_name.text:
                       list_product_ingredient.append(ingredient_name.text)
                
                # Find external identifiers
                external_identifiers = drug.findall(".//db:external-identifiers/db:external-identifier", namespace)
                for external_id in external_identifiers:
                    resource = external_id.find("db:resource", namespace)
                    identifier = external_id.find("db:identifier", namespace)
                    if resource is not None and identifier is not None:
                        dict_external_ids[resource.text] = identifier.text

                reg = (id_drug, nm_drug, ds_drug, ds_drug_indication, id_drugbank,
                       list_food_interaction, dict_drug_interaction, 
                       list_synonym, list_product_ingredient, dict_external_ids,
                       cas_number)
                #print(reg)
                data_list.append(reg)
        # Concatenate the list of dictionaries into a DataFrame
        df = pd.concat([pd.DataFrame([data]) for data in data_list], ignore_index=True)

        # Create DataFrame
        columns = [
            "id_drug", "nm_drug", "ds_drug", "ds_drug_indication", "id_drugbank",
            "food_interactions", "drug_interactions", "synonyms",
            "product_ingredients", "external_ids", "cas_number"
        ]
        df = pd.DataFrame(data_list, columns=columns)
        print("DrugBank data successfully processed into a DataFrame")
        return df

    except Exception as e:
        print(f"Error reading DrugBank XML: {e}")
        raise


def create_drugbank_repository(cnx, cursor):
    # Main function to create the DrugBank repository.
    
    try:
        print("Processing DrugBank repository")

        # Parse the XML file
        tree = etree.parse(PATHS["drugbank_xml"])
        root = tree.getroot()
        namespace = {"db": "http://www.drugbank.ca"}

        # Extract data from XML
        df = read_process_drug_xml(tree, root, namespace)

        # Clear existing data
        clear_drugbank_tables(cnx, cursor)

        # Insert data into the database
        insert_db_drug(df, cnx, cursor)
        insert_db_synonym(df, cnx, cursor)
        insert_db_product_ingredient(df, cnx, cursor)
        insert_db_food_interaction(df, cnx, cursor)
        insert_db_drug_interaction(df, cnx, cursor)
        insert_db_drug_external_id(df, cnx, cursor)

    except Exception as e:
        print(f"Error creating DrugBank repository: {e}")
        raise
