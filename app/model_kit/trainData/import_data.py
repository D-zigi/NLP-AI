'''
Writing all data from the .json db file('datasets.json')
into one Variable 'ARTICLES'
'''
import os
import json

curr_dir = os.path.dirname(__file__)

with open(f"{curr_dir}/datasets.json", 'r') as file:
    DATASETS = json.load(file)
    ARTICLES = []

    for source in DATASETS:
        for article in DATASETS[source]:
            ARTICLES.append(DATASETS[source][article]["text"])