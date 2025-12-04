#Author: Ethan Gruber
#Date modified: December 2025
#Function: Read the reconciled concept CSV file and look up the hierarchy and related labels in the Wikidata SPARQL endpoint

# Import necessary libraries
import array, csv, urllib.request, time, sqlite3
import numpy as np
import xml.etree.ElementTree as ET
from SPARQLWrapper import SPARQLWrapper, JSON

CSV = 'crro-concepts-reconciled.csv'

#insert concepts array into the hier table the nnlp SQLite database
def insert_into_db(concepts):
    create_table = """
    CREATE TABLE IF NOT EXISTS hier (
        id INTEGER PRIMARY KEY,
        concept text NOT NULL, 
        conceptLabel text, 
        parent text,
        parentLabel text,
        altLabel text,
        parentAltLabels text
    );
    """
    
    try:
        with sqlite3.connect('nnlp.db') as conn:
            cursor = conn.cursor()
            #create table if it doesn't exist
            cursor.execute(create_table)   
            conn.commit()
            
            cursor.executemany("""INSERT INTO hier(concept, conceptLabel, parent, parentLabel, altLabel, parentAltLabels) VALUES(?,?,?,?,?,?)""", concepts)
            conn.commit()
    
    except sqlite3.OperationalError as e:
        print(e) 

def write_concept_csv(concepts):
    with open("concept_hierarchy.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(concepts)

def query_wikidata(uri):
    print ("Querying " + uri)
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
    SELECT ?concept ?conceptLabel (GROUP_CONCAT(DISTINCT(?altLabel); separator = "|") AS ?altLabels) ?parent ?parentLabel (GROUP_CONCAT(DISTINCT(?parentAltLabel); separator = "|") AS ?parentAltLabels) WHERE {
      BIND (<""" + uri + """> as ?concept)
      ?concept wdt:P279+|wdt:P31 ?parent .
      FILTER NOT EXISTS {?parent wdt:P31 wd:Q19478619}
      FILTER NOT EXISTS {?parent wdt:P31 wd:Q124711104}
      FILTER NOT EXISTS {?parent wdt:P279 wd:Q27043950}
      OPTIONAL { ?concept skos:altLabel ?altLabel FILTER (langMatches(lang(?altLabel), "en")) }
      OPTIONAL { ?parent skos:altLabel ?parentAltLabel FILTER (langMatches(lang(?parentAltLabel), "en")) }
               
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    } GROUP BY ?concept ?conceptLabel ?parent ?parentLabel
    """)
    
    try:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        rows = []
        
        for result in results['results']['bindings']:
            row = [] 
            for key, binding in result.items():
                row.append(binding['value'])   
            rows.append(row)  
        return rows
        
        
    except Exception as e:
        print(e)


#read the list of concepts and extract only unique Wikidata URIs
def extract_concepts(filename):
    #open a CSV of reconciled concepts
    with open(filename, mode ='r') as file:    
        cr = csv.DictReader(file, delimiter=',', quotechar='"')    
        
        concepts = []
        for row in cr:
            uri = row['wikidata_uri']
            if uri not in concepts:
                concepts.append(uri)
                
        return concepts
 

concepts = extract_concepts(CSV)
#print(concepts)
             
concept_rows = [[ "concept", "conceptLabel", "parent", "parentLabel", "altLabel", "parentAltLabels" ]]

#query Wikidata SPARQL endpoint for each URI
count = 0
for uri in concepts:
    rows = query_wikidata(uri)
    for row in rows:            
        concept_rows.append(row)
    #execute HTTP request at 1 per second
    time.sleep(3)
        
print("Processing completed")
                
#write terminologies into database
print("Inserting into database")
insert_into_db(concept_rows)

#end script