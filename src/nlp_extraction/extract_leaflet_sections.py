# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 18:17:00 2024

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# This script performs the following tasks:
# 1. Reads and processes drug leaflets from the database.
# 2. Extracts specific sections, such as "What is this medication indicated for?" and
#    "What should I know before using this medication?"
#    "How this medication works?"
# 3. Stores extracted data in working tables.
# 4. Updates the leaflet repository with the extracted information.

import re
import pandas as pd

def update_drug_leaflet_repository(cnx, cursor):
    # Update the medication leaflet repository with extracted indications 
    # stored in the working table 'hd_wrk_med_leaflet_section'
    try:
        print("Updating the drug leaflet repository...")
        sql_command = (
           "UPDATE healdb.hd_medication_drug_leaflet AS m "
           "INNER JOIN healdb.hd_wrk_med_leaflet_section AS t "
           "ON t.id_medication = m.id_medication "
           "SET m.ds_indication = t.ds_indication, "
           "    m.ds_precaution = t.ds_precaution, "
           "    m.ds_functionality = t.ds_functionality "
        )    
        cursor.execute(sql_command)
        cnx.commit()
        
    except Exception as e:
        print(f"Error updating the drug leaflet repository: {e}")
    return

def insert_df_session_to_table(df, cnx, cursor):
    # Insert a DataFrame with medication indications and precautions into the 
    # working table 'hd_wrk_med_leaflet_section', after truncating it
    try:
        print("Clearing the table 'hd_wrk_med_leaflet_section'...")
        #cursor.execute("TRUNCATE TABLE healdb.hd_wrk_med_leaflet_section")  
        #cnx.commit()

        # Convert the DataFrame into a list of tuples
        registers = df.to_records(index=False).tolist()
        
        # Execute the insertion query
        print("Inserting DataFrame into 'hd_wrk_med_leaflet_section'...")
        sql_command = (
            "INSERT INTO healdb.hd_wrk_med_leaflet_section "
            "(id_medication, ds_indication, ds_precaution, ds_functionality) "
            "VALUES (%s, %s, %s, %s)"
            )
        cursor.executemany(sql_command, registers)
        cnx.commit()
    except Exception as e:
        print(f"Error inserting DataFrame into 'hd_wrk_med_leaflet_section': {e}")
    return


def find_pattern_last_occurrence(pattern, drug_leaflet_text):
    # Find the last occurrence of a regex pattern in the leaflet text
    matches = [match for match in re.finditer(pattern, drug_leaflet_text)]
    return matches[-1] if matches else None


def read_extract_leaflet_precaution(id_medication, nm_medication, drug_leaflet_text):
    # Read the drug leaflet and extract the precaution section
    try:
        # Normalize and clean the leaflet text
        drug_leaflet_text = drug_leaflet_text.replace('\n', ' ').replace('\t', ' ')
        drug_leaflet_text = re.sub(r'\s+', ' ', drug_leaflet_text)
        
        # Temporarily remove sections enclosed in single or double quotes
        text_no_quotes = re.sub(r'[“”"\'].*?[“”"\']', '', drug_leaflet_text)

        # Patterns to identify the beginning and end of the section
        begin_pattern = r"(?i)(^\d+\.\s*)?O QUE DEVO SABER ANTES DE (USAR|UTILIZAR) (ESTE|ESSE|O|A)? (MEDICAMENTO|PRODUTO|\"?[A-ZÀ-Ú0-9][A-ZÀ-Ú0-9\s®\-]*\"?)\??"
        end_pattern = r"(?i)(^\d+\.\s*)?ONDE(, COMO)? E POR QUANTO TEMPO (POSSO|DEVO) (GUARDAR|QUARDAR) (ESTE|ESSE|O|A)? (MEDICAMENTO|PRODUTO|\"?[A-ZÀ-Ú0-9][A-ZÀ-Ú0-9\s®\-]*\"?)\??"
      
        # Find the beginning of the section    
        begin_match = re.search(begin_pattern, text_no_quotes)
        if not begin_match:
            print(f"Beginning of the precaution section not found for {nm_medication}.")
            return ""

        # Advance the index to skip the section title
        start_index = begin_match.end()

        # Extract the text using the adjusted index
        remaining_text = text_no_quotes[start_index:]

        ds_precaution = ''
        # Find the end of the section
        end_match = re.search(end_pattern, remaining_text)
        if not end_match:
            print(f"End of the precaution section not found for {nm_medication}.")
            return ""

        # Extract the text between the beginning and end of the section
        ds_precaution = remaining_text[:end_match.start()].strip()
        
       # Check if the text start with a parenthesis 
        if ds_precaution.startswith(")"):
            next_begin_match = re.search(begin_pattern, remaining_text, re.MULTILINE)
            if next_begin_match:
                start_index = next_begin_match.end()
                remaining_text = remaining_text[start_index:]
                end_match = re.search(end_pattern, remaining_text, re.MULTILINE)
                if end_match:
                    ds_precaution = remaining_text[:end_match.start()].strip()
                else:
                    return ""
           
        # Remove numbers and trailing periods that may appear at the end of the section
        ds_precaution = re.sub(r'\.\s*\d+\.$', '', ds_precaution).strip()
        
    except Exception as e:
        print(f"Error processing the drug leaflet {nm_medication}: {e}")
    return ds_precaution


def read_extract_leaflet_functionality(id_medication, nm_medication, drug_leaflet_text):
    # Read the drug leaflet and extract the indication section
    try:
        text = drug_leaflet_text.replace('\n', ' ').replace('\t', ' ')
        text = re.sub(r'\s+', ' ', text).strip()

        begin_pattern = r"(?i)(?:^\d+\.\s*)?COMO\s+(?:ESTE|ESSE)\s+(?:MEDICAMENTO|PRODUTO)\s+FUNCIONA\??"
        end_pattern = r"(?i)(?:^\d+\.\s*)?QUANDO\s+N[ÃA]O\s+DEVO\s+USAR"


        begin_match = re.search(begin_pattern, text)
        if not begin_match:
            print(f"{nm_medication}: section start not found (functionality).")
            return ""

        start_index = begin_match.end()
        remaining_text = text[start_index:]

        end_match = re.search(end_pattern, remaining_text)
        if not end_match:
            print(f"{nm_medication}: section end not found (functionality). Trying generic section delimiter...")
            fallback_end = re.search(r"(?i)^\d+\s*[-–]?\s+", remaining_text)
            if fallback_end:
                return remaining_text[:fallback_end.start()].strip()
            else:
                return remaining_text.strip()

        ds_functionality = remaining_text[:end_match.start()].strip()
        return ds_functionality

    except Exception as e:
        print(f"Error extracting functionality ({nm_medication}): {e}")
        return ""


def read_extract_leaflet_indication(id_medication, nm_medication, drug_leaflet_text):
    # Read the drug leaflet and extract the indication section
    
    try:
        # Normalize and clean the text
        drug_leaflet_text = drug_leaflet_text.replace('\n', '')
        drug_leaflet_text = drug_leaflet_text.replace('\t', '')
        drug_leaflet_text = drug_leaflet_text.replace('PARAQUE', 'PARA QUE')
        drug_leaflet_text = drug_leaflet_text.replace('MEDICAMENTOFUNCIONA', 'MEDICAMENTO FUNCIONA')
        drug_leaflet_text = drug_leaflet_text.replace('ÉINDICADO', 'É INDICADO')
        drug_leaflet_text = drug_leaflet_text.replace('PACIENTEPARA', 'PACIENTE PARA')
        drug_leaflet_text = drug_leaflet_text.replace('QUEESTE', 'QUE ESTE')
        drug_leaflet_text = drug_leaflet_text.replace('®', '')
        drug_leaflet_text = re.sub(r"(?i)\bi?i?n?di? ?-?cado\b", 'INDICADO', drug_leaflet_text, flags=re.IGNORECASE)
        drug_leaflet_text = re.sub(r"(?i)\bmedica?ment[eo]\b", 'MEDICAMENTO', drug_leaflet_text, flags=re.IGNORECASE)
 
        # Use regular expressions to identify the start and end of the indication section
        begin_pattern = [
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bm\s*e\s*d\s*i\s*c\s*a\s*m\s*e\s*n\s*t\s*o\b[\w\s]*\b[\w\s]*[e|é|foi]\b\s*i\s*n\s*d\s*i\s*c\s*a\s*d\s*o[\w\s]*[?]",
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bm\s*e\s*d\s*i\s*c\s*a\s*m\s*e\s*n\s*t\s*o\b[\w\s]*\b[\w\s]*[e|é|foi]\b\s*i\s*n\s*d\s*i\s*c\s*a\s*d\s*o\b",
            r"(?i)\bpor\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bm\s*e\s*d\s*i\s*c\s*a\s*m\s*e\s*n\s*t\s*o\b[\w\s]*\b[\w\s]*[e|é|foi]\b\s*i\s*n\s*d\s*i\s*c\s*a\s*d\s*o[\w\s]*[?]",
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bp\s*r\s*o\s*d\s*u\s*t\s*o\b[\w\s]*\b[\w\s]*[e|é|foi]\b\s*i\s*n\s*d\s*i\s*c\s*a\s*d\s*o[\w\s]*[?]",
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bp\s*r\s*o\s*d\s*u\s*t\s*o\b[\w\s]*\b[\w\s]*[e|é|foi]\b\s*i\s*n\s*d\s*i\s*c\s*a\s*d\s*o\b",
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê]\b[\w\s]*[eé][\w\s]*\bi\s*n\s*d\s*i\s*c\s*a\s*d\s*o\b[\w\s]*[?]",
            r"(?i)\b2 - i\s*n\s*d\s*i\s*c\s*a\s*[cç]\s*[aãoõ]\s*[eo]\s*.\b",
            r"(?i)\b1. i\s*n\s*d\s*i\s*c\s*a\s*[cç]\s*[aãoõ]\s*[eo]\s*.\b",
            r"(?i)\bi\s*n\s*d\s*i\s*c\s*a\s*[cç]\s*[aãoõ]\s*[eo]\s*.\b",
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bm\s*e\s*d\s*i\s*c\s*a\s*m\s*e\s*n\s*t\s*o\b[\w\s]*\b[\w\s]*[e|é|foi]\b\s*u\s*s\s*a\s*d\s*o[\w\s]*[?]",
            r"(?i)\bp\s*a\s*r\s*a\b[\w\s]*\bq\s*u\s*[eê][\w\s]*\bs\s*e\s*r\s*v\s*e[\w\s]*\be\s*s\s*[st]\s*e[\w\s]*\bm\s*e\s*d\s*i\s*c\s*a\s*m\s*e\s*n\s*t\s*o[\w\s]*[?]"
        ]
      
        end_pattern = [
            r"(?i)\bc\s*o\s*m\s*o\b[\w\s]*\b[e]\s*[s]\s*[st]\s*[e]\b[w\s]*m\s*e\s*d\s*i\s*c\s*a\s*m\s*e\s*n\s*t\s*o\b\s*\bf\s*u\s*n\s*c\s*i\s*o\s*n\s*a\b",
            r"(?i)\bc\s*o\s*m\s*o\b[\w\s]*\b[e]\s*[s]\s*[st]\s*[e]\b[w\s]*p\s*r\s*o\s*d\s*u\s*t\s*o\b\s*\bf\s*u\s*n\s*c\s*i\s*o\s*n\s*a\b",
            r"(?i)\bc\s*o\s*m\s*o\b[\w\s]*f\s*u\s*n\s*c\s*i\s*o\s*n\s*a\b",
            r"(?i)\bq\s*u\s*a\s*n\s*d\s*o\b[\w\s]\bn\s*[aã]\s*[o]\b[w\s]*\bd\s*e\s*v\s*o\b[\w\s]*\bu\s*s\s*a\s*r\b[\w\s]*",
            r"(?i)\br\s*e\s*s\s*u\s*l\s*t\s*a\s*d\s*o\s*s\b[\w\s]*\be\s*f\s*i\s*c\s*[aá]\s*c\s*i\s*a\b",
            r"(?i)\b3 - contra-indicações\b",
            r"(?i)\bc\s*a\s*r\s*a\s*c\s*t\s*e\s*r\s*[ií]\s*s\s*t\s*i\s*c\s*a\s*s\s*f\s*a\s*r\s*m\s*a\s*c\s*o\s*l\s*[oó]\s*g\s*\s*i\s*c\s*a\s*s\b"
        ]
        
        # Find the desired text by determining its start and end
        index_begin = None
        index_end = None
      
        flag_last = 0
        # Check specific cases to find the last occurrence of the pattern
        if nm_medication.upper() in ('ANDROGEL', 'BUSILVEX', 'ONPATTRO', 'SIKLOS'):
            flag_last = 1
            
        # Use regex to identify the start and end of the section
        for i in range(len(begin_pattern)):
            index_begin = re.search(begin_pattern[i], drug_leaflet_text)
            if flag_last:
                index_begin = find_pattern_last_occurrence(begin_pattern[i], drug_leaflet_text)
                print ("index_begin = ", index_begin)

            if index_begin:
               break

        for i in range(len(end_pattern)):
            index_end = re.search(end_pattern[i], drug_leaflet_text)
            if flag_last:
                index_end = find_pattern_last_occurrence(end_pattern[i], drug_leaflet_text)
            if index_end:
                if index_begin and index_begin.end() <= index_end.start():
                    break
                else:
                    break
                
        if index_begin and index_end and index_begin.end() < index_end.start():
            ds_indication = drug_leaflet_text[index_begin.end():index_end.start()].rstrip()
            if ds_indication.endswith("2."):
                ds_indication = ds_indication[:-2].strip()
        elif index_begin:
            print(f"[Fallback] End of indication section not found for {nm_medication}. Trying generic section delimiter...")
            text_after_start = drug_leaflet_text[index_begin.end():]
            fallback_end = re.search(r"(?i)^\d+\s*[-–]?\s+", text_after_start)
            if fallback_end:
                ds_indication = text_after_start[:fallback_end.start()].strip()
            else:
                ds_indication = text_after_start.strip()
        else:
            print(f"[Fallback] Beginning of indication section not found for {nm_medication}.")
            ds_indication = ""
           
    except ValueError as e:
        ds_indication = ""
        print("Error reading leaflet: ", e)
       
    return ds_indication


def load_df_session(df_drug_leaflet):
    # Extract indications from leaflet texts and store them in a DataFrame.
    df_session = pd.DataFrame(columns=['id_medication', 'ds_indication', 
                                       'ds_precaution', 'ds_functionality'])
    for index, row in df_drug_leaflet.iterrows():
        id_medication = row['id_medication']
        nm_medication = row['nm_medication']
        ds_drug_leaflet_full = row['ds_drug_leaflet_full']
        ds_indication = ''
        ds_functionality = ''
        ds_precaution = ''

        print (f"Extracting section from medication {id_medication} {nm_medication} ")
        ds_indication = read_extract_leaflet_indication(id_medication, nm_medication, ds_drug_leaflet_full)
        ds_precaution = read_extract_leaflet_precaution(id_medication, nm_medication, ds_drug_leaflet_full)
        ds_functionality = read_extract_leaflet_functionality(id_medication, nm_medication, ds_drug_leaflet_full)
        df_session.loc[index] = [id_medication, ds_indication, ds_precaution, ds_functionality]

    return df_session

def read_and_store_drug_leaflets(cnx, cursor):
    # Read and process medication leaflets from the database
    # Fetch medication leaflets from the database and store them in a DataFrame.
    try:
        sql_command = (
            "SELECT d.id_medication, m.nm_medication, d.ds_drug_leaflet_full "
            "FROM healdb.hd_medication_drug_leaflet d "
            "INNER JOIN healdb.hd_medication m ON d.id_medication = m.id_medication "
            "WHERE LENGTH(CAST(d.ds_drug_leaflet_full AS CHAR)) >= 10 "
            "AND d.ds_drug_leaflet_file != 'ERRO' "
        )
        cursor.execute(sql_command)
        registers = cursor.fetchall()

        df_drug_leaflet = pd.DataFrame(columns=["id_medication", "nm_medication", 
                                                "ds_drug_leaflet_full"])
        for register in registers:
            id_medication, nm_medication, ds_drug_leaflet_full = register
            ds_drug_leaflet_str = ds_drug_leaflet_full.decode("utf-8")
            
            reg = (id_medication, nm_medication, ds_drug_leaflet_str)
            df_drug_leaflet.loc[len(df_drug_leaflet)] = reg

        return df_drug_leaflet

    except Exception as e:
        print(f"Error reading and processing leaflets into 'hd_medication_drug_leaflet': {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of failure


def extract_leaflet_sections(cnx, cursor):
    # Main function to:
    # 1. Read drug leaflets.
    # 2. Extract "indication" section.
    # 3. Extract "precaution" section.
    # 4. Extract "functionality" section.
    # 5. Update the drug leaflet repository.
    
    print("Reading leaflets from the repository...")
    df_drug_leaflet = read_and_store_drug_leaflets(cnx, cursor)

    print("Extracting leaflet sections...")
    df_session = load_df_session(df_drug_leaflet)

    print("Inserting extracted indications into the working table...")
    insert_df_session_to_table(df_session, cnx, cursor)

    print("Updating the leaflet repository with extracted indications...")
    update_drug_leaflet_repository(cnx, cursor)

    return
