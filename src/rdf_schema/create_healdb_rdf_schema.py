# -*- coding: utf-8 -*-
"""
Created on Thu May  01 23:05:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Generate the HealDB RDF Schema (not instantiated) from relational DDLs

import os
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from config import PATHS, NAMESPACES

# Namespaces
HEAL = Namespace(NAMESPACES["HEAL"])

# Initialize RDF graph
g = Graph()
g.bind("heal", HEAL)
g.bind("owl", OWL)
g.bind("xsd", XSD)
g.bind("rdfs", RDFS)

# Declare ontology resource
g.add((URIRef(NAMESPACES["HEAL"]), RDF.type, OWL.Ontology))

def parse_sql_create_table(sql_content):
    lines = sql_content.split("\n")
    columns = []
    foreign_keys = []

    for line in lines:
        line = line.strip()
        if line.startswith("`"):
            col_name = line.split("`")[1]
            col_type = line.split()[1]
            columns.append((col_name, col_type))
        elif "FOREIGN KEY" in line:
            fk_col = line.split("`")[1]
            referenced_table = line.split("REFERENCES")[1].split("`")[1]
            foreign_keys.append((fk_col, referenced_table))

    return columns, foreign_keys

def generate_rdf_from_table(table_name, columns, foreign_keys):
    class_name = table_name.replace("hd_", "").title().replace("_", "")
    class_uri = HEAL[class_name]
    g.add((class_uri, RDF.type, OWL.Class))
    g.add((class_uri, RDFS.label, Literal(class_name)))

    for col_name, col_type in columns:
        property_name = col_name.replace("id_", "hasID_").replace("nm_", "hasName_").replace("_", "").title()
        prop_uri = HEAL[property_name]
        g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        g.add((prop_uri, RDFS.domain, class_uri))

        col_range = XSD.string
        if "int" in col_type.lower():
            col_range = XSD.integer
        elif "date" in col_type.lower():
            col_range = XSD.date

        g.add((prop_uri, RDFS.range, col_range))
        g.add((prop_uri, RDFS.label, Literal(property_name)))

    for fk_col, ref_table in foreign_keys:
        object_property = fk_col.replace("id_", "has").title().replace("_", "")
        obj_prop_uri = HEAL[object_property]
        referenced_class = HEAL[ref_table.replace("hd_", "").title().replace("_", "")]

        g.add((obj_prop_uri, RDF.type, OWL.ObjectProperty))
        g.add((obj_prop_uri, RDFS.domain, class_uri))
        g.add((obj_prop_uri, RDFS.range, referenced_class))
        g.add((obj_prop_uri, RDFS.label, Literal(object_property)))

    return
 
def create_healdb_rdf_schema(cnx=None, cursor=None):
    ddl_dir = PATHS["healdb_ddls"]
    sql_files = [os.path.join(ddl_dir, f) for f in os.listdir(ddl_dir) if f.endswith(".sql")]

    for sql_file in sql_files:
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        table_name = os.path.basename(sql_file).replace("healdb_", "").replace(".sql", "")
        columns, foreign_keys = parse_sql_create_table(sql_content)
        generate_rdf_from_table(table_name, columns, foreign_keys)

    output_path = os.path.join(PATHS["output_rdf_schema"], "healdb_complete.ttl")
    g.serialize(destination=output_path, format="turtle")
    print(f"RDF Schema successfully generated at: {output_path}")
    return
