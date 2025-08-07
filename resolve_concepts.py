# Import necessary libraries
import csv, urllib.request
import numpy as np

#import numismatic parser
from nparser import parse_description

def write_concept_csv(concepts):
    with open("concepts.csv", "w") as file:
        file.write("term\n")    
        for line in unique:
            file.write(line + "\n")


concepts = []
description_urls = ['https://docs.google.com/spreadsheets/d/e/2PACX-1vRxzNNLc4uLaPfNO60mNG4QJ09nWg0D4mosOCM-eQfbO4vqTj8skEE6zkJ7IbLdCrHVbWslehKDh5LN/pub?gid=1411485313&single=true&output=csv',
                    'https://docs.google.com/spreadsheets/d/e/2PACX-1vRxzNNLc4uLaPfNO60mNG4QJ09nWg0D4mosOCM-eQfbO4vqTj8skEE6zkJ7IbLdCrHVbWslehKDh5LN/pub?gid=1676912151&single=true&output=csv']

#text = "Trophy; on right, togate figure of L. Aemilius Paullus; on left, three captives (King Perseus of Macedon, Alexander III of Macedon and his sons). Border of dots."
#parse_description(text)

for url in description_urls:
    response = urllib.request.urlopen(url)
    lines = [l.decode('utf-8') for l in response.readlines()]
    cr = csv.DictReader(lines, delimiter=',', quotechar='"')
    
    for row in cr:
        concept_list = parse_description(row['en'])
        concepts = concepts + concept_list


#filter out duplicate concepts and then sort alphabetically
unique = np.array(list(set(concepts))).sort()
print(unique)


