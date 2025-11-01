from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection,Blueprint, datetime
import pymysql.cursors

customerHome_bp=Blueprint("customerHome", __name__)
conn=get_connection()


# redirect to customerHome and display customer name
@customerHome_bp.route('/customerHome')
def customerHome():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT name FROM Customer WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()['name']
    cursor.close()
    return render_template('customerHome.html', name=data)


# view customer's future and past flights
@customerHome_bp.route('/viewMyFlights')
def viewMyFlights():
    # get session email
    email = session['email']

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

    return render_template("viewMyFlights.html", future_flights=future_flights, past_flights=past_flights)


# view customer's future and past flights, as well as searched flights
@customerHome_bp.route('/searchMyFlights', methods=['GET', 'POST'])
def searchMyFlights():
    # get session email
    email = session['email']

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
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    destination_airport = request.form['destination']
    source_airport = request.form['source']

    # get destination airport name
    if (destination_airport):
        cursor = conn.cursor()
        query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
        cursor.execute(query, (destination_airport, destination_airport))
        destination_airport = cursor.fetchone()
        cursor.close()
        if (destination_airport):
            destination_airport = destination_airport['name']
        else:
            error = "No airport found"
            return render_template("viewMyFlights.html", error=error, future_flights=future_flights,
                                   past_flights=past_flights)

    # get source airport name
    if (source_airport):
        cursor = conn.cursor()
        query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
        cursor.execute(query, (source_airport, source_airport))
        source_airport = cursor.fetchone()
        cursor.close()
        if (source_airport):
            source_airport = source_airport['name']
        else:
            error = "No airport found"
            return render_template("viewMyFlights.html", error=error, future_flights=future_flights,
                                   past_flights=past_flights)

    # find correct query based on information given
    if (start_date):
        if (end_date):
            if (source_airport):
                if (destination_airport):
                    cursor = conn.cursor()
                    query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
                    cursor.execute(query, (start_date, end_date, source_airport, destination_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
                else:
                    cursor = conn.cursor()
                    query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s'
                    cursor.execute(query, (start_date, end_date, source_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
            elif (destination_airport):
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s and arr_airport= %s'
                cursor.execute(query, (start_date, end_date, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_date_time<= %s'
                cursor.execute(query, (start_date, end_date))
                search_flights = cursor.fetchall()
                cursor.close()
        else:
            if (source_airport):
                if (destination_airport):
                    cursor = conn.cursor()
                    query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_airport= %s and arr_airport=  %s'
                    cursor.execute(query, (start_date, source_airport, destination_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
                else:
                    cursor = conn.cursor()
                    query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and dep_airport= %s'
                    cursor.execute(query, (start_date, source_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
            elif (destination_airport):
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s and arr_airport=  %s'
                cursor.execute(query, (start_date, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time>= %s'
                cursor.execute(query, (start_date))
                search_flights = cursor.fetchall()
                cursor.close()
    elif (end_date):
        if (source_airport):
            if (destination_airport):
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
                cursor.execute(query, (end_date, source_airport, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s and dep_airport= %s'
                cursor.execute(query, (end_date, source_airport))
                search_flights = cursor.fetchall()
                cursor.close()
        elif (destination_airport):
            cursor = conn.cursor()
            query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s and arr_airport=  %s'
            cursor.execute(query, (end_date, destination_airport))
            search_flights = cursor.fetchall()
            cursor.close()
        else:
            cursor = conn.cursor()
            query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_date_time<= %s'
            cursor.execute(query, (end_date))
            search_flights = cursor.fetchall()
            cursor.close()
    elif (source_airport or destination_airport):
        if (source_airport):
            if (destination_airport):
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_airport= %s and arr_airport=  %s'
                cursor.execute(query, (source_airport, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE dep_airport= %s'
                cursor.execute(query, (source_airport))
                search_flights = cursor.fetchall()
                cursor.close()
        elif (destination_airport):
            cursor = conn.cursor()
            query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on (Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number) WHERE arr_airport=  %s'
            cursor.execute(query, (destination_airport))
            search_flights = cursor.fetchall()
            cursor.close()
    else:
        search_flights = None

    if (not start_date and not end_date and not source_airport and not destination_airport):
        error = "No flights found"
        return render_template("viewMyFlights.html", error=error, future_flights=future_flights,
                               past_flights=past_flights)
    elif (search_flights):
        return render_template("viewMyFlights.html", search_flights=search_flights, future_flights=future_flights,
                               past_flights=past_flights)
    else:
        error = "No flights found"
        return render_template("viewMyFlights.html", error=error, future_flights=future_flights,
                               past_flights=past_flights)


# display searchPurchase page
@customerHome_bp.route('/searchPurchase')
def searchPurchase():
    return render_template("searchPurchase.html")


# search flights
@customerHome_bp.route('/searchPurchaseFlight', methods=['GET', 'POST'])
def searchPurchaseFlight():
    # collect information from forms and convert dates to datetime objects
    source = request.form['source']
    destination = request.form['destination']
    depart_date = request.form['depart_date']
    return_date = request.form['return_date']
    if (depart_date):
        depart_date = datetime.strptime(request.form['depart_date'], '%Y-%m-%d')
    if (return_date):
        return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d')

    # get airport names
    if (depart_date or return_date):
        cursor = conn.cursor()
        query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
        cursor.execute(query, (source, source))
        source_airport = cursor.fetchone()
        cursor.close()
        if (source_airport):
            source_airport = source_airport['name']
        else:
            error = "No airport found"
            return render_template("searchPurchase.html", error=error)

        cursor = conn.cursor()
        query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
        cursor.execute(query, (destination, destination))
        destination_airport = cursor.fetchone()
        cursor.close()
        if (destination_airport):
            destination_airport = destination_airport['name']
        else:
            error = "No airport found"
            return render_template("searchPurchase.html", error=error)

        # search for flights based on whether depart_date, return_date, or both were given
        if (depart_date and not return_date):
            cursor = conn.cursor()
            query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)= %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
            cursor.execute(query,
                           (source_airport, destination_airport, depart_date.year, depart_date.month, depart_date.day))
            departing_flights = cursor.fetchall()
            cursor.close()
            if (departing_flights):
                return render_template("searchPurchase.html", departing_flights=departing_flights)
            else:
                error = "No flights found"
                return render_template("searchPurchase.html", error=error)

        if (return_date and not depart_date):
            cursor = conn.cursor()
            query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)= %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
            cursor.execute(query,
                           (destination_airport, source_airport, return_date.year, return_date.month, return_date.day))
            returning_flights = cursor.fetchall()
            cursor.close()
            if (returning_flights):
                return render_template("searchPurchase.html", returning_flights=returning_flights)
            else:
                error = "No flights found"
                return render_template("searchPurchase.html", error=error)

        if (depart_date and return_date):
            cursor = conn.cursor()
            query = 'SELECT * FROM Flight WHERE dep_airport=%s and arr_airport=%s and year(dep_date_time)= %s and month(dep_date_time) = %s and day(dep_date_time) = %s'
            cursor.execute(query,
                           (source_airport, destination_airport, depart_date.year, depart_date.month, depart_date.day))
            departing_flights = cursor.fetchall()

            cursor.execute(query,
                           (destination_airport, source_airport, return_date.year, return_date.month, return_date.day))
            returning_flights = cursor.fetchall()
            cursor.close()

            if (departing_flights and returning_flights):
                return render_template("searchPurchase.html", departing_flights=departing_flights,
                                       returning_flights=returning_flights)
            elif (departing_flights):
                return render_template("searchPurchase.html", departing_flights=departing_flights)
            elif (returning_flights):
                return render_template("searchPurchase.html", returning_flights=returning_flights)
            else:
                error = "No flighs found"
                return render_template("searchPurchase.html", error=error)

    else:
        error = "Please enter a departing and/or returning date"
        return render_template("searchPurchase.html", error=error)


# purchase flight ticket
@customerHome_bp.route('/purchase', methods=['GET', 'POST'])
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
@customerHome_bp.route('/purchaseInfo', methods=['GET', 'POST'])
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
@customerHome_bp.route('/rate', methods=['GET', 'POST'])
def rate():
    # get session email
    email = session['email']

    # get previous flights
    cursor = conn.cursor()
    query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and purchase_date_time< CURRENT_TIMESTAMP and arr_date_time< CURRENT_TIMESTAMP'
    cursor.execute(query, (email))
    previous_flights = cursor.fetchall()
    cursor.close()

    error = None

    return render_template("rateTemplate.html", previous_flights=previous_flights, error=error)


# rate previous flight
@customerHome_bp.route('/rateFlight', methods=['GET', 'POST'])
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
    if (not rating_flight):
        error = "Flight not found"
        return render_template("rateTemplate.html", previous_flights=previous_flights, error=error)
    elif (rating < 1 or rating > 10):  # check that the rating is valid
        error = "Invalid Rating"
        return render_template("rateTemplate.html", previous_flights=previous_flights, error=error)
    else:
        # create new rating_id as max(rating_id)+1
        cursor = conn.cursor()
        query = 'SELECT max(rating_id) as max_id FROM Flight_Ratings'
        cursor.execute(query)
        max_id = cursor.fetchone()['max_id']
        cursor.close()
        if (not max_id or max_id < 1):
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
        message = "Rating for " + str(airline_name) + " Flight Number " + str(flight_number) + " successfully entered!"
        return render_template('customerHome.html', name=data, message=message)


# display page with spending info for last year and last six months
@customerHome_bp.route('/trackSpending', methods=['GET', 'POST'])
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
    df = pd.DataFrame(columns=['m', 'y', 'spending'])
    df = df.append(m0, ignore_index=True).append(m1, ignore_index=True).append(m2, ignore_index=True).append(m3,
                                                                                                             ignore_index=True).append(
        m4, ignore_index=True).append(m5, ignore_index=True).append(m6, ignore_index=True)
    df["date"] = df['m'].astype(int).astype(str) + "/" + df["y"].astype(int).astype(str)
    df.fillna(0, inplace=True)
    df['relative_month'] = df.index.astype(str)
    df.set_index('relative_month', inplace=True)
    df['0'] = df['date']
    df['1'] = df['spending']

    monthly_df = df[['0', '1']]
    monthly = monthly_df.to_dict('records')

    return render_template("trackSpending.html", year=year, monthly=monthly)


# search spending by date range
@customerHome_bp.route('/searchSpending', methods=['GET', 'POST'])
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
    df = pd.DataFrame(columns=['m', 'y', 'spending'])
    df = df.append(m0, ignore_index=True).append(m1, ignore_index=True).append(m2, ignore_index=True).append(m3,
                                                                                                             ignore_index=True).append(
        m4, ignore_index=True).append(m5, ignore_index=True).append(m6, ignore_index=True)
    df["date"] = df['m'].astype(int).astype(str) + "/" + df["y"].astype(int).astype(str)
    df.fillna(0, inplace=True)
    df['relative_month'] = df.index.astype(str)
    df.set_index('relative_month', inplace=True)
    df['0'] = df['date']
    df['1'] = df['spending']

    monthly_df = df[['0', '1']]
    monthly = monthly_df.to_dict('records')

    # get info from forms and turn them into datetime objects
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    # get number of months in between dates
    num_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

    if num_months < 1:  # check that the end_date comes after the start_date
        error = "End date must be after the start date"
        return render_template("trackSpending.html", year=year, monthly=monthly, error=error)
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
        for i in range(num_months - 1):
            new_month = new_month + 1
            if new_month > 12:
                new_month -= 12
                new_year = new_year + 1
            new = {'year': new_year, 'month': new_month}
            empty = empty.append(new, ignore_index=True)
        spending = pd.DataFrame.from_dict(by_month)

        # combine monthly spending and empty df to get complete breakdown of each month in the searched date range
        search_df = pd.merge(empty, spending, how='left', on=['year', 'month']).fillna(0)
        search_df["date"] = search_df['month'].astype(str) + "/" + search_df["year"].astype(int).astype(str)
        search_df['0'] = search_df['date']
        search_df['1'] = search_df['month_spending']
        new_df = search_df[['0', '1']]
        searched = new_df.to_dict('records')

        return render_template("trackSpending.html", year=year, monthly=monthly, total=total, searched=searched)

