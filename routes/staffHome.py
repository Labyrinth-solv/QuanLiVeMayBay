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



@staffHome_bp.route('/viewFlights', methods=['GET', 'POST'])
def viewFlights():
	username = session['username']
	cursor = conn.cursor(DictCursor)

	# 🔹 Lấy danh sách sân bay (dropdown)
	cursor.execute("SELECT DISTINCT name, city FROM airport ORDER BY city")
	airports = cursor.fetchall()

	# 🔹 Lấy danh sách tất cả các chuyến bay (dùng cho dropdown hoặc hiển thị toàn bộ)
	cursor.execute('''
		SELECT flight_number, dep_airport, arr_airport, dep_date_time
		FROM Flight
		WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
		ORDER BY dep_date_time DESC
	''', (username,))
	flights = cursor.fetchall()

	# Nếu là GET → hiển thị chuyến bay 30 ngày tới
	if request.method == 'GET':
		cursor.execute('''
			SELECT * FROM Flight
			WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
			  AND dep_date_time > CURRENT_DATE
			  AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
		''', (username,))
		next30 = cursor.fetchall()
		cursor.close()
		return render_template('viewFlights.html',
							   next30=next30,
							   airports=airports,
							   flights=flights,
							   search_flights=None,
							   error=None)

	# Nếu là POST → lọc theo điều kiện
	start_date = request.form.get('start_date')
	end_date = request.form.get('end_date')
	source_airport = request.form.get('source')
	destination_airport = request.form.get('destination')

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

	cursor.execute(query, tuple(params))
	search_flights = cursor.fetchall()
	cursor.close()

	if not search_flights:
		error = "No flights found matching your criteria."
		return render_template('viewFlights.html',
							   next30=[],
							   search_flights=[],
							   airports=airports,
							   flights=flights,
							   error=error)

	return render_template('viewFlights.html',
						   next30=[],
						   search_flights=search_flights,
						   airports=airports,
						   flights=flights,
						   error=[])



@staffHome_bp.route('/searchFlightCustomers', methods=['POST'])
def searchFlightCustomers():
	username = session['username']
	flight_number = request.form.get('flight_number')

	# 🔹 Lấy danh sách chuyến bay (để giữ dropdown)
	cursor = conn.cursor(DictCursor)
	cursor.execute('''
		SELECT flight_number, dep_airport, arr_airport, dep_date_time
		FROM Flight
		WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
		ORDER BY dep_date_time DESC
	''', (username,))
	flights = cursor.fetchall()

	# 🔹 Truy vấn khách hàng
	cursor.execute('''
		SELECT Customer.email, Customer.name AS customer_name
		FROM Customer
		JOIN Ticket ON Customer.email = Ticket.email
		WHERE Ticket.name IN (SELECT name FROM Airline_Staff WHERE username = %s)
		AND Ticket.flight_number = %s
	''', (username, flight_number))
	customers = cursor.fetchall()
	cursor.close()

	# 🔹 Nếu không có khách hàng
	if not customers:
		error2 = f"No customers found for flight {flight_number}."
		return render_template(
			'viewFlights.html',
			flights=flights,
			search_flight_customers=[],
			error2=error2
		)

	# 🔹 Có khách hàng
	return render_template(
		'viewFlights.html',
		flights=flights,
		search_flight_customers=customers,
		error2=None
	)


	#XỬ LÍ CHO createFlight.html
# display form to create a new flight and display all flights for next 30 days run by their airline
# @staffHome_bp.route('/createFlight', methods=['GET', 'POST'])
# def createFlight():
#     username = session['username']
#
#     # lấy các chuyến bay sắp tới (giữ nguyên)
#     cursor = conn.cursor()
#     query = '''
#         SELECT * FROM Flight
#         WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
#         AND dep_date_time > CURRENT_DATE
#         AND dep_date_time < DATE_ADD(NOW(), INTERVAL 1 MONTH)
#     '''
#     cursor.execute(query, (username,))
#     next30 = cursor.fetchall()
#     cursor.close()
#
#     #  lấy danh sách sân bay
#     cursor = conn.cursor()
#     cursor.execute("SELECT name, city FROM Airport")
#     airports = cursor.fetchall()
#     cursor.close()
#
#     #  lấy danh sách máy bay của hãng nhân viên
#     cursor = conn.cursor()
#     query = '''
#         SELECT A.ID
#         FROM Airplane A
#         JOIN Airline_Staff S ON A.name = S.name
#         WHERE S.username = %s
#     '''
#     cursor.execute(query, (username,))
#     airplanes = cursor.fetchall()
#     cursor.close()
#
#     #  trạng thái cố định
#     statuses = ['on-time', 'delayed']
#
#     return render_template(
#         'createFlight.html',
#         next30=next30,
#         airports=airports,
#         airplanes=airplanes,
#         statuses=statuses
#     )

# allow staff to create a new flight
@staffHome_bp.route('/createFlight', methods=['GET', 'POST'])
def createFlight():
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
		cursor = conn.cursor(DictCursor)
		query = '''
			SELECT Airplane.ID, Airplane.airplane_name
			FROM Airplane
			JOIN Airline_Staff ON Airplane.name = Airline_Staff.name
			WHERE Airline_Staff.username = %s
		'''
		cursor.execute(query, (username,))
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
	base_price = float(request.form['base_price'])
	ID = request.form['ID']
	status = request.form['status']
	message=f"Fail"

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
		cursor.execute('SELECT * FROM Flight WHERE flight_number = %s', (flight_number,))
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
						INSERT INTO flight VALUES
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
	cursor.execute('SELECT ID FROM Airplane')
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
		message=message
	)


#     return render_template('changeStatus.html')


# allow staff to change flight status
@staffHome_bp.route('/changeStatus', methods=['GET', 'POST'])
def changeFlightStatus():
	username = session['username']
	cursor = conn.cursor(DictCursor)

	# Lấy tất cả chuyến bay của hãng mà nhân viên đang thuộc
	cursor.execute('''
		SELECT flight_number, dep_airport, arr_airport, dep_date_time, status 
		FROM Flight 
		WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)
		ORDER BY dep_date_time DESC
	''', (username,))
	flights = cursor.fetchall()
	cursor.close()

	if request.method == 'GET':
		return render_template('changeStatus.html', username=username, flights=flights, error=None)

	# Khi người dùng submit form
	flight_number = request.form.get('flight_number')
	desired_status = request.form.get('desired_status')

	cursor = conn.cursor()
	query = "UPDATE Flight SET status = %s WHERE flight_number = %s"
	cursor.execute(query, (desired_status, flight_number))
	conn.commit()
	cursor.close()

	return render_template('changeStatus.html', username=username, flights=flights, error="Status updated successfully.")

# display form to add airplane and all airplanes owned by staff's airline
@staffHome_bp.route('/addAirplane', methods=['GET', 'POST'])
def addAirplane():

	# get session username
	username = session['username']

	# GET METHOD Truyền dữ liệu vào bảng khi người dùng gọi lần đầu
	cursor = conn.cursor(DictCursor)
	query = 'SELECT name from airline WHERE name in (SELECT name FROM Airline_Staff WHERE username = %s)'
	cursor.execute(query, (username,))
	airlines = cursor.fetchall()
	cursor.close()

	return render_template('addAirplane.html', airlines=airlines)


# allow staff to add airplane
@staffHome_bp.route('/createAirplane', methods=['GET', 'POST'])
def createAirplane():
    # get session username
    username = session['username']

    # get airplanes owned by staff's airline
    cursor = conn.cursor()
    query = 'SELECT * FROM Airplane WHERE name IN (SELECT name FROM Airline_Staff WHERE username = %s)'
    cursor.execute(query, (username,))
    airplanes = cursor.fetchall()
    cursor.close()

    # get info from forms
    ID = request.form['ID']
    seats = request.form['seats']
    airplane_name = request.form['airplane_name']
    airline_name = request.form['airline_name']

    # check that the airplane does not already exist
    cursor = conn.cursor()
    query = 'SELECT * FROM Airplane WHERE name = %s AND ID = %s'
    cursor.execute(query, (airline_name, ID))
    exists = cursor.fetchall()
    cursor.close()

    if exists:  # check that the airplane does not already exist
        error = "This Airplane already exists"
        return render_template('addAirplane.html', airplanes=airplanes, error=error)
    else:
        # add airplane to system
        cursor = conn.cursor()
        ins = 'INSERT INTO Airplane VALUES (%s, %s, %s, %s)'
        cursor.execute(ins, (airline_name, ID, seats, airplane_name))
        conn.commit()
        cursor.close()

        # send success message to staffHome
        message = f"{airline_name} Airplane {ID} successfully added!"
        return render_template('staffHome.html', message=message)



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

