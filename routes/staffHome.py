from pymysql.cursors import DictCursor

from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, Blueprint, datetime
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


@staffHome_bp.route('/searchStaffFlights', methods=['GET', 'POST'])
def searchStaffFlights():
    username = session['username']
    cursor = conn.cursor(DictCursor)

    # 🔹 Lấy danh sách chuyến bay 30 ngày tới (cho phần next30)
    cursor.execute('''
        SELECT * FROM Flight 
        WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
          AND dep_date_time > CURRENT_DATE
          AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
    ''', (username,))
    next30 = cursor.fetchall()
    cursor.close()

    # 🔹 Lấy danh sách sân bay (để hiển thị dropdown)
    cursor = conn.cursor(DictCursor)
    cursor.execute("SELECT DISTINCT name, city FROM Airport ORDER BY city")
    airports = cursor.fetchall()
    cursor.close()

    # Nếu là GET (chưa submit form) → chỉ hiển thị form rỗng
    if request.method == 'GET':
        return render_template('viewFlights.html',
                               next30=next30,
                               airports=airports,
                               search_flights=None,
                               error=None)

    # 🔹 Lấy dữ liệu từ form POST
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    source_airport = request.form.get('source')
    destination_airport = request.form.get('destination')

    # 🔹 Build query linh hoạt (thay vì 7-8 if lồng nhau)
    query = '''
        SELECT * FROM Flight 
        WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
    '''
    params = [username]

    if start_date:
        query += ' AND dep_date_time >= %s'
        params.append(start_date)
    if end_date:
        query += ' AND dep_date_time <= %s'
        params.append(end_date)
    if source_airport:
        query += ' AND dep_airport = %s'
        params.append(source_airport)
    if destination_airport:
        query += ' AND arr_airport = %s'
        params.append(destination_airport)

    cursor = conn.cursor(DictCursor)
    cursor.execute(query, tuple(params))
    search_flights = cursor.fetchall()
    cursor.close()

    # 🔹 Trả kết quả ra template
    if not search_flights:
        error = "No flights found matching your criteria."
        return render_template("viewFlights.html",
                               error=error,
                               next30=next30,
                               airports=airports)
    else:
        return render_template("viewFlights.html",
                               search_flights=search_flights,
                               next30=next30,
                               airports=airports)


@staffHome_bp.route('/searchFlightCustomers', methods=['GET', 'POST'])
def searchFlightCustomers():
    username = session['username']

    # lấy các chuyến bay của hãng nhân viên
    cursor = conn.cursor()
    query = '''
        SELECT flight_number, dep_airport, arr_airport, dep_date_time
        FROM Flight
        WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
        AND dep_date_time > CURRENT_DATE
        AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
    '''
    cursor.execute(query, (username,))
    flights = cursor.fetchall()
    cursor.close()

    # Nếu GET: chỉ hiển thị dropdown
    if request.method == 'GET':
        return render_template('viewFlights.html', flights=flights)

    # Nếu POST: lấy flight được chọn
    flight_number = request.form.get('flight_number')

    cursor = conn.cursor()
    query = '''
        SELECT Customer.email, Customer.name AS customer_name, Ticket.seat_number
        FROM Customer
        JOIN Ticket ON Customer.email = Ticket.email
        WHERE Ticket.name IN (SELECT name FROM Airline_Staff WHERE username = %s)
        AND Ticket.flight_number = %s
    '''
    cursor.execute(query, (username, flight_number))
    search_flight_customers = cursor.fetchall()
    cursor.close()

    if search_flight_customers:
        return render_template(
            'viewFlights.html',
            flights=flights,
            search_flight_customers=search_flight_customers
        )
    else:
        error2 = "No customers found or invalid flight number."
        return render_template('viewFlights.html', flights=flights, error2=error2)


    #XỬ LÍ CHO createFlight.html
# display form to create a new flight and display all flights for next 30 days run by their airline
@staffHome_bp.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
    username = session['username']

    # lấy các chuyến bay sắp tới (giữ nguyên)
    cursor = conn.cursor()
    query = '''
        SELECT * FROM Flight 
        WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
        AND dep_date_time > CURRENT_DATE
        AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
    '''
    cursor.execute(query, (username,))
    next30 = cursor.fetchall()
    cursor.close()

    #  lấy danh sách sân bay
    cursor = conn.cursor()
    cursor.execute("SELECT name, city FROM Airport")
    airports = cursor.fetchall()
    cursor.close()

    #  lấy danh sách máy bay của hãng nhân viên
    cursor = conn.cursor()
    query = '''
        SELECT A.ID 
        FROM Airplane A 
        JOIN Airline_Staff S ON A.name = S.name 
        WHERE S.username = %s
    '''
    cursor.execute(query, (username,))
    airplanes = cursor.fetchall()
    cursor.close()

    #  trạng thái cố định
    statuses = ['on-time', 'delayed']

    return render_template(
        'createFlight.html',
        next30=next30,
        airports=airports,
        airplanes=airplanes,
        statuses=statuses
    )

# allow staff to create a new flight
@staffHome_bp.route('/createStaffFlight', methods=['GET', 'POST'])
def createStaffFlight():
    username = session['username']

    # Lấy danh sách chuyến bay 30 ngày tới
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = '''
        SELECT * FROM Flight
        WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
        AND dep_date_time > CURRENT_DATE
        AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
    '''
    cursor.execute(query, (username,))
    next30 = cursor.fetchall()
    cursor.close()

    # Nếu là GET request → chỉ hiển thị trang
    if request.method == 'GET':
        # Lấy danh sách sân bay
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT name, city FROM Airport")
        airports = cursor.fetchall()
        cursor.close()

        # Lấy danh sách máy bay của hãng
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT ID FROM Airplane WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)", (username,))
        airplanes = cursor.fetchall()
        cursor.close()

        statuses = ['on-time', 'delayed']

        return render_template(
            'createFlight.html',
            next30=next30,
            airports=airports,
            airplanes=airplanes,
            statuses=statuses
        )

    # Nếu là POST request → xử lý form
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

    # Lấy tên hãng của nhân viên
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT name FROM Airline_Staff WHERE username = %s', (username,))
    name_data = cursor.fetchone()
    cursor.close()

    if not name_data:
        error = "You are not authorized to create a new flight"
    else:
        name = name_data['name']

        # Kiểm tra trùng số hiệu
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM Flight WHERE name = %s AND flight_number = %s', (name, flight_number))
        taken = cursor.fetchone()
        cursor.close()

        if taken:
            error = "This flight number is already in use"
        else:
            # Kiểm tra sân bay
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('SELECT * FROM Airport WHERE name = %s', (source,))
            src_airport = cursor.fetchone()
            cursor.execute('SELECT * FROM Airport WHERE name = %s', (destination,))
            dest_airport = cursor.fetchone()
            cursor.close()

            if not (src_airport and dest_airport):
                error = "Airport does not exist"
            else:
                # Kiểm tra máy bay
                cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute('SELECT * FROM Airplane WHERE name = %s AND ID = %s', (name, ID))
                plane = cursor.fetchone()
                cursor.close()

                if not plane:
                    error = "Airplane does not exist"
                elif status not in ['on-time', 'delayed']:
                    error = "Status must be either on-time or delayed"
                else:
                    # Thêm chuyến bay mới
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO Flight VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        name,
                        flight_number,
                        dep_date + " " + dep_time + ":00",
                        source,
                        destination,
                        arr_date + " " + arr_time + ":00",
                        base_price,
                        ID,
                        status
                    ))
                    conn.commit()
                    cursor.close()

                    message = f"{name} Flight Number {flight_number} was successfully created!"
                    error = None

    # Sau khi tạo hoặc lỗi → reload lại dữ liệu và render cùng trang
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT name, city FROM Airport')
    airports = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT ID FROM Airplane WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)', (username,))
    airplanes = cursor.fetchall()
    cursor.close()

    statuses = ['on-time', 'delayed']

    # Cập nhật danh sách chuyến bay mới nhất
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('''
        SELECT * FROM Flight
        WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
        AND dep_date_time > CURRENT_DATE
        AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
    ''', (username,))
    next30 = cursor.fetchall()
    cursor.close()

    return render_template(
        'createFlight.html',
        next30=next30,
        airports=airports,
        airplanes=airplanes,
        statuses=statuses,
        error=error if 'error' in locals() else None,
        message=message if 'message' in locals() else None
    )


# display form to change flight status
@staffHome_bp.route('/changeStatus', methods=['GET', 'POST'])
def changeStatus():
    return render_template('changeStatus.html')


# allow staff to change flight status
@staffHome_bp.route('/changeFlightStatus', methods=['GET', 'POST'])
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

    if (desired_status not in ['on-time', 'delayed']):  # check that the desired status is on-time or delayed
        error = "Status must be either on-time or delayed"
        return render_template('changeStatus.html', error=error)
    elif (not searched_flight):  # check that the searched flight exists
        error = "No flight found"
        return render_template('changeStatus.html', error=error)
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
        message = airline_name + " Flight Number " + flight_number + " successfully updated to '" + desired_status
        return render_template('staffHome.html', first_name=data['first_name'], last_name=data['last_name'],
                               message=message)


# display form to add airplane and all airplanes owned by staff's airline
@staffHome_bp.route('/addAirplane', methods=['GET', 'POST'])
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
@staffHome_bp.route('/createAirplane', methods=['GET', 'POST'])
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
@staffHome_bp.route('/addAirport', methods=['GET', 'POST'])
def addAirport():
	return render_template('addAirport.html')


# allow staff to add airport
@staffHome_bp.route('/createAirport', methods=['GET', 'POST'])
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


# allow staff to log out
@staffHome_bp.route('/staffLogout')
def staffLogout():
	username = session['username']
	session.pop('username')
	message= username+" has been successfully logged out"
	return render_template('index.html', message = message)

