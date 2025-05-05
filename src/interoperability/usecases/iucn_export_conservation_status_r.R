# -*- coding: utf-8 -*-

# Created on Mon Apr 21 2025

# Author: Márcia Jacobina Andrade Martins
# Instituto de Computação - IC
# Universidade Estadual de Campinas - UNICAMP
# E-mail: m905106@dac.unicamp.br
# 

# This script retrieves detailed conservation information for medicinal plants classified as
# "PM" (Planta Medicinal) in the Brazilian Common Denomination (DCB) list, including:
#  - IUCN conservation status (category and year)
#  - Geographic distribution with origin and presence status
#  - Reported threats and habitats
#
# It uses the IUCN Red List API v4 and processes all active ingredients found in the HealDB database.
# Results are saved to JSON files.

library(DBI)
library(RMariaDB)
library(iucnredlist)
library(jsonlite)

# Function to normalize scientific names (genus + species), removing extra characters
normalize_scientific_name <- function(name) {
  name <- gsub("[\u00A0\u200B]", " ", name)        # Remove invisible Unicode spaces
  name <- gsub("\\s+", " ", name)                  # Normalize spacing
  name <- trimws(name)                             # Trim leading/trailing spaces
  name_clean <- gsub("\\s*\\(.*?\\)$", "", name)   # Remove authors in parentheses at end
  words <- unlist(strsplit(name_clean, " "))
  valid_words <- grep("^[a-zA-Z-]+$", words, value = TRUE)
  if (length(valid_words) >= 2) {
    paste(valid_words[1:2], collapse = " ")
  } else {
    paste(valid_words, collapse = " ")
  }
}

# Function to fetch and format IUCN conservation status using API
fetch_iucn_data <- function(scientific_names, api) {
  results <- list()
  
  for (name in scientific_names) {
    cat(paste0("Processing: ", name, "\n"))
    parts <- unlist(strsplit(name, " "))
    
    if (length(parts) == 2) {
      genus <- parts[1]
      species <- parts[2]
      entry <- list(name = name)
      
      taxa_data <- tryCatch(
        { assessments_by_name(api, genus = genus, species = species) },
        error = function(e) structure(list(), class = "try-error")
      )
      
      if (inherits(taxa_data, "try-error") || nrow(taxa_data) == 0) {
        entry$error <- "No assessments found"
        results[[name]] <- entry
        next
      }
      
      entry$assessments <- lapply(seq_len(nrow(taxa_data)), function(i) {
        row <- taxa_data[i, ]
        assessment_id <- row$assessment_id
        
        detail <- tryCatch(
          { assessment_data(api, assessment_id) },
          error = function(e) NULL
        )

        category_code <- if (!is.null(detail$red_list_category$code)) detail$red_list_category$code else NA
        category_description <- if (!is.null(detail$red_list_category$description$en)) detail$red_list_category$description$en else NA
        location_names <- if (!is.null(detail$locations)) {
          sapply(detail$locations, function(loc) loc$description$en)
        } else {
          list()
        }
        threats <- if (!is.null(detail$threats)) {
          sapply(detail$threats, function(th) th$description$en)
        } else {
          list()
        }
        
        list(
          scope = row$scopes_description_en,
          year_published = row$year_published,
          assessment_id = assessment_id,
          category = category_code,
          category_description = category_description,
          possibly_extinct = if (!is.null(detail)) detail$possibly_extinct else NA,
          possibly_extinct_in_the_wild = if (!is.null(detail)) detail$possibly_extinct_in_the_wild else NA,
          locations = location_names,
          threats = threats
        )
      })
      
      results[[name]] <- entry
      Sys.sleep(1.5)  # Delay to respect API rate limits
    } else {
      results[[name]] <- list(name = name, error = "Invalid scientific name format")
    }
  }
  
  return(results)
}

# Connect to HealDB database
con <- dbConnect(RMariaDB::MariaDB(),
                 dbname = "healdb",
                 host = "localhost",
                 port = 3306,
                 user = "root",
                 password = "root")

# Medicinal plant active ingredients from HealDB
query_healdb <- "
SELECT 
  h1.id_active_ingredient,
  LOWER(TRIM(SUBSTRING_INDEX(h1.nm_active_ingredient, ' ', 2))) AS scientific_name
FROM hd_active_ingredient h1
JOIN hd_dcb_list h2 ON TRIM(UPPER(h1.nm_active_ingredient)) = TRIM(UPPER(h2.nm_dcb))
JOIN hd_dcb_classification h3 ON h2.id_dcb_classification = h3.id_dcb_classification
WHERE h3.tp_dcb_classification = 'PM'
ORDER BY 2
"

# All medicinal plants (PM) from DCB list
query_dcb <- "
SELECT 
  hdl.id_dcb,
  hdl.nr_dcb,
  LOWER(TRIM(SUBSTRING_INDEX(hdl.nm_dcb, ' ', 2))) AS scientific_name
FROM hd_dcb_list hdl
JOIN hd_dcb_classification hdc ON hdl.id_dcb_classification = hdc.id_dcb_classification
WHERE hdc.tp_dcb_classification = 'PM'
ORDER BY 3
"

# Run queries
healdb_data <- dbGetQuery(con, query_healdb)
dcb_data <- dbGetQuery(con, query_dcb)
dbDisconnect(con)

# Normalize scientific names
healdb_data$scientific_name <- sapply(healdb_data$scientific_name, normalize_scientific_name)
dcb_data$scientific_name <- sapply(dcb_data$scientific_name, normalize_scientific_name)

# Initialize the IUCN API with authorized token
api <- init_api("RsivKtqPc4T7gFP2UM43A8ke3t1rYG2FmMGs")

# Run IUCN queries for both lists
result_healdb <- fetch_iucn_data(healdb_data$scientific_name, api)
result_dcb <- fetch_iucn_data(dcb_data$scientific_name, api)

# Add extra columns to HealDB Result
for (i in names(result_healdb)) {
  df <- healdb_data[healdb_data$scientific_name == i, ]
  if (nrow(df) == 1) {
    result_healdb[[i]]$id_active_ingredient <- df$id_active_ingredient
  }
}

# Add extra columns to DCB Result
for (i in names(result_dcb)) {
  df <- dcb_data[dcb_data$scientific_name == i, ]
  if (nrow(df) == 1) {
    result_dcb[[i]]$id_dcb <- df$id_dcb
    result_dcb[[i]]$nr_dcb <- df$nr_dcb
  }
}


# Export results to JSON files
write_json(result_healdb, "C:/project/healdb/data/output/interoperability/iucn/iucn_conservation_healdb.json", pretty = TRUE, auto_unbox = TRUE)
write_json(result_dcb, "C:/project/healdb/data/output/interoperability/iucn/iucn_conservation_dcb.json", pretty = TRUE, auto_unbox = TRUE)

cat("\nExport completed for HealDB and DCB.\n")
