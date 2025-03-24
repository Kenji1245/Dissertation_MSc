# Aim of the Project
The aim of the project is to design a NoSQL Database with a user-friendly interface for easy retrieval of unstructured data.

for additional information on this project, please check my report "Designing a NoSQL Database with a user-friendly interface for easy retrieval of unstructured data", which can be accessed on my GitHub. 

# Introduction
This software application contains a search engine that is capable of easily retrieving unstructured data from a NoSQL Database (MongoDB). This is done by implementing a natural language processing method known as BERT to interpret information within text and retrieve it by query.

# Natural Language Processing (BERT)
BERT is a natural language processing model designed to comprehend the context of 
words within a sentence, by using a bidirectional approach to capture the full context 
of a word based on all of its surroundings. The natural processing language goes into several steps:

## Tokenisation 
Tokenisation is the process of separating large strings of written 
language into smaller parts, known as tokens. 
## Stop word removal 
This process involves the removal of words that occur 
commonly across text data. These words typically have no significance in NLP 
tasks and are not very discriminative.  
## Stemming/Lemmatization 
Stemming involves the process of removing 
inflected forms of wards and transforming them into their base or root form. 
Example of the form: “ing”, “s”, “ly” or “ed”. Lemmatization is similar to stemming 
with minor differences. It involves the process of reducing a word to its root 
form. An example of this involves: stemming the word “caring” into “care” 
instead of “car”.  
## Part of Speech (POS) 
POS assigns a tag to each word according to its 
syntactic functions. This process is needed to identify if the given word is a 
“noun”, “verb”, “adjective”, “preposition”, “conjunction” or “interjection” etc.  
## Named entity Recognition (NER) 
NER is a technique which identifies various 
named entities within the textual data and assigns them within a unique 
category. These entities can be a person, time, locations, events, products, 
themes etc. (Wang et al., 2024).

# Tools Used
- HTML (Hypertext Markup Language)
- CSS (Cascading Style Sheets)
- Flask (Python)
- MongoDB (NoSQL)
- XML (Extensible Markup Language)

# Website Pages
Shows the pages for used for user-interface.

## Upload Page
![image](https://github.com/user-attachments/assets/cb8f8707-ed64-46f2-92f4-b8b79dece310)

The upload page allows the user to upload an XML file onto the system, during this process the data from the XML file is stored onto the MongoDB data.

## BERT Search Page
![image](https://github.com/user-attachments/assets/8cc5ec9f-4fb2-4c4e-9d30-694e748b9f40)

The BERT page allows users to search the MongoDB database using natural language processing (BERT). To do this, the user inputs a sentence and selects search. The text from the data and the input from the user goes through a "BERT" process where both are analysed for their contextual meaning and are compared to see how similar they are. The most similar texts are placed on the top of the page in descending order. For example, when the users inputs the word "speed", all texts within the database that have a contextual similarity with the words "speed" will show up on the screen. 

## Keyword Search Page
![image](https://github.com/user-attachments/assets/028cc879-d175-4de2-af94-fd1eab4675ce)


Allows the user to search database using keyword search. For example, when the user inputs the word "complain", all text that contains the word "complain" within the database will show on the screen. 

## View Data Page
![image](https://github.com/user-attachments/assets/9e931a5f-c793-4005-9cfd-b19c78053d5e)

Allows users to view all data on MongoDB database. 



