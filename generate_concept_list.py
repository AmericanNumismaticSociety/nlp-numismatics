#Author: Ethan Gruber
#Date Modified: August 2025
#Function: iterate through the obverse and reverse type description sheets for a typology in order to generate a list of NLP concepts for post-processing reconcilation in OpenRefine

# Import necessary libraries
import argparse, csv, json, urllib.request
import numpy as np

#import numismatic parser
from nparser import parse_description

#using argparse for command line arguments
parser = argparse.ArgumentParser(prog='generate_concept')
parser.add_argument('-p', '--project', help="specify typology project code")
parser.add_argument('-f', '--file', help="load text file with a description on each line")

#output unique concept terms into a CSV file for subsequent reconcilation
def write_concept_csv(concepts, project):
    with open(project + "-concepts.csv", "w") as file:
        print("Writing " + project + "-concepts.csv")
        file.write("term\n")    
        for line in concepts:
            file.write(line + "\n")
   
#iterate through all CSV URLs for type descriptions and parse with NLP tools         
def process_type_descriptions(description_urls):
    concepts = []
    
    for url in description_urls:
        response = urllib.request.urlopen(url)
        lines = [l.decode('utf-8') for l in response.readlines()]
        cr = csv.DictReader(lines, delimiter=',', quotechar='"')
    
        for row in cr:
            concept_list = parse_description(row['en'])
            concepts = concepts + concept_list
        
    #filter out duplicate concepts
    unique = np.array(list(set(concepts)))
    unique.sort()
    
    return unique

#extract CSV URLs for a project given a command line argument
def extract_type_descriptions(project):
    with open('/usr/local/projects/typology-update/projects.json', 'r') as file:
        data = json.load(file)
        
        description_urls = []
        
        for typology in data['projects']:
            if typology['name'] == project:
                if 'o' in typology and 'r' in typology:
                    description_urls.append(typology['o'])
                    description_urls.append(typology['r'])
                else:
                    if 'parts' in typology:
                        for part in typology['parts']:
                            description_urls.append(part['o'])
                            description_urls.append(part['r'])
                            
        return description_urls
            



#BEGIN PROCESSING
args = parser.parse_args()

#if the project argument is set, then load the CSV URLs from typology-update JSON file
if args.project is not None:
    project = args.project
    
    print("Processing " + project)
    
    description_urls = extract_type_descriptions(project)
    
    concepts = process_type_descriptions(description_urls)
    
    write_concept_csv(concepts, project)

#if the file argument is set, then load descriptions from a text file, with one type description per line
elif args.file is not None:
    filename = args.file
    
    print("File: " + filename)
else:
    print("No project or file specified")
       
    
        
                
   


#description_urls = ['https://docs.google.com/spreadsheets/d/e/2PACX-1vRxzNNLc4uLaPfNO60mNG4QJ09nWg0D4mosOCM-eQfbO4vqTj8skEE6zkJ7IbLdCrHVbWslehKDh5LN/pub?gid=1411485313&single=true&output=csv','https://docs.google.com/spreadsheets/d/e/2PACX-1vRxzNNLc4uLaPfNO60mNG4QJ09nWg0D4mosOCM-eQfbO4vqTj8skEE6zkJ7IbLdCrHVbWslehKDh5LN/pub?gid=1676912151&single=true&output=csv']


#text = "Trophy; on right, togate figure of L. Aemilius Paullus; on left, three captives (King Perseus of Macedon, Alexander III of Macedon and his sons). Border of dots."
#parse_description(text)




