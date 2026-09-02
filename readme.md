# HealDB Project

## **Overview**

HealDB is a comprehensive project designed to manage, analyze, and
interoperate data related to medications, drug leaflets, active
ingredients, diseases, symptoms, drug interactions, and food
interactions. This project includes functionalities for webcrawler,
repositories management, data extraction, translation, and
interoperability, with a focus on integrating multiple data sources.

------------------------------------------------------------------------

## **Project Structure**

``` plaintext
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
    │   │   │       └── similar
    │   │   ├── Arquivo_sintomas.csv
    │   │   ├── CID-10-CAPITULOS.csv
    │   │   ├── CID-10-CATEGORIAS.csv
    │   │   ├── CID-10-GRUPOS.csv
    │   │   ├── CID-10-SUBCATEGORIAS.csv
    │   │   ├── consulta_medicamento_anvisa.csv
    │   │   ├── DADOS_ABERTOS_MEDICAMENTOS.csv
    │   │   ├── drugbank_file.xml
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
    │   │   │   └── ddls_summary.xlsx
    │   │   ├── icd_eng
    │   │   │   ├── blocks.txt
    │   │   │   ├── categories.txt
    │   │   │   └── chapters.txt
    │   │   └── ontologies
    │   │       ├── ATC.ttl
    │   │       ├── chebi.owl
    │   │       ├── healdb_mini.ttl
    │   │       └── _attempts
    │   │           ├── pc_cooccurrence_chemical_and_disease_000001.ttl
    │   │           ├── pc_cooccurrence_chemical_and_disease_000002.ttl
    │   │           ├── pc_cooccurrence_chemical_and_disease_000003.ttl
    │   │           └── pc_disease.ttl
    │   └── output
    │       ├── downloadBulas
    │       ├── translation
    │       │   └── output_active_ing_translate_meta.csv
    │       ├── interoperability
    │       │   ├── _attempts
    │       │   │   ├── iucn_conservation_dcb_r.json
    │       │   │   ├── iucn_conservation_healdb_r.json
    │       │   │   ├── pubchem_diseases_labels.csv
    │       │   │   ├── pubchem_mesh_disease_healdb.csv
    │       │   │   └── pubchem_mesh_ids_healdb.csv
    │       │   ├── atc
    │       │   │   ├── atc_attributes_healdb.csv
    │       │   │   └── atc_attributes_theraphealdb.csv
    │       │   ├── chebi
    │       │   │   ├── chebi_attributes_healdb.csv
    │       │   │   └── chebi_attributes_healdb_json.json
    │       │   ├── clinical_trials
    │       │   │   ├── clinical_trials_healdb.csv
    │       │   │   └── clinical_trials_healdb.json
    │       │   ├── iucn
    │       │   │   ├── iucn_conservation_dcb.json
    │       │   │   └── iucn_conservation_healdb.json
    │       │   ├── pubchem
    │       │   │   └── pubchem_reference_healdb.json
    │       │   └── rxnorm
    │       │       └── rxnorm_enrichment_healdb.json
    │       └── rdf_schema
    │           ├── healdb_complete.ttl
    │           └── healdb_mini.ttl
    ├── doc
    ├── logs
    ├── notebooks
    │   ├── exploracao_healdb_completa.ipynb
    │   └── exploracao_healdb_completa.html
    ├── src
    │   ├── rdf_schema
    │   │   ├── __init__.py
    │   │   ├── main_rdf_schema.py
    │   │   ├── create_healdb_rdf_schema.py
    │   │   └── create_mini_healdb_rdf_schema.py
    │   ├── interoperability
    │   │   ├── __init__.py
    │   │   ├── main_interoperability.py
    │   │   ├── linking
    │   │   │   ├── __init__.py
    │   │   │   ├── insert_external_id.py
    │   │   │   ├── fill_missing_external_ids.py
    │   │   │   ├── import_dcb_data.py
    │   │   │   ├── link_cas_to_active_ing.py
    │   │   │   ├── link_drugbank_to_active_ing.py
    │   │   │   ├── link_kegg_related_ids_to_active_ing.py
    │   │   │   ├── link_rxcui_related_ids_to_active_ing.py
    │   │   │   ├── link_rxcui_to_active_ing.py
    │   │   │   ├── link_wikidata_ids_to_wrk_table.py
    │   │   │   ├── validate_wikidata_chebi.py
    │   │   │   ├── validate_wikidata_pubchem.py
    │   │   │   └── populate_external_ids_types.py
    │   │   └── usecases
    │   │       ├── __init__.py
    │   │       ├── _attempts
    │   │       │   ├── iucn_export_conservation_status_r.r
    │   │       │   ├── pubchem_disease_mesh_query.txt
    │   │       │   ├── pubchem_disease_query.txt
    │   │       │   └── pubchem_mesh_ids_query.txt
    │   │       ├── atc_attributes_query.txt
    │   │       ├── atc_attributes_theraphealdb_query.txt
    │   │       ├── chebi_attributes_query.txt
    │   │       ├── clinical_trials_export.py
    │   │       ├── iucn_export_conservation_status.py
    │   │       ├── pubchem_export_references.py
    │   │       └── rxnorm_export_enriched_ingredients.py
    │   ├── nlp_extraction
    │   │   ├── __init__.py
    │   │   ├── main_nlp_extraction.py
    │   │   ├── extract_leaflet_sections.py
    │   │   ├── extract_diseases_from_indications.py
    │   │   ├── link_medications_with_diseases.py
    │   │   ├── process_disease_data_json.py
    │   │   └── translate_leaflet_section.py
    │   ├── repositories
    │   │   ├── __init__.py
    │   │   ├── main_repository.py
    │   │   ├── create_activeingr_repository.py
    │   │   ├── create_diseases_repository.py
    │   │   ├── create_drugbank_repository.py
    │   │   ├── create_leaflets_repository.py
    │   │   ├── create_medications_repository.py
    │   │   ├── create_symptoms_repository.py
    │   │   └── drugbank_inserts.py
    │   ├── translation
    │   │   ├── __init__.py
    │   │   ├── main_translation.py
    │   │   ├── import_translated_active_ingredients_meta.py
    │   │   ├── translate_active_ingredients.py
    │   │   ├── translate_active_ingredients_meta.ipynb
    │   │   ├── translate_disease_descriptions.py
    │   │   ├── translate_drug_interactions.py
    │   │   ├── translate_food_interactions.py
    │   │   └── validate_translation_and_link_active_ing.py
    │   └── webcrawler
    │       ├── __init__.py
    │       ├── main_webcrawler.py
    │       └── webcrawler_leaflet.py
    ├── tests
    ├── requirements.txt
    ├── config.py
    ├── db_utils.py
    └── main.py
```

## Key Features

1.  Data Management
    -   Input Data: Includes CSV files, XML files, and directories for
        storing electronic leaflets.
    -   Output Data: Stores JSON and CSV files generated during analysis
        and interoperability.
2.  Web Crawler: Automates data extraction from the ANVISA Electronic
    Leaflet System.
3.  Repository Management: Automates the creation and population of
    repositories for HealDB.
4.  Translation: Enables translation of data for interoperability.
5.  NLP Extraction: Uses Natural Language Processing to extract
    diseases, symptoms, leaflets, interactions, and more.
6.  Interoperability:
    -   Linking: Associates active ingredients with standardized
        external identifiers (e.g., RxCUI, CAS, DRUGBANK, KEGG, PubChem,
        Wikidata).
    -   Use Cases: Demonstrates how external identifiers can be used to
        extract insights from biomedical ontologies and data sources
        (e.g., ChEBI, IUCN, PubChem, ATC, RxNorm, ClinicalTrials.gov).

## Exploratory Analysis Notebook

-   **`exploracao_healdb_completa.ipynb`**
    -   **Purpose**: Interactive notebook for exploratory analysis of
        HealDB data. Provides an overview of the database structure and
        content through visualizations and key questions.
    -   **Key Features**:
        -   Presents visual summaries (e.g., bar charts, pizzas,
            dispersion) using `matplotlib`, `pandas`, and `seaborn`,
            based on HealDB data.
        -   Answers analytical questions about medications, active
            ingredients, and diseases.
        -   Helps verify relationships between medications, diseases,
            and interactions.
        -   Summarizes key findings from the analyses.
    -   **Questions addressed in the notebook include**:
        -   What are the main regulatory category of these medications?
        -   How are medications distributed across therapeutic classes?
        -   Which medications are closest to expiration?
        -   Which companies supply the most medications?
        -   What are the TOP 10 most commonly used active ingredients?
        -   Which active ingredients are present in the largest number
            of medications, in decreasing order of occurrence?
        -   Which existing medications contain a certain active
            ingredient?
        -   What are the TOP 15 most frequent disease categories treated
            by the medications?
        -   What are the TOP 15 most frequent disease categories treated
            by the active ingredients?
        -   What are the average scores by ICD category?
        -   For a specific disease, which are the associated medications
            and their scores?
        -   What is the distribution of the association score between
            the medication and the disease?
        -   Are there drug interactions between two specific active
            ingredients?
        -   What are the drug interactions of a given medication?
        -   Does a given medication interact with food?
        -   What are the TOP 20 active ingredients with the highest
            number of drug interactions, in decreasing order of
            frequency?

## How to Run

### Requirements

1.  Install Python 3.9+.
2.  Install required libraries from requirements.txt:

```bash
pip install -r requirements.txt
```

### Running the Project

-   Configure the config.py file with your environment settings.

-   Run the main script:

    ```bash
    python main.py
    ```

## Inputs

The `data/input` folder contains all input data files required for
processing, translation, and interoperability tasks.
Key components include:

-   **CID-10 files**: International Classification of Diseases
    (`CID-10-CAPITULOS.csv`, `CID-10-CATEGORIAS.csv`,
    `CID-10-GRUPOS.csv`, `CID-10-SUBCATEGORIAS.csv`).
-   `DADOS_ABERTOS_MEDICAMENTOS.csv`: Publicly available data on
    medications.
-   `consulta_medicamento_anvisa.csv`: Comprehensive list of medications
    and their attributes obtained from ANVISA.
-   `drugbank_file.xml`: DrugBank XML file containing structured
    biomedical data.
-   `Arquivo_sintomas.csv`: List of symptoms from the Bireme/MeSH
    vocabulary.
-   `input_active_ing_translate_meta`: Dataset of active ingredients in
    Portuguese, used for translation with Meta's SeamlessM4T model.
-   `lista_dcb.xlsx`: List of Brazilian Common Denominations (DCB).

### Subfolders within `data/input`

-   **`bulas/`**: Drug leaflet files organized by regulatory category
    (e.g., generic, herbal medicine).
-   **`ddls/`**: SQL DDL files representing HealDB table structures,
    used to generate the RDF schema.
-   **`icd_eng/`**: ICD English files extracted from WHO, used as
    reference for the English descriptions of groups, categories and
    chapters. (`blocks.txt`, `categories.txt`, `chapters.txt`)
-   **`ontologies/`**: External biomedical ontologies used in
    interoperability (`chebi.owl`, `ATC.ttl`) and the HealDB mini RDF
    representation (`healdb_mini.ttl`). Historical PubChem RDF files
    used in an exploratory implementation are isolated under
    `ontologies/_attempts/`.

These files serve as the foundational datasets for web crawling,
creation of repositories, natural language processing, translations, and
interoperability tasks.

## Usage

## **Webcrawler**

Scripts for web scraping and data extraction from ANVISA's Electronic Leaflet System.

-   **`main_webcrawler.py`**
    -   Purpose: Automates web scraping to collect leaflets data.
    -   **Usage:**

    ```bash
    python src/webcrawler/main_webcrawler.py
    ```
-   **`webcrawler_leaflet.py`**
    -   Purpose: Automates the process of collecting and organizing
        leaflets from the ANVISA Electronic Leaflet System.
    -   Key Processes:
        -   Utilizes Selenium to navigate and interact with the website,
            automating the retrieval of data for all leaflet categories.
        -   Uses BeautifulSoup to scrape medication data from the
            website's tables and store it in a structured format.
        -   Downloads PDF files of the leaflets and saves them in
            category-specific folders.
        -   Generates an Excel file for each category, containing a
            complete list of medications and their associated PDF file
            paths.
        -   Provides the foundation for subsequent data integration into
            HealDB via the repository scripts.

## **Repositories**

Scripts for creating and populating HealDB repositories.

-   **`main_repository.py`**
    -   Purpose: Orchestrates repository creation.
    -   **Usage:**

    ```bash
    python src/repositories/main_repository.py
    ```
-   **`create_activeingr_repository.py`**
    -   Purpose: Generates the repository for active ingredients.
    -   Key Processes:
        -   Splits active ingredients in the medication field using the
            "+" separator.
        -   Stores results in a temporary table, associating medications
            with normalized active ingredients.
        -   Adds active ingredients to the active_ingredient repository.
        -   Links medications to their active ingredients.
-   **`create_diseases_repository.py`**
    -   Purpose: Constructs a repository of diseases using ICD
        (International Classification of Diseases) data as input.
    -   Key Processes:
        -   Extracts data from ICD-related files (groups, categories,
            and subcategories).
        -   Populates the disease repository by organizing and linking
            the ICD information hierarchically.
        -   Enables integration of standardized disease data into HealDB
            for interoperability and advanced queries.
-   **`create_medications_repository.py`**
    -   Purpose: Builds a structured medication repository using ANVISA
        data.
    -   Key Processes:
        -   Cleans existing data and resets tables.
        -   Reads and processes data from a ANVISA CSV file about
            medications, filtering canceled medications.
        -   Populates related tables (companies, categories, classes).
        -   Normalizes active ingredients and ensures consistency.
-   **`create_symptoms_repository.py`**
    -   Purpose: Generates a structured repository of symptoms using
        hierarchical data from the BIREME/MeSH controlled vocabulary.
    -   Key Processes:
        -   Clears and resets data in both temporary and permanent
            symptom tables to ensure consistency.
        -   Imports and processes a CSV file (extracted from BIREME/MeSH
            repository) containing symptoms data into a temporary table.
        -   Transforms symptoms into a hierarchical format, creating
            parent-child relationships, and stores them in the symptom
            repository.
-   **`create_drugbank_repository.py`**
    -   Purpose: Processes the DrugBank XML file and integrates its data
        into HealDB for comprehensive drug management.
    -   Key Processes:
        -   Extracts information about drugs, including identifiers,
            names, descriptions, and usage indications.
        -   Captures details on drug-food interactions to identify
            potential effects of food on drug efficacy or safety.
        -   Maps synonyms for each drug to enhance data reachability and
            consistency.
        -   Organizes product ingredients for accurate representation of
            drug components.
        -   Processes drug-drug interactions to establish relationships
            between related drugs.
-   **`create_leaflets_repository.py`**
    -   Purpose: Populates the repository with leaflet data extracted
        from PDF files categorized by ANVISA leaflet types.
    -   Key Processes:
        -   Reads and processes Excel files listing leaflets for each
            category.
        -   Deduplicates data to retain the most recent versions.
        -   Extracts text from PDFs using PyMuPDF for text-based files
            and Pytesseract for image-based files.
        -   Stores extracted content and metadata in the
            medication_drug_leaflet table.
        -   Handles additional OCR processing for leaflets identified as
            images when needed.

## **Translation**

Scripts for translating data and validating translations.

-   **`main_translation.py`**
    -   Purpose: Executes all translation-related processes.
    -   **Usage:**

    ```bash
    python src/translation/main_translation.py
    ```
-   **`translate_active_ingredients.py`**
    -   Purpose: Translates active ingredients from Portuguese to
        English using the OpenAI API and updates the HealDB database
        with the translations.
    -   Key Processes:
        -   Copies active ingredients into a translation table for
            processing.
        -   Translates active ingredients using the "gpt-4" model
        -   Updates the translation table with the initial English
            translation, while also including fields for manual review
            and final adjustments.
-   **`translate_active_ingredients_meta.ipynb`**
    -   Purpose: Uses the SeamlessMT4 model from META to translate
        active ingredients into English via Google Colab.
    -   Key Processes:
        -   Exports active ingredients to a CSV file.
        -   Processes the data in a Jupyter Notebook.
        -   Translates using SeamlessMT4 and stores results in a
            DataFrame.
        -   Exports the translated DataFrame to a CSV file.
    -   Usage: Run the Jupyter Notebook in Google Colab for translation
        processing.
-   **`import_translated_active_ingredients_meta.py`**
    -   Purpose: Imports and validates SeamlessMT4 translations of
        active ingredients against DrugBank data.
    -   Key Processes:
        -   Imports translations from a CSV file.
        -   Compares translations to DrugBank entries.
        -   Computes the total matches between the translated active
            ingredients and DrugBank entries.
-   **`translate_drug_interactions.py`**
    -   Purpose: Translates drug interactions from English to Portuguese
        using the OpenAI API (GPT-3.5) and integrates the translated
        data into HealDB.
    -   Key Processes:
        -   Maps interactions to active ingredients in HealDB.
        -   Replaces drug names with placeholders (XXX/YYY) for
            efficient translation.
        -   Translates unique descriptions and substitutes placeholders
            with Portuguese active ingredient names.
        -   Enriches HealDB with translated drug interaction data.
-   **`translate_food_interactions.py`**
    -   Purpose: Translates food interactions from English to Portuguese
        using the OpenAI API (GPT-3.5) and integrates the translated
        data into HealDB.
    -   Key Processes:
        -   Maps interactions to active ingredients in HealDB.
        -   Replaces drug names with a placeholder (XXX) for efficient
            translation.
        -   Translates unique descriptions and substitutes the
            placeholder with Portuguese active ingredient names.
        -   Enriches HealDB with translated food interaction data.
-   **`validate_translation_and_link_active_ing.py`**
    -   Purpose: Validates translations of active ingredients by
        comparing them to DrugBank data and links them to related drugs.
    -   Key Processes:
        -   Compares automatically translated terms (GPT-4) with
            DrugBank tables for drugs, synonyms, and product
            ingredients.
        -   Validates manually translated terms in the same tables.
        -   Stores the final translation (manual if available, otherwise
            automatic).
        -   Links active ingredients in Portuguese to corresponding
            DrugBank drugs in English, enabling the capture of related
            drug interactions.
-   **`translate_disease_descriptions.py`**
    -   Purpose: Updates the English descriptions of ICD-10 disease
        groups, categories, and subcategories in HealDB using WHO
        reference files and GPT-4 translation when necessary. This
        supports multilingual access and improves international
        interoperability.
    -   Key Processes:
        -   Loads ICD-10 English descriptions from official WHO CSV
            files (blocks.txt, categories.txt) and populates
            `ds_group_eng`, `ds_cat_eng`, and `ds_subcat_eng`.
        -   For ICDs not found in the reference files, translates the
            Portuguese descriptions into English using the OpenAI GPT-4
            API.
        -   For subcategory translations, more context are provided,
            passing to the API the category translations when available.
        -   The translations are stored in the HealDB tables:
            `hd_icd_group`, `hd_icd_category`, and `hd_icd_subcategory`.

## **NLP Extraction**

Scripts for extracting data using NLP techniques.

-   **`main_nlp_extraction.py`**
    -   Purpose: Executes NLP workflows for leaflet analysis.

    -   **Usage:**

        ```bash
           python src/nlp_extraction/main_nlp_extraction.py
        ```
-   **`extract_leaflet_sections.py`**
    -   Purpose: Processes drug leaflets to extract specific sections,
        such as indications and precautions, and updates the leaflet
        repository.
    -   Key Processes:
        -   Reads and processes drug leaflets from the database.
        -   Extracts sections like "Para que este medicamento é
            indicado?" and "O que devo saber antes de usar esse
            medicamento?" using regex.
        -   Stores the extracted data in temporary tables.
        -   Updates the leaflet repository with the processed
            information.
-   **`translate_leaflet_section.py`**
    -   Purpose: Translates the indication section from drug leaflets
        into English, enabling the use of medical text analysis tools
        for symptom and disease extraction.
    -   Key Processes:
        -   Copies indication texts into a translation table.
        -   Translates using OpenAI's GPT-3.5 API.
        -   Resolves translation issues and updates missing or
            problematic entries.
        -   Stores final English translations in the leaflet repository.
-   **`extract_diseases_from_indications.py`**
    -   Purpose: Extracts candidate diseases and symptoms from English
        translated drug-leaflet indication text using Amazon Comprehend
        Medical (ICD-10-CM inference).
    -   Key Processes:
        -   Reads translated indication text from the database.
        -   Optionally normalizes the input text (e.g., replaces the
            medication name with a placeholder) to reduce noise.
        -   Sends texts to Amazon Comprehend Medical for ICD code
            extraction using the `infer_icd10_cm` endpoint.
        -   Stores the raw JSON response (and the submitted text) in the
            database for traceability and later processing.
-   **`process_disease_data_json.py`**
    -   Purpose: Transforms the stored Amazon Comprehend Medical JSON
        responses into structured relational records for analysis and
        downstream linking.
    -   Key Processes:
        -   Reads API responses stored in the database.
        -   Converts JSON strings into dictionaries/objects.
        -   Extracts entity-level metadata (e.g., entity text, offsets,
            category/type, entity score).
        -   Extracts ICD-10-CM concepts (e.g., `code`, `description`,
            `score`) associated with each entity.
        -   Extracts entity traits (e.g., `DIAGNOSIS`, `SYMPTOM`,
            `NEGATION`) and stores them separately.
        -   Saves the extracted content into structured tables to
            support auditing and linking logic.
-   **`link_medications_with_diseases.py`**
    -   Purpose: Links medications to diseases (ICD) by applying a
        transparent cutoff policy over the extracted ICD-10-CM
        candidates and mapping them to HealDB's ICD tables.
    -   Key Processes:
        -   Uses the structured entity/ICD/trait tables as input.
        -   Keeps only clinically relevant entities (e.g., `DX_NAME`)
            and excludes negated mentions (`NEGATION` trait).
        -   Applies a minimum entity confidence threshold (default:
            Entity.Score ≥ 0.70).
        -   Selects the top ICD-10-CM concept per entity (highest ICD
            score).
        -   Maps ICD-10-CM to HealDB ICD tables using:
            -   Exact subcategory match when available, and
            -   A fallback to the 3-character category prefix when the
                subcategory is missing.
        -   Classifies ICD scores into confidence level (default: MEDIUM
            ≥ 0.30, HIGH ≥ 0.60) and keeps only MEDIUM/HIGH links.
        -   Writes an audit table with cutoff flags and mapping
            outcomes, plus the final deduplicated medication--disease
            associations for analysis and reporting.

## **Interoperability**

Scripts for integrating data from external sources and linking them to
active ingredients in HealDB. This enables interoperability with other
health data sources, ontologies, and biomedical databases.

-   **`main_interoperability.py`**

    -   Purpose: Central script for orchestrating all interoperability
        processes.

    -   **Usage:**

        ```bash
        python src/interoperability/main_interoperability.py
        ```

        ### Linking

-   **`import_dcb_data.py`**

    -   Purpose: Imports and processes DCB (Denominações Comuns
        Brasileiras) data into the HealDB database.
    -   Key Processes:
        -   Loads DCB data from an Excel file.
        -   Maps and inserts DCB classifications and descriptions.
        -   Populates the DCB list with details such as DCB numbers,
            names, CAS numbers, and classification history.

-   **`populate_external_ids_types.py`**

    -   Purpose: Creates and populates a static table with the possible
        external identifiers types.
    -   Key Processes:
        -   Defines external ID system (RXNORM, KEGG, DRUGBANK, PUBCHEM,
            SNOMEDCT and others).
        -   Inserts this data into the external identifier type table
            for consistency in linking.

-   **`insert_external_id.py`**

    -   Purpose: Inserts external identifiers (e.g., RXCUI, KEGG,
        PubChem) associated with active ingredients into the
        `hd_active_ingredient_ext_id` table in the HealDB database,
        ensuring referential integrity and avoiding duplicates.
    -   Key Processes:
        -   Validates whether the external ID type (`tp_ext_id`) exists
            in the `hd_type_ext_id` table before proceeding.
        -   Inserts the external ID into the
            `hd_active_ingredient_ext_id` association table only if a
            matching record for the given active ingredient does not
            already exist, ensuring data integrity and avoiding
            duplication.

-   **`link_cas_to_active_ing.py`**

    -   Purpose: Links CAS numbers to active ingredients in HealDB,
        using the official Brazilian DCB list as the primary source.
    -   Key Processes:
        -   Clears the `hd_active_ingredient_ext_id` table to prepare
            for new CAS mappings.
        -   Matches active ingredient names with DCB entries using
            normalized string comparison.
        -   Filters out invalid or reference-only CAS numbers (e.g.,
            starting with "\[Ref").
        -   Skips duplicates by checking for existing CAS associations.
        -   Inserts valid CAS mappings into the external ID table
            identifying the source as "DCB".

-   **`link_drugbank_to_active_ing.py`**

    -   Purpose: Refreshes and stores DrugBank identifiers for active
        ingredients in HealDB by persisting the results of a previous
        harmonization step (name translation/matching), enabling
        interoperability and DrugBank-based analyses.
    -   Key Processes:
        -   Removes existing rows for `tp_ext_id = 'DRUGBANK_ID'` from
            `hd_active_ingredient_ext_id` to allow clean re-runs.
        -   Inserts DrugBank IDs into hd_active_ingredient_ext_id with:
            -   `tp_ext_id = 'DRUGBANK_ID'`
            -   `fl_origin_ext_id = 'DRUGBANK'`
        -   Builds the mapping using a join between:
            -   `hd_priv_active_ingredient_drug` (active ingredient
                \<-\> drug mapping from the harmonization pipeline), and
            -   `db_drug` (DrugBank drug table containing
                `id_drugbank`).
        -   Avoids duplicate inserts by checking if the active
            ingredient already has a `DRUGBANK_ID` registered
            (`NOT EXISTS`).
        -   Commits changes and prints status messages for traceability
            during execution.

-   **`link_rxcui_to_active_ing.py`**

    -   Purpose: Links RxNorm Concept Unique Identifiers (RxCUI) to
        active ingredients in HealDB using the RxNorm API.
    -   Key Processes:
        -   Retrieves active ingredients with English names from the
            translation table.
        -   Queries the RxNorm API to obtain the corresponding RxCUI for
            each name.
        -   Inserts valid RxCUI mappings into the external ID table,
            marking the source as "RXNORM".

-   **`link_rxcui_related_ids_to_active_ing.py`**

    -   Purpose: Links RxNorm-related external identifiers (e.g., SNOMED
        CT, ATC, UNII) to active ingredients in HealDB by querying the
        RxNorm API for each RxCUI linked to active ingredient.
    -   Key Processes:
        -   Retrieves all active ingredients from the database that
            already have a mapped RxCUI.
        -   Queries the RxNorm API for each RxCUI to fetch related
            identifiers (e.g., SNOMED CT codes, ATC classifications).
        -   Processes multiple values per identifier (e.g., several ATC
            codes for one RxCUI).
        -   Inserts valid related identifiers into the external ID
            table, marking "RXNORM" as the source.

-   **`link_wikidata_ids_to_wrk_table.py`**

    -   Purpose: Retrieves external identifiers from Wikidata using
        RxCUI as input and stores the results in a working table.
    -   Key Processes:
        -   Fetches all RxCUI values linked to active ingredients in
            HealDB.
        -   Queries the Wikidata SPARQL endpoint in batches to retrieve
            identifiers like CAS, DrugBank, PubChem, ChEBI, SNOMED CT,
            ATC, UNII, and KEGG.
        -   Inserts the results into the working table
            `hd_wrk_wikidata_ext_id`, including the Wikidata entity URL.

-   **`validate_wikidata_chebi.py`**

    -   Purpose: Validates ChEBI identifiers retrieved from Wikidata and
        flags whether each identifier represents the preferred chemical
        entity for the active ingredient.
    -   Key Processes:
        -   Resets `fl_preferred` for `CHEBI` records in
            `hd_wrk_wikidata_ext_id`.
        -   Queries the ChEBI API for each ChEBI identifier stored in
            the Wikidata working table.
        -   Inspects incoming and outgoing ontology relations.
        -   Marks an identifier as non-preferred when it participates in
            `is tautomer of`, `is conjugate acid of`, or
            `is conjugate base of` relations; otherwise marks it as
            preferred.
        -   Stores the result in `fl_preferred` (`Y` or `N`) for the
            corresponding RxCUI and ChEBI ID.

-   **`validate_wikidata_pubchem.py`**

    -   Purpose: Validates PubChem Compound IDs retrieved from Wikidata
        by checking whether PubChem associates the compound with the
        same RxCUI used by HealDB.
    -   Key Processes:
        -   Resets `fl_preferred` for `PUBCHEM_CID` records in
            `hd_wrk_wikidata_ext_id`.
        -   Queries the PubChem PUG View API for each PubChem CID.
        -   Recursively locates and extracts the `RXCUI` section from
            the returned JSON.
        -   Compares the PubChem RxCUI with the HealDB RxCUI.
        -   Stores `Y` in `fl_preferred` when the values match and `N`
            when they do not match or no RxCUI is returned.

-   **`link_kegg_related_ids_to_active_ing`**

    -   Purpose: Links KEGG Compound IDs (from Wikidata) to active
        ingredients in HealDB and uses them to retrieve PubChem and
        ChEBI identifiers (via KEGG API) and associate them with the
        same active ingredients.
    -   Key Processes:
        -   Clears existing KEGG-related identifiers from the external
            ID table to avoid duplication.
        -   Retrieves KEGG Compound IDs previously linked via Wikidata
            in the working table and maps them to active ingredients.
        -   Queries the KEGG API to extract related PubChem CIDs and the
            primary ChEBI ID.
        -   Inserts the KEGG ID (source: Wikidata) into the external ID
            table.
        -   Inserts all associated PubChem CIDs and the first ChEBI ID
            found (source: KEGG) into the external ID table.

-   **`fill_missing_external_ids.py`**

    -   Purpose: Fills in missing external identifiers (CAS, ATC,
        SNOMEDCT, UNII_CODE, CHEBI, PUBCHEM_CID) for active ingredients
        in HealDB by using RxCUI matches from the Wikidata working
        table.
    -   Key Processes:
        -   Identifies active ingredients that have a mapped RxCUI but
            are missing specific external IDs.
        -   Searches the `hd_wrk_wikidata_ext_id` working table for ATC,
            SNOMEDCT, UNII_CODE, CHEBI and PUBCHEM_CID codes linked to
            those RxCUIs.
        -   Inserts only identifiers not already present in the
            hd_active_ingredient_ext_id table.
        -   Chooses one CAS number per active ingredient when there are
            multiple options.

### Use Cases

Each use case demonstrates a specific integration of HealDB with
external biomedical or environmental data sources. Results for these use
cases are available in the `Output` section.

-   **`chebi_attributes_query.txt`**
    -   Purpose: Demonstrates semantic interoperability between HealDB
        and the ChEBI ontology through SPARQL queries executed in Apache
        Jena Fuseki.
    -   Key Processes:
        -   Uses the persistent Fuseki dataset `healdb_full`, with
            separate named graphs for HealDB and ChEBI.
        -   Links HealDB active ingredients to ChEBI entities through
            external ChEBI identifiers represented with `owl:sameAs`.
        -   Retrieves chemical descriptors using the current ChemROF
            vocabulary (`https://w3id.org/chemrof/`).
        -   Retrieves molecular formula, mass, monoisotopic mass,
            SMILES, InChI, and InChIKey.
        -   Uses `SELECT DISTINCT` to avoid duplicate associations in
            the result.
-   **`pubchem_export_references.py`**
    -   Purpose: Retrieves up to three scientific publications
        associated with antidepressant active ingredients in HealDB by
        using their PubChem CIDs.
    -   Key Processes:
        -   Selects active ingredients classified as antidepressants
            that have a `PUBCHEM_CID`.
        -   Uses the PubChemRDF REST API to retrieve PubChem Reference
            resources associated with each compound through
            `vocab:discussesAsDerivedByTextMining`.
        -   Resolves each PubChem Reference to a PMID through
            `dcterms:identifier`.
        -   Uses NCBI ESummary to retrieve publication metadata such as
            title, journal, and publication date.
        -   Exports up to three publications per active ingredient to
            `pubchem_reference_healdb.json`.
-   **`iucn_export_conservation_status.py`**
    -   Purpose: Retrieves conservation status, threats, and geographic
        distribution of plant-based ingredients from the IUCN Red List
        API.
    -   Key Processes:
        -   Filters active ingredients and DCBs classified as
            plant-based (type "PM").
        -   Normalizes scientific names and retrieves assessment data
            using IUCN API.
        -   Extracts category, threats, location, extinction risk, and
            scope of assessments.
-   **`rxnorm_export_enriched_ingredients.py`**
    -   Purpose: Enriches HealDB active ingredients with RxNorm clinical
        and pharmacological information.
    -   Key Processes:
        -   Selects active ingredients with RxCUI.
        -   Retrieves preferred names, TTY, detailed status (including
            current activity and release dates), synonyms, clinical
            presentations (SCD), and branded presentations (SBD, BPCK,
            SBDF, SBDC).
        -   Structures and exports data to JSON.
-   **`atc_attributes_query.txt` and
    `atc_attributes_theraphealdb_query.txt`**
    -   Purpose: Identify ATC therapeutic classes for each active
        ingredient based on ATC codes, enabling semantic comparisons
        between ATC and HealDB classifications using SPARQL query.
    -   Key Processes:
        -   `atc_attributes_query.txt`: Extracts therapeutic class, UMLS
            identifiers, preferred/alternative labels from ATC ontology.
        -   `atc_attributes_theraphealdb_query.txt`: Adds HealDB's
            therapeutic class linked to medications, allowing
            comparative analysis.
-   **`clinical_trials_export.py`**
    -   Purpose: Links HealDB active ingredients to clinical trials
        registered on ClinicalTrials.gov.
    -   Key Processes:
        -   Queries the ClinicalTrials.gov API v2 using the English name
            of each active ingredient.
        -   Retrieves NCT ID, study title, conditions, interventions,
            and outcome measures.
        -   Stores the retrieved data in the `hd_wrk_clinical_trials`
            working table while avoiding duplicate active ingredient/NCT
            associations.
        -   Exports the results to `clinical_trials_healdb.csv` and to
            the nested JSON file `clinical_trials_healdb.json`,
            organized by active ingredient.

### Use Case Attempts (Experimental)

These exploratory implementations were tested but were not incorporated
into the final HealDB interoperability use cases. They are retained in
`_attempts` folders for traceability and reproducibility.

-   **PubChem RDF disease/MeSH experiment** ---
    `pubchem_disease_query.txt`, `pubchem_disease_mesh_query.txt`, and
    `pubchem_mesh_ids_query.txt`
    -   **Purpose**: Explore associations between HealDB active
        ingredients and diseases through PubChem RDF co-occurrence data
        and MeSH identifiers.
    -   **Approach**:
        -   PubChem RDF files were loaded into Apache Jena Fuseki during
            the exploratory implementation.
        -   SPARQL queries linked PubChem CIDs to disease resources and
            MeSH identifiers.
        -   The resulting mappings were exported to CSV files under
            `data/output/interoperability/_attempts`.
    -   **Why it was discarded**:
        -   Co-occurrence reflects shared mentions in publications and
            does not establish a therapeutic or causal relationship.
        -   The experiment produced broad and potentially irrelevant
            associations.
        -   Mapping to MeSH did not sufficiently remove this noise.
    -   **Decision**: The disease-oriented experiment was replaced by
        the ClinicalTrials.gov use case, which provides explicit
        relationships between interventions and clinical conditions.
    -   **Traceability**: The PubChem RDF source files used in this
        experiment are retained under `data/input/ontologies/_attempts`.
-   **`iucn_export_conservation_status_r.r`**
    -   **Purpose**: Retrieve conservation status and threats for
        medicinal-plant names using the IUCN Red List API v4 through R.
    -   **Approach**:
        -   DCB names classified as medicinal plants (`PM`) were
            queried.
        -   Results included conservation category, extinction
            information, geographic scope, locations, and threats.
        -   The R implementation was created while authentication issues
            were being investigated in Python.
    -   **Decision**: After the Python integration was established, the
        R version was retained in `_attempts` as a historical
        implementation.

## **RDF Schema**

Scripts that convert the relational structure of HealDB --- based on the
DDLs of its database tables --- into an RDF schema saved in Turtle
(.ttl) format.

-   **`main_rdf_schema.py`**
    -   Purpose: Central script for orchestrating the RDF schema
        generation pipeline.

    -   **Usage:**

        ```bash
        python src/rdf_schema/main_rdf_schema.py
        ```
-   **`create_mini_healdb_rdf_schema.py`**
    -   Purpose: Generates a simplified RDF schema (`healdb_mini.ttl`)
        with classes, properties, and instances based on selected HealDB
        tables, focused on semantic integration of active ingredients,
        external identifiers, medications, regulatory categories, and
        therapeutic classes.
    -   Key Processes:
        -   Defines RDF classes and properties (datatype and object) for
            core entities: Active Ingredients, External Identifiers,
            Identifier Types, Medications, Therapeutic Classes, and
            Regulatory Categories.
        -   Extracts data from selected MySQL tables and generates RDF
            triples representing entities and their relationships.
        -   Establishes `owl:sameAs` links for ChEBI and ATC external
            identifiers to support semantic alignment with the
            corresponding ontologies.
        -   Outputs the simplified RDF file (`healdb_mini.ttl`) used in
            SPARQL queries and interoperability scenarios.
-   **`create_healdb_rdf_schema.py`**
    -   Purpose: Converts the SQL DDL definitions of the HealDB
        relational schema into a complete RDF schema in Turtle (.ttl)
        format.
    -   Key Processes:
        -   Reads DDL´s SQL files from the folder defined by
            `PATHS["healdb_ddls"]`.

        -   Parses CREATE TABLE statements to extract columns, data
            types, and foreign keys.

        -   Maps SQL elements to OWL constructs:

            -   Tables → `owl:Class`
            -   Columns → `owl:DatatypeProperty`
            -   Foreign keys → `owl:ObjectProperty`

        -   Automatically generates labels for classes and properties
            based on naming patterns (e.g., id\_ → hasID\_, nm\_ →
            hasName\_).

        -   Saves the resulting RDF schema to `healdb_complete.ttl`,
            without instantiating data, for ontology-based modeling and
            future SPARQL extensions.

        -   **Note:** This script generates only the RDF schema (classes
            and properties), without populating it with data from the
            tables. Future steps may use this structure to instantiate
            individuals.

## **Config**

Ensure `config.py` contains accurate paths and API tokens for the
required resources. Defines file paths, API credentials, and project
settings for managing data inputs, outputs, and integrations. Includes
configurations for:

-   Input/output directories (e.g., drug leaflets, ICD files, DrugBank
    XML, RDF Schema).
-   API credentials and endpoints for OpenAI, AWS, IUCN, RxNorm,
    PubChem, and ClinicalTrials.gov.
-   Web scraping settings, including browser preferences and download
    directories.
-   Category mappings for leaflet types and conservation statuses.
-   External ID URLs for health-related data sources (e.g., RxNorm,
    KEGG, Wikidata).
-   API endpoints used in interoperability use cases to fetch biomedical
    and environmental data.
-   Namespaces used in RDF schema generation and external ontologies.
-   File and folder paths for ontology inputs (e.g., `chebi.owl`,
    `atc.ttl`) and RDF schema outputs.
-   Definition of default models and headers for OpenAI requests (e.g.,
    model version, content type).

Ensure all values are adjusted to match your environment and secure
sensitive information like API keys.

## Output

1.  **Drug leaflets from Anvisa** (data/output/downloadBulas):
    -   Folder containing the downloaded drug leaflets from the Anvisa
        Portal.
2.  **Interoperability Data** (`data/output/interoperability`):
    -   Output folder for the use cases involving external data
        integration. Includes results from:

        -   **ChEBI**: Chemical attributes of active ingredients
            retrieved from the ChEBI ontology through SPARQL, using
            ChemROF properties for the current chemical descriptors.
            -   `chebi_attributes_healdb.csv`: Table with chemical
                attributes for each active ingredient including
                molecular formula, mass, monoisotopic mass, SMILES,
                InChI, and InChIKey.
            -   `chebi_attributes_healdb_json.json`: Same content in
                JSON format for programmatic consumption and
                interoperability use cases.
        -   **PubChem**: Scientific publications associated with active
            ingredients, retrieved by linking PubChem CIDs to PubChem
            Reference resources through the PubChemRDF REST API and
            resolving their PMIDs; publication metadata is retrieved
            with NCBI ESummary.
            -   `pubchem_reference_healdb.json`: Contains up to three
                PubMed publications per active ingredient, including
                title, journal, publication date, and PMID.
        -   **IUCN**: Conservation status, geographic distribution, and
            threats related to medicinal plants.
            -   `iucn_conservation_healdb.json`: Enrichment of
                plant-based active ingredients in HealDB with IUCN
                conservation data.
            -   `iucn_conservation_dcb.json`: Similar data but based on
                the Brazilian Common Denominations (DCB) list.
        -   **RxNorm**: Clinical and pharmacological data retrieved
            using RxCUI identifiers.
            -   `rxnorm_enrichment_healdb.json`: Includes standardized
                names, RxNorm types (TTY), clinical and branded drug
                presentations, synonyms, and status information.
        -   **ATC**: Therapeutic class attributes and UMLS identifiers
            associated with active ingredients.
            -   `atc_attributes_healdb.csv`: Identification of ATC
                therapeutic classes for active ingredients using
                external identifiers.
            -   `atc_attributes_theraphealdb.csv`: Comparative listing
                showing both ATC and HealDB therapeutic classes for each
                active ingredient, allowing semantic alignment analysis.
        -   **ClinicalTrials.gov**: Clinical studies involving active
            ingredients from HealDB, retrieved via the
            ClinicalTrials.gov v2 API.
            -   `clinical_trials_healdb.csv`: Structured table listing
                clinical trials by NCT ID, title, conditions,
                interventions, and outcomes per active ingredient.
            -   `clinical_trials_healdb.json`: Same data as CSV, but
                formatted by active ingredient for easier programmatic
                use and hierarchical analysis.
3.  **Translation of active ingredients**:
    -   `output_active_ing_translate_meta.csv`: CSV file containing
        active ingredients translated from Portuguese to English using
        Meta's SeamlessM4T model.
4.  **RDF Schema** (`data/output/rdf_schema`):
    -   `healdb_mini.ttl`: Simplified RDF schema including instances
        from HealDB tables `hd_active_ingredient`,
        `hd_active_ingredient_ext_id`, `hd_type_ext_id`,
        `hd_medication`, `hd_medication_active_ingredient`,
        `hd_therapeutic_class`, and `hd_regulatory_category`. Provides a
        minimal and structured representation for semantic integration.
    -   `healdb_complete.ttl`: Full RDF schema with class and property
        definitions based on HealDB's relational schema. It includes
        structural definitions but does not instantiate data.
5.  **Experimental Use Case Outputs**
    (`data/output/interoperability/_attempts`):
    -   Outputs from exploratory use cases that were tested but not
        integrated into HealDB due to quality or strategic
        considerations. These files remain available for future
        reference.
        -   `pubchem_mesh_disease_healdb.csv`: Mapping between active
            ingredients (via PubChem CID) and co-occurring diseases.
        -   `pubchem_mesh_ids_healdb.csv`: Mapping of PubChem diseases
            to MeSH IDs.
        -   `pubchem_diseases_labels.csv`: Disease labels and synonyms
            from PubChem's RDF dataset.
        -   `iucn_conservation_healdb_r.json`: IUCN conservation data
            retrieved via an R script for HealDB active ingredients.
        -   `iucn_conservation_dcb_r.json`: IUCN conservation data
            retrieved via an R script for Brazilian Common Denominations
            (DCB) of type Medicinal Plant, "PM".

## Contributing

Contributions are welcome! To contribute:

-   Fork this repository.
-   Create a feature branch.
-   Submit a pull request.

## License

This project is Open Source.

## Contact

For questions or feedback, contact:

-   Developer: Márcia Jacobina Andrade S. Martins
-   Email: m905106@dac.unicamp.br
