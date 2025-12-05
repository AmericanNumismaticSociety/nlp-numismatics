#Author: Ethan Gruber
#Date modified: December 2025
#Function FastAPI in order to parse typological descriptions into reconciled concepts

#FastAPI

#Import necessary libraries
import sqlite3
import json
import os
import numpy as np

#import numismatic parser
from nparser import parse_description

from typing import Union
from fastapi import APIRouter, FastAPI, Response

app = FastAPI()
router = APIRouter()

@app.get("/")
def read_root():
    return {"API": "Pass 'text' request parameter to /extract path for JSON response of concepts"}


#parse typological descriptions with the NLP library and look them up in SQLlite for a JSON response that will turn into NUDS subject terms
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
                if row:
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
        
        
@app.get("/expand")
def lookup_uri(identifiers: Union[str, None] = None):
    try:
        identifiers
    except NameError:
        return {"error": "id parameter undefined"}
    else:        
        if len(identifiers) > 0:
            output = []          
            conn = sqlite3.connect('nnlp.db')
            
            ids = identifiers.split('|')
            
            for id in ids:
                uri = "http://www.wikidata.org/entity/" + id
                
                cur = conn.cursor()
                cur.execute('SELECT concept,conceptLabel,parent,parentLabel,altLabel,parentAltLabels FROM hier WHERE concept =?', (uri,))            
                results = cur.fetchall()                
                
                if results:
                    object = {"concept": uri}
                    object.update({"label": results[0][1]})
                    
                    if results[0][4] and len(results[0][4]) > 0:
                        object.update({"altLabels": results[0][4].split('|')}) 
                                    
                    object.update({"parents": []})
                    for row in results:                    
                        parent = {"uri": row[2], "label": row[3]}
                        
                        if row[5] and len(row[5]) > 0:
                            labels = row[5].split('|')
                            labelsObject = {"altLabels": labels}
                            parent.update(labelsObject)
                                
                        
                        object["parents"].append(parent)
                    output.append(object)                        
                    
                else:
                    output.append({"concept": uri, "warning": "not found"})
                    
            #close sqlite connect and return JSON object    
            conn.close()
            return output
        else:
            return {"error": "id parameter is blank"}
        