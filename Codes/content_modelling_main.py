# Importing necessary packages
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
from pymongo import MongoClient
import time
import json

import cv2
import os
from PIL import Image
import sys
import textwrap

from gtts import gTTS
from googletrans import Translator
from gingerit.gingerit import GingerIt
from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
import pyLDAvis
import pyLDAvis.gensim
import warnings
warnings.filterwarnings("ignore")
import requests
import nltk
import regex as re
import pathlib
nltk.download('all')


# Setting up FLASK Cross Origin 
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)


# Connecting MongoDB NoSQL Database acting as an API source 
database = MongoClient("mongodb+srv://maltesh:27861518@mongo-1.emgh2.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = database.sanjan_fyp
news_data = db["news_data"] # selecting table news_data 



# Get the summary of the text
def get_summary(text, pct):
    # using summarize for modelling content to required length of text
    summary = summarize(text,ratio=pct,split=True)
    return summary

# Get the keywords of the text
def get_keywords(text):
    # extracting keywords 
    res = keywords(text, ratio=0.1, words=None, split=False, scores=False, pos_filter=('NN', 'JJ'), lemmatize=False, deacc=False)
    res = res.split('\n')
    return res

# Tokenize the sentence into words & remove punctuation
def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

def split_sentences(text):
    sentence_delimiters = re.compile(u'[\\[\\]\n.!?]')
    sentences = sentence_delimiters.split(text)
    #print(sentences)
    return sentences

def split_into_tokens(text):
    tokens = nltk.word_tokenize(text)
    #print(tokens)
    return tokens

def textSpace(data):
    rx = r"\.(?=\S)"
    result = re.sub(rx, ". ", data)
    return result

# Performing OCR Process
def get_string(img_path):
    from PIL import Image
    from pytesseract import image_to_string 
    image = Image.open(img_path)
    result = image_to_string(image,lang='eng')
    return result


# Flask routing starts here

@app.route('/text_content', methods=['GET', 'POST'])
@cross_origin()
def text_content():
    posteddata = request.get_json()
    output_text_language = posteddata["slan"]
    actual_text = posteddata["inptext"]
    language_code = {"marathi":"mr","bengali":"bn","hindi":"hi","telugu":"te","kannada":"kn","german":"de","french":"fr","japanese":"ja","punjabi":"pa"}
    data = str(actual_text)
    data = textSpace(data)
    summerized_data = get_summary(data, 0.4)
    keywords_summerized_text = get_keywords(data)
    sentence_split = split_sentences(data)
    sentence_split_tokens = split_into_tokens(data)
    result = []
    for i in range(len(summerized_data)):
        result.append(summerized_data[i])
    final_data = ' '.join(result)
    final_data = final_data.replace("[","")
    final_data = final_data.replace("\\","")
    final_data = final_data.replace('"',"")
    total_length = 0 
    for i in range(len(summerized_data)):
        total_length += len(summerized_data[i])
    try:
        parser = GingerIt()
        summerized_text_final = parser.parse(final_data)['result']
    except:
        summerized_text_final = final_data
    translator = Translator()
    language_translated = translator.translate(final_data, dest=language_code[output_text_language])
    translated_text = language_translated.text
    try:
        myobj = gTTS(text=translated_text, lang=language_code[output_text_language], slow=False)
        myobj.save("/home/maltesh/Maltesh/Projects/Content-model/Content-Modelling-System/CMS/Transit Storage/audio/audio.mp3")
        audio_conversion = "success"
    except:
        audio_conversion = "failure"
    final_return_message = {
        "initial_length":len(data),
        "summerized_length":total_length,
        "converted_language_to":output_text_language,
        "keywords_identified":keywords_summerized_text,
        "summerized_text":summerized_text_final,
        "summerized_text_in_language":translated_text,
        "audio_format":audio_conversion,
        "status":200
        }
    return jsonify(final_return_message)



@app.route('/api_content', methods=['GET', 'POST'])
@cross_origin()
def api_content():
    posteddata = request.get_json()
    news_category = posteddata["category"]
    output_text_language = posteddata["slan"]
    news_heading = posteddata["heading"]
    language_code = {"marathi":"mr","bengali":"bn","hindi":"hi","telugu":"te","kannada":"kn","german":"de","french":"fr","japanese":"ja","punjabi":"pa"}
    data = news_data.find({"category":news_category,"heading":news_heading})[0]['news']
    data = textSpace(data)
    summerized_data = get_summary(data, 0.3)
    keywords_summerized_text = get_keywords(data)
    sentence_split = split_sentences(data)
    sentence_split_tokens = split_into_tokens(data)
    result = []
    for i in range(len(summerized_data)):
        result.append(summerized_data[i])
    final_data = ' '.join(result)
    final_data = final_data.replace("[","")
    final_data = final_data.replace("\\","")
    final_data = final_data.replace('"',"")
    total_length = 0
    for i in range(len(summerized_data)):
        total_length += len(summerized_data[i])
    try:
        parser = GingerIt()
        summerized_text_final = parser.parse(final_data)['result']
    except:
        summerized_text_final = final_data
    translator = Translator()
    language_translated = translator.translate(final_data, dest=language_code[output_text_language])
    translated_text = language_translated.text
    try:
        myobj = gTTS(text=translated_text, lang=language_code[output_text_language], slow=False)
        myobj.save("/home/maltesh/Maltesh/Projects/Content-model/Content-Modelling-System/CMS/Transit Storage/audio/audio.mp3")
        audio_conversion = "success"
    except:
        audio_conversion = "failure"

    final_return_message = {
        "initial_length":len(data),
        "summerized_length":total_length,
        "converted_language_to":output_text_language,
        "keywords_identified":keywords_summerized_text,
        "summerized_text":summerized_text_final,
        "summerized_text_in_language":translated_text,
        "audio_format":audio_conversion,
        "status":200
        }
    return jsonify(final_return_message)



@app.route('/image_content', methods=['GET', 'POST'])
@cross_origin()
def poimage_contentst():
    posteddata = request.get_json()
    output_text_language = posteddata["slan"]
    string_converted = get_string('/home/maltesh/Maltesh/Projects/Content-model/Content-Modelling-System/CMS/Transit Storage/OCR-Image-Store/image.jpeg')
    input_string = textwrap.indent(text=string_converted, prefix=' ')
    input_string = input_string.replace("\n","")
    input_string = input_string.replace("  ","")
    input_string = input_string.replace("ABSTRACT","")
    input_string = input_string.replace("INTRODUCTION","")
    input_string = input_string.split(' ')
    input_string = ' '.join(input_string)
    language_code = {"marathi":"mr","bengali":"bn","hindi":"hi","telugu":"te","kannada":"kn","german":"de","french":"fr","japanese":"ja","punjabi":"pa"}
    data = str(input_string)
    data = textSpace(data)
    summerized_data = get_summary(data, 0.2)
    keywords_summerized_text = get_keywords(data)
    sentence_split = split_sentences(data)
    sentence_split_tokens = split_into_tokens(data)
    result = []
    for i in range(len(summerized_data)):
        result.append(summerized_data[i])
    final_data = ' '.join(result)
    final_data = final_data.replace("[","")
    final_data = final_data.replace("\\","")
    final_data = final_data.replace('"',"")
    total_length = 0
    for i in range(len(summerized_data)):
        total_length += len(summerized_data[i])
    try:
        parser = GingerIt()
        summerized_text_final = parser.parse(final_data)['result']
    except:
        summerized_text_final = final_data
    translator = Translator()
    language_translated = translator.translate(final_data, dest=language_code[output_text_language])
    translated_text = language_translated.text
    try:
        myobj = gTTS(text=translated_text, lang=language_code[output_text_language], slow=False)
        myobj.save("/home/maltesh/Maltesh/Projects/Content-model/Content-Modelling-System/CMS/Transit Storage/audio/audio.mp3")
        audio_conversion = "success"
    except:
        audio_conversion = "failure"
    final_return_message = {
        "initial_length":len(data),
        "summerized_length":total_length,
        "converted_language_to":output_text_language,
        "keywords_identified":keywords_summerized_text,
        "summerized_text":summerized_text_final,
        "summerized_text_in_language":translated_text,
        "audio_format":audio_conversion,
        "status":200
        }
    return jsonify(final_return_message)


@app.route('/doc_upload', methods=['GET', 'POST'])
@cross_origin()
def doc_upload():
    posteddata = request.get_json()
    output_text_language = posteddata["slan"]
    f = open("/home/maltesh/Maltesh/Projects/Content-model/Content-Modelling-System/CMS/Transit Storage/Document-Store/file.txt", "r")
    data = f.read()
    language_code = {"marathi":"mr","bengali":"bn","hindi":"hi","telugu":"te","kannada":"kn","german":"de","french":"fr","japanese":"ja","punjabi":"pa"}
    summerized_data = get_summary(data, 0.4)
    keywords_summerized_text = get_keywords(data)
    sentence_split = split_sentences(data)
    sentence_split_tokens = split_into_tokens(data)
    result = []
    for i in range(len(summerized_data)):
        result.append(summerized_data[i])
    final_data = ' '.join(result)
    final_data = final_data.replace("[","")
    final_data = final_data.replace("\\","")
    final_data = final_data.replace('"',"")
    total_length = 0
    for i in range(len(summerized_data)):
        total_length += len(summerized_data[i])
    try:
        parser = GingerIt()
        summerized_text_final = parser.parse(final_data)['result']
    except:
        summerized_text_final = final_data
    translator = Translator()
    language_translated = translator.translate(final_data, dest=language_code[output_text_language])
    translated_text = language_translated.text
    try:
        myobj = gTTS(text=translated_text, lang=language_code[output_text_language], slow=False)
        myobj.save("/home/maltesh/Maltesh/Projects/Content-model/Content-Modelling-System/CMS/Transit Storage/audio/audio.mp3")
        audio_conversion = "success"
    except:
        audio_conversion = "failure"
    final_return_message = {
        "initial_length":len(data),
        "summerized_length":total_length,
        "converted_language_to":output_text_language,
        "keywords_identified":keywords_summerized_text,
        "summerized_text":summerized_text_final,
        "summerized_text_in_language":translated_text,
        "audio_format":audio_conversion,
        "status":200
        }
    return jsonify(final_return_message)



@app.route('/fileupload',methods=['POST'])
@cross_origin()
def fileupload():
    current_directory = pathlib.Path(__file__).parent.absolute()
    file = request.files['image']
    file.save(os.path.join(current_directory,"../Transit Storage/OCR-Image-Store", "image.jpeg"))
    return 'file saved'    


@app.route('/textupload',methods=['POST'])
@cross_origin()
def textupload():
    current_directory = pathlib.Path(__file__).parent.absolute()
    file = request.files['doc']
    file.save(os.path.join(current_directory,"../Transit Storage/Document-Store", "file.txt"))
    return 'file saved'    


# Main routing segment
if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
