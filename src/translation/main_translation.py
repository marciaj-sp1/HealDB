import sys
from pathlib import Path
from datetime import datetime

# Add the project root directory to the Python Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


from db_utils import open_connection, close_connection
from src.translation.translate_active_ingredients import translate_active_ingredients
from src.translation.import_translated_active_ingredients_meta import import_translated_active_ingredients_meta
from src.translation.validate_translation_and_link_active_ing import validate_translation_and_link_active_ing
from src.translation.translate_drug_interactions import translate_drug_interactions
from src.translation.translate_food_interactions import translate_food_interactions


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
            (translate_active_ingredients, "translate_active_ingredients"),
            (import_translated_active_ingredients_meta, "import_translated_active_ingredients_meta"),
            (validate_translation_and_link_active_ing, "validate_translation_and_link_active_ing"),
            (translate_drug_interactions, "translate_drug_interactions"),
            (translate_food_interactions, "translate_food_interactions")            
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
