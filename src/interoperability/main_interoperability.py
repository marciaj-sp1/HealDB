import sys
from pathlib import Path
from datetime import datetime

# Add the project root directory to the Python Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))


from db_utils import open_connection, close_connection
from src.interoperability.import_dcb_data import import_dcb_data
from src.interoperability.iucn_conservation_status_PM import iucn_conservation_status_PM
from src.interoperability.populate_external_ids_types import populate_external_ids_types
from src.interoperability.link_cas_to_active_ing import link_cas_to_active_ing
from src.interoperability.link_rxcui_to_active_ing import link_rxcui_to_active_ing
from src.interoperability.link_rxcui_related_ids_to_active_ing import link_rxcui_related_ids_to_active_ing
from src.interoperability.link_wikidata_ids_to_wrk_table import link_wikidata_ids_to_wrk_table
from src.interoperability.link_kegg_related_ids_to_active_ing import link_kegg_related_ids_to_active_ing
from src.interoperability.fill_missing_external_ids import fill_missing_external_ids



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
            (import_dcb_data, "import_dcb_data"),
            (iucn_conservation_status_PM, "iucn_conservation_status_PM"),
            (populate_external_ids_types, "populate_external_ids_types"),
            (link_cas_to_active_ing, "link_cas_to_active_ing"),
            (link_rxcui_to_active_ing, "link_rxcui_to_active_ing"),
            (link_rxcui_related_ids_to_active_ing, "link_rxcui_related_ids_to_active_ing"),
            (link_wikidata_ids_to_wrk_table, "link_wikidata_ids_to_wrk_table"),
            (link_kegg_related_ids_to_active_ing, "link_kegg_related_ids_to_active_ing"),
            (fill_missing_external_ids, "fill_missing_external_ids")
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
