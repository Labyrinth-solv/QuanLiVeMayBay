from pymysql.cursors import DictCursor
from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection, Blueprint, datetime

search_bp = Blueprint("search", __name__)
conn = get_connection()


@search_bp.route('/searchFlight', methods=['GET', 'POST'])
def searchFlight():
    cursor = conn.cursor(DictCursor)

    # Lấy danh sách sân bay cho select
    cursor.execute("SELECT name FROM airport")
    airports = cursor.fetchall()

    # Nếu là GET: chỉ hiển thị chuyến bay từ hôm nay trở đi
    if request.method == 'GET':
        query = """
            SELECT 
                f.flight_number,
                f.name AS airline_name,
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
            WHERE f.dep_date_time >= CURDATE()
            GROUP BY 
                f.flight_number, f.name, f.dep_airport, f.arr_airport, 
                f.dep_date_time, f.arr_date_time, f.base_price, f.status, a.ID, a.seats
            ORDER BY f.dep_date_time ASC;
        """
        cursor.execute(query)
        flights = cursor.fetchall()

        return render_template(
            "search.html",
            flights=flights,
            airports=airports,
            dep_airport='',
            arr_airport='',
            dep_date=''
        )

    # Nếu là POST: lọc theo điều kiện người dùng nhập
    dep_airport = request.form.get('dep_airport')
    arr_airport = request.form.get('arr_airport')
    dep_date = request.form.get('dep_date')

    query = """
        SELECT 
            f.flight_number,
            f.name AS airline_name,
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
        WHERE 1=1
    """
    params = []

    # Lọc theo ngày nếu có chọn, nếu không thì vẫn lấy từ hôm nay
    if dep_date:
        query += " AND DATE(f.dep_date_time) >= %s"
        params.append(dep_date)
    else:
        query += " AND f.dep_date_time >= CURDATE()"

    if dep_airport:
        query += " AND f.dep_airport = %s"
        params.append(dep_airport)

    if arr_airport:
        query += " AND f.arr_airport = %s"
        params.append(arr_airport)

    query += """
        GROUP BY 
            f.flight_number, f.name, f.dep_airport, f.arr_airport, 
            f.dep_date_time, f.arr_date_time, f.base_price, f.status, a.ID, a.seats
        ORDER BY f.dep_date_time ASC;
    """

    cursor.execute(query, params)
    flights = cursor.fetchall()
    cursor.close()

    if not flights:
        error = "Không có chuyến bay phù hợp."
        return render_template(
            "viewFlights.html",
            flights=[],
            airports=airports,
            error=error,
            dep_airport=dep_airport,
            arr_airport=arr_airport,
            dep_date=dep_date
        )

    return render_template(
        "viewFlights.html",
        flights=flights,
        airports=airports,
        dep_airport=dep_airport,
        arr_airport=arr_airport,
        dep_date=dep_date
    )
