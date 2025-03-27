# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:14:07 2023

Author: Márcia Jacobina Andrade S. Martins
Instituto de Computação - IC
Universidade Estadual de Campinas - UNICAMP
E-mail: m905106@dac.unicamp.br

"""

# Automate the collection and storage of leaflets from ANVISA’s Electronic 
# Leaflet System using web crawling and scraping techniques for all regulatory 
# leaflet categories. The process ensures a systematic download and 
# rganization of files, enabling their integration into the HealDB database 
# in a structured manner.



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
import pandas as pd
import shutil
import os
from config import PATHS, ANVISA, BROWSER_OPTIONS

# Web crawling and scraping for ANVISA's electronic leaflet system.
# Uses Selenium for automation and BeautifulSoup for parsing web content.


# Define the browser to access the ANVISA electronic leaflet system
webdriver_service = Service(PATHS["chromedriver"])

options = Options()
options.add_argument("start-maximized")

# Use BROWSER_OPTIONS from config
options.add_experimental_option("prefs", BROWSER_OPTIONS["prefs"])

driver = webdriver.Chrome(service=webdriver_service, options=options)

# Access the ANVISA electronic leaflet system
url = ANVISA["url"]
driver.get(url)
time.sleep(5)

# Loop through all categories
category = 1
start_page = 1

while category <= 9:
    original_window = driver.current_window_handle
    time.sleep(5)
    
    try:
        driver.find_element(By.XPATH, '//*[@id="-container"]/button').click()
        time.sleep(5)
    except NoSuchElementException as e:
        print(f"Error selecting category button: {e}")
        break

    # Determine category name
    if category == 1:
        box = driver.find_element(By.LINK_TEXT, 'Biológico')
        category_name = 'biologico'
    elif category == 2:
        box = driver.find_element(By.LINK_TEXT, 'Dinamizado')
        category_name = 'dinamizado'
    elif category == 3:
        box = driver.find_element(By.LINK_TEXT, 'Específico')
        category_name = 'especifico'
    elif category == 4:
        box = driver.find_element(By.LINK_TEXT, 'Fitoterápico')
        category_name = 'fitoterapico'
    elif category == 5:
        box = driver.find_element(By.LINK_TEXT, 'Genérico')
        category_name = 'generico'
    elif category == 6:
        box = driver.find_element(By.LINK_TEXT, 'Novo')
        category_name = 'novo'
    elif category == 7:
        box = driver.find_element(By.LINK_TEXT, 'Produto de Terapia Avançada')
        category_name = 'prod_tp'
    elif category == 8:
        box = driver.find_element(By.LINK_TEXT, 'Radiofármaco')
        category_name = 'radiofarmaco'
    elif category == 9:
        box = driver.find_element(By.LINK_TEXT, 'Similar')
        category_name = 'similar'

    category += 1
    box.click()
    time.sleep(5)

    try:
        driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/form/div/div[3]/input[1]').click()
        time.sleep(5)
    except NoSuchElementException as e:
        print(f"Error selecting consultation button: {e}")
        continue

    try:
        driver.find_element(By.XPATH, '//*[@id="containerTable"]/div/div/div/div/button[3]').click()
        time.sleep(5)
    except NoSuchElementException:
        pass

    # Parse table and download leaflets
    soup = BeautifulSoup(driver.page_source, 'lxml')
    table = soup.find('table', class_='table table-hover table-striped ng-scope ng-table')
    headers = [i.text.strip() for i in table.find_all('th', class_='ng-scope')]
    
    df = pd.DataFrame(columns=headers)
    df = df.drop(columns=['Histórico de Bulas', 'Bula do Profissional'])
    
    try:
        last_page = int(soup.find('a', {'ng-switch-when': 'last'}).text)
    except AttributeError:
        last_page = 1

    current_page = start_page
    while current_page <= last_page:
        print(f"Processing page {current_page} of category {category_name}...")
        driver.switch_to.new_window('tab')

        for row in table.find_all('tr')[3:]:
            before_files = os.listdir(PATHS["download_dir"])
            row_data = row.find_all('td')
            row_values = [data.text.strip() for data in row_data[1:5]]
            
            leaflet_link = row.find_all('td')[5].find('a').get('href')
            leaflet_url = f'https://consultas.anvisa.gov.br/{leaflet_link}'
            driver.get(leaflet_url)
            time.sleep(5)

            while any(fname.endswith('.crdownload') or fname.endswith('.tmp') for fname in os.listdir(PATHS["download_dir"])):
                time.sleep(2)

            after_files = os.listdir(PATHS["download_dir"])
            downloaded_file = list(set(after_files) - set(before_files))[0]
            row_values.append(downloaded_file)
            df.loc[len(df)] = row_values

        driver.close()
        driver.switch_to.window(original_window)
        current_page += 1

        if current_page > last_page:
            break

        driver.find_element(By.CSS_SELECTOR, "a[ng-switch-when='next']").click()
        time.sleep(10)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        table = soup.find('table', class_='table table-hover table-striped ng-scope ng-table')

    # Process Empresa - CNPJ column
    df[['Empresa', 'CNPJ']] = df['Empresa - CNPJ'].str.rsplit('-', 1, expand=True)
    df['CNPJ'] = df['CNPJ'].str.strip()
    df.drop(columns=['Empresa - CNPJ'], inplace=True)

    # Move downloaded files to the category folder
    source_folder = PATHS["download_dir"]
    target_folder = os.path.join(PATHS["leaflets_dir"], category_name)

    all_files = os.listdir(source_folder)
    for file in all_files:
        shutil.move(os.path.join(source_folder, file), os.path.join(target_folder, file))

    # Save files to Excel and CSV
    file_excel = os.path.join(target_folder, f'{category_name}{start_page}.xlsx')
    file_csv = os.path.join(target_folder, f'{category_name}{start_page}.csv')

    df.to_excel(file_excel)
    df.to_csv(file_csv, sep=";")

    print(f"Files {file_excel} and {file_csv} for category {category_name} successfully saved!")