#Import packages
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from datetime import datetime
import pandas as pd

#Configure MySQL
conn = pymysql.connect(host= 'localhost', #connect to your own host
                       user='root', # use your own user
                       password = '17012005', # use your own password
                       db='PythonProject', # this is the project you create and then run the SQL Queries in
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


#Initialize the app from Flask
app = Flask(__name__)

# display index page
@app.route('/')
def hello():
	return render_template('index.html')


# display customerLogin page
@app.route('/customerLogin')
def customerLogin():
	return render_template('customerLogin.html')


# authenticate customerLogin
@app.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
	#grabs information from the forms
	email = request.form['email']
	password = request.form['password']
	
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s and md5(password) = md5(%s)'
	cursor.execute(query, (email, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	# check if the customer data was found
	if(data):
		#creates a session for the the user
		#session is a built in
		session['email'] = email
		return redirect(url_for('customerHome'))
	else:
		#returns an error message to the html page
		error = 'Invalid login'
		return render_template('customerLogin.html', error=error)


# display staffLogin page
@app.route('/staffLogin')
def staffLogin():
	return render_template('staffLogin.html')


# authenticates staffLogin
@app.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Airline_Staff WHERE username = %s and md5(password) = md5(%s)'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None

	# check if user exists
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('staffHome'))
	else:
		#returns an error message to the html page
		error = 'Invalid login'
		return render_template('staffLogin.html', error=error)


# display customerRegister page
@app.route('/customerRegister')
def customerRegister():
	return render_template('customerRegister.html')


# authenticates customerRegister
@app.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
	#grabs information from the forms
	email = request.form['email']
	name = request.form['name']
	password = request.form['password']
	building_number = int(request.form['building_number'])
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phone_number = int(request.form['phone_number'])
	passport_number = int(request.form['passport_number'])
	passport_exp = request.form['passport_exp']
	passport_country = request.form['passport_country']
	date_of_birth = request.form['date_of_birth']
	
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Customer WHERE email = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None

	# check if the customer already exists
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('customerRegister.html', error = error)
	else:
		# add customer to system
		cursor = conn.cursor()
		ins = 'INSERT INTO Customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_exp, passport_country, date_of_birth))
		conn.commit()
		cursor.close()

		# send success message to index
		message = "Customer "+email+" successfully created!"
		return render_template('index.html', message = message)


# display staffRegister page
@app.route('/staffRegister')
def staffRegister():
	return render_template('staffRegister.html')


# authenticates staffRegister
@app.route('/staffRegisterAuth', methods=['GET', 'POST'])
def staffRegisterAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	date_of_birth = request.form['date_of_birth']
	name = request.form['airline_name']
	phone_number_1 = request.form['phone_number_1']
	phone_number_2 = request.form['phone_number_2']
	phone_number_3 = request.form['phone_number_3']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None

	# check if the airline_staff already exists
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('staffRegister.html', error = error)
	else:
		#cursor used to send queries
		cursor = conn.cursor()
		#executes query
		query = 'SELECT * FROM Airline WHERE name = %s'
		cursor.execute(query, (name))
		#stores the results in a variable
		data1 = cursor.fetchone()
		cursor.close()

		# check that the airline exists
		if(data1):
			# add staff to the system
			cursor = conn.cursor()
			ins = 'INSERT INTO Airline_Staff VALUES(%s, %s, %s, %s, %s, %s)'
			cursor.execute(ins, (username, password, first_name, last_name, date_of_birth, name))
			conn.commit()
			cursor.close()

			# send success message to index
			message = "Airline Staff "+username+" successfully created!"
			return render_template('index.html', message = message)
		else:
            #If the the airline doesn't exist, redo
			error = "This airline does not exist"
			return render_template('staffRegister.html', error = error) 


# display search page
@app.route('/search')
def search():
	return render_template('search.html')


# search for flights
@app.route('/searchFlight', methods=['GET', 'POST'])
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


# display checkStatus page
@app.route('/checkStatus')
def checkStatus():
	return render_template('checkStatus.html')

		
# check flight status
@app.route('/status', methods=['GET', 'POST'])
def status():
	#grabs information from the forms
	airline_name = request.form['airline_name']
	flight_number = request.form['flight_number']
	departure_date = datetime.strptime(request.form['departure_date'], '%Y-%m-%d')

	# get information on searched flights
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name=%s and flight_number=%s and year(dep_date_time) = %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
	cursor.execute(query, (airline_name, flight_number, departure_date.year, departure_date.month, departure_date.day))
	statuses = cursor.fetchall()
	cursor.close()

	# display found flights or error
	if(statuses):
		return render_template("checkStatus.html", statuses= statuses)
	else:
		error = "No flights found"
		return render_template("checkStatus.html", error = error)


# redirect to customerHome and display customer name
@app.route('/customerHome')
def customerHome():
	email  = session['email']
	cursor = conn.cursor()
	query = 'SELECT name FROM Customer WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()['name'] 
	cursor.close()
	return render_template('customerHome.html', name= data)


# view customer's future and past flights
@app.route('/viewMyFlights')
def viewMyFlights():
	# get session email
	email  = session['email']
	
	# show future flights
	cursor = conn.cursor()
	query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and dep_date_time> CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	future_flights = cursor.fetchall()
	cursor.close()

	# show past flights
	cursor = conn.cursor()
	query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and dep_date_time< CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	past_flights = cursor.fetchall()
	cursor.close()

	return render_template("viewMyFlights.html", future_flights = future_flights, past_flights = past_flights)


# view customer's future and past flights, as well as searched flights
@app.route('/searchMyFlights', methods=['GET', 'POST'])
def searchMyFlights():

	# get session email
	email  = session['email']
	
	# show future flights
	cursor = conn.cursor()
	query = 'SELECT * FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and dep_date_time> CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	future_flights = cursor.fetchall()
	cursor.close()

	# show past flights
	cursor = conn.cursor()
	query = 'SELECT * FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and dep_date_time< CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	past_flights = cursor.fetchall()
	cursor.close()

	# allow to search by date range, destination, or source 
	start_date= request.form['start_date']
	end_date = request.form['end_date']
	destination_airport = request.form['destination']
	source_airport = request.form['source']

	# get destination airport name
	if(destination_airport):	
		cursor = conn.cursor()
		query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
		cursor.execute(query, (destination_airport, destination_airport))
		destination_airport = cursor.fetchone()
		cursor.close()
		if(destination_airport):
			destination_airport = destination_airport['name']
		else:
			error = "No airport found"
			return render_template("viewMyFlights.html", error = error, future_flights = future_flights, past_flights = past_flights)

	# get source airport name
	if(source_airport):
		cursor = conn.cursor()
		query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
		cursor.execute(query, (source_airport, source_airport))
		source_airport = cursor.fetchone()
		cursor.close()
		if(source_airport):
			source_airport = source_airport['name']
		else:
			error = "No airport found"
			return render_template("viewMyFlights.html", error = error, future_flights = future_flights, past_flights = past_flights)
	
	# find correct query based on information given
	if(start_date):
		if(end_date):
			if(source_airport):
				if(destination_airport):
					cursor = conn.cursor()
					query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
					cursor.execute(query, (start_date, end_date, source_airport, destination_airport))
					search_flights = cursor.fetchall()
					cursor.close()
				else:
					cursor = conn.cursor()
					query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s'
					cursor.execute(query, (start_date, end_date, source_airport))
					search_flights = cursor.fetchall()
					cursor.close()
			elif(destination_airport):
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s and arr_airport= %s'
				cursor.execute(query, (start_date, end_date, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s'
				cursor.execute(query, (start_date, end_date))
				search_flights = cursor.fetchall()
				cursor.close()
		else:
			if(source_airport):
				if(destination_airport):
					cursor = conn.cursor()
					query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_airport= %s and arr_airport=  %s'
					cursor.execute(query, (start_date, source_airport, destination_airport))
					search_flights = cursor.fetchall()
					cursor.close()
				else:
					cursor = conn.cursor()
					query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_airport= %s'
					cursor.execute(query, (start_date, source_airport))
					search_flights = cursor.fetchall()
					cursor.close()
			elif(destination_airport):
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and arr_airport=  %s'
				cursor.execute(query, (start_date, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s'
				cursor.execute(query, (start_date))
				search_flights = cursor.fetchall()
				cursor.close()
	elif(end_date):
		if(source_airport):
			if(destination_airport):
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
				cursor.execute(query, (end_date, source_airport, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s and dep_airport= %s'
				cursor.execute(query, (end_date, source_airport))
				search_flights = cursor.fetchall()
				cursor.close()
		elif(destination_airport):
			cursor = conn.cursor()
			query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s and arr_airport=  %s'
			cursor.execute(query, (end_date, destination_airport))
			search_flights = cursor.fetchall()
			cursor.close()
		else:
			cursor = conn.cursor()
			query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s'
			cursor.execute(query, (end_date))
			search_flights = cursor.fetchall()
			cursor.close()
	elif(source_airport or destination_airport):
		if(source_airport):
			if(destination_airport):
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_airport= %s and arr_airport=  %s'
				cursor.execute(query, (source_airport, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_airport= %s'
				cursor.execute(query, (source_airport))
				search_flights = cursor.fetchall()
				cursor.close()
		elif(destination_airport):
			cursor = conn.cursor()
			query ='SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE arr_airport=  %s'
			cursor.execute(query, (destination_airport))
			search_flights = cursor.fetchall()
			cursor.close()
	else:
		search_flights = None


	if(not start_date and not end_date and not source_airport and not destination_airport):
		error = "No flights found"
		return render_template("viewMyFlights.html", error = error, future_flights = future_flights, past_flights = past_flights)
	elif(search_flights):
		return render_template("viewMyFlights.html", search_flights = search_flights, future_flights = future_flights, past_flights = past_flights)
	else:
		error = "No flights found"
		return render_template("viewMyFlights.html", error = error, future_flights = future_flights, past_flights = past_flights)
	

# display searchPurchase page
@app.route('/searchPurchase')
def searchPurchase():
	return render_template("searchPurchase.html")


# search flights
@app.route('/searchPurchaseFlight', methods=['GET', 'POST'])
def searchPurchaseFlight():
	
	# collect information from forms and convert dates to datetime objects
	source = request.form['source']
	destination = request.form['destination']
	depart_date = request.form['depart_date']
	return_date = request.form['return_date']
	if(depart_date):
		depart_date = datetime.strptime(request.form['depart_date'], '%Y-%m-%d')
	if (return_date):
		return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d')

	# get airport names
	if(depart_date or return_date):
		cursor = conn.cursor()
		query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
		cursor.execute(query, (source, source))
		source_airport = cursor.fetchone()
		cursor.close()
		if(source_airport):
			source_airport = source_airport['name']
		else:
			error = "No airport found"
			return render_template("searchPurchase.html", error = error)
		
		cursor = conn.cursor()
		query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
		cursor.execute(query, (destination, destination))
		destination_airport = cursor.fetchone()
		cursor.close()
		if(destination_airport):
			destination_airport = destination_airport['name']
		else:
			error = "No airport found"
			return render_template("searchPurchase.html", error = error)

		# search for flights based on whether depart_date, return_date, or both were given
		if(depart_date and not return_date):
			cursor = conn.cursor()
			query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)= %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
			cursor.execute(query, (source_airport, destination_airport, depart_date.year, depart_date.month, depart_date.day))
			departing_flights = cursor.fetchall()
			cursor.close()
			if(departing_flights):
				return render_template("searchPurchase.html", departing_flights = departing_flights)
			else:
				error = "No flights found"
				return render_template("searchPurchase.html", error = error)

		if(return_date and not depart_date):
			cursor = conn.cursor()
			query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)= %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
			cursor.execute(query, (destination_airport, source_airport, return_date.year, return_date.month, return_date.day))
			returning_flights = cursor.fetchall()
			cursor.close()
			if(returning_flights):
				return render_template("searchPurchase.html", returning_flights = returning_flights)
			else:
				error = "No flights found"
				return render_template("searchPurchase.html", error = error)

		if(depart_date and return_date):
			cursor = conn.cursor()
			query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)= %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
			cursor.execute(query, (source_airport, destination_airport, depart_date.year, depart_date.month, depart_date.day))
			departing_flights = cursor.fetchall()

			cursor.execute(query, (destination_airport, source_airport, return_date.year, return_date.month, return_date.day))
			returning_flights = cursor.fetchall()
			cursor.close()

			if(departing_flights and returning_flights):
				return render_template("searchPurchase.html", departing_flights = departing_flights, returning_flights = returning_flights)
			elif(departing_flights):
				return render_template("searchPurchase.html", departing_flights = departing_flights)
			elif(returning_flights):
				return render_template("searchPurchase.html", returning_flights = returning_flights)
			else:
				error = "No flighs found"
				return render_template("searchPurchase.html", error = error)
	
	else:
		error = "Please enter a departing and/or returning date"
		return render_template("searchPurchase.html", error = error)


# purchase flight ticket
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
	# collect info from forms
	airline_name = request.form['airline_name']
	flight_number = request.form['flight_number']

	# check that flight exists
	cursor = conn.cursor()
	query = 'SELECT ID FROM Flight WHERE name=%s and flight_number=%s'
	cursor.execute(query, (airline_name, flight_number))
	ID = cursor.fetchone()
	cursor.close()

	if(not ID):
		error2 = "Invalid Airline Name or Flight Number"
		return render_template("searchPurchase.html", error2= error2)
	else:
		# get plane capacity
		cursor = conn.cursor()
		query = 'SELECT seats FROM Airplane WHERE ID=%s'
		cursor.execute(query, (ID['ID']))
		capacity = cursor.fetchone()['seats']
		cursor.close()

		# get tickets sold
		cursor = conn.cursor()
		query = 'SELECT count(distinct ID) as tickets_sold FROM Ticket WHERE name=%s and flight_number=%s'
		cursor.execute(query, (airline_name, flight_number))
		tickets_sold = cursor.fetchone()['tickets_sold']
		cursor.close()

		# calculate sold_price by capacity and tickets sold
		if(tickets_sold>=capacity):
			error2 = "This flight is sold out"
			return render_template("searchPurchase.html", error2= error2)
		elif(tickets_sold/capacity >= 0.7 ):
			cursor = conn.cursor()
			query = 'SELECT *, base_price*1.2 as sale_price FROM Flight WHERE name=%s and flight_number=%s'
			cursor.execute(query, (airline_name, flight_number))
			flight_info = cursor.fetchone()
			cursor.close()
			return render_template("searchPurchase.html", flight_info = flight_info, processing = 1)
		else:
			cursor = conn.cursor()
			query = 'SELECT *, base_price as sale_price FROM Flight WHERE name=%s and flight_number=%s'
			cursor.execute(query, (airline_name, flight_number))
			flight_info = cursor.fetchone()
			cursor.close()
			return render_template("searchPurchase.html", flight_info = flight_info, processing = 1)


# input purchase information
@app.route('/purchaseInfo', methods=['GET', 'POST'])
def purchaseInfo():
	# get session email
	email  = session['email']

	# get info from forms
	airline_name = request.form['airline_name']
	flight_number = request.form['flight_number']
	card_type = request.form['card_type']
	card_number = request.form['card_number']
	name_on_card = request.form['name_on_card']
	exp_date = request.form['expiration_date']

	# check that the flight exists
	cursor = conn.cursor()
	query = 'SELECT ID FROM Flight WHERE name=%s and flight_number=%s'
	cursor.execute(query, (airline_name, flight_number))
	ID = cursor.fetchone()
	cursor.close()

	# check that the card type is valid
	if(card_type not in ["credit", "Credit", "CREDIT", "debit", "Debit", "DEBIT"]):
		error2 = "Invalid card type. Cards must be credit or debit"
		return render_template("searchPurchase.html", error2= error2)
	elif(not ID): # check that the flight exists
		error2 = "Invalid Airline Name or Flight Number"
		return render_template("searchPurchase.html", error2= error2)
	else:
		# get plane capacity
		cursor = conn.cursor()
		query = 'SELECT seats FROM Airplane WHERE ID=%s'
		cursor.execute(query, (ID['ID']))
		capacity = cursor.fetchone()['seats']
		cursor.close()

		# get tickets sold
		cursor = conn.cursor()
		query = 'SELECT count(distinct ID) as tickets_sold FROM Ticket WHERE name=%s and flight_number=%s'
		cursor.execute(query, (airline_name, flight_number))
		tickets_sold = cursor.fetchone()['tickets_sold']
		cursor.close()

		# calculate sold_price from capcity and tickets sold
		if(tickets_sold>=capacity):
			error2 = "This flight is sold out"
			return render_template("searchPurchase.html", error2= error2) 
		else:
			cursor = conn.cursor()
			query = 'SELECT base_price FROM Flight WHERE name=%s and flight_number=%s'
			cursor.execute(query, (airline_name, flight_number))
			base_price = cursor.fetchone()['base_price']
			cursor.close()
			if(tickets_sold/capacity >= 0.7 ):
				sold_price = base_price*1.2
			else:
				sold_price = base_price

			# create new ticket ID that is max(ticket_id)+1
			cursor = conn.cursor()
			query = 'SELECT max(ID) as max_ID FROM Ticket'
			cursor.execute(query)
			max_id = cursor.fetchone()['max_ID']
			cursor.close()
			ticket_id = max_id + 1

			# create new ticket
			cursor = conn.cursor()
			query = 'INSERT INTO Ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)'
			cursor.execute(query, (ticket_id, email, airline_name, flight_number, sold_price, card_type, card_number, name_on_card, exp_date))
			conn.commit()
			cursor.close()

			# get customer name
			cursor = conn.cursor()
			query = 'SELECT name FROM Customer WHERE email = %s'
			cursor.execute(query, (email))
			data = cursor.fetchone()['name'] 
			cursor.close()

			# send success message to customerHome
			message = "Ticket "+str(ticket_id)+" for "+str(airline_name)+" Flight Number "+str(flight_number)+" successfully purchased!"
			return render_template('customerHome.html', name= data, message = message)


# display previous flights in page to rate previous flights
@app.route('/rate', methods=['GET', 'POST'])
def rate():
	# get session email
	email = session['email']
	
	# get previous flights
	cursor = conn.cursor()
	query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and purchase_date_time< CURRENT_TIMESTAMP and arr_date_time< CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	previous_flights = cursor.fetchall()
	cursor.close()

	error= None

	return render_template("rateTemplate.html", previous_flights = previous_flights, error = error)


# rate previous flight
@app.route('/rateFlight', methods=['GET', 'POST'])
def rateFlight():
	
	# get session email
	email = session['email']
	
	# get previous flights
	cursor = conn.cursor()
	query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and purchase_date_time< CURRENT_TIMESTAMP and arr_date_time< CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	previous_flights = cursor.fetchall()
	cursor.close()
	
	# get info from forms
	airline_name = request.form['airline_name']
	flight_number = request.form['flight_number']
	rating = int(request.form['rating'])
	comment = request.form['comment']
	
	# get info on the flight the customer is rating
	cursor = conn.cursor()
	query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and Flight.name = %s and Flight.flight_number = %s and purchase_date_time< CURRENT_TIMESTAMP and arr_date_time< CURRENT_TIMESTAMP'
	cursor.execute(query, (email, airline_name, flight_number))
	rating_flight = cursor.fetchone()
	cursor.close()

	# check that the flight exists
	if(not rating_flight):
		error = "Flight not found"
		return render_template("rateTemplate.html", previous_flights = previous_flights, error= error)
	elif (rating < 1 or rating > 10): # check that the rating is valid
		error = "Invalid Rating"
		return render_template("rateTemplate.html", previous_flights = previous_flights, error= error)
	else:
		# create new rating_id as max(rating_id)+1
		cursor = conn.cursor()
		query = 'SELECT max(rating_id) as max_id FROM Flight_Ratings'
		cursor.execute(query)
		max_id = cursor.fetchone()['max_id']
		cursor.close()
		if(not max_id or max_id < 1):
			rating_id = 1
		else:
			rating_id = max_id + 1
		
		# add rating to Flight_Ratings relation
		cursor = conn.cursor()
		ins = 'INSERT INTO Flight_Ratings VALUES(%s, %s, %s, %s, %s)'
		cursor.execute(ins, (rating_id, airline_name, flight_number, rating, comment))
		conn.commit()
		cursor.close()

		# get customer name
		cursor = conn.cursor()
		query = 'SELECT name FROM Customer WHERE email = %s'
		cursor.execute(query, (email))
		data = cursor.fetchone()['name'] 
		cursor.close()

		# send success message to customerHome
		message = "Rating for "+str(airline_name)+" Flight Number "+str(flight_number)+" successfully entered!"
		return render_template('customerHome.html', name= data, message = message)
	

# display page with spending info for last year and last six months
@app.route('/trackSpending', methods=['GET', 'POST'])
def trackSpending():
	# get session email
	email = session['email']

	# get spending for the last year
	cursor = conn.cursor()
	query = 'SELECT sum(sold_price) as total_spent FROM Ticket WHERE email=%s and purchase_date_time=> DATE_ADD(NOW(), INTERVAL -1 YEAR) and purchase_date_time<= CURRENT_TIMESTAMP'
	cursor.execute(query, (email))
	year = cursor.fetchone()['total_spent']
	cursor.close()

	# get spending for this month
	cursor = conn.cursor()
	query = 'SELECT month(CURRENT_DATE) as m, year(CURRENT_DATE) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month IS NULL'
	cursor.execute(query, (email))
	m0 = cursor.fetchone()

	# get spending for last month
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -1 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -1 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 1'
	cursor.execute(query, (email))
	m1 = cursor.fetchone()

	# get spending for two months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -2 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -2 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 2'
	cursor.execute(query, (email))
	m2 = cursor.fetchone()

	# get spending for three months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -3 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -3 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 3'
	cursor.execute(query, (email))
	m3 = cursor.fetchone()
	
	# get spending for four months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -4 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -4 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 4'
	cursor.execute(query, (email))
	m4 = cursor.fetchone()

	# get spending for five months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -5 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -5 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 5'
	cursor.execute(query, (email))
	m5 = cursor.fetchone()

	# get spending for six months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -6 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -6 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 6'
	cursor.execute(query, (email))
	m6 = cursor.fetchone()
	cursor.close()

	# combine all monthly spending into dataframe, reorganize, and send to html as a dictionary
	df = pd.DataFrame(columns = ['m', 'y', 'spending'])
	df = df.append(m0, ignore_index= True).append(m1, ignore_index = True).append(m2, ignore_index=True).append(m3, ignore_index=True).append(m4, ignore_index=True).append(m5, ignore_index=True).append(m6, ignore_index=True)
	df["date"] = df['m'].astype(int).astype(str) + "/" + df["y"].astype(int).astype(str)
	df.fillna(0, inplace=True)
	df['relative_month'] = df.index.astype(str)
	df.set_index('relative_month', inplace=True)
	df['0'] = df['date']
	df['1']= df['spending']

	monthly_df = df[['0','1']]
	monthly = monthly_df.to_dict('records')

	return render_template("trackSpending.html", year = year, monthly = monthly)


# search spending by date range
@app.route('/searchSpending', methods=['GET', 'POST'])
def searchSpending():

	# get session email
	email = session['email']

	# get spending for past year
	cursor = conn.cursor()
	query = 'SELECT sum(sold_price) as total_spent FROM Ticket WHERE email=%s and purchase_date_time> (DATE_ADD(NOW(), INTERVAL -1 YEAR))'
	cursor.execute(query, (email))
	year = cursor.fetchone()['total_spent']
	cursor.close()

	# get spending for this month
	cursor = conn.cursor()
	query = 'SELECT month(CURRENT_DATE) as m, year(CURRENT_DATE) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month IS NULL'
	cursor.execute(query, (email))
	m0 = cursor.fetchone()

	# get spending for last month
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -1 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -1 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 1'
	cursor.execute(query, (email))
	m1 = cursor.fetchone()

	# get spending for two months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -2 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -2 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 2'
	cursor.execute(query, (email))
	m2 = cursor.fetchone()

	# get spending for three months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -3 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -3 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 3'
	cursor.execute(query, (email))
	m3 = cursor.fetchone()
	
	# get spending for four months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -4 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -4 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 4'
	cursor.execute(query, (email))
	m4 = cursor.fetchone()

	# get spending for five months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -5 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -5 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 5'
	cursor.execute(query, (email))
	m5 = cursor.fetchone()

	# get spending for six months ago
	query = 'SELECT month(DATE_ADD(NOW(), INTERVAL -6 MONTH)) as m, year(DATE_ADD(NOW(), INTERVAL -6 MONTH)) as y, sum(sold_price) as spending FROM monthly_spending WHERE email = %s and relative_month = 6'
	cursor.execute(query, (email))
	m6 = cursor.fetchone()
	cursor.close()

	# combine monthly spending into df, reorganize, and send to html as dictionary
	df = pd.DataFrame(columns = ['m', 'y', 'spending'])
	df = df.append(m0, ignore_index= True).append(m1, ignore_index = True).append(m2, ignore_index=True).append(m3, ignore_index=True).append(m4, ignore_index=True).append(m5, ignore_index=True).append(m6, ignore_index=True)
	df["date"] = df['m'].astype(int).astype(str) + "/" + df["y"].astype(int).astype(str)
	df.fillna(0, inplace=True)
	df['relative_month'] = df.index.astype(str)
	df.set_index('relative_month', inplace=True)
	df['0'] = df['date']
	df['1']= df['spending']

	monthly_df = df[['0','1']]
	monthly = monthly_df.to_dict('records')

	# get info from forms and turn them into datetime objects
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	start = datetime.strptime(start_date, '%Y-%m-%d')
	end = datetime.strptime(end_date, '%Y-%m-%d')

	# get number of months in between dates 
	num_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

	if num_months < 1: # check that the end_date comes after the start_date
		error = "End date must be after the start date"
		return render_template("trackSpending.html", year = year, monthly = monthly, error = error)
	else:
		# get total spending in searched date range
		cursor = conn.cursor()
		query = 'SELECT sum(sold_price) as total FROM Ticket WHERE email=%s and purchase_date_time>=%s and purchase_date_time<=%s'
		cursor.execute(query, (email, start_date, end_date))
		total = cursor.fetchone()['total']
		cursor.close()

		# get spending by month in searched date range
		cursor = conn.cursor()
		query = 'SELECT year(purchase_date_time) as year, month(purchase_date_time) as month, sum(sold_price) as month_spending FROM Ticket WHERE email=%s and purchase_date_time>=%s and purchase_date_time<=%s group by month(purchase_date_time), year(purchase_date_time)'
		cursor.execute(query, (email, start_date, end_date))
		by_month = cursor.fetchall()
		cursor.close()

		# create empty df with all months represented in searched date range
		d = {'year': [start.year], 'month': [start.month]}
		empty = pd.DataFrame(d)
		new_month = start.month
		new_year = start.year
		for i in range(num_months-1):
			new_month  = new_month + 1
			if new_month > 12:
				new_month -= 12
				new_year = new_year + 1
			new = {'year': new_year, 'month': new_month}
			empty = empty.append(new, ignore_index = True)
		spending = pd.DataFrame.from_dict(by_month)

		# combine monthly spending and empty df to get complete breakdown of each month in the searched date range
		search_df = pd.merge(empty, spending,  how='left', on=['year','month']).fillna(0)
		search_df["date"] = search_df['month'].astype(str) + "/" + search_df["year"].astype(int).astype(str)
		search_df['0'] = search_df['date']
		search_df['1']= search_df['month_spending']
		new_df = search_df[['0','1']]
		searched = new_df.to_dict('records')

		return render_template("trackSpending.html", year = year, monthly = monthly, total = total, searched = searched)
		

# redirect to staffHome and display staff name
@app.route('/staffHome')
def staffHome():
	# get session username
	username  = session['username']

	# get staff's name
	cursor = conn.cursor()
	query = 'SELECT first_name, last_name FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone() 
	cursor.close()
	error = None
	return render_template('staffHome.html', first_name= data['first_name'], last_name = data['last_name'], error = error)


# allow staff to view all flights of their airline 
@app.route('/viewFlights', methods=['GET', 'POST'])
def viewFlights():
	# get session username
	username  = session['username']

	# get all flights for next 30 days run by their airline
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
	cursor.execute(query, (username))
	next30 = cursor.fetchall() 
	cursor.close()

	return render_template('viewFlights.html', next30 = next30)


# allow staff to search flights run by their airline
@app.route('/searchStaffFlights', methods=['GET', 'POST'])
def searchStaffFlights():
	# get session username
	username  = session['username']

	# get all flights for next 30 days run by their airline
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
	cursor.execute(query, (username))
	next30 = cursor.fetchall() 
	cursor.close()

	# get info from forms 
	start_date= request.form['start_date']
	end_date = request.form['end_date']
	source_airport = request.form['source']
	destination_airport = request.form['destination']

	# get name of destination airport
	if(destination_airport):	
		cursor = conn.cursor()
		query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
		cursor.execute(query, (destination_airport, destination_airport))
		destination_airport = cursor.fetchone()
		cursor.close()
		if(destination_airport):
			destination_airport = destination_airport['name']
		else:
			error = "No airport found"
			return render_template("viewFlights.html", error = error, next30 = next30)
	
	# get name of source airport
	if(source_airport):
		cursor = conn.cursor()
		query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
		cursor.execute(query, (source_airport, source_airport))
		source_airport = cursor.fetchone()
		cursor.close()
		if(source_airport):
			source_airport = source_airport['name']
		else:
			error = "No airport found"
			return render_template("viewFlights.html", error = error, next30 = next30)
	
	# select correct query based on the information given
	if(start_date):
		if(end_date):
			if(source_airport):
				if(destination_airport):
					cursor = conn.cursor()
					query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
					cursor.execute(query, (username, start_date, end_date, source_airport, destination_airport))
					search_flights = cursor.fetchall()
					cursor.close()
				else:
					cursor = conn.cursor()
					query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s'
					cursor.execute(query, (username, start_date, end_date, source_airport))
					search_flights = cursor.fetchall()
					cursor.close()
			elif(destination_airport):
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s and arr_airport= %s'
				cursor.execute(query, (username, start_date, end_date, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s'
				cursor.execute(query, (username, start_date, end_date))
				search_flights = cursor.fetchall()
				cursor.close()
		else:
			if(source_airport):
				if(destination_airport):
					cursor = conn.cursor()
					query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_airport= %s and arr_airport=  %s'
					cursor.execute(query, (username, start_date, source_airport, destination_airport))
					search_flights = cursor.fetchall()
					cursor.close()
				else:
					cursor = conn.cursor()
					query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_airport= %s'
					cursor.execute(query, (username, start_date, source_airport))
					search_flights = cursor.fetchall()
					cursor.close()
			elif(destination_airport):
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and arr_airport=  %s'
				cursor.execute(query, (username, start_date, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT  * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s'
				cursor.execute(query, (username, start_date))
				search_flights = cursor.fetchall()
				cursor.close()
	elif(end_date):
		if(source_airport):
			if(destination_airport):
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
				cursor.execute(query, (username, end_date, source_airport, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s and dep_airport= %s'
				cursor.execute(query, (username, end_date, source_airport))
				search_flights = cursor.fetchall()
				cursor.close()
		elif(destination_airport):
			cursor = conn.cursor()
			query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s and arr_airport=  %s'
			cursor.execute(query, (username, end_date, destination_airport))
			search_flights = cursor.fetchall()
			cursor.close()
		else:
			cursor = conn.cursor()
			query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s'
			cursor.execute(query, (username, end_date))
			search_flights = cursor.fetchall()
			cursor.close()
	elif(source_airport or destination_airport):
		if(source_airport):
			if(destination_airport):
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_airport= %s and arr_airport=  %s'
				cursor.execute(query, (username, source_airport, destination_airport))
				search_flights = cursor.fetchall()
				cursor.close()
			else:
				cursor = conn.cursor()
				query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_airport= %s'
				cursor.execute(query, (username, source_airport))
				search_flights = cursor.fetchall()
				cursor.close()
		elif(destination_airport):
			cursor = conn.cursor()
			query ='SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and arr_airport=  %s'
			cursor.execute(query, (username, destination_airport))
			search_flights = cursor.fetchall()
			cursor.close()
	else:
		search_flights = None

	if(not start_date and not end_date and not source_airport and not destination_airport):
		error = "No flights found"
		return render_template("viewFlights.html", error = error, next30 = next30)
	elif(search_flights):
		return render_template("viewFlights.html", search_flights = search_flights, next30 = next30)
	else:
		error = "No flights found"
		return render_template("viewFlights.html", error = error, next30 = next30)


# allow staff to search all of the customers on a flight
@app.route('/searchFlightCustomers', methods=['GET', 'POST'])
def searchFlightCustomers():
	# get session username
	username  = session['username']

	# get all flights for next 30 days run by their airline
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
	cursor.execute(query, (username))
	next30 = cursor.fetchall() 
	cursor.close()

	# get info from forms
	flight_number = request.form['flight_number']

	# get all tickets for customers on search flight
	cursor = conn.cursor()
	query = 'SELECT * FROM Customer left join Ticket on Customer.email = Ticket.email WHERE Ticket.name in (SELECT name FROM Airline_Staff WHERE username = %s) and flight_number = %s'
	cursor.execute(query, (username, flight_number))
	search_flight_customers = cursor.fetchall() 
	cursor.close()

	if(search_flight_customers):
		return render_template('viewFlights.html', next30 = next30, search_flight_customers = search_flight_customers)
	else: 
		error2 = "Invalid or empty flight"
		return render_template('viewFlights.html', next30 = next30, error2 = error2)


# display form to create a new flight and display all flights for next 30 days run by their airline
@app.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
	# get session username
	username  = session['username']

	# get all flights for next 30 days run by their airline
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
	cursor.execute(query, (username))
	next30 = cursor.fetchall() 
	cursor.close()

	return render_template('createFlight.html', next30 = next30)


# allow staff to create a new flight
@app.route('/createStaffFlight', methods=['GET', 'POST'])
def createStaffFlight():

	# get session username
	username  = session['username']

	# get all flights for next 30 days run by their airline
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
	cursor.execute(query, (username))
	next30 = cursor.fetchall() 
	cursor.close()

	# get info from forms
	flight_number= request.form['flight_number']
	source= request.form['source']
	destination= request.form['destination']
	dep_date= request.form['dep_date']
	dep_time= request.form['dep_time']
	arr_date= request.form['arr_date']
	arr_time= request.form['arr_time']
	base_price= request.form['base_price']
	ID= request.form['ID']
	status= request.form['status']

	# get name of airline of staff
	cursor = conn.cursor()
	query = 'SELECT name FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	name = cursor.fetchone()
	cursor.close()
	
	#check that the user is an airline staff
	if(not name):
		error = "You are not authorized to create a new flight"
		return render_template('createFlight.html', next30 = next30, error= error)
	else:
		name = name['name']

		# check that flight number isn't taken in airline
		cursor = conn.cursor()
		query = 'SELECT name, flight_number FROM Flight WHERE name = %s and flight_number = %s'
		cursor.execute(query, (name, flight_number))
		taken = cursor.fetchone() 
		cursor.close()

		if(taken): # check that flight number isn't taken in airline
			error = "This flight number is already in use"
			return render_template('createFlight.html', next30 = next30, error= error)
		else:
			#check that source and destination airports exist
			cursor = conn.cursor()
			query = 'SELECT name  FROM Airport WHERE name = %s'
			cursor.execute(query, (source))
			source_airport = cursor.fetchone() 

			cursor.execute(query, (destination))
			destination_airport = cursor.fetchone() 
			cursor.close()
			if(not (source_airport and destination_airport)):
				error = "Airport does not exist"
				return render_template('createFlight.html', next30 = next30, error= error)
			else:
				#check that airplane exists in airline
				cursor = conn.cursor()
				query = 'SELECT name, ID FROM Airplane WHERE name = %s and ID = %s'
				cursor.execute(query, (name, ID))
				plane = cursor.fetchone() 
				cursor.close()
				if(not plane):
					error = "Airplane does not exist"
					return render_template('createFlight.html', next30 = next30, error= error)
				else:
					#check that status is on-time or delayed
					if(status not in ['on-time','delayed']):
						error = "Status must be either on-time or delayed"
						return render_template('createFlight.html', next30 = next30, error= error)
					else:
						# add flight to system
						cursor = conn.cursor()
						ins = 'INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
						cursor.execute(ins, (name, flight_number, dep_date+" "+dep_time+":00", source, destination, arr_date+" "+arr_time+":00", base_price, ID, status))
						conn.commit()
						cursor.close()
						
						# get staff's name
						cursor = conn.cursor()
						query = 'SELECT first_name, last_name FROM Airline_Staff WHERE username = %s'
						cursor.execute(query, (username))
						data = cursor.fetchone() 
						cursor.close()

						#send success message to staffHome
						message = name+" Flight Number "+flight_number+" was successfully created!"
						return render_template('staffHome.html', first_name= data['first_name'], last_name = data['last_name'], message = message)


# display form to change flight status
@app.route('/changeStatus', methods=['GET', 'POST'])
def changeStatus():
	return render_template('changeStatus.html')


# allow staff to change flight status
@app.route('/changeFlightStatus', methods=['GET', 'POST'])
def changeFlightStatus():
	
	# get session username
	username = session['username']

	# get name of airline
	cursor = conn.cursor()
	query = 'SELECT name FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchone()['name']
	cursor.close()
	
	# get info from forms
	flight_number = request.form['flight_number']
	depart_date = datetime.strptime(request.form['depart_date'], '%Y-%m-%d')
	desired_status = request.form['desired_status']

	# check that the searched flight exists 
	cursor = conn.cursor()
	query = 'SELECT * FROM Flight WHERE name = %s and flight_number = %s and year(dep_date_time) = %s and month(dep_date_time) = %s and day(dep_date_time)= %s'
	cursor.execute(query, (airline_name, flight_number, depart_date.year, depart_date.month, depart_date.day))
	searched_flight = [cursor.fetchone()]
	cursor.close()

	if(desired_status not in ['on-time','delayed']): # check that the desired status is on-time or delayed
		error = "Status must be either on-time or delayed"
		return render_template('changeStatus.html',  error= error)
	elif(not searched_flight): # check that the searched flight exists
		error = "No flight found"
		return render_template('changeStatus.html', error= error)
	else:
		# update the status of the searched flight
		cursor = conn.cursor()
		ins = 'UPDATE Flight SET status = %s WHERE name = %s and flight_number= %s'
		cursor.execute(ins, (desired_status, airline_name, flight_number))
		conn.commit()
		cursor.close()

		# get staff's name
		cursor = conn.cursor()
		query = 'SELECT first_name, last_name FROM Airline_Staff WHERE username = %s'
		cursor.execute(query, (username))
		data = cursor.fetchone() 
		cursor.close()

		# send success message to staffHome
		message = airline_name+" Flight Number "+flight_number+" successfully updated to '"+desired_status
		return render_template('staffHome.html', first_name = data['first_name'], last_name = data['last_name'], message = message)


# display form to add airplane and all airplanes owned by staff's airline
@app.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():

	# get session username
	username = session['username']

	# gert airplanes owned by staff's airline
	cursor = conn.cursor()
	query = 'SELECT * from Airplane WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s)'
	cursor.execute(query, (username))
	airplanes = cursor.fetchall()
	cursor.close()

	return render_template('addAirplane.html', airplanes = airplanes)


# allow staff to add airplane
@app.route('/createAirplane', methods=['GET', 'POST'])
def createAirplane():
	# get session username
	username = session['username']

	# gert airplanes owned by staff's airline
	cursor = conn.cursor()
	query = 'SELECT * from Airplane WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s)'
	cursor.execute(query, (username))
	airplanes = cursor.fetchall()
	cursor.close()

	# get name of staff's airline
	cursor = conn.cursor()
	query = 'SELECT name FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	airline_name = cursor.fetchone()
	cursor.close()

	#check that the user is an airline staff
	if(not airline_name):
		error = "You are not authorized to add an Airplane"
		return render_template('addAirplane.html', airplanes = airplanes, error = error)
	else: 
		airline_name = airline_name['name']

		# get info from forms
		ID = request.form['ID']
		seats = request.form['seats']

		# check that the airplane does not already exist
		cursor = conn.cursor()
		query = 'SELECT * from Airplane WHERE name = %s and ID = %s'
		cursor.execute(query, (airline_name, ID))
		exists = cursor.fetchall()
		cursor.close()

		if(exists): # check that the airplane does not already exist
			error = "This Airplane already exists"
			return render_template('addAirplane.html', airplanes = airplanes, error = error)
		else:
			# add airplane to system
			cursor = conn.cursor()
			ins = 'INSERT INTO Airplane VALUES (%s, %s, %s)'
			cursor.execute(ins, (airline_name, ID, seats))
			conn.commit()
			cursor.close()

			# get staff's name
			cursor = conn.cursor()
			query = 'SELECT first_name, last_name FROM Airline_Staff WHERE username = %s'
			cursor.execute(query, (username))
			data = cursor.fetchone() 
			cursor.close()

			# send success message to staffHome
			message = airline_name+" Airplane "+ID+" successfully added!"
			return render_template('staffHome.html', first_name = data['first_name'], last_name = data['last_name'], message = message)


# display form to add airport
@app.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
	return render_template('addAirport.html')


# allow staff to add airport
@app.route('/createAirport', methods=['GET', 'POST'])
def createAirport():

	# get session username
	username = session['username']

	#check that the user is an airline staff
	cursor = conn.cursor()
	query = 'SELECT first_name, last_name FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone() 
	cursor.close()

	if(not data):
		error = "You are not authorized to add an Airplane"
		return render_template('addAirport.html', error = error)
	else:
		# get info from froms
		name = request.form['name']
		city = request.form['city']

		# check that the airport doesn't already exist
		cursor = conn.cursor()
		query = 'SELECT * from Airport WHERE name = %s'
		cursor.execute(query, (name))
		exists = cursor.fetchall()
		cursor.close()

		if(exists): # check that the airport doesn't already exist
			error = "This Airport already exists in the system"
			return render_template('addAirport.html', error = error)
		else:
			# add airport to the system
			cursor = conn.cursor()
			ins = 'INSERT INTO Airport VALUES (%s, %s)'
			cursor.execute(ins, (name, city))
			conn.commit()
			cursor.close()

			# send success message to staffHome
			message = name+" Airport successfully added!"
			return render_template('staffHome.html', first_name = data['first_name'], last_name = data['last_name'], message = message)


# display ratings for all flights run by staff's airline
@app.route('/ratings', methods=['GET', 'POST'])
def ratings():

	# get session username
	username = session['username']

	# get average flight ratings
	cursor = conn.cursor()
	query = 'SELECT flight_number, avg(rating) as avg_rating FROM Flight_Ratings WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) group by flight_number'
	cursor.execute(query, (username))
	avg_ratings = cursor.fetchall()
	cursor.close()

	# get all ratings and comments
	cursor = conn.cursor()
	query = 'SELECT flight_number, rating, comment FROM Flight_Ratings WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s)'
	cursor.execute(query, (username))
	all_ratings = cursor.fetchall()
	cursor.close()

	# combine avg ratings and individual ratings into one df, reorganize, and send to html as dictionary
	avg_df = pd.DataFrame(avg_ratings)
	all_df = pd.DataFrame(all_ratings)
	combined = pd.merge(all_df, avg_df,  how='left', on=['flight_number']).sort_values(by=['flight_number'])
	ratings = combined.to_dict('records')

	return render_template('viewRatings.html', ratings = ratings)


# display most frequent customers
@app.route('/frequentCustomers', methods=['GET', 'POST'])
def frequentCustomers():

	# get session username
	username = session['username']

	# get count of tickets by customer
	cursor = conn.cursor()
	query = 'SELECT email, count(ID) as count FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 YEAR) GROUP BY email ORDER BY count DESC'
	cursor.execute(query, (username))
	counts = cursor.fetchall()
	cursor.close()

	return render_template('viewCustomers.html', counts = counts)


# allow staff to search for all flights taken by a particular customer
@app.route('/viewCustomers', methods=['GET', 'POST'])
def viewCustomers():

	# get session username
	username = session['username']

	# get count of tickets by customer
	cursor = conn.cursor()
	query = 'SELECT email, count(ID) as count FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 YEAR) GROUP BY email ORDER BY count DESC'
	cursor.execute(query, (username))
	counts = cursor.fetchall()
	cursor.close()

	# get info from forms
	email = request.form['email']

	# get all flights for which the searched customer has bought tickets
	cursor = conn.cursor()
	query = 'SELECT Flight.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, Flight.ID, Ticket.ID, sold_price, purchase_date_time FROM Flight, Ticket WHERE Flight.flight_number = Ticket.flight_number and Flight.name = Ticket.name and email = %s and Flight.name in (SELECT name FROM Airline_Staff WHERE username = %s)'
	cursor.execute(query, (email, username))
	flights = cursor.fetchall()
	cursor.close()

	if(not flights): # check that the customer has bought any tickets
		error = "No flights found"
		return render_template('viewCustomers.html', error = error, counts = counts)
	else:
		return render_template('viewCustomers.html', counts = counts, email = email, flights = flights)
	

# display tickets sold in last year, in last month, and form to allow staff to search for tickets sold by date range
@app.route('/reports', methods=['GET', 'POST'])
def reports():

	# get session username
	username = session['username']

	# get tickets sold in the last year
	cursor = conn.cursor()
	query = 'SELECT count(ID) as sold FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 YEAR) and purchase_date_time <= CURRENT_TIMESTAMP'
	cursor.execute(query, (username))
	last_year = cursor.fetchone()['sold']
	cursor.close()

	# get tickets sold in the last month
	cursor = conn.cursor()
	query = 'SELECT count(ID) as sold FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 MONTH) and purchase_date_time <= CURRENT_TIMESTAMP'
	cursor.execute(query, (username))
	last_month = cursor.fetchone()['sold']
	cursor.close()

	return render_template('viewReports.html', last_year = last_year, last_month = last_month)


# display tickets sold in last year, in last month, and in searched date range
@app.route('/viewReports', methods=['GET', 'POST'])
def viewReports():

	# get session username
	username = session['username']

	# get tickets sold in the last year
	cursor = conn.cursor()
	query = 'SELECT count(ID) as sold FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 YEAR) and purchase_date_time <= CURRENT_TIMESTAMP'
	cursor.execute(query, (username))
	last_year = cursor.fetchone()['sold']
	cursor.close()

	# get tickets sold in the last month
	cursor = conn.cursor()
	query = 'SELECT count(ID) as sold FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 MONTH) and purchase_date_time <= CURRENT_TIMESTAMP'
	cursor.execute(query, (username))
	last_month = cursor.fetchone()['sold']
	cursor.close()

	# get info from forms and turn them into datetime objects
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	start = datetime.strptime(start_date, '%Y-%m-%d')
	end = datetime.strptime(end_date, '%Y-%m-%d')

	# get number of months in between dates 
	num_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

	if num_months < 1: # check that the end_date comes after the start_date
		error = "End date must be after the start date"
		return render_template('viewReports.html', last_year = last_year, last_month = last_month, error = error)
	else:
		# get total tickets sold in searched date range
		cursor = conn.cursor()
		query = 'SELECT count(ID) as total FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >=%s and purchase_date_time <=%s'
		cursor.execute(query, (username, start_date, end_date))
		searched_total = cursor.fetchone()['total']
		cursor.close()

		# get spending by month in searched date range
		cursor = conn.cursor()
		query = 'SELECT year(purchase_date_time) as year, month(purchase_date_time) as month, count(ID) as sold FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and purchase_date_time >=%s and purchase_date_time <=%s GROUP BY month(purchase_date_time), year(purchase_date_time)'
		cursor.execute(query, (username, start_date, end_date))
		by_month = cursor.fetchall()
		cursor.close()

		# create empty df with all months represented in searched date range
		d = {'year': [start.year], 'month': [start.month]}
		empty = pd.DataFrame(d)
		new_month = start.month
		new_year = start.year
		for i in range(num_months-1):
			new_month  = new_month + 1
			if new_month > 12:
				new_month -= 12
				new_year = new_year + 1
			new = {'year': new_year, 'month': new_month}
			empty = empty.append(new, ignore_index = True)
		
		spending = pd.DataFrame.from_dict(by_month)

		# combine monthly spending and empty df to get complete breakdown of each month in the searched date range
		search_df = pd.merge(empty, spending,  how='left', on=['year','month']).fillna(0)
		search_df["date"] = search_df['month'].astype(int).astype(str) + "/" + search_df["year"].astype(int).astype(str)
		search_df['0'] = search_df['date']
		search_df['1']= search_df['sold'].astype(int)
		new_df = search_df[['0','1']]
		searched_monthly = new_df.to_dict('records')

		return render_template('viewReports.html', last_year = last_year, last_month = last_month, searched_total = searched_total, searched_monthly = searched_monthly)


# display quarterly revenue for each quarter in the last year
@app.route('/quarterlyRevenue', methods=['GET', 'POST'])
def quarterlyRevenue():

	# get session username
	username = session['username']

	# get current year and month
	cursor = conn.cursor()
	query = 'SELECT year(NOW()) as y, month(NOW()) as m'
	cursor.execute(query)
	current = cursor.fetchone()
	cursor.close()
	year = current['y']
	month = current['m']

	if(month >= 1 and month <= 3):
		# get all four quarters of the year before
		# first quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 1 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 1 and month(purchase_date_time) <= 3 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q1 = cursor.fetchone()
		cursor.close()

		# second quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 2 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 4 and month(purchase_date_time) <= 6 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q2 = cursor.fetchone()
		cursor.close()

		# third quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 3 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 7 and month(purchase_date_time) <= 9 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q3 = cursor.fetchone()
		cursor.close()

		# fourth quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 4 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 10 and month(purchase_date_time) <= 12 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q4 = cursor.fetchone()
		cursor.close()
	elif(month>= 4 and month <= 6):
		# get last 3 quarters of the year before and the first quarter of this year
		# second quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 2 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 4 and month(purchase_date_time) <= 6 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q1 = cursor.fetchone()
		cursor.close()

		# third quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 3 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 7 and month(purchase_date_time) <= 9 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q2 = cursor.fetchone()
		cursor.close()

		# fourth quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 4 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 10 and month(purchase_date_time) <= 12 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q3 = cursor.fetchone()
		cursor.close()

		# first quarter of this year
		cursor = conn.cursor()
		query = 'SELECT 1 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 1 and month(purchase_date_time) <= 3 and year(purchase_date_time) = %s'
		cursor.execute(query, (year, username, year))
		q4 = cursor.fetchone()
		cursor.close()
	elif(month>= 7 and month <= 9):
		# get last 2 quarters of the year before and the first 2 quarters of this year
		# third quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 3 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 7 and month(purchase_date_time) <= 9 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q1 = cursor.fetchone()
		cursor.close()

		# fourth quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 4 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 10 and month(purchase_date_time) <= 12 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q2 = cursor.fetchone()
		cursor.close()

		# first quarter of this year
		cursor = conn.cursor()
		query = 'SELECT 1 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 1 and month(purchase_date_time) <= 3 and year(purchase_date_time) = %s'
		cursor.execute(query, (year, username, year))
		q3 = cursor.fetchone()
		cursor.close()

		# second quarter of this year
		cursor = conn.cursor()
		query = 'SELECT 2 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 4 and month(purchase_date_time) <= 6 and year(purchase_date_time) = %s'
		cursor.execute(query, (year, username, year))
		q4 = cursor.fetchone()
		cursor.close()
	else:
		# get last quarter of the year before and the first 3 quarters of this year
		# fourth quarter of last year
		cursor = conn.cursor()
		query = 'SELECT 4 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 10 and month(purchase_date_time) <= 12 and year(purchase_date_time) = %s'
		cursor.execute(query, (year-1, username, year-1))
		q1 = cursor.fetchone()
		cursor.close()

		# first quarter of this year
		cursor = conn.cursor()
		query = 'SELECT 1 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 1 and month(purchase_date_time) <= 3 and year(purchase_date_time) = %s'
		cursor.execute(query, (year, username, year))
		q2 = cursor.fetchone()
		cursor.close()

		# second quarter of this year
		cursor = conn.cursor()
		query = 'SELECT 2 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 4 and month(purchase_date_time) <= 6 and year(purchase_date_time) = %s'
		cursor.execute(query, (year, username, year))
		q3 = cursor.fetchone()
		cursor.close()

		# third quarter of this year
		cursor = conn.cursor()
		query = 'SELECT 3 as q, %s as y, sum(sold_price) as revenue FROM Ticket WHERE name in (SELECT name FROM Airline_Staff WHERE username =%s) and month(purchase_date_time) >= 7 and month(purchase_date_time) <= 9 and year(purchase_date_time) = %s'
		cursor.execute(query, (year, username, year))
		q4 = cursor.fetchone()
		cursor.close()


	df = pd.DataFrame(columns = ['q', 'y', 'revenue'])
	df = df.append(q1, ignore_index = True).append(q2, ignore_index = True).append(q3, ignore_index = True).append(q4, ignore_index = True).fillna(0)

	df["quarter"] = 'Q'+df['q'].astype(int).astype(str) + "/" + df['y'].astype(int).astype(str)
	df['0'] = df['quarter']
	df['1']= df['revenue'].astype(int)
	new_df = df[['0','1']]
	quarters = new_df.to_dict('records')

	return render_template('viewRevenue.html', quarters = quarters)


# display top 3 most popular desintations for last 3 months and last year
@app.route('/topDestinations', methods=['GET', 'POST'])
def topDestinations():

	# get top 3 destinations for the last 3 months
	cursor = conn.cursor()
	query = 'SELECT arr_airport, count(Ticket.ID) as count FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE purchase_date_time <= CURRENT_TIMESTAMP and purchase_date_time>= DATE_ADD(NOW(), INTERVAL -3 MONTH) GROUP BY arr_airport ORDER BY arr_airport DESC LIMIT 3'
	cursor.execute(query)
	months = cursor.fetchall()
	cursor.close()

	# get top 3 destinations for the last year
	cursor = conn.cursor()
	query = 'SELECT arr_airport, count(Ticket.ID) as count FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE purchase_date_time <= CURRENT_TIMESTAMP and purchase_date_time>= DATE_ADD(NOW(), INTERVAL -1 YEAR) GROUP BY arr_airport ORDER BY arr_airport DESC LIMIT 3'
	cursor.execute(query)
	year = cursor.fetchall()
	cursor.close()

	return render_template('viewDestinations.html', months = months, year= year)


# display existing phone numbers
@app.route('/addPhoneNumber', methods=['GET', 'POST'])
def addPhoneNumber():

	# get session username
	username = session['username']

	# get existing phone numbers for this username
	cursor = conn.cursor()
	query = 'SELECT phone_number FROM Phone_Number WHERE username = %s'
	cursor.execute(query, (username))
	phones = cursor.fetchall()
	cursor.close()

	return render_template('addPhoneNumber.html', phones = phones)


# allow staff to add phone numbers to their profile
@app.route('/addNumber', methods=['GET', 'POST'])
def addNumber():

	# get session username
	username = session['username']

	# get existing phone numbers for this username
	cursor = conn.cursor()
	query = 'SELECT phone_number FROM Phone_Number WHERE username = %s'
	cursor.execute(query, (username))
	phones = cursor.fetchall()
	cursor.close()

	# get info from forms
	phone_number = request.form['phone_number']

	# check to see if the phone number already exist for the username
	cursor = conn.cursor()
	query = 'SELECT phone_number FROM Phone_Number WHERE username = %s and phone_number = %s'
	cursor.execute(query, (username, phone_number))
	exists = cursor.fetchall()
	cursor.close()

	if(exists): # check to see if the phone number already exist for the username
		error = "This phone number already exists in your account"
		return render_template('addPhoneNumber.html', phones = phones, error = error)
	else:
		# add phone number
		cursor = conn.cursor()
		ins = 'INSERT INTO Phone_Number VALUES(%s, %s)'
		cursor.execute(ins, (username, phone_number))
		conn.commit()
		cursor.close()

		# get updated phone numbers
		cursor = conn.cursor()
		query = 'SELECT phone_number FROM Phone_Number WHERE username = %s'
		cursor.execute(query, (username))
		phones = cursor.fetchall()
		cursor.close()

		message = "Phone number "+phone_number+" successfully added!"
		return render_template('addPhoneNumber.html', phones = phones, message = message)


# allow customers to log out
@app.route('/customerLogout')
def customerLogout():
	email = session['email']
	session.pop('email')
	message= email+" has been successfully logged out"
	return render_template('index.html', message = message)


# allow staff to log out
@app.route('/staffLogout')
def staffLogout():
	username = session['username']
	session.pop('username')
	message= username+" has been successfully logged out"
	return render_template('index.html', message = message)
		

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION


if __name__ == "__main__":
	app.run(debug=True)
