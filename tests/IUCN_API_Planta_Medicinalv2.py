import requests
import urllib.parse

# Token and Base URLs for IUCN API
TOKEN = "9bb4facb6d23f48efbf424bb05c0c1ef1cf6f468393bc745d42179ac4aca5fee"
BASE_COUNTRY_URL = "https://apiv3.iucnredlist.org/api/v3/species/countries/name/"
BASE_THREATS_URL = "https://apiv3.iucnredlist.org/api/v3/threats/species/name/"
BASE_SPECIES_URL = "https://apiv3.iucnredlist.org/api/v3/species/"

# Conservation categories and meanings
CATEGORY_MEANINGS = {
    "EX": "Extinct",
    "EW": "Extinct in the Wild",
    "RE": "Regionally Extinct",
    "CR": "Critically Endangered",
    "EN": "Endangered",
    "VU": "Vulnerable",
    "LR/cd": "Lower Risk: Conservation Dependent",
    "NT": "Near Threatened",
    "LR/nt": "Lower Risk: Near Threatened",
    "LC": "Least Concern",
    "LR/lc": "Lower Risk: Least Concern",
    "DD": "Data Deficient",
    "NA": "Not Applicable (regional category)"
}

# List of plants to query
#plants = [
#    "ACHILLEA MILLEFOLIUM", "ACONITUM NAPELLUS", "ACTAEA RACEMOSA",
#    "VALERIANA OFFICINALIS", "VITEX AGNUS-CASTUS", "ZINGIBER OFFICINALE"
#]

# List of 90 plants
plants = [
    "ACHILLEA MILLEFOLIUM", "ACONITUM NAPELLUS", "ACTAEA RACEMOSA", "AESCULUS HIPPOCASTANUM", 
    "ALLIUM SATIVUM", "ALOE FEROX MILL.", "ALPINIA ZERUMBET", "ANANAS COMOSUS", 
    "ARCTOSTAPHYLOS UVA-URSI", "ARNICA MONTANA", "ATROPA BELLADONNA", "BACOPA MONNIERI", 
    "BERBERIS LAURINA", "BORAGO OFFICINALIS", "CALENDULA OFFICINALIS", "CAPSICUM ANNUUM", 
    "CASSIA FISTULA", "CENTELLA ASIATICA", "CEPHAELIS IPECACUANHA", "CEREUS JAMACARU", 
    "CINCHONA CALISAYA", "CINNAMOMUM VERUM", "CORDIA VERBENACEA", "CRATAEGUS RHIPIDOPHYLLA", 
    "CROTON HELIOTROPIIFOLIUS", "CURCUMA LONGA", "CYNARA SCOLYMUS", "DORSTENIA ARIFOLIA", 
    "ECHINACEA ANGUSTIFOLIA", "ECHINACEA PURPUREA", "EQUISETUM ARVENSE", "ERYTHRINA VELUTINA", 
    "EUCALYPTUS GLOBULUS", "FRANGULA PURSHIANA", "FUCUS VESICULOSUS", "GARCINIA CAMBOGIA", 
    "GENTIANA LUTEA", "GINKGO BILOBA", "GLYCINE MAX", "GLYCYRRHIZA GLABRA", 
    "HAMAMELIS VIRGINIANA", "HARPAGOPHYTUM PROCUMBENS", "HEDERA HELIX", "HIMATANTHUS LANCIFOLIUS", 
    "HUMULUS LUPULUS", "HYDRASTIS CANADENSIS", "HYPERICUM PERFORATUM", "JATEORHIZA PALMATA", 
    "JUNIPERUS SABINA", "MATRICARIA CHAMOMILLA", "MATRICARIA RECUTITA", "MELILOTUS OFFICINALIS", 
    "MELISSA OFFICINALIS", "MENTHA CRISPA", "MIKANIA GLOMERATA", "MIKANIA LAEVIGATA", 
    "MYROXYLON BALSAMUM", "NASTURTIUM OFFICINALE", "ORYZA SATIVA", "PAPAVER SOMNIFERUM", 
    "PASSIFLORA ALATA", "PASSIFLORA INCARNATA", "PAULLINIA CUPANA", "PELARGONIUM SIDOIDES", 
    "PERSEA AMERICANA", "PEUMUS BOLDUS", "PINUS PINASTER", "PIPER METHYSTICUM", 
    "PLANTAGO OVATA", "POLYGALA SENEGA", "POLYGONUM PUNCTATUM", "POLYPODIUM LEUCATOMOS", 
    "RHEUM PALMATUM", "RHODIOLA ROSEA", "RUTA GRAVEOLENS", "SALIX ALBA", 
    "SCHINUS TEREBINTHIFOLIA", "SENNA ALEXANDRINA", "SERENOA REPENS", "STRYCHNOS NUX-VOMICA", 
    "STRYPHNODENDRON ADSTRINGENS", "SYMPHYTUM OFFICINALE", "SYZYGIUM AROMATICUM", 
    "TANACETUM PARTHENIUM", "TRIBULUS TERRESTRIS", "TRIFOLIUM PRATENSE", "VACCINIUM MACROCARPON", 
    "VALERIANA OFFICINALIS", "VITEX AGNUS-CASTUS", "ZINGIBER OFFICINALE"
]





# Initialize counters
not_found = 0

def query_country_data(plant_name):
    """Query IUCN API for plant distribution by country."""
    encoded_name = urllib.parse.quote(plant_name)
    url = f"{BASE_COUNTRY_URL}{encoded_name}?token={TOKEN}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            print(f"Country Data for {plant_name}:")
            for entry in data["result"]:
                country = entry.get("country", "N/A")
                presence = entry.get("presence", "N/A")
                origin = entry.get("origin", "N/A")
                print(f"  Country: {country}, Presence: {presence}, Origin: {origin}")
            print("-----------------------------")
        else:
            print(f"No country data found for {plant_name}")
            return False
    else:
        print(f"Error {response.status_code} for {plant_name}")
        return False
    return True

def query_threats(plant_name):
    """Query IUCN API for plant threats."""
    encoded_name = urllib.parse.quote(plant_name)
    url = f"{BASE_THREATS_URL}{encoded_name}?token={TOKEN}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            print(f"Threats for {plant_name}:")
            for threat in data["result"]:
                title = threat.get('title', 'N/A')
                scope = threat.get('scope', 'N/A')
                severity = threat.get('severity', 'N/A')
                print(f"  Threat: {title}, Scope: {scope}, Severity: {severity}")
            print("-----------------------------")
        else:
            print(f"No threats found for {plant_name}")
            return False
    else:
        print(f"Error {response.status_code} for {plant_name}")
        return False
    return True

def query_conservation_status(plant_name):
    """Query IUCN API for plant conservation status."""
    encoded_name = urllib.parse.quote(plant_name)
    url = f"{BASE_SPECIES_URL}{encoded_name}?token={TOKEN}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            for entry in data["result"]:
                category = entry.get("category", "N/A")
                meaning = CATEGORY_MEANINGS.get(category, "Unknown status")
                print(f"Conservation Status for {plant_name}: {category} - {meaning}")
            print("-----------------------------")
        else:
            print(f"No conservation status found for {plant_name}")
            return False
    else:
        print(f"Error {response.status_code} for {plant_name}")
        return False
    return True

# Main loop to query data for all plants
for plant in plants:
    print(f"Querying: {plant}")
    
    found_country_data = query_country_data(plant)
    found_threats = query_threats(plant)
    found_status = query_conservation_status(plant)

    if not found_country_data and not found_threats and not found_status:
        not_found += 1

print(f"\nTotal plants without data: {not_found} out of {len(plants)}")
