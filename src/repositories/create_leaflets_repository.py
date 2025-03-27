# -*- coding: utf-8 -*-
"""
Created on Sat Nov  15 08:00:20 2024

Author: Márcia Jacobina Andrade Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Populate the repository with drug leaflet data extracted from PDF files, categorized 
# according to ANVISA's leaflet types (e.g., biological, homeopathic, specific, herbal,
# generic, new, advanced therapy, radiopharmaceutical, and similar). 
# he script processes both textual and image-based PDFs, applies OCR when needed, 
# and stores the extracted full-text content for further processing and analysis.

import os
import csv
import io
from datetime import datetime
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd
from config import PATHS, LEAFLET_CATEGORIES
import chardet  # Library for encoding detection

def is_pdf_textual(file_path):
    # Function to check if a PDF contains textual content
    try:
        with fitz.open(file_path) as pdf_document:
            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                if page.get_text().strip():
                    return True
        return False
    except Exception as e:
        print(f"Error processing the PDF: {e}")
        return False

def preprocess_image(img):
    # Function to preprocess an image for OCR
    img = img.convert("L")  # Convert to grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)  # Enhance contrast
    img = img.filter(ImageFilter.BLUR)  # Apply smoothing
    return img

def extract_text_from_image_pdf(pdf_path):
    # Function to extract text from an image-based PDF
    text = ""
    try:
        with fitz.open(pdf_path) as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    image_data = pdf_document.extract_image(xref)
                    image_bytes = Image.open(io.BytesIO(image_data["image"]))
                    img = preprocess_image(image_bytes)
                    text += pytesseract.image_to_string(img, lang='por') + "\n"
    except Exception as e:
        print(f"Error extracting text from image PDF: {e}")
    return text

def extract_text_pdf_no_page_break(pdf_path):
    # Function to extract text from a textual PDF
    try:
        text = ""
        with fitz.open(pdf_path) as pdf_document:
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text += page.get_text("text")
        return text
    except Exception as e:
        print(f"Error extracting text from textual PDF: {e}")
        return ""

def fetch_id_medication(cursor, nr_cnpj_company, nm_medication, tp_regulatory_category):
    # Function to fetch the `id_medication`
    try:
        sql_command = (
            "SELECT id_medication "
            "FROM healdb.hd_medication "
            "WHERE nr_cnpj_company = %s "
            "  AND nm_medication = %s "
            "  AND tp_regulatory_category = %s "
        )
        register = (nr_cnpj_company, nm_medication, tp_regulatory_category)
        cursor.execute(sql_command, register)
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        print(f"Error fetching id_medication: {e}")
        return None

def process_drug_leaflet_image(cnx, cursor, ls_category, ls_nm_category):
    # Function to reprocess leaflets as images

    # Reprocess leaflets initially identified as text but better processed as images.
    
    # SQL query to select leaflets for reprocessing
    sql_command = (
        "SELECT m.id_medication, m.tp_regulatory_category, d.ds_drug_leaflet_file " 
        "FROM healdb.hd_medication_drug_leaflet d "
        "JOIN healdb.hd_medication m ON d.id_medication = m.id_medication "
        "WHERE d.ds_drug_leaflet_file IN ('bula_1685670002732.pdf', "
        "                                 'bula_1685650681626.pdf', "
        "                                 'bula_1685116552182.pdf', "
        "                                 'bula_1685640040256.pdf') "
    )
    cursor.execute(sql_command)
    registers = cursor.fetchall()

    # Prepare a dataframe to store reprocessed leaflet information
    columns = ["id_medication", "drug_leaflet"]
    df_drug_leaflet = pd.DataFrame(columns=columns)

    print("Reprocessing leaflets as images...")
    for register in registers:
        id_medication = register[0]
        tp_regulatory_category = register[1]
        ds_drug_leaflet_file = register[2]

        # Map regulatory category to its corresponding folder
        index = ls_nm_category.index(tp_regulatory_category)
        category = ls_category[index]

        # Build the file path for the leaflet
        pdf_path = os.path.join(PATHS["leaflets_dir"], category, ds_drug_leaflet_file)

        # Extract text from the image-based PDF
        pdf_text = extract_text_from_image_pdf(pdf_path)

        # Append the reprocessed data to the dataframe
        df_drug_leaflet.loc[len(df_drug_leaflet)] = (id_medication, pdf_text)

    # Update the database with the reprocessed leaflets
    update_medication_drug_leaflet(cnx, cursor, df_drug_leaflet)
    return

def update_medication_drug_leaflet(cnx, cursor, df_drug_leaflet):
    # Function to update leaflets in the database
    
    # Update the full text of reprocessed leaflets in the database.
   
    for _, row in df_drug_leaflet.iterrows():
        id_medication = row["id_medication"]
        pdf_file = row["drug_leaflet"]
        register = (pdf_file, id_medication)
        
        # Update the drug leaflet in the database
        update_query = (
            "UPDATE healdb.hd_medication_drug_leaflet " 
            "SET ds_drug_leaflet_full = %s " 
            "WHERE id_medication = %s "
        )
        cursor.execute(update_query, register)
    cnx.commit()
    return

def create_leaflets_repository(cnx, cursor):
    # Function to process drug leaflets and update the database
    
    # Process drug leaflets, identify the best processing approach (text or image),
    # and create the leaflets repository.
    
    print("Processing leaflets")
    try:
        # Clean working and final tables
        cursor.execute("TRUNCATE TABLE healdb.hd_wrk_drug_leaflet;")
        cursor.execute("TRUNCATE TABLE healdb.hd_wrk_drug_leaflet_dedup;")
        cursor.execute("DELETE FROM healdb.hd_medication_drug_leaflet;")
        cnx.commit()

        # Iterate over leaflet categories
        for category, tp_regulatory_category in LEAFLET_CATEGORIES.items():
            try:
                csv_file = os.path.join(PATHS["leaflets_dir"], category, f"{category}.csv")

                # Detect encoding of the file
                with open(csv_file, "rb") as f:
                    raw_data = f.read()
                    detected_encoding = chardet.detect(raw_data)['encoding']

                # Open file with detected encoding
                with open(csv_file, "r", encoding=detected_encoding, errors="replace") as file:
                    csv_reader = csv.reader(file, delimiter=";")
                    next(csv_reader)  # Skip header row

                    for row in csv_reader:
                        try:
                            nm_medication, dt_publication, ds_drug_leaflet_file, nm_company, nr_cnpj_company = row[1], row[3], row[4], row[5], row[6]
                            if ds_drug_leaflet_file and ds_drug_leaflet_file.lower() != "erro":
                                ds_drug_leaflet_file = f"{ds_drug_leaflet_file.rsplit('.', 1)[0]}.pdf"
                                date_obj = datetime.strptime(dt_publication, "%d/%m/%Y") if dt_publication else None
                                formatted_date = date_obj.strftime("%Y-%m-%d") if date_obj else None
                                register = (nm_medication, formatted_date, 
                                            tp_regulatory_category, 
                                            ds_drug_leaflet_file, nm_company, 
                                            nr_cnpj_company)
                                sql_command = (
                                    "INSERT INTO healdb.hd_wrk_drug_leaflet "
                                    "(nm_medication, dt_publication, tp_regulatory_category, "
                                    "ds_drug_leaflet_file, nm_company, nr_cnpj_company) "
                                    "VALUES (%s, %s, %s, %s, %s, %s) "
                                )
                                cursor.execute(sql_command, register)
                        except Exception as e:
                            print(f"Error processing row {row}: {e}")
                cnx.commit()

            except Exception as e:
                print(f"Error processing category {category}: {e}")

        # Deduplicate leaflets
        try:
            sql_command = (
                "INSERT INTO healdb.hd_wrk_drug_leaflet_dedup "
                "(nm_medication, dt_publication, tp_regulatory_category, " 
                "ds_drug_leaflet_file, nm_company, nr_cnpj_company) "
                "SELECT nm_medication, MAX(dt_publication), tp_regulatory_category, " 
                "MAX(ds_drug_leaflet_file), nm_company, nr_cnpj_company "
                "FROM healdb.hd_wrk_drug_leaflet "
                "GROUP BY nm_medication, tp_regulatory_category, nm_company, nr_cnpj_company; "
            )
            cursor.execute(sql_command)
            cnx.commit()
        except Exception as e:
            print(f"Error during deduplication: {e}")

        # Insert final data into the repository
        try:
            cursor.execute("SELECT * FROM healdb.hd_wrk_drug_leaflet_dedup;")
            for row in cursor.fetchall():
                try:
                    nm_medication, tp_regulatory_category, nm_company, nr_cnpj_company, dt_publication, ds_drug_leaflet_file = row
                    id_medication = fetch_id_medication(cursor, nr_cnpj_company, nm_medication, tp_regulatory_category)
                    if not id_medication:
                        print(f"Warning: No id_medication found for {nm_medication}. Skipping.")
                        continue

                    category = next((k for k, v in LEAFLET_CATEGORIES.items() if v == tp_regulatory_category), None)
                    leaflet_path = os.path.join(PATHS["leaflets_dir"], category, ds_drug_leaflet_file)

                    if is_pdf_textual(leaflet_path):
                        leaflet_text = extract_text_pdf_no_page_break(leaflet_path)
                    else:
                        leaflet_text = extract_text_from_image_pdf(leaflet_path)

                    register = (id_medication, ds_drug_leaflet_file, dt_publication, leaflet_text, "")
                    sql_command = (
                        "INSERT INTO healdb.hd_medication_drug_leaflet "
                        "(id_medication, ds_drug_leaflet_file, dt_publication, ds_drug_leaflet_full, ds_indication) "
                        "VALUES (%s, %s, %s, %s, %s) "
                    )
                    cursor.execute(sql_command, register)
                except Exception as e:
                    print(f"Error inserting final data for row {row}: {e}")
            cnx.commit()
        except Exception as e:
            print(f"Error inserting final data: {e}")

        # Reprocess leaflets as images if needed
        process_drug_leaflet_image(cnx, cursor, list(LEAFLET_CATEGORIES.keys()), list(LEAFLET_CATEGORIES.values()))

    except Exception as e:
        print(f"Error during processing: {e}")
    return
