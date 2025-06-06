import sys
from pathlib import Path
from datetime import datetime

# Add the project root directory to the Python Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from db_utils import open_connection, close_connection
from src.nlp_extraction.extract_leaflet_sections import extract_leaflet_sections
from src.nlp_extraction.translate_leaflet_sections import translate_leaflet_sections
from src.nlp_extraction.extract_diseases_from_indications import extract_diseases_from_indications
from src.nlp_extraction.process_disease_data_json import process_disease_data_json
from src.nlp_extraction.link_medications_with_diseases import link_medications_with_diseases



def log_execution_time(func_name, start_time, end_time):
    # Logs the time taken for a specific function to execute.
    # Displays the duration in hours, minutes, and seconds.
    
    duration = end_time - start_time
    total_seconds = duration.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(
        f"Function '{func_name}' executed in {int(hours)}h {int(minutes)}m {seconds:.2f}s."
    )
    return


def main():
    # Main entry point for the script.
    # Manages database connection and processes repositories.
        
    try:
        # Open the database connection
        cnx, cursor = open_connection()

        # Create repositories and measure execution time
        for func, func_name in [
            (extract_leaflet_sections, "extract_leaflet_sections"),
            (translate_leaflet_sections, "translate_leaflet_sections"),
            (extract_diseases_from_indications, "extract_diseases_from_indications"),
            (process_disease_data_json, "process_disease_data_json"),
            (link_medications_with_diseases, "link_medications_with_diseases")
        ]:
            start_time = datetime.now()
            func(cnx, cursor)  # Execute the function
            end_time = datetime.now()
            log_execution_time(func_name, start_time, end_time)

    finally:
        # Ensure the database connection is properly closed
        close_connection(cnx, cursor)
        
    return


if __name__ == "__main__":
    main()
