# -*- coding: utf-8 -*-
"""
Created on Sun Nov  17 17:00:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Provide helper functions to populate a DrugBank-based repository using 
# data extracted from an XML file. This includes structured information 
# about drugs cataloged in DrugBank, such as synonyms, product ingredients (salt forms), 
# food interactions, drug interactions, and external identifiers that enable 
# interoperability with other biomedical databases. The main drug attributes 
# include: DrugBank identifier, name, description, and therapeutic indication.


def insert_db_drug(df, cnx, cursor):
    # Insert drugs into the db_drug table
    try:
        print("Inserting drugs into db_drug")

        # Insert data
        sql_command = (
            "INSERT INTO healdb.db_drug (id_drug, nm_drug, ds_drug, ds_drug_indication, id_drugbank) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        cursor.executemany(sql_command, df[["id_drug", "nm_drug", "ds_drug", "ds_drug_indication", "id_drugbank"]].values.tolist())
        cnx.commit()
                
    except Exception as e:
        print(f"Error inserting drugs: {e}")
    return

def insert_db_synonym(df, cnx, cursor):
    # Insert synonyms
    try:
        print("Inserting synonyms")

        for _, row in df.iterrows():
            for synonym in row["synonyms"]:
                sql_command = (
                    "INSERT INTO healdb.db_synonym (id_drug, nm_synonym) "
                    "VALUES (%s, %s)"
                )
                cursor.execute(sql_command, (row["id_drug"], synonym))
        cnx.commit()

    except Exception as e:
        print(f"Error inserting synonyms: {e}")
    return

def insert_db_product_ingredient(df, cnx, cursor):
    # Insert product ingredients
    try:
        print("Inserting product ingredients")

        for _, row in df.iterrows():
            for ingredient in row["product_ingredients"]:
                sql_command = (
                    "INSERT INTO healdb.db_product_ingredient (id_drug, nm_product_ingredient) "
                    "VALUES (%s, %s)"
                )
                cursor.execute(sql_command, (row["id_drug"], ingredient))
        cnx.commit()

    except Exception as e:
        print(f"Error inserting product ingredients: {e}")
    return

def insert_db_food_interaction(df, cnx, cursor):
    # Insert food interactions
    try:
        print("Inserting food interactions")

        # Insert data
        for _, row in df.iterrows():
            for interaction in row["food_interactions"]:
                sql_command = (
                    "INSERT INTO healdb.db_food_interaction (id_drug, ds_interaction) "
                    "VALUES (%s, %s)"
                )
                cursor.execute(sql_command, (row["id_drug"], interaction))
        cnx.commit()

    except Exception as e:
        print(f"Error inserting food interactions: {e}")
    return

def execute_batch_insert(cnx, cursor, values):
    # Execute batch insertion into the drug interaction table
    # due to the high volume of data
    
    # Executes a batch insert into the db_drug_interaction table
    try:
        command_sql = (
            "INSERT INTO healdb.db_drug_interaction "
            "(id_drug, id_drug_2, ds_interaction) "
            "VALUES (%s, %s, %s)"
        )
        # Perform batch insertion using executemany
        cursor.executemany(command_sql, values)
        # Commit the transaction
        cnx.commit()
    except Exception as e:
        # Handle any error during the batch insertion
        print(f"Error during batch insert into db_drug_interaction: {e}")
        # Rollback the transaction to avoid partial commits
        cnx.rollback()
        raise  # Re-raise the exception for further handling
    return

def search_id_drug(drugbank_ids, cursor):
    # Search for the drug identifier in the db_drug table
    
    # Searches for drug identifiers in the db_drug table
    try:
        # Convert the list of DrugBank IDs into a tuple for the SQL query
        print('Search drug ID')
        drugbank_ids_tuple = tuple(drugbank_ids)

        # Build the SQL query to fetch drug IDs
        command_sql = (
            "SELECT id_drugbank, id_drug "
            "FROM healdb.db_drug "
            "WHERE id_drugbank IN ({})".format(', '.join(['%s'] * len(drugbank_ids)))
        )

        # Execute the query with the list of DrugBank IDs
        cursor.execute(command_sql, drugbank_ids_tuple)

        # Fetch all matching results
        results = cursor.fetchall()

        # Create a dictionary mapping DrugBank IDs to drug IDs
        id_drug_dict = {id_drugbank: id_drug for id_drugbank, id_drug in results}
        print('End search drug ID')
        return id_drug_dict

    except Exception as e:
        # Handle any error during the search process
        print(f"Error during search_id_drug: {e}")
        raise  # Re-raise the exception for further handling
    return

def insert_db_drug_interaction(df, cnx, cursor, batch_size=2000):
    # Insert the drug interactions
    
    try:
        print("Inserting drug interactions")
    
        drug_interaction_drugbank_ids = set()
        for _, row in df.iterrows():
            drug_interactions = row[6]  # Dictionary of drug interactions
            drug_interaction_drugbank_ids.update(drug_interactions.keys())
    
        # Fetch the drug IDs for all interaction IDs at once
        id_drug_2_dict = search_id_drug(drug_interaction_drugbank_ids, cursor)

        values_to_insert = []
 
        # Iterate over the rows of the dataframe
        for row in df.itertuples(index=False):
            id_drug = row[0]
            drug_interactions = row[6]  # Dictionary of drug interactions
     
            # Iterate over the drug interactions and add them to the list of values
            for drug_interaction_drugbank_id, ds_interaction in drug_interactions.items():
                # Get the drug ID directly from the dictionary
                id_drug_2 = id_drug_2_dict.get(drug_interaction_drugbank_id)
         
                if id_drug_2 is not None:
                    values_to_insert.append((id_drug, id_drug_2, ds_interaction))
                
            # Insert in batches when the batch size is reached
            if len(values_to_insert) >= batch_size:
                execute_batch_insert(cnx, cursor, values_to_insert)
                values_to_insert = []

        # Insert the remaining values (if any)
        if values_to_insert:
            execute_batch_insert(cnx, cursor, values_to_insert)

    except Exception as e:
        print(f"Error inserting drug interactions: {e}")
    return


def insert_db_drug_external_id(df, cnx, cursor):
    # Insert external IDs that represent the drugs
    
    try:
        print("Inserting external IDs")

        for _, row in df.iterrows():
            for resource, identifier in row["external_ids"].items():
                sql_command = (
                    "INSERT INTO healdb.db_drug_external_id (id_drug, tp_external_id, cd_external_id) "
                    "VALUES (%s, %s, %s)"
                )
                cursor.execute(sql_command, (row["id_drug"], resource, identifier))
        cnx.commit()

    except Exception as e:
        print(f"Error inserting external IDs: {e}")
    return