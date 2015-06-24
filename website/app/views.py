from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt

#db = mdb.connect(user="root", host="localhost", db="world_innodb", charset='utf8')
db = mdb.connect(user="root", host="localhost", db="protest", charset='utf8')

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

@app.route('/db')
def cities_page():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name FROM City LIMIT 15;")
        query_results = cur.fetchall()
    cities = ""
    for result in query_results:
        cities += result[0]
        cities += "<br>"
    return cities

@app.route("/db_fancy")
def cities_page_fancy():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")

        query_results = cur.fetchall()
    cities = []
    for result in query_results:
        cities.append(dict(name=result[0], country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities)

@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/output')
def cities_output():
  #pull 'ID' from input field and store it
  #CHANGED!
  #DateHour = request.args.get('ID')
  hourly = request.args.get('ID')
  city_table = request.args.get('city')
  if city_table == 'Oakland':
    # city_t = 'oak_year_predict'
    city_t = 'oak_year_pred_geo' #add geotags
    print city_t
  elif city_table =='San Francisco':
    # city_t = 'sf_year_predict'
    city_t = 'sf_year_pred_geo'

  try:
    with db:
      cur = db.cursor()
	    #just select the city from the world_innodb that the user inputs
	    #CHANGED!
      cur.execute("SELECT predict_protest, jpg, city, hourly, Latitude, Longitude FROM (%s) WHERE hourly IN ('%s');" %(city_t, hourly))
	    #cur.execute("SELECT predict_protest, jpg, city, hourly FROM oak_year_predict WHERE hourly IN ('%s');" %hourly)
	    #cur.execute("SELECT predict_protest FROM oak_wk_predict WHERE DateHour IN ('%s');" %DateHour)
      query_results = cur.fetchall()
	  
    the_city = query_results[0][2]
    the_date = query_results[0][3]
    latitude = query_results[0][4]
    longitude = query_results[0][5]

    if query_results[0][0] == 1:
      the_result = 'There are no protests anticipated at this time'
      picture = 'https://igcdn-photos-e-a.akamaihd.net/hphotos-ak-xaf1/t51.2885-15/11377903_1666635923568228_1658724902_n.jpg'
      return render_template("output.html", picture = picture, the_result = the_result, the_city = the_city, city_table = city_table, the_date = the_date, latitude = 'none', longitude = 'none')
    elif query_results[0][0] == -1:
      the_result = 'A protest is imminent'
      picture = query_results[0][1]#'https://igcdn-photos-f-a.akamaihd.net/hphotos-ak-xfa1/t51.2885-15/11410430_774743549311445_853552540_n.jpg'
      return render_template("output.html", picture = picture, the_result = the_result, the_city = the_city, city_table = city_table, the_date = the_date, latitude = latitude, longitude = longitude)
    else:
      the_result = 'There are no protests anticipated at this time!'
	    #the_result = query_results[0]
      picture = ''
      return render_template("output.html", picture = picture, the_result = the_result, the_city = the_city, city_table = city_table, the_date = the_date, latitude = latitude, longitude = longitude)

	  # return render_template("output.html", picture = picture, the_result = the_result, the_city = the_city, city_table = city_table, the_date = the_date, latitude = latitude, longitude = longitude)
  
  except IndexError:
  	return render_template("oops.html")


@app.route('/notifications')
def cities_notifications():
  return render_template("notifications.html")

@app.route('/slides')
def cities_slides():
  return render_template("slides.html")

  # cities = []
  # for result in query_results:
  #   cities.append(dict(name=result[0], country=result[1], population=result[2]))
  # the_result = ''
  # return render_template("output.html", cities = cities, the_result = the_result)
  
  #USE THIS WHEN you want to dynamically predict new data
  #call a function from a_Model package. note we are only pulling one result in the query
  # pop_input = cities[0]['population']
  # the_result = ModelIt(city, pop_input)
  # return render_template("output.html", cities = cities, the_result = the_result)