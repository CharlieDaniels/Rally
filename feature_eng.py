#---import saved csv file as utf8
import pandas as pd
import re
import numpy as np
from sklearn.covariance import EllipticEnvelope
from sklearn.svm import OneClassSVM
import matplotlib.pyplot as plt
import matplotlib.font_manager
from sklearn.datasets import load_boston
from sklearn import svm
from sklearn.linear_model import LinearRegression

path = '/Users/Charlotte/Documents/Insight/csv_files/sf_protest_year.csv'

data_frame = pd.read_csv(path,encoding = 'utf-8')

#--clean data
#drop "unnamed column'
data_frame.drop(data_frame.columns[[0]], axis=1, inplace=True)

#clean "NaN" out of captions
data_frame['caption'] = data_frame['caption'].where(data_frame['caption'].notnull(),'nothin')

#function to remove emoji's from captions
def emoji_remove(mytext):
    try:
        Cap_clean = mytext.encode('ascii', 'ignore')
    except AttributeError:
        return None
    mytext = Cap_clean
    return mytext

#Get rid of emoji's in captions in-place
data_frame['caption'] = data_frame['caption'].map(lambda x:emoji_remove(x))

#Add Hourly column in datetime format
data_frame['hourly'] = data_frame['created_time'].map(lambda x:x[:13])


#--Engineer features
def feature_eng(data_frame):
    protest_count=[]
    post_count=[]
    blmatter_count=[]
    justice_count=[]
    breathe_count=[]
    riot_count=[]
      
    for i in range(len(data_frame)):
        post_count.append(1)
        try:
            if re.search(ur'(P|p)rotest\w*',data_frame['caption'][i],re.UNICODE): 
                protest_count.append(1)
            else:
                protest_count.append(0)
        #if the caption is empty:
        except AttributeError:
            protest_count.append(0)
        try: 
            if re.search(ur'(B|b)lacklivesmatter\w*',data_frame['caption'][i],re.UNICODE):
                blmatter_count.append(1)
            else:
                blmatter_count.append(0)
        except AttributeError:
            blmatter_count.append(0)
        try: 
            if re.search(ur'(J|j)ustice\w*',data_frame['caption'][i],re.UNICODE):
                justice_count.append(1)
            else:
                justice_count.append(0)
        except AttributeError:
            justice_count.append(0)
        try: 
            if re.search(ur'(I|i)cantbreathe\w*',data_frame['caption'][i],re.UNICODE):
                breathe_count.append(1)
            else:
                breathe_count.append(0)
        except AttributeError:
            breathe_count.append(0)
        try: 
            if re.search(ur'(R|r)iot\w*',data_frame['caption'][i],re.UNICODE):
                riot_count.append(1)
            else:
                riot_count.append(0)
        except AttributeError:
            riot_count.append(0)
            
    data_frame['protest_count'] = protest_count
    data_frame['post_count'] = post_count
    data_frame['blm_tag_count'] = blmatter_count
    data_frame['justice_count'] = justice_count
    data_frame['breathe_count'] = breathe_count
    data_frame['riot_count'] = riot_count

    return data_frame

#Drop unnecessary columns (hour, DayT, photo, user)
data_frame.drop(data_frame.columns[[2,6,15]], axis=1, inplace=True)

# Groupby hourly
df_oak_group = data_frame.groupby(['hourly'])

#sum after hourly grouping
df_oak_count = df_oak_group.aggregate(np.sum)

#----------Run outlier detection

def outlier_detect(data_frame):
    #pandas to numpy - digestible by scikit
    columns = ['blm_tag_count','protest_count','justice_count','riot_count','breathe_count']
    features = data_frame[list(columns)].values

    clf = OneClassSVM(nu=0.008, gamma=0.05)
    clf.fit(features)
    y_pred = clf.predict(features)

    mask=[y_pred==-1]
    oak_array = np.asarray(data_frame.hourly)
    protest_predict = oak_array[mask]
    protest_hours = list(protest_predict)
    
    return protest_hours