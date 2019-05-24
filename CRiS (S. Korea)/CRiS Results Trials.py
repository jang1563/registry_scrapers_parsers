# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +

#The standard CRIS XML doesn't include anything that tells us about results status
#but we can automate getting another data download of just trials with results
#and compare

# +
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from time import time
import os
import xmltodict
import json
import re
from requests import get
from bs4 import BeautifulSoup
from pathlib import Path
import platform

platform = platform.platform()
cwd = os.getcwd()
download_path = os.path.join(cwd,'CRiS Downloads')
#adjust this to fit your specific file structure 
parent = str(Path(cwd).parents[0]) 

if "Darwin" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver')
elif "Windows" in platform:
    chrome_driver = os.path.join(parent, 'Drivers', 'chromedriver.exe')
else:
    print("No OS/Chromedriver match. OS: {}".format(platform))

# +
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : download_path,
        'disk-cache-size': 4096,
        'safebrowsing.enabled': 'false'}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(executable_path=chrome_driver, options=chromeOptions)
driver.get('https://cris.nih.go.kr/cris/en/search/detail_search.jsp')
select_results = Select(driver.find_element_by_id('s_results_yn'))
select_results.select_by_value('Y')
driver.find_element_by_xpath("//input[@alt='Search']").click()
sleep(3)
results_trials_count = (driver.find_element_by_xpath("//strong[@class='searchtbtnb']")).text
driver.find_element_by_xpath("//img[@alt='Download']").click()
sleep(2)
handles = driver.window_handles
driver.switch_to.window(handles[-1])
select = Select(driver.find_element_by_id('data_dtype'))
select.select_by_value('xml')
driver.find_element_by_xpath("//img[@alt='confirm']").click()

dl_check = 0
start_time = time()
while dl_check == 0 and time() - start_time < 600:
    count = 0
    for file in os.listdir(download_path):
        if file.endswith(".xml"):
            count = 1
        else:
            count = 0
    if count == 1:
        dl_check = 1
        driver.quit()
    else:
        dl_check = 0
        sleep(5)
# -

print(os.listdir(download_path))
file_name = ''
for file in os.listdir(download_path):
    if file.endswith('.xml'):
        file_name = file
print(file_name)

# +
#there's, as far as I can tell, a single instance of a problematic html element (&#1;) making the XML invalid. 
#Upon Investigation, it appears to be completely inconsequential so rather than messing around with encoding, 
#much easier to just delete that 1 instance

xmlstring = open(download_path + '/' + file_name, 'r', encoding="utf8").read()
xml_fixed = re.sub(r'&#1;', '', xmlstring)

# +
cris_results_trials = []

results_trials = xmltodict.parse(xml_fixed)
for trial in results_trials['trials']['trial']:
    cris_results_trials.append(json.dumps(trial))

if len(cris_results_trials) == int(results_trials_count):
    print("CRIS Results Download/Parse Successful: {} records".format(results_trials_count))
else:
    print("Results Trial Issue: CRIS Contains {}, Scrape Contains {}".format(results_trials_count, len(cris_trials)))

# +
#creates a csv with no headers and a single column with all trials in json in their own row.

import csv
from datetime import date

def cris_results_csv():
    with open('cris_results - ' + str(date.today()) + '.csv','w', newline = '')as cris_results_csv:
        writer=csv.writer(cris_results_csv)
        for val in cris_results_trials:
            writer.writerow([val])

#If you want a CSV run this function after the script runs

# +
#cris_results_csv()
# -

