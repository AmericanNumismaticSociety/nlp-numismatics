#Author: Ethan Gruber
#Date modified: December 2025
#Function: Read the *-reconciled.csv files within this directory in order to populate the terms table in nnlp.db with unique terms and associated URIs

#drop table 'concepts' before reloading from CSV

# Import necessary libraries
import os, array, csv, urllib.request, time, sqlite3
import pandas as pd
import numpy as np

#insert concepts array into the hier table the nnlp SQLite database
def insert_into_db(concepts):
    
    create_table = """
    CREATE TABLE IF NOT EXISTS concepts (
        id INTEGER PRIMARY KEY,
        term text NOT NULL, 
        preferred_label text, 
        wikidata_uri text,
        nomisma_uri text
    );
    """
    
    drop_table = """
    DROP TABLE IF EXISTS concepts;
    """
    
    try:
        with sqlite3.connect('nnlp.db') as conn:
            cursor = conn.cursor()
            #drop table if it exists prior to reloading unique concepts
            cursor.execute(drop_table)
            conn.commit()
            
            #create table if it doesn't exist
            cursor.execute(create_table)   
            conn.commit()
            
            cursor.executemany("""INSERT INTO concepts(term,preferred_label,wikidata_uri,nomisma_uri) VALUES(:term, :preferred_label, :wikidata_uri, :nomisma_uri)""", concepts)
            conn.commit()
    
    except sqlite3.OperationalError as e:
        print(e) 


#BEGIN PRCESSING
             
concept_rows = []

files = os.listdir('.')     

for filename in files:
    if "-reconciled.csv" in filename:
        with open(filename, mode ='r') as file:    
            cr = csv.DictReader(file, delimiter=',', quotechar='"')
            for row in cr:
                term = row['term']
                
                row_exists = False
                
                #find term within the concept_rows array
                for concept_row in concept_rows:
                    if concept_row['term'] == term:
                        row_exists = True
                        print(term + " already exists in array")
                        break
                    
                #if row_exists remains false, then insert the row from the source CSV file into concept_rows[]
                if row_exists == False:
                    concept_rows.append(row)
      
        
#print(concept_rows)

#write terminologies into database
print("Inserting into database")
insert_into_db(concept_rows)

print("Processing completed")

#end script