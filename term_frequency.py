import sys, re 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import collections
import pandas as pd
import datetime
import pickle

import sklearn.feature_extraction.text as stext
from nltk import word_tokenize          
from nltk.stem import WordNetLemmatizer

#this is the lemmatizer that separates the words. 
#you need to strip punctuation and capital letters (this does that)
class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        doc = doc.lower()
        doc = re.sub("[^a-z]", " ", doc) #replace punctuation with spaces
        # doc = re.sub("thanks", "thank", doc)
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if len(self.wnl.lemmatize(t)) > 2]

#build the tf-idf objects, adding an extra stop word (ignored)
tfidf = stext.TfidfVectorizer(input='content', ngram_range=(1,2), 
                              stop_words=stext.ENGLISH_STOP_WORDS.union(['oakland','www','worldwide']), min_df=0.02,
                              max_df=0.95, tokenizer=LemmaTokenizer(), strip_accents='unicode', norm='l2')


#---------------import table
#CHANGE NAME
import sqlalchemy
import pandas as pd

#Your database info
username='root'
password='YOUR_PASSWORD'
server='localhost'
databaseName='protest'
tableName='oakland_year' #a year's worth of oakland instagram data

#Create connection with sql database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName
sqlEngine = sqlalchemy.create_engine(engineString)
con = sqlEngine.connect()

#Generate/execute query
column_h = 'hourly'
column_blm = 'blm_tag_count'
column_protest = 'protest_count'
query_group = "SELECT * " + "FROM " +  tableName
print(query_group)

sqlResult_group = con.execute(query_group)

#Create dataframe from result
full_df = pd.DataFrame(sqlResult_group.fetchall())

#weekly for oakland
full_df.columns = ['index','DateHour', 'DateT', 'HourT', 'Latitude', 'Longitude', 'YearT', 'caption', 'comment_count', 'created_time', 'id', 'like_count', 'link', 'tags', 'jpg', 'city', 'hourly', 'protest_count', 'post_count', 'blm_tag_count']

protest_blm = full_df.ix[full_df.apply(lambda x: x['protest_count'] == 1 or x['blm_tag_count'] == 1, axis=1),:]
protest_blm.head(2)

all_messages = full_df['caption']

#train on a list of all the comments
trained = tfidf.fit(all_messages.dropna()) #EVERYTHING
#get the features (words)
feats = np.asarray(tfidf.get_feature_names())
print len(feats)

protest_captions = protest_blm['caption']

#train on a list of PROTESTS (occur too rarely in corpus)
trained = tfidf.fit(protest_captions.dropna().values) #EVERYTHING
#get the features (words)
feats = np.asarray(tfidf.get_feature_names())
print len(feats)

retained = tfidf.transform(protest_captions.dropna()) #protests

len(protest_captions.values)

#get the highest rank features (their indices)
best_retained = sorted(retained.nonzero()[1], key = lambda x:retained[0,x], reverse=True)
#best_notretained = sorted(notretained.nonzero()[1], key = lambda x:notretained[0,x], reverse=True) #not protests results

for b in best_retained:
    print retained[0,b], feats[b]

