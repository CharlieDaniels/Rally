
# coding: utf-8

# In[171]:



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


# In[172]:

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


# In[160]:

#FOR PROTEST TERM FREQUENCY ANALYSIS
#build the tf-idf objects
tfidf = stext.TfidfVectorizer(input='content', ngram_range=(1,2), 
                              stop_words=stext.ENGLISH_STOP_WORDS.union(['oakland','www','worldwide','going','protest','protestors']), min_df=0.02,
                              max_df=0.95, tokenizer=LemmaTokenizer(), strip_accents='unicode', norm='l2')


# In[164]:

#FOR FULL TFIDF
#build the tf-idf objects, lowered min
tfidf = stext.TfidfVectorizer(input='content', ngram_range=(1,2), 
                              stop_words=stext.ENGLISH_STOP_WORDS.union(['oakland','www','worldwide','going','selfie','repost','cali']), min_df=0.005,
                              max_df=0.94, tokenizer=LemmaTokenizer(), strip_accents='unicode', norm='l2')


# In[6]:

#---------------import table
#CHANGE NAME
import sqlalchemy
import pandas as pd

#Your database info
username='root'
password=''
server='localhost'
databaseName='protest'
tableName='oakland_year' #a year's worth of oakland instagram data


# In[7]:

#Create connection with sql database
engineString = 'mysql+pymysql://'+ username +':'+ password +'@'+ server +'/'+databaseName
sqlEngine = sqlalchemy.create_engine(engineString)
con = sqlEngine.connect()


# In[8]:

#works!
#Generate/execute query
column_h = 'hourly'
column_blm = 'blm_tag_count'
column_protest = 'protest_count'
query_group = "SELECT * " + "FROM " +  tableName
print(query_group)


# In[9]:

sqlResult_group = con.execute(query_group)


# In[10]:

#Create dataframe from result
full_df = pd.DataFrame(sqlResult_group.fetchall())


# In[11]:

#weekly for oakland
full_df.columns = ['index','DateHour', 'DateT', 'HourT', 'Latitude', 'Longitude', 'YearT', 'caption', 'comment_count', 'created_time', 'id', 'like_count', 'link', 'tags', 'jpg', 'city', 'hourly', 'protest_count', 'post_count', 'blm_tag_count']


# In[155]:

full_df.tail(2)


# In[63]:

#select only the rows with protest contained in the caption
#select only the rows with protest and blm tag
protest_blm = full_df.ix[full_df.apply(lambda x: x['protest_count'] == 1 or x['blm_tag_count'] == 1, axis=1),:]
protest_blm.head(2)


# In[ ]:

#--------------------------Added table


# In[156]:

captions_df = full_df['caption']


# In[65]:

all_messages = captions_df


# In[166]:

#train on a list of ALL THE COMMENTS
trained = tfidf.fit(all_messages.dropna()) #EVERYTHING
#get the features (words)
feats = np.asarray(tfidf.get_feature_names())
print len(feats)


# In[101]:

protest_captions = protest_blm['caption']


# In[161]:

#train on a list of PROTESTS (occur too rarely in corpus)
trained = tfidf.fit(protest_captions.dropna().values) #EVERYTHING
#get the features (words)
feats = np.asarray(tfidf.get_feature_names())
print len(feats)


# In[162]:

feats


# In[77]:

protest_captions = protest_blm['caption']


# In[167]:

# #transform the comments of type retained and not retained using the tfidf. The
# #comments are passed in as a single comment, and it outputs a sparse matrix of size (1, len(features)

retained = tfidf.transform(protest_captions.dropna()) #protests


# In[168]:

notretained = tfidf.transform(all_messages.dropna()) #not protests


# In[169]:

#get the highest rank features (their indices)
best_retained = sorted(retained.nonzero()[1], key = lambda x:retained[0,x], reverse=True)
best_notretained = sorted(notretained.nonzero()[1], key = lambda x:notretained[0,x], reverse=True) #not protests results


# In[145]:

len(best_retained)


# In[170]:

#the rest of this is just about plotting them
for b in best_retained:
    print retained[0,b], feats[b]


# In[ ]:

for b in best_retained:
    if (retained[0,b] > 0.1) & (retained[0,b]/notretained[0,b] > 2.0):
        print feats[b], retained[0,b], retained[0,b]/notretained[0,b]



for b in best_notretained:
    if (notretained[0,b] > 0.1) & (notretained[0,b]/retained[0,b] > 2.0):
        print feats[b], notretained[0,b], notretained[0,b]/retained[0,b]


compare_feats = list(set(best_retained[:8]).union(best_notretained[:8]))
compare_feats = sorted(compare_feats, key=lambda x:retained[0,x], reverse=True)


plt.gcf().set_size_inches((7,4))
plt.bar(np.arange(len(compare_feats)),[retained[0,c] for c in compare_feats], width=0.3, fc='r', label='retained')
plt.bar(np.arange(len(compare_feats))+0.3, [notretained[0,c] for c in compare_feats], width=0.3, fc='b', label='churned')
plt.ylabel('tf-idf term frequency score', size=16)
plt.legend(loc=1, fontsize=16)
plt.xticks(np.arange(len(compare_feats))+0.3, feats[compare_feats], rotation=90)
plt.tick_params(labelsize=16)
plt.tick_params(axis='x', pad=-10)
plt.yticks(np.arange(0,0.45,0.1), np.arange(0,0.45,0.1))
plt.xlim((-0.3,len(compare_feats)))
#plt.savefig('../../site/figures/tf-idf-comments', bbox_inches='tight')

