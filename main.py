import sys
from pathlib import Path
from datetime import datetime

# Add the project root directory to the Python Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from db_utils import open_connection, close_connection
from src.webcrawler.main_webcralwer import main as webcrawler_main
from src.repositories.main_repository import main as repositories_main
from src.translation.main_translation import main as translation_main
from src.nlp_extraction.main_nlp_extraction import main as nlp_extraction_main
from src.interoperability.main_interoperability import main as interoperability_main
from src.ontology.main_ontology import main as ontology_main


def log_execution_time(func_name, start_time, end_time):
    # Logs the time taken for a specific function to execute.
    duration = end_time - start_time
    total_seconds = duration.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(
        f"Function '{func_name}' executed in {int(hours)}h {int(minutes)}m {seconds:.2f}s."
    )

def execute_function_with_timing(func, func_name):
    # Executes a function and logs its execution time.
    start_time = datetime.now()
    func()
    end_time = datetime.now()
    log_execution_time(func_name, start_time, end_time)

def main():
    # Main entry point for the script.
    try:
        # Open the database connection
        cnx, cursor = open_connection()

        # Execute each main function in sequence
        for func, func_name in [
            (webcrawler_main, "Webcrawler"),
            (repositories_main, "Repositories"),
            (translation_main, "Translation"),
            (nlp_extraction_main, "NLP Extraction"),
            (interoperability_main, "Interoperability"),
            (ontology_main, "Ontology")
        ]:
            execute_function_with_timing(func, func_name)

    finally:
        # Ensure the database connection is properly closed
        close_connection(cnx, cursor)

if __name__ == "__main__":
    main()
