from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection,Blueprint, datetime
import pymysql.cursors

check_bp=Blueprint("check", __name__)
conn=get_connection()


# display checkStatus page
@check_bp.route('/checkStatus')
def checkStatus():
    return render_template('checkStatus.html')


# check flight status
@check_bp.route('/status', methods=['GET', 'POST'])
def status():
    # grabs information from the forms
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
    if (statuses):
        return render_template("checkStatus.html", statuses=statuses)
    else:
        error = "No flights found"
        return render_template("checkStatus.html", error=error)
