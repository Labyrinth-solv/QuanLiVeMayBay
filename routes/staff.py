from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, Blueprint
import pymysql.cursors

staff_bp = Blueprint("staff", __name__)
conn = get_connection()

# display staffLogin page
@staff_bp.route('/staffLogin')
def staffLogin():
    return render_template('staffLogin.html')


# authenticates staffLogin
@staff_bp.route('/staffLoginAuth', methods=['GET', 'POST'])
def staffLoginAuth():
    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM airline_staff WHERE username = %s AND md5(password) = md5(%s)'
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()

    if data:
        session['username'] = username
        return redirect(url_for('staffHome.staffHome'))
    else:
        error = 'Invalid login'
        return render_template('staffLogin.html', error=error)



