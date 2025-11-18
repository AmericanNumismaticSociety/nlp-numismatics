#FastAPI

#Import necessary libraries
import sqlite3
import json
import os
import numpy as np

#import numismatic parser
from nparser import parse_description

from typing import Union
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"API": "Pass 'text' request parameter to /extract path for JSON response of concepts"}


@app.get("/extract")
def read_item(text: Union[str, None] = None):
    try:
        text
    except NameError:
        return {"error": "text parameter undefined"}
    else:
        
        if len(text) > 0:
            concepts = []
        
            #text = "Trophy; on right, togate figure of L. Aemilius Paullus; on left, three captives (King Perseus of Macedon and his sons). Border of dots."
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
            
            return output
        else:
            return {"error": "text parameter is blank"}