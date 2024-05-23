'''
Scraping data from the URLs stored in the db accordingly.
Using BrautifulSoup receiving text data from each 'url' variable,
and writing the data in 'text' variable.

**All in 'datasets.json' file** 
'''
import os
import json
import requests
from bs4 import BeautifulSoup


def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ''
    for paragraph in soup.find_all('p'):
        text += paragraph.get_text()
    return text


curr_dir = os.path.dirname(__file__)

with open(f"{curr_dir}/datasets.json", 'r') as file:
    '''
    OPENING "datasets.json" file, that is by default contains
    multiple resources, with multiple urls from each resource
    like 'Wikipedia' etc.
    LOADING the data from each and
    SCRAPING the text.
    '''
    DATASETS = json.load(file)

    for source in DATASETS:
        source_articles = DATASETS[source]
        for article in source_articles:
            url = source_articles[article]["url"]
            if not "text" in source_articles[article]:
                print(f"scraping from '{article}' - '{source}'")
                source_articles[article]["text"] = scrape_text(url)

        DATASETS[source] = source_articles

with open(f"{curr_dir}/datasets.json", 'w') as file:
    '''
    ADDING scraped text to the existing file.
    '''
    #Rewriting the json file(adding "text" for each article etc.)
    json.dump(DATASETS, file, indent=4)

print("All data is ready to go!")