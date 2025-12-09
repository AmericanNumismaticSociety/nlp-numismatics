# Import necessary libraries
import nltk  # Natural Language Toolkit for text processing

#these need to be downloaded before the first run, but can be commented out later
#nltk.download('maxent_ne_chunker')
#nltk.download('words')
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('averaged_perceptron_tagger')
#nltk.download('punkt_tab')
#nltk.download('averaged_perceptron_tagger_eng')
#nltk.download('maxent_ne_chunker_tab')

import re    # Regular expressions for text cleaning
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords  # Stopwords for text filtering
from nltk.stem.porter import PorterStemmer  # Stemming
from nltk.stem.wordnet import WordNetLemmatizer  # Lemmatization
from nltk import pos_tag, ne_chunk  # Part of speech tagging and named entity recognition
from nltk.tree import Tree

def parse_description(text):
    # Tokenization
    concepts = []
    sentences = sent_tokenize(text)
    for sentence in sentences:       
        
        #get rid of simple "border of dots sentences
        if "border of dots" not in sentence.lower():
            # Remove punctuation characters from the first sentence
            text = re.sub(r"[^a-zA-Z0-9]", " ", sentence)
            
             #look for named entities conforming to 'Name of Place'
            entities = re.findall(r"[A-Z][a-z]+\sof\s[A-Z][a-z]+", text) 
            people_num = re.findall(r"[A-Z][a-z]+[\sI|V|X]+\sof\s[A-Z][a-z]+", text)
            
            #replace these entities from the sentence that is post-processed for NER
            for entity in entities:
                if "Bust" not in entity and "Head" not in entity:
                    concepts.append(entity)
                    sentence = sentence.replace(entity, "")
            
            for entity in people_num:
                if "Bust" not in entity and "Head" not in entity:
                    concepts.append(entity)
                    sentence = sentence.replace(entity, "")
                
            # Tokenization
            words = word_tokenize(text)
                
            # Removing stop words
            stop_words = set(stopwords.words("english"))
            
            #add numismatic stopwords
            stop_words.update(['left', 'right', 'facing'])
            
            #filter nouns into concepts for reconciliation    
            
            #comment these out to run the nnlp FastAPI service, but uncomment them in order to generate the concept CSV prior to reconciliation in generate_concept_list.py
            tagged_words = nltk.pos_tag(words)
            for i, word_pair in enumerate(tagged_words):        
                #process adjectives + nouns as one concept together, then nouns
                if "JJ" in word_pair[1]:
                    if len(tagged_words) > i + 1:
                        concept = word_pair[0] + " " + tagged_words[i + 1][0]
                        concepts.append(concept)
                elif "NN" in word_pair[1]:
                    concept = word_pair[0]
                    concepts.append(concept)
            
            
            # Named entity recognition
            for chunk in ne_chunk(pos_tag(word_tokenize(sentence))):            
                if hasattr(chunk, 'label'):
                    concept = ' '.join(c[0] for c in chunk)
                    concepts.append(concept)
                else:    
                    if "NN" in chunk[1]:
                        word = chunk[0].lower()
                        if word not in stop_words and len(word) >= 3:
                            concepts.append(word)
                            #print(word)
    

    return concepts


