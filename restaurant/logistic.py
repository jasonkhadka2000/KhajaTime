import pandas as pd
from pathlib import Path
import pickle
import os 
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from joblib import dump, load
from scipy import sparse

#loading the model
def load_model():
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL_FILE = os.path.join(BASE_DIR, 'restaurant/models/modelf.joblib')
    # with open(MODEL_FILE, 'rb') as f:
    #     model = pickle.load(f)
    # return model
    model1=load(MODEL_FILE)
    return model1

def load_vector():
    BASE_DIR = Path(__file__).resolve().parent.parent
    Vector_FILE = os.path.join(BASE_DIR, 'restaurant/models/vectorizerf.joblib')
    # with open(Vector_FILE, 'rb') as f:
    #     vector = pickle.load(f)
    # return vector
    vector1=load(Vector_FILE)
    return vector1

#creating a sampledataFrame
def createDataFrame(review):
    tableRows=[
            [45,50,review]
        ]
    columns=[ 'HelpfulnessNumerator','HelpfulnessDenominator','Text']
    data=pd.DataFrame(columns=columns,data=tableRows)
    return data

#preprocessing the data
import re
from bs4 import BeautifulSoup

def decontracted(phrase):
    # specific
    phrase = re.sub(r"won't", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)

    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase

stopwords= set(['br', 'the', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",\
            "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', \
            'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their',\
            'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', \
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', \
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', \
            'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',\
            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',\
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',\
            'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than', 'too', 'very', \
            's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', \
            've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn',\
            "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',\
            "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", \
            'won', "won't", 'wouldn', "wouldn't"])

from tqdm import tqdm

def preProcessReviews(data):
    preprocessed_reviews = []
    for sentance in tqdm(data['Text'].values):
        sentance = re.sub(r"http\S+", "", sentance)
        sentance = BeautifulSoup(sentance, 'lxml').get_text()
        sentance = decontracted(sentance)
        sentance = re.sub("\S*\d\S*", "", sentance).strip()
        sentance = re.sub('[^A-Za-z]+', ' ', sentance)
        sentance = ' '.join(e.lower() for e in sentance.split() if e.lower() not in stopwords)
        preprocessed_reviews.append(sentance.strip())
    return preprocessed_reviews


#main prediction
def prediction(review):
    sentiment={
        1:"postive",
        0:"not postive",
    }
    model = load_model()
    vector=load_vector()
    data=createDataFrame(review)
    preProcessedReviews=preProcessReviews(data)
    print(preProcessedReviews)
    sample_review= [ preProcessedReviews[i] for i in data.index.values]
    data['preprocessed']=sample_review
    data=data.drop(columns=['Text'])
    print(data)

    # count_vect=CountVectorizer()
    final_test_vectors = vector.transform(data['preprocessed'].values)
    test_feats = data[['HelpfulnessNumerator' ,	'HelpfulnessDenominator']].values
    test_data = sparse.hstack(( test_feats, final_test_vectors))
    print("the result is")
    pred=model.predict(test_data)
    return sentiment[pred[0]]