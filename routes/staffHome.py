from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, Blueprint
import pymysql.cursors

staffHome_bp = Blueprint("staffHome", __name__)
conn = get_connection()


# redirect to staffHome and display staff name
@staffHome_bp.route('/staffHome')
def staffHome():
	# get session username
	username  = session['username']

	# get staff's name
	cursor = conn.cursor()
	query = 'SELECT name FROM Airline_Staff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	cursor.close()
	error = None
	return render_template('staffHome.html', username= username, error = error)


# allow staff to view all flights of their airline
@staffHome_bp.route('/viewFlights', methods=['GET', 'POST'])
def viewFlights():
    # get session username
    username = session['username']

    # get all flights for next 30 days run by their airline
    cursor = conn.cursor()
    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
    cursor.execute(query, (username))
    next30 = cursor.fetchall()
    cursor.close()

    return render_template('viewFlights.html', next30=next30)


# allow staff to search flights run by their airline
@staffHome_bp.route('/searchStaffFlights', methods=['GET', 'POST'])
def searchStaffFlights():
    # get session username
    username = session['username']

    # get all flights for next 30 days run by their airline
    cursor = conn.cursor()
    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
    cursor.execute(query, (username))
    next30 = cursor.fetchall()
    cursor.close()

    # get info from forms
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    source_airport = request.form['source']
    destination_airport = request.form['destination']

    # get name of destination airport
    if destination_airport:
        cursor = conn.cursor()
        query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
        cursor.execute(query, (destination_airport, destination_airport))
        destination_airport = cursor.fetchone()
        cursor.close()
        if (destination_airport):
            destination_airport = destination_airport['name']
        else:
            error = "No airport found"
            return render_template("viewFlights.html", error=error, next30=next30)

    # get name of source airport
    if source_airport:
        cursor = conn.cursor()
        query = 'SELECT name FROM Airport WHERE name=%s or city=%s'
        cursor.execute(query, (source_airport, source_airport))
        source_airport = cursor.fetchone()
        cursor.close()
        if (source_airport):
            source_airport = source_airport['name']
        else:
            error = "No airport found"
            return render_template("viewFlights.html", error=error, next30=next30)

    # select correct query based on the information given
    if start_date:
        if end_date:
            if source_airport:
                if destination_airport:
                    cursor = conn.cursor()
                    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
                    cursor.execute(query, (username, start_date, end_date, source_airport, destination_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
                else:
                    cursor = conn.cursor()
                    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s and dep_airport= %s'
                    cursor.execute(query, (username, start_date, end_date, source_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
            elif destination_airport:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s and arr_airport= %s'
                cursor.execute(query, (username, start_date, end_date, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_date_time<= %s'
                cursor.execute(query, (username, start_date, end_date))
                search_flights = cursor.fetchall()
                cursor.close()
        else:
            if source_airport:
                if destination_airport:
                    cursor = conn.cursor()
                    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_airport= %s and arr_airport=  %s'
                    cursor.execute(query, (username, start_date, source_airport, destination_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
                else:
                    cursor = conn.cursor()
                    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and dep_airport= %s'
                    cursor.execute(query, (username, start_date, source_airport))
                    search_flights = cursor.fetchall()
                    cursor.close()
            elif destination_airport:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s and arr_airport=  %s'
                cursor.execute(query, (username, start_date, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT  * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time>= %s'
                cursor.execute(query, (username, start_date))
                search_flights = cursor.fetchall()
                cursor.close()
    elif end_date:
        if source_airport:
            if destination_airport:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s and dep_airport= %s and arr_airport=  %s'
                cursor.execute(query, (username, end_date, source_airport, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s and dep_airport= %s'
                cursor.execute(query, (username, end_date, source_airport))
                search_flights = cursor.fetchall()
                cursor.close()
        elif destination_airport:
            cursor = conn.cursor()
            query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s and arr_airport=  %s'
            cursor.execute(query, (username, end_date, destination_airport))
            search_flights = cursor.fetchall()
            cursor.close()
        else:
            cursor = conn.cursor()
            query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time<= %s'
            cursor.execute(query, (username, end_date))
            search_flights = cursor.fetchall()
            cursor.close()
    elif source_airport or destination_airport:
        if source_airport:
            if destination_airport:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_airport= %s and arr_airport=  %s'
                cursor.execute(query, (username, source_airport, destination_airport))
                search_flights = cursor.fetchall()
                cursor.close()
            else:
                cursor = conn.cursor()
                query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_airport= %s'
                cursor.execute(query, (username, source_airport))
                search_flights = cursor.fetchall()
                cursor.close()
        elif destination_airport:
            cursor = conn.cursor()
            query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and arr_airport=  %s'
            cursor.execute(query, (username, destination_airport))
            search_flights = cursor.fetchall()
            cursor.close()
    else:
        search_flights = None

    if not start_date and not end_date and not source_airport and not destination_airport:
        error = "No flights found"
        return render_template("viewFlights.html", error=error, next30=next30)
    elif search_flights:
        return render_template("viewFlights.html", search_flights=search_flights, next30=next30)
    else:
        error = "No flights found"
        return render_template("viewFlights.html", error=error, next30=next30)



# allow staff to search all of the customers on a flight
@staffHome_bp.route('/searchFlightCustomers', methods=['GET', 'POST'])
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


    #XỬ LÍ CHO createFlight.html
# display form to create a new flight and display all flights for next 30 days run by their airline
@staffHome_bp.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
    # get session username
    username = session['username']

    # get all flights for next 30 days run by their airline
    cursor = conn.cursor()
    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
    cursor.execute(query, (username))
    next30 = cursor.fetchall()
    cursor.close()

    return render_template('createFlight.html', next30=next30)


# allow staff to create a new flight
@staffHome_bp.route('/createStaffFlight', methods=['GET', 'POST'])
def createStaffFlight():
    # get session username
    username = session['username']

    # get all flights for next 30 days run by their airline
    cursor = conn.cursor()
    query = 'SELECT * FROM Flight WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s) and dep_date_time > CURRENT_DATE and dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)'
    cursor.execute(query, (username))
    next30 = cursor.fetchall()
    cursor.close()

    # get info from forms
    flight_number = request.form['flight_number']
    source = request.form['source']
    destination = request.form['destination']
    dep_date = request.form['dep_date']
    dep_time = request.form['dep_time']
    arr_date = request.form['arr_date']
    arr_time = request.form['arr_time']
    base_price = request.form['base_price']
    ID = request.form['ID']
    status = request.form['status']

    # get name of airline of staff
    cursor = conn.cursor()
    query = 'SELECT name FROM Airline_Staff WHERE username = %s'
    cursor.execute(query, (username))
    name = cursor.fetchone()
    cursor.close()

    # check that the user is an airline staff
    if (not name):
        error = "You are not authorized to create a new flight"
        return render_template('createFlight.html', next30=next30, error=error)
    else:
        name = name['name']

        # check that flight number isn't taken in airline
        cursor = conn.cursor()
        query = 'SELECT name, flight_number FROM Flight WHERE name = %s and flight_number = %s'
        cursor.execute(query, (name, flight_number))
        taken = cursor.fetchone()
        cursor.close()

        if (taken):  # check that flight number isn't taken in airline
            error = "This flight number is already in use"
            return render_template('createFlight.html', next30=next30, error=error)
        else:
            # check that source and destination airports exist
            cursor = conn.cursor()
            query = 'SELECT name  FROM Airport WHERE name = %s'
            cursor.execute(query, source)
            source_airport = cursor.fetchone()

            cursor.execute(query, destination)
            destination_airport = cursor.fetchone()
            cursor.close()
            if not (source_airport and destination_airport):
                error = "Airport does not exist"
                return render_template('createFlight.html', next30=next30, error=error)
            else:
                # check that airplane exists in airline
                cursor = conn.cursor()
                query = 'SELECT name, ID FROM Airplane WHERE name = %s and ID = %s'
                cursor.execute(query, (name, ID))
                plane = cursor.fetchone()
                cursor.close()
                if (not plane):
                    error = "Airplane does not exist"
                    return render_template('createFlight.html', next30=next30, error=error)
                else:
                    # check that status is on-time or delayed
                    if (status not in ['on-time', 'delayed']):
                        error = "Status must be either on-time or delayed"
                        return render_template('createFlight.html', next30=next30, error=error)
                    else:
                        # add flight to system
                        cursor = conn.cursor()
                        ins = 'INSERT INTO Flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                        cursor.execute(ins,
                                       (name, flight_number, dep_date + " " + dep_time + ":00", source, destination,
                                        arr_date + " " + arr_time + ":00", base_price, ID, status))
                        conn.commit()
                        cursor.close()

                        # Lấy username từ session
                        username = session['username']

                        # Gửi thông báo thành công
                        message = name + " Flight Number " + flight_number + " was successfully created!"

                        # Trả về giao diện staffHome.html với username và message
                        return render_template('staffHome.html', username=username, message=message)

