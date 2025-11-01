from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection,Blueprint, datetime
import pymysql.cursors


search_bp=Blueprint("search", __name__)
conn=get_connection()


# display search page
@search_bp.route('/search')
def search():
	return render_template('search.html')


# search for flights
@search_bp.route('/searchFlight', methods=['GET', 'POST'])
def searchFlight():
	#grabs information from the forms
	source = request.form['source']
	destination = request.form['destination']
	depart_date = datetime.strptime(request.form['depart_date'], '%Y-%m-%d')
	return_date = request.form['return_date']

	# get name of source airport
	cursor = conn.cursor()
	query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
	cursor.execute(query, (source, source))
	source_airport = cursor.fetchone()

	# get name of destination airport
	cursor.execute(query, (destination, destination))
	destination_airport = cursor.fetchone()
	cursor.close()

	# check that both airports exist
	if(not (source_airport and destination_airport)):
		error = "No Airports found"
		return render_template("search.html", error = error)
	else:
		# find one way flights
		cursor = conn.cursor()
		query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)=%s and month(dep_date_time)=%s and day(dep_date_time)=%s'
		cursor.execute(query, (source_airport['name'], destination_airport['name'], depart_date.year, depart_date.month, depart_date.day))
		one_way = cursor.fetchall()

		# if return_date was given, find round_trip flights
		if(return_date):
			return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d')
			cursor.execute(query, (destination_airport['name'], source_airport['name'], return_date.year, return_date.month, return_date.day))
			round_trip = cursor.fetchall()
			cursor.close()
		else:
			round_trip = None

		# return one_way and round_trip
		if(one_way or round_trip):
			return render_template("search.html", one_way = one_way, round_trip= round_trip)
		else:
			error = "No flights found"
			return render_template("search.html", error = error)


