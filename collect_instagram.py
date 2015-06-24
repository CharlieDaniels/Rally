#collect all instagram posts in 1.5 years in a given city

from instagram import client, subscriptions
from instagram.client import InstagramAPI
import urlparse
import urllib
from pandas import Series, DataFrame
import pandas as pd
import re
import numpy as np
from datetime import datetime
from pytz import timezone
import pytz
import matplotlib
import matplotlib.pyplot as plt
from pandas import Series,DataFrame
import traceback
import time

#gather data from instagram

def collect_instagram(city):

  api = InstagramAPI(client_id='CLIENT_ID', 
                     client_secret='CLIENT_SECRET')

  max_tag_id = None

  protest_dict = {'YearT':[],'DateT':[],'DayT':[],'DateHour':[],'HourT':[],'created_time':[],'Latitude':[],'Longitude':[],'Photo':[],'caption':[],'comment_count':[],'like_count':[],'id':[],'link':[],'user':[],'tags':[]}

  tag_dict = {'id':[],'tags':[],'created_time':[],'DateHour':[]}

  start = time.time()

  while True:
    try:  
        tagged, next_url = api.tag_recent_media(count=30,tag_name='city',max_tag_id=max_tag_id)
        #throttle to 3600/hour
        end = time.time()
        if (end-start) < 1:
          time.sleep(1-(end-start))
        start = time.time()
          
        for media in tagged:
          media_test = media.__dict__
          timet = media_test['created_time']
          aware_timet = pytz.utc.localize(timet)
          Timet = aware_timet.astimezone(timezone('US/Pacific'))
          DayT = Timet.strftime('%A')
          DateHour = Timet.strftime('%Y%B%d%H')
          DateT = Timet.strftime('%B%d')
          YearT = Timet.strftime('%Y')
          HourT = Timet.strftime('%H')  
          try:
            locationt = str(media_test['location'])

          except KeyError:
            locationt = ''

          Locat = re.search(r'Point: \((\S+), (\S+)\)\)',locationt)    
          try:
            LatitudeT = float(Locat.groups(1)[0])
            LongitudeT = float(Locat.groups(1)[1])
          except AttributeError:
            LatitudeT = np.nan
            LongitudeT = np.nan

          try:
            Tags = media_test['tags']

          except KeyError:
            Tags = ''

          Id = media_test['id']
          Link = media_test['link']
          User = media_test['user']
          Images = media_test['images']
          caption = media_test['caption']
          comment_count = media_test['comment_count']
          like_count = media_test['like_count']

          protest_dict['id'].append(Id)
          protest_dict['link'].append(Link)
          protest_dict['user'].append(User)
          protest_dict['DayT'].append(DayT)
          protest_dict['HourT'].append(HourT)
          protest_dict['DateHour'].append(DateHour)
          protest_dict['YearT'].append(YearT)
          protest_dict['tags'].append(Tags)
          protest_dict['DateT'].append(DateT)
          protest_dict['created_time'].append(Timet)
          protest_dict['Latitude'].append(LatitudeT)
          protest_dict['Longitude'].append(LongitudeT)
          protest_dict['Photo'].append(Images)
          protest_dict['caption'].append(caption)
          protest_dict['comment_count'].append(comment_count)
          protest_dict['like_count'].append(like_count)
          
          tag_dict['id'].append(Id)
          tag_dict['tags'].append(Tags)
          tag_dict['created_time'].append(Timet)
          tag_dict['DateHour'].append(DateHour)

        #take 1 year of data  
        if timet.month == 6 and timet.year == 2014:
          break
    
    except Exception, e:
      print 'caught error in body, continuing: %s' % e
      traceback.print_exc()


    p = urlparse.urlparse(next_url)
    max_tag_id = urlparse.parse_qs(p.query)['max_tag_id'][0]

  #construct dataframes
  df_protest = DataFrame(protest_dict)
  df_tag = DataFrame(tag_dict)
  #extract standard resolution photo from JSON
  df_protest['jpg'] = df_protest['Photo'].map(lambda x: x['standard_resolution'].url)
  #save as csv
  df_protest.to_csv('protest_year.csv')
  df_tag.to_csv('tag_year.csv')








