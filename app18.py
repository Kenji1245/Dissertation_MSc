from flask import Flask, render_template, request, redirect, url_for, send_file, Response
from pymongo import MongoClient
from lxml import etree
import os
import xml.etree.ElementTree as ET
from io import BytesIO

import csv
import io

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer

import spacy
nlp = spacy.load('en_core_web_sm')
from bs4 import BeautifulSoup

from bson.objectid import ObjectId

from transformers import BertTokenizer

from transformers import BertTokenizer, BertModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

# Load the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Load the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['xmldb']
collection = db['xmlfiles']

collection_label = db['xmlfiles_label']

# Route to the home page 
@app.route('/home')
def home_form():
    return render_template('home.html')

# Route to main upload file page
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to the upload page also includes post function that when file is uploaded, it gets stored onto mongoDB
@app.route('/upload', methods=['POST','GET'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        parse_and_save(filepath)
        parse_and_save_label_data(filepath)
        return 'File uploaded and content saved to MongoDB'
    
# A function which parse (seperates the lines of the xml file into segments) and saves  onto MongoDB
def parse_and_save(filepath):
    with open(filepath, 'rb') as f:

        infile = open(filepath,"r",encoding='utf-8')
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        body = soup.find('body')

        lines = body.get_text().split("\n")

        for line in lines[1:]:
            if(len(line.strip()) > 0): # line.strip - removes any leading or trailing whitespaces
                line_part = line.split("\t") # line.split - splits a string into a list 
        
                info1 = line_part[0]
                info2 = line_part[1]
                info3 = line_part[2]
                post_id = line_part[3]
                main_post = line_part[4]
                post_num = line_part[5]        
                date = line_part[6]
                user = line_part[7]
                title = line_part[8]
                text1 = line_part[9].replace("\n", "")
                save_to_db(info1, info2, info3, post_id, main_post, post_num, date, user, title, text1)

# A function which saves the lines onto MongoDB
def save_to_db(info1, info2, info3, post_id, main_post, post_num, date, user, title, text1):
    document = {'info1':info1, 'info2': info2, 'info3': info3, 'post_id':post_id, 'main_post':main_post,'post_num':post_num, 'date':date, 'user':user, 'title':title, 'text1':text1}
    collection.insert_one(document)

# A function that enables the user to edit the text on MongoDB
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_data(id):
    if request.method == 'POST':
        info1 = request.form['info1']
        info2 = request.form['info2']
        info3 = request.form['info3']
        post_id = request.form['post_id']
        main_post = request.form['main_post']
        post_num = request.form['post_num']
        date = request.form['date']
        user = request.form['user']
        title = request.form['title']
        text1 = request.form['text1']
        myquery = {'_id': ObjectId(id)}
        newvalues = {'$set': {'info1': info1, 'info2': info2, 'info3': info3, 'post_id': post_id, 'main_post': main_post, 'post_num': post_num, 'date': date, 'user': user, 'title': title, 'text1': text1}}
        collection.update_one(myquery, newvalues)
        return redirect(url_for('display_data'))
    item = collection.find_one({'_id': ObjectId(id)})
    return render_template('update.html', item=item)


# A function which displays the data from MongoDB 
@app.route('/display')
def display_data():
    data = list(collection.find())
    return render_template('display.html', data=data)


# A function which parse the labelled data from the file
def parse_and_save_label_data(filepath):
    with open(filepath, 'rb') as f:
        infile = open(filepath,"r",encoding='utf-8')
        contents = infile.read()
        soup = BeautifulSoup(contents,'xml')
        body = soup.find('body')

        labeled_data = body.findAll('segment')

        for i in range(len(labeled_data)):
            label = labeled_data[i]['features']
            text = labeled_data[i].get_text()
            label = str(label)
            text = str(text)
            save_to_db_label(label, text)

# A function which saves the labelled data onto MongoDB
def save_to_db_label(label, text):
    document_label = {'label':label, 'text': text}
    collection_label.insert_one(document_label)

# A function which allows the user to edit label data
@app.route('/edit_label/<id>', methods=['GET', 'POST'])
def edit_label_data(id):
    if request.method == 'POST':
        label = request.form['label']
        text = request.form['text']
        myquery = {'_id': ObjectId(id)}
        newvalues = {'$set': {'label': label, 'text': text}}
        collection_label.update_one(myquery, newvalues)
        return redirect(url_for('display_label_data'))
    label_item = collection_label.find_one({'_id': ObjectId(id)})
    return render_template('update_label.html', label_item=label_item)


# A function which displays the labelled data from MongoDB 
@app.route('/display_label')
def display_label_data():
    label_data = list(collection_label.find())
    return render_template('display_label.html', label_data=label_data)


# A function which searches the database based on information placed on query using regular expression
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        search_field = request.form.get('field')
        filter_criteria = {search_field: {'$regex': query, '$options': 'i'}} if search_field and query else {}
        dict = {'info1': 1, 'info2': 1, 'info3': 1, 'post_id': 1, 'main_post': 1, 'post_num': 1, 'date': 1, 'user': 1, 'title': 1, 'text1': 1}
        data = list(collection.find(filter_criteria, dict))
        return render_template('search.html', data=data)
    return render_template('search.html')
    

# A function which searches the database based on information placed on query for label
@app.route('/search_label', methods=['GET', 'POST'])
def search_label():
    if request.method == 'POST':
        label_query = request.form['query']
        search_label_field = request.form.get('field')
        filter_label_criteria = {search_label_field: {'$regex': label_query, '$options': 'i'}} if search_label_field and label_query else {}
        search_data = list(collection_label.find(filter_label_criteria, {'label': 1, 'text': 1}))
        return render_template('search_label.html', search_data=search_data)
    return render_template('search_label.html')

# A function which searches the database based on information placed on query using BERT NLP
@app.route('/search_BERT', methods=['GET','POST'])
def search_BERT():

    
    if request.method == 'POST':
        # request.form is a document used to request something from the database based on the query inputted by the user
        BERT_query = request.form['query'] 
        dict = {'info1': 1, 'info2': 1, 'info3': 1, 'post_id': 1, 'main_post': 1, 'post_num': 1, 'date': 1, 'user': 1, 'title': 1, 'text1': 1,'vector':1,'similarity_score':1}
        # finds and displays up to the first 20 documents. collection.find(query, projection, option)
        dataTable = list(collection.find({}, dict)) 
        results = []
        for dataEntry in dataTable:

            # Load English stopwords
            stop_words = stopwords.words('english')

            # Download necessary resources
            nltk.download('wordnet')

            # Initialize lemmatizer
            lemmatizer = WordNetLemmatizer()

            # Split the sentence into individual words 
            wordsText = dataEntry['text1'].split()
            wordsQuery = BERT_query.split()

            # Use a list comprehension to remove stop words 
            filtered_wordsText = [word for word in wordsText if word not in stop_words]
            filtered_wordsQuery = [word for word in wordsQuery if word not in stop_words]

            # Lemmatization with part-of-speech (POS) specification
            lemmatized_with_posText = [lemmatizer.lemmatize(word, pos='v') for word in filtered_wordsText]  # 'v' for verbs
            lemmatized_with_posQuery = [lemmatizer.lemmatize(word, pos='v') for word in filtered_wordsQuery]  # 'v' for verbs

            # Join the filtered words back into a sentence 
            filtered_sentenceText = ' '.join(lemmatized_with_posText)
            filtered_sentenceQuery = ' '.join(lemmatized_with_posQuery)

            # Tokenize the sentences
            # Text from database gets tokenised
            tokens1 = tokenizer.tokenize(filtered_sentenceText,padding=True, truncation=True, max_length=50, add_special_tokens = True)
            # Query gets tokenised
            querytokens = tokenizer.tokenize(filtered_sentenceQuery,padding=True, truncation=True, max_length=50, add_special_tokens = True)


            # Add [CLS] and [SEP] tokens
            tokens = ['[CLS]'] + tokens1 + ['[SEP]'] + querytokens + ['[SEP]']

            # Step 2: Encoding Sentences
            # Convert tokens to input IDs
            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            # Step 3: Calculating Sentence Similarity using BERT Transformer

            # Convert tokens to input IDs
            text_input_ids = torch.tensor(tokenizer.convert_tokens_to_ids(tokens1)).unsqueeze(0)  # Batch size 1
            query_input_ids = torch.tensor(tokenizer.convert_tokens_to_ids(querytokens)).unsqueeze(0)  # Batch size 1

            # Obtain the BERT embeddings
            with torch.no_grad():
                outputs1 = model(text_input_ids)
                outputs2 = model(query_input_ids)
                embeddings1 = outputs1.last_hidden_state[:, 0, :]  # [CLS] token
                queryEmbeddings = outputs2.last_hidden_state[:, 0, :]  # [CLS] token

            # Get data form the form
            # print(" ID ",dataEntry["_id"])
            
            # convert the embedding tensor of text into a embedding list
            tensor_list = embeddings1.tolist()

        
            # Updates/add the embedding list of text onto the database.
            collection.update_one(
                {"_id": dataEntry["_id"]},
                {"$set": {"vector":tensor_list}},
                upsert = True
            )

            # Converts the embedding list from database back into a embedding tensor.
            # The storing of embedding vector on the database allows for lower response time since embedding
            # vector can be fetched from database instead of always producing a new one everytime a different 
            # search occurs.
            embedding_tensor = torch.tensor(dataEntry["vector"])

            # Calculate similarity
            similarity_score = cosine_similarity(embedding_tensor, queryEmbeddings)


            # convert similarity_score array into a float
            float_value_ss = float(similarity_score)


            # Update the similarity score on our data entry
            dataEntry['similarity_score'] = float_value_ss
            
            # Also need to update/add the similarity score onto the database
            collection.update_one(
                {"_id": dataEntry["_id"]},
                {"$set": {"similarity_score":float_value_ss}},
                upsert = True
            )
            
        

            # Only include text elements with a similarity of over 70%
            if similarity_score > 0.40:
                results.append(dataEntry)
                # Sorts the results by similarity score in descending order
                results.sort(key=lambda x: x["similarity_score"], reverse = True)
        return render_template('search_BERT.html',data=results)
    
    return render_template('search_BERT.html')

@app.route('/export', methods=['POST'])
def export_to_xml():
    data = collection.find()

    root = ET.Element("root")
    for document in data:
        item = ET.SubElement(root, "item")
        for key, value in document.items():
            if key == "_id":
                continue
            child = ET.SubElement(item, key)
            child.text = str(value)
    
    tree = ET.ElementTree(root)
    xml_data = BytesIO()
    tree.write(xml_data)
    xml_data.seek(0)

    return send_file(xml_data, as_attachment=True, download_name='output.xml', mimetype='application/xml')



if __name__ == '__main__':
    app.run(debug=True)


