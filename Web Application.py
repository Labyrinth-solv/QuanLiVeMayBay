#Import packages
from flask import Flask, render_template, request, session, url_for, redirect, Blueprint
import pymysql.cursors
from datetime import datetime
import pandas as pd
from db_config import get_connection
import routes.customer
from routes import customer, staff, search, checkStatus, customerHome, staffHome

#Initialize the app from Flask
app = Flask(__name__)
conn=get_connection()

app.register_blueprint(customer.customer_bp)
app.register_blueprint(staff.staff_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(checkStatus.check_bp)
app.register_blueprint(customerHome.customerHome_bp)
app.register_blueprint(staffHome.staffHome_bp)


# display index page
@app.route('/')
def hello():
	return render_template('index.html')



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
