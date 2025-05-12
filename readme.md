# HealDB Project

## **Overview**
HealDB is a comprehensive project designed to manage, analyze, and interoperate data related to medications, drug leaflets,
active ingredients, diseases, symptoms, drug interactions, and food interactions. 
This project includes functionalities for webcrawler, repositories management, data extraction, translation, and
interoperability, with a focus on integrating multiple data sources. 

---

## **Project Structure**
```plaintext
C:\project
└── healdb
    ├── data
    │   ├── input
    │   │   ├── bulas
    │   │   │   └── categorias
    │   │   │       ├── biologico
    │   │   │       ├── dinamizado
    │   │   │       ├── especifico
    │   │   │       ├── fitoterapico
    │   │   │       ├── generico
    │   │   │       ├── novo
    │   │   │       ├── prod_tp
    │   │   │       ├── radiofarmaco
    │   │   │       ├── similar
    │   │   ├── CID-10-CAPITULOS.csv
    │   │   ├── CID-10-CATEGORIAS.csv
    │   │   ├── CID-10-GRUPOS.csv
    │   │   ├── CID-10-SUBCATEGORIAS.csv
    │   │   ├── consulta_medicamento_anvisa.csv
    │   │   ├── DADOS_ABERTOS_MEDICAMENTOS.csv
    │   │   ├── input_active_ing_translate_meta
    │   │   ├── lista_dcb.xlsx
    │   │   ├── ddls
    │   │   │   ├── healdb_hd_active_ingredient.sql
    │   │   │   ├── healdb_hd_active_ingredient_ext_id.sql
    │   │   │   ├── healdb_hd_company.sql
    │   │   │   ├── healdb_hd_drug_interaction.sql
    │   │   │   ├── healdb_hd_icd_category.sql
    │   │   │   ├── healdb_hd_icd_group.sql
    │   │   │   ├── healdb_hd_icd_subcategory.sql
    │   │   │   ├── healdb_hd_medication.sql
    │   │   │   ├── healdb_hd_medication_active_ingredient.sql
    │   │   │   ├── healdb_hd_medication_disease.sql
    │   │   │   ├── healdb_hd_medication_drug_leaflet.sql
    │   │   │   ├── healdb_hd_regulatory_category.sql
    │   │   │   ├── healdb_hd_symptom.sql
    │   │   │   ├── healdb_hd_therapeutic_class.sql
    │   │   │   ├── healdb_hd_type_ext_id.sql
    │   │   │   ├── ddls_summary.xlsx
    │   │   ├── ontologies
    │   │   │   └── ATC.ttl   # RDF Schema ChEBI
    │   │   │   └── chebi.owl   # RDF Schema ATC
    │   │   │   └── healdb_mini.owl   # RDF Schema subset HealDB   │
    │   ├── output
    │   │   ├── downloadBulas
    │   │   ├── translation
    │   │   │   ├── output_active_ing_translate_meta.csv
    │   │   ├── interoperability
    │   │   │   ├── chebi
    │   │   │   │   ├── chebi_attributes_healdb.csv
    │   │   │   │   └── chebi_attributes_healdb_json.json
    │   │   │   ├── iucn
    │   │   │   │   ├── iucn_conservation_dcb.json
    │   │   │   │   ├── iucn_conservation_healdb.json
    │   │   │   ├── pubchem
    │   │   │   │   └── pubchem_reference_healdb.json
    │   │   │   ├── rxnorm
    │   │   │   │   └── rxnorm_enrichment_healdb.json
    │   │   │   ├── atc
    │   │   │   │   └── atc_attributes_healdb.csv
    │   │   │   │   └── atc_attributes_theraphealdb.csv
    │   │   ├── rdf_schema
    │   │   │   ├── healdb_complete.ttl
    │   │   │   └── healdb_mini.ttl
    │
    ├── doc
    ├── logs
    ├── tests
    ├── src
    │   ├── rdf_schema
    │   │   ├── __init__.py
    │   │   ├── main_rdf_schema.py
    │   │   ├── create_healdb_rdf_schema.py         # Complete RDF schema for HealDB
    │   │   ├── create_mini_healdb_rdf_schema.py    # Mini RDF schema with instance data
    │
    │   ├── interoperability
    │   │   ├── __init__.py
    │   │   ├── main_interoperability.py
    │   │   ├── linking
    │   │   │   ├── __init__.py
    │   │   │   ├── import_dcb_data.py
    │   │   │   ├── populate_external_ids_types.py
    │   │   │   ├── external_ids_insert.py
    │   │   │   ├── link_cas_to_active_ing.py
    │   │   │   ├── link_rxcui_to_active_ing.py
    │   │   │   ├── link_rxcui_related_ids_to_active_ing.py
    │   │   │   ├── link_wikidata_ids_to_wrk_table.py
    │   │   │   ├── link_kegg_related_ids_to_active_ing.py
    │   │   │   ├── fill_missing_external_ids.py
    │   │   ├── usecases
    │   │   │   ├── __init__.py
    │   │   │   ├── chebi_attributes_query.txt              # SPARQL query for CHEBI
    │   │   │   ├── iucn_export_conservation_status.py      # IUCN integration
    │   │   │   ├── pubchem_export_references.py            # PubChem integration
    │   │   │   ├── rxnorm_export_enriched_ingredients.py   # RxNorm integration
    │   │   │   ├── atc_attributes_query.txt                # SPARQL query for ATC
    │   │   │   ├── atc_attributes_theraphealdb_query.txt   # SPARQL query for ATC
    │
    │   ├── nlp_extraction
    │   │   ├── __init__.py
    │   │   ├── main_nlp_extraction.py
    │   │   ├── extract_leaflet_sections.py
    │   │   ├── translate_leaflet_indication.py
    │   │   ├── extract_diseases_from_indications.py
    │   │   ├── process_disease_data_json.py
    │   │   ├── link_medications_with_diseases.py
    │
    │   ├── repositories
    │   │   ├── __init__.py
    │   │   ├── main_repository.py
    │   │   ├── create_activeingr_repository.py
    │   │   ├── create_diseases_repository.py
    │   │   ├── create_drugbank_repository.py
    │   │   ├── create_leaflets_repository.py
    │   │   ├── create_medications_repository.py
    │   │   ├── create_symptoms_repository.py
    │   │   ├── drugbank_inserts.py
    │
    │   ├── translation
    │   │   ├── __init__.py
    │   │   ├── main_translation.py
    │   │   ├── translate_active_ingredients.py
    │   │   ├── translate_active_ingredients_meta.ipynb
    │   │   ├── import_translated_active_ingredients_meta.py
    │   │   ├── translate_drug_interactions.py
    │   │   ├── translate_food_interactions.py
    │   │   ├── validate_translation_and_link_active_ing.py
    │
    │   ├── webcrawler
    │   │   ├── __init__.py
    │   │   ├── main_webcrawler.py
    │   │   ├── webcrawler_leaflet.py
    │
    ├── requirements.txt
    ├── config.py
    ├── db_utils.py
    ├── main.py

```

## Key Features
1. Data Management
   * Input Data: Includes CSV files, XML files, and directories for storing electronic leaflets.
   * Output Data: Stores JSON and CSV files generated during analysis and interoperability.
2. Web Crawler: Automates data extraction from the ANVISA Electronic Leaflet System.
3. Repository Management: Automates the creation and population of repositories for HealDB.
4. Translation: Enables translation of data for interoperability.
5. NLP Extraction: Uses Natural Language Processing to extract diseases, symptoms, leaflets, interactions, and more.
6. Interoperability:
   * Linking: Associates active ingredients with standardized external identifiers (e.g., RxCUI, CAS, KEGG, PubChem, Wikidata).
   * Use Cases: Demonstrates how external identifiers can be used to extract insights from biomedical ontologies and 
data sources (e.g., ChEBI, IUCN, PubChem, ATC, RxNorm).
## How to Run
### Requirements
1. Install Python 3.9+.
2. Install required libraries from requirements.txt:
  ```bash
  pip install -r requirements.txt
  ```


### Running the Project
*  Configure the config.py file with your environment settings.
*  Run the main script:
   ```bash
   python main.py
   ```

## Inputs
The `data/input` folder contains all input data files required for processing, translation, and interoperability tasks. 
Key components include:

   - **CID-10 files**: International Classification of Diseases (chapters, categories, groups, subcategories).
   - DADOS_ABERTOS_MEDICAMENTOS.csv: Publicly available data on medications.
   - consulta_medicamento_anvisa.csv: Comprehensive list of medications and their attributes obtained from ANVISA.
   - drugbank_file.xml: DrugBank XML file containing structured biomedical data.
   - Arquivo_sintomas.xlsx: List of symptoms from the Bireme/MeSH vocabulary. 
   - input_active_ing_translate_meta: Dataset of active ingredients in Portuguese, used for translation with 
     Meta´s SeamlessM4T model.
   - lista_dcb.xlsx: List of Brazilian Common Denominations (DCB).

- ###  Subfolders

     - **`bulas/`**: Drug leaflet files organized by regulatory category (e.g., generic, herbal medicine).
     - **`ddls/`**: : SQL DDL files representing HealDB table structures, used to generate the RDF schema.
     - **`ontologies/`**: External biomedical ontologies used in interoperability(e.g. `chebi.owl`, `atc.ttl`), and 
  a subset of HealDB RDF Schema (e.g. `healdb_mini.ttl`).

These files serve as the foundational datasets for web crawling, creation of repositories, natural language processing, 
translations, and interoperability tasks.
## Usage
## **Webcrawler**
Scripts for web scraping and data extraction from ANVISA's Electronic Leaflet System.

- **`main_webcrawler.py`**  
  - Purpose: Automates web scraping to collect leaflets data.  
  - **Usage:**  
  ```bash
  python src/webcrawler/main_webcrawler.py
  ```
- **`webcrawler_leaflet.py`**  
  - Purpose: Automates the process of collecting and organizing leaflets from the ANVISA Electronic Leaflet System.
  - Key Processes:
    - Utilizes Selenium to navigate and interact with the website, automating the retrieval of data for all leaflet categories.
    - Uses BeautifulSoup to scrape medication data from the website's tables and store it in a structured format.
    - Downloads PDF files of the leaflets and saves them in category-specific folders.
    - Generates an Excel file for each category, containing a complete list of medications and their associated PDF file paths.
    - Provides the foundation for subsequent data integration into HealDB via the repository scripts.
    
## **Repositories**
Scripts for creating and populating HealDB repositories.

- **`main_repositories.py`**  
  - Purpose: Orchestrates repository creation.  
  - **Usage:**  
  ```bash
  python src/repositories/main_repositories.py
  ```

- **`create_activeingr_repository.py`**  
  - Purpose: Generates the repository for active ingredients.
  - Key Processes:
    - Splits active ingredients in the medication field using the "+" separator.
    - Stores results in a temporary table, associating medications with normalized active ingredients.
    - Adds active ingredients to the active_ingredient repository.
    - Links medications to their active ingredients.


- **`create_diseases_repository.py`**  
  - Purpose: Constructs a repository of diseases using ICD (International Classification of Diseases) data as input.
  - Key Processes:
    - Extracts data from ICD-related files (groups, categories, and subcategories).
    - Populates the disease repository by organizing and linking the ICD information hierarchically.
    - Enables integration of standardized disease data into HealDB for interoperability and advanced queries.


- **`create_medications_repository.py`**  
  - Purpose: Builds a structured medication repository using ANVISA data.
  - Key Processes:
    - Cleans existing data and resets tables.
    - Reads and processes data from a ANVISA CSV file about medications, filtering canceled medications.
    - Populates related tables (companies, categories, classes).
    - Normalizes active ingredients and ensures consistency.


- **`create_symptoms_repository.py`**  
  - Purpose: Generates a structured repository of symptoms using hierarchical data from the BIREME/MeSH controlled vocabulary.
  - Key Processes:
    - Clears and resets data in both temporary and permanent symptom tables to ensure consistency.
    - Imports and processes a CSV file (extracted from BIREME/MeSH repository) containing symptoms data into a temporary table.
    - Transforms symptoms into a hierarchical format, creating parent-child relationships, and stores them in the symptom repository.


- **`create_drugbank_repository.py`**  
  - Purpose: Processes the DrugBank XML file and integrates its data into HealDB for comprehensive drug management.
  - Key Processes:
    - Extracts information about drugs, including identifiers, names, descriptions, and usage indications.
    - Captures details on drug-food interactions to identify potential effects of food on drug efficacy or safety.
    - Maps synonyms for each drug to enhance data reachability and consistency.
    - Organizes product ingredients for accurate representation of drug components.
    - Processes drug-drug interactions to establish relationships between related drugs.


- **`create_leaflets_repository.py`**  
  - Purpose: Populates the repository with leaflet data extracted from PDF files categorized by ANVISA leaflet types.
  - Key Processes:
    - Reads and processes Excel files listing leaflets for each category.
    - Deduplicates data to retain the most recent versions.
    - Extracts text from PDFs using PyMuPDF for text-based files and Pytesseract for image-based files.
    - Stores extracted content and metadata in the medication_drug_leaflet table.
    - Handles additional OCR processing for leaflets identified as images when needed.

## **Translation**
Scripts for translating data and validating translations.

- **`main_translation.py`**  
  - Purpose: Executes all translation-related processes.  
  - **Usage:**  
  ```bash
  python src/translation/main_translation.py
  ```

- **`translate_active_ingredients.py`**  
  - Purpose: Translates active ingredients from Portuguese to English using the OpenAI API and updates the HealDB database with the translations.
  - Key Processes:
    - Copies active ingredients into a translation table for processing.
    - Translates active ingredients using the "gpt-4" model 
    - Updates the translation table with the initial English translation, while also including fields for manual review and final adjustments.


- **`translate_active_ingredients_meta.ipynb`**  
  - Purpose: Uses the SeamlessMT4 model from META to translate active ingredients into English via Google Colab.
  - Key Processes:
    - Exports active ingredients to a CSV file.
    - Processes the data in a Jupyter Notebook.
    - Translates using SeamlessMT4 and stores results in a DataFrame.
    - Exports the translated DataFrame to a CSV file.
  - Usage: Run the Jupyter Notebook in Google Colab for translation processing.


- **`import_translated_active_ingredients_meta.py`**  
  - Purpose: Imports and validates SeamlessMT4 translations of active ingredients against DrugBank data.
  - Key Processes:
    - Imports translations from a CSV file.
    - Compares translations to DrugBank entries.
    - Computes the total matches between the translated active ingredients and DrugBank entries.
  

- **`translate_drug_interactions.py`**  
  - Purpose: Translates drug interactions from English to Portuguese using the OpenAI API (GPT-3.5) and integrates the translated data into HealDB.
  - Key Processes:
    - Maps interactions to active ingredients in HealDB.
    - Replaces drug names with placeholders (XXX/YYY) for efficient translation.
    - Translates unique descriptions and substitutes placeholders with Portuguese active ingredient names.
    - Enriches HealDB with translated drug interaction data.


- **`translate_food_interactions.py`**  
  - Purpose: Translates food interactions from English to Portuguese using the OpenAI API (GPT-3.5) and integrates the translated data into HealDB.
  - Key Processes:
    - Maps interactions to active ingredients in HealDB.
    - Replaces drug names with a placeholder (XXX) for efficient translation.
    - Translates unique descriptions and substitutes the placeholder with Portuguese active ingredient names.
    - Enriches HealDB with translated food interaction data.


- **`validate_translation_and_link_active_ing.py`**
  - Purpose: Validates translations of active ingredients by comparing them to DrugBank data and links them to related drugs.
  - Key Processes:
    - Compares automatically translated terms (GPT-4) with DrugBank tables for drugs, synonyms, and product ingredients.
    - Validates manually translated terms in the same tables.
    - Stores the final translation (manual if available, otherwise automatic).
    - Links active ingredients in Portuguese to corresponding DrugBank drugs in English, enabling the capture of related drug interactions.

## **NLP Extraction**
Scripts for extracting data using NLP techniques.

- **`main_nlp_extraction.py`**  
  - Purpose: Executes NLP workflows for leaflet analysis.  
  - **Usage:**  
    ```bash   
       python src/nlp_extraction/main_nlp_extraction.py
    ```

- **`extract_leaflet_sections.py`**  
  - Purpose: Processes drug leaflets to extract specific sections, such as indications and precautions, and updates the leaflet repository.
  - Key Processes:
    - Reads and processes drug leaflets from the database.
    - Extracts sections like "Para que este medicamento é indicado?" and "O que devo saber antes de usar esse medicamento?" using regex.
    - Stores the extracted data in temporary tables.
    - Updates the leaflet repository with the processed information.


- **`translate_leaflet_indication.py`**  
  - Purpose: Translates the indication section from drug leaflets into English, 
  enabling the use of medical text analysis tools for symptom and disease extraction.
  - Key Processes: 
    - Copies indication texts into a translation table.
    - Translates using OpenAI’s GPT-3.5 API.
    - Resolves translation issues and updates missing or problematic entries.
    - Stores final English translations in the leaflet repository.


- **`extract_diseases_from_indications.py`**  
  - Purpose: Extracts diseases and symptoms from drug leaflet indications translated to English using Amazon Comprehend Medical.
  - Key Processes:
    - Reads translated indications.
    - Sends texts to Amazon Comprehend Medical for ICD code extraction using the ```comprehend_client_infer_icd10_acm``` API.
    - Saves results in JSON format and maps ICD codes with confidence scores to the database.


- **`process_disease_data_json.py`**  
  - Purpose: Processes the JSON response from Amazon Comprehend Medical, 
  extracting detailed information such as ICD codes, descriptions, and scores, and stores it in the database.
  - Key Processes:
    - Reads API responses stored in the database.
    - Transforms JSON strings into dictionaries.
    - Extracts data fields like c, ```icd_text```, 
    ```description```, and ```score```.
    - Saves extracted information for further analysis and linking.


- **`link_medications_with_diseases.py`**  
  - Purpose: Links medications with corresponding diseases using 
  ICD codes identified by Amazon Comprehend Medical from drug indication 
  text analysis.
  - Key Processes:
    - Filters ICD data based on confidence scores (>0.7) with additional conditions for lower scores.
    - Links extracted ICD codes to existing categories and subcategories in the HealDB ICD repository.
    - Updates the new medication-disease mapping table to reflect advanced research findings.


## **Interoperability**
Scripts for integrating data from external sources and linking them to active ingredients in HealDB.
This enables interoperability with other health data sources, ontologies, and biomedical databases.

- **`main_interoperability.py`**  
  - Purpose: Central script for orchestrating all interoperability processes.
  - **Usage:**  
    ```bash
    python src/interoperability/main_interoperability.py
    ```
### Linking

- **`import_dcb_data.py`**  

  - Purpose: Imports and processes DCB (Denominações Comuns Brasileiras) data into the HealDB database.
  - Key Processes:
    - Loads DCB data from an Excel file.
    - Maps and inserts DCB classifications and descriptions.
    - Populates the DCB list with details such as DCB numbers, names, CAS numbers, and classification history.

- **`populate_external_ids_types.py`**  

  - Purpose: Creates and populates a static table with the possible external identifiers types.
  - Key Processes:
    - Defines external ID system (RXNORM, KEGG, PUBCHEM, SNOMEDCT and others).
    - Inserts this data into the external identifier type table for consistency in linking.


- **`external_ids_insert`**  

  - Purpose: Inserts external identifiers (e.g., RXCUI, KEGG, PubChem) associated with active ingredients into the ```hd_active_ingredient_ext_id``` table in the HealDB database, ensuring referential integrity and avoiding duplicates.
  - Key Processes:
    - Validates whether the external ID type (```tp_ext_id```) exists in the ```hd_type_ext_id``` table before proceeding.
    - Inserts the external ID into the ```hd_active_ingredient_ext_id``` association table only if a matching record for the given active ingredient does not already exist, ensuring data integrity and avoiding duplication.


- **`link_cas_to_active_ing`**  

  - Purpose: Links CAS numbers to active ingredients in HealDB, using the official Brazilian DCB list as the primary source.
  - Key Processes:
    - Clears the ```hd_active_ingredient_ext_id``` table to prepare for new CAS mappings.
    - Matches active ingredient names with DCB entries using normalized string comparison.
    - Filters out invalid or reference-only CAS numbers (e.g., starting with “[Ref”).
    - Skips duplicates by checking for existing CAS associations.
    - Inserts valid CAS mappings into the external ID table identifying the source as “DCB”.


- **`link_rxcui_to_active_ing`**  

  - Purpose: Links RxNorm Concept Unique Identifiers (RxCUI) to active ingredients in HealDB using the RxNorm API.
  - Key Processes:
    - Retrieves active ingredients with English names from the translation table.
    - Queries the RxNorm API to obtain the corresponding RxCUI for each name.
    - Inserts valid RxCUI mappings into the external ID table, marking the source as “RXNORM”.
  

- **`link_rxcui_related_ids_to_active_ing`**  
  - Purpose: Links RxNorm-related external identifiers (e.g., SNOMED CT, ATC, UNII, DrugBank) to active ingredients in HealDB by querying the RxNorm API for each RxCUI linked to active ingredient.
  - Key Processes:
    - Retrieves all active ingredients from the database that already have a mapped RxCUI.
    - Queries the RxNorm API for each RxCUI to fetch related identifiers (e.g., SNOMED CT codes, ATC classifications).
    - Processes multiple values per identifier (e.g., several ATC codes for one RxCUI). 
    - Inserts valid related identifiers into the external ID table, marking “RXNORM” as the source.


- **`link_wikidata_ids_to_wrk_table`**
  - Purpose: Retrieves external identifiers from Wikidata using RxCUI as input and stores the results in a working table.
  - Key Processes:
    - Fetches all RxCUI values linked to active ingredients in HealDB.
    - Queries the Wikidata SPARQL endpoint in batches to retrieve identifiers like CAS, DrugBank, PubChem, ChEBI, SNOMED CT, ATC, UNII, and KEGG.
    - Inserts the results into the working table ```hd_wrk_wikidata_ext_id```, including the Wikidata entity URL.


- **`link_kegg_related_ids_to_active_ing`**  
  - Purpose: Links KEGG Compound IDs (from Wikidata) to active ingredients in HealDB and uses them to retrieve PubChem and ChEBI identifiers (via KEGG API) and associate them with the same active ingredients. 
  - Key Processes: 
    - Clears existing KEGG-related identifiers from the external ID table to avoid duplication.
    - Retrieves KEGG Compound IDs previously linked via Wikidata in the working table and maps them to active ingredients.
    - Queries the KEGG API to extract related PubChem CIDs and the primary ChEBI ID.
    - Inserts the KEGG ID (source: Wikidata) into the external ID table.
    - Inserts all associated PubChem CIDs and the first ChEBI ID found (source: KEGG) into the external ID table.
  

- **`fill_missing_external_ids`**  
  - Purpose: Fills in missing external identifiers (CAS, ATC, SNOMEDCT, UNII_CODE, CHEBI, PUBCHEM_CID) for active ingredients in HealDB by using RxCUI matches from the Wikidata working table.
  - Key Processes:
    - Identifies active ingredients that have a mapped RxCUI but are missing specific external IDs.
    - Searches the ```hd_wrk_wikidata_ext_id``` working table for ATC, SNOMEDCT, UNII_CODE, CHEBI and PUBCHEM_CID codes linked to those RxCUIs.
    - Inserts only identifiers not already present in the hd_active_ingredient_ext_id table.
    - Chooses one CAS number per active ingredient when there are multiple options.

### Use Cases

- **`chebi_attributes_query.txt`**
  - Purpose: Demonstrates semantic interoperability between HealDB and ChEBI using SPARQL queries.
  - Key Processes:
    - Joins graphs from HealDB and ChEBI in Apache Jena Fuseki.
    - Retrieves chemical attributes like formula, mass, SMILES, InChI, and InChIKey.
    - Links ingredients via owl:sameAs to extract structured ontology data in ChEBI.

- **`pubchem_export_references.py`**
  - Purpose: Extracts PubMed references linked to PubChem CIDs of antidepressant ingredients.
  - Key Processes:
    - Filters active ingredients by therapeutic class and maps them to PubChem CIDs.
    - Calls _Entrez API_ to retrieve related PMIDs and publication metadata.
    - Exports up to 3 references per ingredient to JSON.

- **`iucn_export_conservation_status.py`**
  - Purpose: Retrieves conservation and threat data for plant-based ingredients using the IUCN API.
  - Key Processes:
    - Retrieves active ingredients and DCB names classified as "PM" (plant-based).
    - Normalizes scientific names and queries IUCN Red List API.
    - Collects the following data:
      - Conservation status (e.g., "Vulnerable", "Endangered") - retrieved from the fields "category" and "category_description". 
      - Assessment year and geographical scope (e.g., Global, Europe, Mediterranean, Pan-Africa) - retrieved from the fields "year_published" and "scopes".
      - Extinction information - retrieved from the fields "possibly_extinct" and "possibly_extinct_in_the_wild".
      - Main threats - retrieved from the "threats" field as a list.
      - Geographical locations - retrieved from the "locations" field as a list.
    - Summarizes and saves results as JSON files for active ingredients and DCB data.

- **`rxnorm_export_enriched_ingredients.py`**
  - Purpose: Enriches HealDB active ingredients with clinical and pharmacological data 
  from the RxNorm API using RxCUI identifiers.
  - Key Processes:
    - Select active ingredients with RxCUI from ``hd_active_ingredient_ext_id``.
    - Retrieve preferred name, TTY, status, and synonyms via RxNorm API.
    - Extract clinical presentations (SCD) and branded presentations 
  (SBD, BPCK, SBDF, SBDC).
    - Structure data retrieved into dictionaries and export to ``rxnorm_enrichment_healdb.json``.

- **`atc_attributes_query.txt` and `atc_attributes_theraphealdb_query.txt`**
  - Purpose: Identifies the ATC therapeutic class associated with each active ingredient based on its ATC codes, 
  enabling semantic analysis by linking ATC data with active ingredients in HealDB.
  - Key Processes:
    - `atc_attributes_query.txt`: Extracts therapeutic class information based on ATC codes and UMLS identifiers, 
    linking them to active ingredients within the HealDB dataset. Includes labels and alternative labels to enhance 
    semantic alignment. 
    - `atc_attributes_theraphealdb_query.txt`: Extends the previous query by including therapeutic class data from 
    HealDB, enabling a comparative analysis between ATC and HealDB classifications. It links the therapeutic class 
    of each medication with the active ingredients associated with these medications.

- **`mesh_xxxx.py`**
  - Purpose: Placeholder for future queries exploring UNII relationships.
  - Key Processes:

## **RDF Schema**
Scripts that convert the relational structure of HealDB — based on the DDLs 
of its database tables — into an RDF schema saved in Turtle (.ttl) format.

- **`main_rdf_schema.py`**  
  - Purpose: Central script for orchestrating the RDF schema generation pipeline.
  - **Usage:**  
    ```bash
    python src/interoperability/rdf_schema/main_rdf_schema.py
    ```

- **`create_mini_healdb_rdf_schema.py`**
  - Purpose: Generates a simplified RDF schema (`healdb_mini.ttl`) that includes classes, properties, and instances 
 from the HealDB database, focusing on active ingredients, their external identifiers, types of identifiers, 
 medications, regulatory categories, and therapeutic classes. It provides a minimal but comprehensive representation 
 of HealDB, supporting interoperability use cases and SPARQL queries.
  - Key Processes:
    - Defines RDF classes, datatype and object properties for the entities: Active Ingredients, External Identifiers, 
    Identifier Types, Medications, Regulatory Categories, and Therapeutic Classes.
    - Converts HealDB data into RDF triples, instantiating classes and their relationships based on data fetched 
    from MySQL tables such as  `hd_active_ingredient`, `hd_active_ingredient_ext_id`, `hd_type_ext_id`, 
  `hd_medication`, `hd_medication_active_ingredient`, `hd_therapeutic_class`, and `hd_regulatory_category`.
    - Creates object properties to link Active Ingredients to Therapeutic Classes via Medications.
    - Defines ``owl:sameAs`` links for external IDs of type ChEBI and ATC, enhancing linkage with external ontologies.
    - Generates and saves the output as `healdb_mini.ttl`, used in interoperability use cases and SPARQL queries.
  
- **`create_healdb_rdf_schema.py`** 
  - Purpose: Converts the DDL files of HealDB's relational database into a complete RDF schema written in 
  Turtle (.ttl) format. 
  - Key Processes: 
    - Reads DDL´s sql files from the folder defined by ```PATHS ["healdb_ddls"]```.
    - Parses CREATE TABLE statements to extract columns, data types, and foreign keys. 
    - Maps SQL elements to OWL constructs:
      - Tables → ```owl:Class```
      - Columns → ```owl:DatatypeProperty```
      - Foreign keys → ```owl:ObjectProperty```
    - Automatically generates labels for classes and properties based on naming patterns (e.g., id_ → hasID_, nm_ → hasName_).
    - Writes the ontology to a file: ```healdb_complete.ttl``` in the directory defined by ```PATHS["output_rdf_schema"]```.
    - **Note:** This script generates only the RDF schema (classes and properties), without populating it with data from 
    the tables. Future steps may use this structure to instantiate individuals.

## **Config**
Ensure `config.py` contains accurate paths and API tokens for the required resources.
Defines file paths, API credentials, and project settings for managing data inputs, outputs, and integrations. 
Includes configurations for:

- Input/output directories (e.g., drug leaflets, ICD files, DrugBank XML, RDF Schema).
- API credentials and endpoints for OpenAI, AWS, IUCN and RxNorm.
- Web scraping settings, including browser preferences and download directories.
- Category mappings for leaflet types and conservation statuses.
- External ID URLs for health-related data sources (e.g., RxNorm, KEGG, Wikidata).
- API endpoints used in interoperability use cases to fetch biomedical and environmental data.
- Namespaces used in RDF schema generation and external ontologies.

Ensure all values are adjusted to match your environment and secure sensitive information like API keys.


## Output

1. Drug leaflets from Anvisa (data/output/downloadBulas):
   - Folder containing the downloaded drug leaflets from the Anvisa Portal. 
2. Interoperability Data (data/output/interoperability):
   - Output folder for the use cases involving external data integration. Includes results from:
     - ChEBI: Chemical attributes of ingredients via SPARQL query.
     - PubChem: Scientific publications retrieved for active ingredients.
     - IUCN: Conservation status and threats for plant-based ingredients.
       - `iucn_conservation_healdb.json`: Conservation data for active ingredients.
       - `iucn_conservation_dcb.json`: Conservation data for DCB names.
     - RxNorm: Enriched active ingredients with RxNorm clinical and pharmacological data.
     - ATC: Therapeutic class attributes associated with active ingredients, including ATC codes, 
     UMLS identifiers, and preferred labels.
       - `atc_attributes_healdb.csv`: Identification of ATC therapeutic classes for active ingredients in HealDB.
       - `atc_attributes_theraphealdb.csv`: Comparative listing of therapeutic classes from both ATC and HealDB 
       for each active ingredient.
     
     - MESH: (in progress)
3. Translation of active ingredients: 
   - output_active_ing_translate_meta.csv: File containing the translation of active ingredients using the Meta model.
4. RDF Schema (data/output/rdf_schema):
   - healdb_mini.ttl: Simplified RDF schema encompassing data from the following HealDB tables: `hd_active_ingredient`, 
   `hd_active_ingredient_ext_id`, `hd_type_ext_id`, `hd_medication`, `hd_medication_active_ingredient`, 
   `hd_therapeutic_class`, and `hd_regulatory_category`. This schema provides a structured representation of 
   active ingredients, their external identifiers and types, medications, therapeutic classes, and regulatory categories.
   - healdb_complete.ttl: Complete RDF schema structure generated from the full HealDB DDLs (no data instantiation).

## Contributing
Contributions are welcome! To contribute:

- Fork this repository.
- Create a feature branch.
- Submit a pull request.
## License
This project is Open Source. 

## Contact
For questions or feedback, contact:

- Developer: Márcia Jacobina Andrade S. Martins
- Email: m905106@dac.unicamp.br

