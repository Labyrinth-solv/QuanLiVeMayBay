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

    cursor=conn.cursor(DictCursor)
    query= 'SELECT * FROM airport'
    cursor.execute(query)
    airports=cursor.fetchall()
    cursor.close()
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
        WHERE f.dep_date_time >= CURRENT_DATE
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
        cursor.execute("SELECT * FROM flight")
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

        message = f"✅ Successfully rated {airline_name} Flight {flight_number}!"
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
    # get session email
    email = session['email']

    # get spending for the last year
    cursor = conn.cursor()
    query = 'SELECT sum(sold_price) as total_spent FROM Ticket WHERE email=%s and purchase_date_time >= DATE_ADD(NOW(), INTERVAL -1 YEAR) and purchase_date_time<= CURRENT_TIMESTAMP'
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
    df = pd.concat([df, pd.DataFrame([m0,m1,m2,m3,m4,m5,m6])], ignore_index=True)
    df["date"] = df['m'].astype(int).astype(str) + "/" + df["y"].astype(int).astype(str)
    df.fillna(0, inplace=True)
    df['relative_month'] = df.index.astype(str)
    df.set_index('relative_month', inplace=True)
    df['0'] = df['date']
    df['1'] = df['spending']

    monthly_df = df[['0', '1']]
    monthly = monthly_df.to_dict('records')

    return render_template("trackSpending.html", year=year, monthly=monthly, name = email)


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

