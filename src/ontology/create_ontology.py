# -*- coding: utf-8 -*-
"""
Created on Sun Nov  17 10:30:00 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Generating the HealDB Ontology from Relational Database DDLs 

import os
from config import PATHS

def generate_turtle_from_sql(sql_content, table_name):
    # Parse CREATE TABLE statements and generate Turtle ontology.
    lines = sql_content.split("\n")
    columns = []
    foreign_keys = []

    for line in lines:
        line = line.strip()
        if line.startswith("`"):  # Column definition
            col_name = line.split("`")[1]  # Extract column name
            col_type = line.split()[1]    # Extract column type
            columns.append((col_name, col_type))
        elif "FOREIGN KEY" in line:  # Foreign key definition
            fk_col = line.split("`")[1]  # Extract foreign key column name
            referenced_table = line.split("REFERENCES")[1].split("`")[1]  # Referenced table
            foreign_keys.append((fk_col, referenced_table))

    # Generate Turtle ontology
    ttl_lines = [
        "@prefix : <http://example.org/healdb#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    ]

    class_name = table_name.replace("hd_", "").title().replace("_", "")
    ttl_lines.append(f":{class_name} a owl:Class ;")
    ttl_lines.append(f'    rdfs:label "{class_name.replace("_", " ")}" .\n')

    for col_name, col_type in columns:
        property_name = col_name.replace("id_", "hasID_").replace("nm_", "hasName_").replace("_", "").title()
        col_range = "xsd:string"
        if "int" in col_type.lower():
            col_range = "xsd:integer"
        elif "varchar" in col_type.lower() or "text" in col_type.lower():
            col_range = "xsd:string"
        elif "date" in col_type.lower():
            col_range = "xsd:date"

        ttl_lines.append(f":{property_name} a owl:DatatypeProperty ;")
        ttl_lines.append(f"    rdfs:domain :{class_name} ;")
        ttl_lines.append(f"    rdfs:range {col_range} ;")
        ttl_lines.append(f'    rdfs:label "{property_name.replace("_", " ")}" .\n')

    for fk_col, ref_table in foreign_keys:
        object_property = fk_col.replace("id_", "has").title().replace("_", "")
        referenced_class = ref_table.replace("hd_", "").title().replace("_", "")

        ttl_lines.append(f":{object_property} a owl:ObjectProperty ;")
        ttl_lines.append(f"    rdfs:domain :{class_name} ;")
        ttl_lines.append(f"    rdfs:range :{referenced_class} ;")
        ttl_lines.append(f'    rdfs:label "{object_property.replace("_", " ")}" .\n')

    return "\n".join(ttl_lines)

def create_ontology (cns, cursor):
   # Read SQL files from the configured ontology DDL directory
   ddl_dir = PATHS["ontology_ddls"]
   sql_files = [os.path.join(ddl_dir, f) for f in os.listdir(ddl_dir) if f.endswith(".sql")]

   # Generate Turtle for all tables
   turtle_outputs = []
   for sql_file in sql_files:
       with open(sql_file, 'r', encoding='utf-8') as file:
           sql_content = file.read()
       table_name = os.path.basename(sql_file).replace("healdb_", "").replace(".sql", "")
       ttl = generate_turtle_from_sql(sql_content, table_name)
       turtle_outputs.append(ttl)

   # Combine all outputs into a single Turtle ontology
   turtle_ontology = "\n\n".join(turtle_outputs)

   # Save the Turtle ontology to a file
   turtle_output_path = os.path.join(PATHS["output_onto_dir"], "healdb_ontology.ttl")
   with open(turtle_output_path, 'w', encoding='utf-8') as ttl_file:
       ttl_file.write(turtle_ontology)

   print(f"Ontology generated: {turtle_output_path}")
   return
