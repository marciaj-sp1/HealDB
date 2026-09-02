# -*- coding: utf-8 -*-

# Insert External IDs Module
# Provides helper functions to insert External Ids data into MySQL tables.

def insert_external_id(cursor, cnx, id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id):
    # Inserts external identifiers into the hd_active_ingredient_ext_id table.
    # Ensures that the external ID type exists before inserting and prevents duplicate entries.
    
     # Check if the external ID type exists in hd_type_ext_id before inserting
    check_type_query = "SELECT COUNT(*) FROM healdb.hd_type_ext_id WHERE tp_ext_id = %s"
    cursor.execute(check_type_query, (tp_ext_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        print(f"Warning: External ID type '{tp_ext_id}' not found in hd_type_ext_id.")
        return  

    # Insert only if the external ID does not already exist for this active ingredient
    sql_command = (
        "INSERT INTO healdb.hd_active_ingredient_ext_id "
        "(id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id) "
        "SELECT %s, %s, %s, %s FROM DUAL "
        "WHERE NOT EXISTS ("
        "    SELECT 1 FROM hd_active_ingredient_ext_id "
        "    WHERE id_active_ingredient = %s AND tp_ext_id = %s AND cd_ext_id = %s "
        ")"
    )
    
    try:
        register_ext_id = (id_active_ingredient, tp_ext_id, cd_ext_id, fl_origin_ext_id,
                           id_active_ingredient, tp_ext_id, cd_ext_id)
        #print(register_ext_id)
        cursor.execute(sql_command, register_ext_id)
        cnx.commit()

    except Exception as e:
        print(f"Error inserting {tp_ext_id} for Active Ingredient ID {id_active_ingredient}: {e}")
        
    return