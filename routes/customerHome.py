import pandas as pd
from pymysql.cursors import DictCursor

from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection,Blueprint, datetime
import pymysql.cursors

customerHome_bp=Blueprint("customerHome", __name__)
conn=get_connection()


# redirect to customerHome and display customer name
@customerHome_bp.route('/customerHome')
def customerHome():
    email = session['email']
    cursor = conn.cursor(DictCursor)
    query = 'SELECT name FROM Customer WHERE email = %s'
    cursor.execute(query, (email,))
    data = cursor.fetchone()
    cursor.close()
    return render_template('customerHome.html', name=data)


# view customer's future and past flights
@customerHome_bp.route('/viewMyFlights')
def viewMyFlights():
    # get session email
    email = session['email']

    cursor=conn.cursor(DictCursor)
    query= 'SELECT * FROM airport'
    cursor.execute(query)
    airports=cursor.fetchall()
    cursor.close()
    # show future flights
    cursor = conn.cursor()
    query = ('SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time '
             'FROM Ticket '
             'left join Flight '
             '  on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number '
             'WHERE email=%s and dep_date_time> CURRENT_TIMESTAMP')
    cursor.execute(query, (email))
    future_flights = cursor.fetchall()
    cursor.close()

    # show past flights
    cursor = conn.cursor()
    query = 'SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport, dep_date_time, arr_date_time, status, sold_price, Ticket.ID, purchase_date_time FROM Ticket left join Flight on Ticket.name = Flight.name and Ticket.flight_number = Flight.flight_number WHERE email=%s and dep_date_time< CURRENT_TIMESTAMP'
    cursor.execute(query, (email))
    past_flights = cursor.fetchall()
    cursor.close()

    return render_template("viewMyFlights.html", future_flights=future_flights, past_flights=past_flights, name = email, airports=airports)


@customerHome_bp.route('/searchMyFlights', methods=['GET', 'POST'])
def searchMyFlights():
    email = session['email']
    cursor = conn.cursor()

    # --- Future & Past Flights ---
    cursor.execute("""
        SELECT * FROM Ticket
        LEFT JOIN Flight ON Ticket.name = Flight.name
                        AND Ticket.flight_number = Flight.flight_number
        WHERE email=%s AND dep_date_time > CURRENT_TIMESTAMP
    """, (email,))
    future_flights = cursor.fetchall()

    cursor.execute("""
        SELECT * FROM Ticket
        LEFT JOIN Flight ON Ticket.name = Flight.name
                        AND Ticket.flight_number = Flight.flight_number
        WHERE email=%s AND dep_date_time < CURRENT_TIMESTAMP
    """, (email,))
    past_flights = cursor.fetchall()

    # --- Search filters ---
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    destination_airport = request.form.get('destination')
    source_airport = request.form.get('source')

    cursor=conn.cursor(DictCursor)
    query= 'SELECT * FROM airport'
    cursor.execute(query)
    airports=cursor.fetchall()

    # --- Dynamic query building ---
    query = """
        SELECT Ticket.name, Ticket.flight_number, dep_airport, arr_airport,
               dep_date_time, arr_date_time, status, sold_price,
               Ticket.ID, purchase_date_time
        FROM Ticket
        LEFT JOIN Flight ON Ticket.name = Flight.name
                        AND Ticket.flight_number = Flight.flight_number
        WHERE 1=1
    """
    params = []



    # Append conditions dynamically
    if start_date:
        query += " AND dep_date_time >= %s"
        params.append(start_date)
    if end_date:
        query += " AND dep_date_time <= %s"
        params.append(end_date)
    if source_airport:
        query += " AND dep_airport = %s"
        params.append(source_airport)
    if destination_airport:
        query += " AND arr_airport = %s"
        params.append(destination_airport)

    # --- Execute if user provided filters ---
    search_flights = None
    if any([start_date, end_date, source_airport, destination_airport]):
        cursor.execute(query, tuple(params))
        search_flights = cursor.fetchall()

    cursor.close()

    # --- Render ---
    if not any([start_date, end_date, source_airport, destination_airport]):
        error = "No flights found"
        return render_template("viewMyFlights.html", error=error, airports=airports,
                               future_flights=future_flights, past_flights=past_flights)
    elif search_flights:
        return render_template("viewMyFlights.html", search_flights=search_flights, airports=airports,
                               future_flights=future_flights, past_flights=past_flights)
    else:
        error = "No flights found"
        return render_template("viewMyFlights.html", error=error, airports=airports,
                               future_flights=future_flights, past_flights=past_flights)


@customerHome_bp.route('/searchPurchase', methods=['GET'])
def searchPurchase():
    with conn.cursor() as cursor:
        cursor.execute("""
        SELECT 
            f.flight_number,
            f.name,
            f.dep_airport,
            f.arr_airport,
            f.dep_date_time,
            f.arr_date_time,
            f.base_price,
            f.status,
            a.ID AS airplane_id,
            a.seats AS total_seats,
            (a.seats - COUNT(t.id)) AS available_seats
        FROM flight f
        JOIN airplane a ON f.id = a.ID
        LEFT JOIN ticket t ON t.flight_number = f.flight_number
        GROUP BY 
        f.flight_number, f.name, f.dep_airport, f.arr_airport,
        f.dep_date_time, f.arr_date_time, f.base_price, f.status, a.ID, a.seats;
        """)
        flights = cursor.fetchall()

    email = session.get('email', 'Guest')
    return render_template('searchPurchase.html', name=email, flights=flights)


@customerHome_bp.route('/purchase', methods=['POST'])
def purchase():
    selected = request.form['selected_flight']
    airline_name, flight_number = selected.split('|')

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM flight 
            WHERE name=%s AND flight_number=%s
        """, (airline_name, flight_number))
        flight_info = cursor.fetchone()

    email = session.get('email', 'Guest')
    return render_template('searchPurchase.html', name=email, flights=[], flight_info=flight_info)


@customerHome_bp.route('/purchaseInfo', methods=['POST'])
def purchaseInfo():
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    sold_price = request.form['sold_price']

    email = session.get('email')
    if not email:
        return redirect('/login')

    with conn.cursor() as cursor:
        cursor.execute("SELECT ID FROM ticket ORDER BY ID DESC LIMIT 1")
        last = cursor.fetchone()
        if last and last['ID'].startswith("TK"):
            num = int(last['ID'][2:]) + 1
        else:
            num = 1
        new_id = f"TK{num:03}"

        cursor.execute("""
            INSERT INTO ticket (ID, email, name, flight_number, sold_price, purchase_date_time)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (new_id, email, airline_name, flight_number, sold_price))
        conn.commit()

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM flight where dep_date_time>=CURRENT_DATE")
        flights = cursor.fetchall()

    return render_template('searchPurchase.html', name=email, flights=flights, message="✅ Purchase completed successfully!")



# display previous flights in page to rate previous flights
@customerHome_bp.route('/rate', methods=['GET', 'POST'])
def rate():
    # get session email
    email = session['email']

    # lấy danh sách chuyến bay đã hoàn thành
    cursor = conn.cursor(DictCursor)
    query = '''
        SELECT 
            T.name AS airline_name, 
            T.flight_number, 
            F.dep_airport, 
            F.arr_airport, 
            F.dep_date_time, 
            F.arr_date_time, 
            F.status, 
            F.base_price,
            T.sold_price, 
            T.ID
        FROM Ticket T
        JOIN Flight F ON T.name = F.name AND T.flight_number = F.flight_number
        WHERE T.email = %s 
          AND T.purchase_date_time < CURRENT_TIMESTAMP 
          AND F.arr_date_time < CURRENT_TIMESTAMP
        ORDER BY F.arr_date_time DESC
    '''
    cursor.execute(query, (email,))
    previous_flights = cursor.fetchall()
    cursor.close()

    return render_template("rateTemplate.html", previous_flights=previous_flights)



# rate previous flight
@customerHome_bp.route('/rateFlight', methods=['POST'])
def rateFlight():
    email = session['email']

    # lấy thông tin form
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    rating = int(request.form['rating'])
    comment = request.form['comment']

    # kiểm tra chuyến bay có thực sự thuộc lịch sử của người dùng không
    cursor = conn.cursor(DictCursor)
    check_query = '''
        SELECT 1
        FROM Ticket T
        JOIN Flight F ON T.name = F.name AND T.flight_number = F.flight_number
        WHERE T.email = %s 
          AND F.name = %s 
          AND F.flight_number = %s 
          AND F.arr_date_time < CURRENT_TIMESTAMP
    '''
    cursor.execute(check_query, (email, airline_name, flight_number))
    flight_exists = cursor.fetchone()
    cursor.close()

    if not flight_exists:
        error = "You can only rate flights you have completed."
    elif rating < 1 or rating > 10:
        error = "Rating must be between 1 and 10."
    else:
        # tạo id mới cho rating
        cursor = conn.cursor(DictCursor)
        cursor.execute('SELECT COALESCE(MAX(rating_id), 0) AS max_id FROM Flight_Ratings')
        max_id = cursor.fetchone()['max_id']
        rating_id = max_id + 1
        cursor.close()

        # thêm đánh giá
        cursor = conn.cursor()
        ins = '''
            INSERT INTO Flight_Ratings (rating_id, name, flight_number, rating, comment)
            VALUES (%s, %s, %s, %s, %s)
        '''
        cursor.execute(ins, (rating_id, airline_name, flight_number, rating, comment))
        conn.commit()
        cursor.close()

        message = f" Successfully rated {airline_name} Flight {flight_number}!"
        # tải lại danh sách chuyến bay để hiển thị lại
        cursor = conn.cursor(DictCursor)
        query = '''
            SELECT 
                T.name AS airline_name, 
                T.flight_number, 
                F.dep_airport, 
                F.arr_airport, 
                F.dep_date_time, 
                F.arr_date_time, 
                F.status, 
                T.sold_price, 
                T.ID
            FROM Ticket T
            JOIN Flight F ON T.name = F.name AND T.flight_number = F.flight_number
            WHERE T.email = %s 
              AND T.purchase_date_time < CURRENT_TIMESTAMP 
              AND F.arr_date_time < CURRENT_TIMESTAMP
            ORDER BY F.arr_date_time DESC
        '''
        cursor.execute(query, (email,))
        previous_flights = cursor.fetchall()
        cursor.close()

        return render_template('rateTemplate.html', previous_flights=previous_flights, message=message)

    # nếu có lỗi thì render lại với error
    cursor = conn.cursor(DictCursor)
    query = '''
        SELECT 
            T.name AS airline_name, 
            T.flight_number, 
            F.dep_airport, 
            F.arr_airport, 
            F.dep_date_time, 
            F.arr_date_time, 
            F.status, 
            T.sold_price, 
            T.ID
        FROM Ticket T
        JOIN Flight F ON T.name = F.name AND T.flight_number = F.flight_number
        WHERE T.email = %s 
          AND T.purchase_date_time < CURRENT_TIMESTAMP 
          AND F.arr_date_time < CURRENT_TIMESTAMP
        ORDER BY F.arr_date_time DESC
    '''
    cursor.execute(query, (email,))
    previous_flights = cursor.fetchall()
    cursor.close()

    return render_template('rateTemplate.html', previous_flights=previous_flights, error=error)



# display page with spending info for last year and last six months
@customerHome_bp.route('/trackSpending', methods=['GET', 'POST'])
def trackSpending():
    email = session['email']
    cursor = conn.cursor(DictCursor)

    # 🔹 Tổng chi tiêu trong 1 năm qua
    cursor.execute('''
        SELECT COALESCE(SUM(sold_price), 0) AS total_spent
        FROM Ticket
        WHERE email=%s
          AND purchase_date_time BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()
    ''', (email,))
    year_total = cursor.fetchone()['total_spent']

    # 🔹 Lấy chi tiêu 6 tháng gần nhất
    monthly = []
    # Duyệt từ 6 tháng trước → đến tháng hiện tại
    for i in range(6, -1, -1):
        cursor.execute('''
            SELECT 
                MONTH(DATE_ADD(NOW(), INTERVAL -%s MONTH)) AS month,
                COALESCE(SUM(sold_price), 0) AS spending
            FROM Ticket
            WHERE email = %s
              AND purchase_date_time >= DATE_FORMAT(DATE_ADD(NOW(), INTERVAL -%s MONTH), '%%Y-%%m-01')
              AND purchase_date_time < DATE_FORMAT(DATE_ADD(NOW(), INTERVAL -%s + 1 MONTH), '%%Y-%%m-01')
        ''', (i, email, i, i))

        row = cursor.fetchone()
        month = row['month'] if row and row['month'] is not None else 0
        spending = float(row['spending'] or 0)
        monthly.append({
            'month': month,
            'spending': spending
        })

    cursor.close()

    # 🔹 Dữ liệu cho phần tìm kiếm
    searched = []
    total = 0
    error = None

    # 🔹 Nếu người dùng gửi form POST (tìm theo khoảng ngày)
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                raise ValueError("Start date cannot be after end date.")
        except Exception as e:
            error = str(e) if str(e) else "Invalid date input"
            return render_template('trackSpending.html',
                                   year=year_total,
                                   monthly=monthly,
                                   searched=[],
                                   total=0,
                                   name=email,
                                   error=error)

        cursor = conn.cursor(DictCursor)

        # 🔹 Tổng chi tiêu trong khoảng chọn
        cursor.execute('''
            SELECT COALESCE(SUM(sold_price), 0) AS total
            FROM Ticket
            WHERE email=%s
              AND purchase_date_time BETWEEN %s AND %s
        ''', (email, start_date, end_date))
        total = float(cursor.fetchone()['total'] or 0)

        # 🔹 Chi tiêu từng tháng trong khoảng
        cursor.execute('''
            SELECT MONTH(purchase_date_time) AS month,
                   COALESCE(SUM(sold_price), 0) AS spending
            FROM Ticket
            WHERE email=%s
              AND purchase_date_time BETWEEN %s AND %s
            GROUP BY MONTH(purchase_date_time)
            ORDER BY MONTH(purchase_date_time)
        ''', (email, start_date, end_date))
        by_month = cursor.fetchall()
        cursor.close()

        searched = [{'month': r['month'], 'spending': float(r['spending'] or 0)} for r in by_month]


    # 🔹 Render template
    return render_template('trackSpending.html',
                           year=year_total,
                           monthly=monthly,
                           searched=searched,
                           total=total,
                           name=email,
                           error=error)
