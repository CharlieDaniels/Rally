#---------------Add geotag

#CHANGE NAME
import sqlalchemy
import pandas as pd

#Database info
username='root'
password=''
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

#select only the rows with protest contained in the caption
#select only the rows with protest and blm tag
protest_blm = full_df.ix[full_df.apply(lambda x: x['protest_count'] == 1 or x['blm_tag_count'] == 1, axis=1),:]

# Group
latlong = protest_blm.groupby(['hourly'])['Latitude','Longitude','city'].mean()

latlong = latlong.reset_index()

#---------------Merge predicitons and max liked photo
#Get Cleaned data from SQL

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
oak_tot = pd.DataFrame(sqlResult_group.fetchall())

#weekly for oakland
oak_tot.columns = ['index','DateHour', 'DateT', 'HourT', 'Latitude', 'Longitude', 'YearT', 'caption', 'comment_count', 'created_time', 'id', 'like_count', 'link', 'tags', 'jpg', 'city', 'hourly', 'protest_count', 'post_count', 'blm_tag_count']

oak_tot.tail(2)

#select only the rows with protest and blm tag
protest_in_caption = oak_tot.ix[oak_tot.apply(lambda x: x['protest_count'] == 1 or x['blm_tag_count'] == 1, axis=1),:]
protest_in_caption.tail(2)

#Take max of likes
#max_liked_pic = oak_tot.groupby(['hourly'])['like_count','jpg','city'].max()
max_liked_pic = protest_in_caption.groupby(['hourly'])['like_count','jpg','city'].max()
max_liked_pic

#drop extra 'like' column
max_liked_pic.drop(max_liked_pic.columns[[0]], axis=1, inplace=True)
max_liked_pic.tail(2)

#the table with predictions from outlier detection
oak_per_hour.head(2)

oak_per_hour.drop(oak_per_hour.columns[[1,2]], axis=1, inplace=True)

oak_per_hour.tail(2)

#Merge predictions and top photo
pred_and_top_photo = pd.merge(oak_per_hour, max_liked_pic.reset_index(), on='hourly', how='left')
pred_and_top_photo

pred_and_top_photo.tail(2)

#RENAME
pred_and_top_photo['city'] = 'Oakland'

#IF you want to check results before sending to SQL
#RENAME save protest and tag dataframe to csv file
pred_and_top_photo.to_csv('oak_topphoto_predict.csv')

#print merged table only where protests are predicted to check completion
pred_and_top_photo.loc[pred_and_top_photo['predict_protest'] == -1]

#--------merge geotag table

pred_photo_geo = pd.merge(pred_and_top_photo, latlong, on='hourly', how='left')
pred_photo_geo

pred_photo_geo.loc[pred_photo_geo['predict_protest'] == -1]

#RENAME
#return the above table to SQL
#These are the results from the dataset on whether or not there is a protest in the given table
from sqlalchemy import create_engine
from sqlalchemy.types import String 

#export full dataframe to mysql

oak_yr_predict_sql = pred_photo_geo

engine = create_engine("mysql+pymysql://root@localhost/protest?charset=utf8mb4")
 
oak_yr_predict_sql.to_sql('oak_year_pred_geo', engine, if_exists='append')

con.close()
