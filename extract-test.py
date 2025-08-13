#!/usr/bin/env python3

# Import necessary libraries
import numpy as np
import sqlite3
import json
import os
import urllib.parse
import sys

#import numismatic parser
from nparser import parse_description

concepts = []

text = "Trophy; on right, togate figure of L. Aemilius Paullus; on left, three captives (King Perseus of Macedon and his sons). Border of dots."
concept_list = parse_description(text)
concepts = concepts + concept_list

#filter out duplicate concepts and then sort alphabetically
unique = np.array(list(set(concepts)))
unique.sort()

keywords = []
#establish SQLite connection
conn = sqlite3.connect('nnlp.db')
for concept in unique:
    cur = conn.cursor()
    cur.execute('SELECT term,preferred_label,wikidata_uri FROM concepts WHERE term =?', (concept,))
    row = cur.fetchone()
    keywords.append(row)    
conn.close()

#output rows into JSON response
output = []
for keyword in keywords:
    object = {"label": keyword[1], "uri": keyword[2]}
    output.append(object)
 

print("Content-Type: text/plain")    # HTML is following
print()              
o = urllib.parse.parse_qsl("http://google.com?query=query&query=query2")
print(o)
    
#HTTP output
#print("Content-Type: application/json")    # HTML is following
#print()                             # blank line, end of headers

#print(json.dumps(output))
