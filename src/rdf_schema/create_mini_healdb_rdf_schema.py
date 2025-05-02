# -*- coding: utf-8 -*-
"""
Created on Sun Apr 13 18:31:00 2025

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Script to generate the HealDB RDF Schema in Turtle format using data from a MySQL database.
# The RDF Schema includes classes, object and data properties for Active Ingredients, their 
# External Identifiers, and the types of those identifiers. It also adds owl:sameAs links 
# between the internal identifiers and their  corresponding external URIs (e.g., ChEBI).

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from config import PATHS, NAMESPACES

# Namespaces
HEAL = Namespace(NAMESPACES["HEAL"])
CHEBI = Namespace(NAMESPACES["CHEBI"])

# Initialize RDF graph
g = Graph()
g.bind("heal", HEAL)
g.bind("owl", OWL)
g.bind("xsd", XSD)
g.bind("rdfs", RDFS)

def create_classes_and_properties():
    # Define OWL classes and object/data properties used in the RDF Schema.
    
    g.add((URIRef(NAMESPACES["HEAL"]), RDF.type, OWL.Ontology))

    # OWL Classes
    g.add((HEAL.ActiveIngredient, RDF.type, OWL.Class))
    g.add((HEAL.ExternalIdentifier, RDF.type, OWL.Class))
    g.add((HEAL.IdentifierType, RDF.type, OWL.Class))

    # Object properties
    g.add((HEAL.hasExternalIdentifier, RDF.type, OWL.ObjectProperty))
    g.add((HEAL.hasExternalIdentifier, RDFS.domain, HEAL.ActiveIngredient))
    g.add((HEAL.hasExternalIdentifier, RDFS.range, HEAL.ExternalIdentifier))

    g.add((HEAL.hasIdentifierType, RDF.type, OWL.ObjectProperty))
    g.add((HEAL.hasIdentifierType, RDFS.domain, HEAL.ExternalIdentifier))
    g.add((HEAL.hasIdentifierType, RDFS.range, HEAL.IdentifierType))

    # Data properties
    g.add((HEAL.activeIngredientName, RDF.type, OWL.DatatypeProperty))
    g.add((HEAL.activeIngredientName, RDFS.domain, HEAL.ActiveIngredient))
    g.add((HEAL.activeIngredientName, RDFS.range, XSD.string))

    g.add((HEAL.externalIdValue, RDF.type, OWL.DatatypeProperty))
    g.add((HEAL.externalIdValue, RDFS.domain, HEAL.ExternalIdentifier))
    g.add((HEAL.externalIdValue, RDFS.range, XSD.string))

    g.add((HEAL.externalIdOrigin, RDF.type, OWL.DatatypeProperty))
    g.add((HEAL.externalIdOrigin, RDFS.domain, HEAL.ExternalIdentifier))
    g.add((HEAL.externalIdOrigin, RDFS.range, XSD.string))

    g.add((HEAL.externalIdUpdatedAt, RDF.type, OWL.DatatypeProperty))
    g.add((HEAL.externalIdUpdatedAt, RDFS.domain, HEAL.ExternalIdentifier))
    g.add((HEAL.externalIdUpdatedAt, RDFS.range, XSD.dateTime))

    g.add((HEAL.identifierTypeShortDesc, RDF.type, OWL.DatatypeProperty))
    g.add((HEAL.identifierTypeShortDesc, RDFS.domain, HEAL.IdentifierType))
    g.add((HEAL.identifierTypeShortDesc, RDFS.range, XSD.string))

    g.add((HEAL.identifierTypeLongDesc, RDF.type, OWL.DatatypeProperty))
    g.add((HEAL.identifierTypeLongDesc, RDFS.domain, HEAL.IdentifierType))
    g.add((HEAL.identifierTypeLongDesc, RDFS.range, XSD.string))

def populate_rdf_schema(cnx, cursor):
    
    # Connects to the database, reads the data from HealDB, and populates the 
    # rdf schema with individuals and owl:sameAs links.
    
    # Load identifier types
    cursor.execute("SELECT tp_ext_id, ds_short_type, ds_long_type FROM hd_type_ext_id")
    id_type_map = {}
    for tp_ext_id, short_desc, long_desc in cursor.fetchall():
        id_type_uri = HEAL[f"IDTYPE_{tp_ext_id}"]
        id_type_map[tp_ext_id] = id_type_uri

        g.add((id_type_uri, RDF.type, HEAL.IdentifierType))
        g.add((id_type_uri, HEAL.identifierTypeShortDesc, Literal(short_desc)))
        g.add((id_type_uri, HEAL.identifierTypeLongDesc, Literal(long_desc)))

    # Load active ingredients
    cursor.execute("SELECT id_active_ingredient, nm_active_ingredient FROM hd_active_ingredient")
    ai_map = {}
    for id_ai, name in cursor.fetchall():
        ai_uri = HEAL[f"AI_{id_ai}"]
        ai_map[id_ai] = ai_uri

        g.add((ai_uri, RDF.type, HEAL.ActiveIngredient))
        g.add((ai_uri, HEAL.activeIngredientName, Literal(name)))

    # Load external identifiers
    cursor.execute("SELECT id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id, dt_updated FROM hd_active_ingredient_ext_id")
    for id_ai, tp_ext_id, cd_ext_id, origin, dt_updated in cursor.fetchall():
        clean_cd_ext_id = cd_ext_id.replace(":", "_").replace("-", "_").strip()
        ext_uri = HEAL[f"{tp_ext_id}_{clean_cd_ext_id}"]

        g.add((ext_uri, RDF.type, HEAL.ExternalIdentifier))
        g.add((ext_uri, HEAL.externalIdValue, Literal(cd_ext_id)))
        g.add((ext_uri, HEAL.externalIdOrigin, Literal(origin)))
        if dt_updated:
            g.add((ext_uri, HEAL.externalIdUpdatedAt, Literal(dt_updated, datatype=XSD.dateTime)))

        g.add((ext_uri, HEAL.hasIdentifierType, id_type_map[tp_ext_id]))
        g.add((ai_map[id_ai], HEAL.hasExternalIdentifier, ext_uri))

        # Add owl:sameAs only for ChEBI
        if tp_ext_id == "CHEBI":
            external_uri = URIRef(f"http://purl.obolibrary.org/obo/CHEBI_{cd_ext_id}")
            g.add((ext_uri, OWL.sameAs, external_uri))

    return

def create_mini_healdb_rdf_schema (cnx, cursor):
    create_classes_and_properties()
    populate_rdf_schema(cnx, cursor)
    output_file = f"{PATHS['output_rdf_schema']}/healdb.ttl"
    g.serialize(destination=output_file, format="turtle")
    print(f"RDF Schema successfully generated and saved to: {output_file}")

    return


























