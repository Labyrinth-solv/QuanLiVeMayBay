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
        return redirect(url_for('staffHome'))
    else:
        error = 'Invalid login'
        return render_template('staffLogin.html', error=error)


# display staffRegister page
@staff_bp.route('/staffRegister')
def staffRegister():
    return render_template('staffRegister.html')


# authenticates staffRegister
@staff_bp.route('/staffRegisterAuth', methods=['POST'])
def staffRegisterAuth():
    username = request.form['username']
    password = request.form['password']
    name = request.form['airline_name']

    cursor = conn.cursor()
    # kiểm tra username đã tồn tại chưa
    cursor.execute('SELECT * FROM airline_staff WHERE username = %s', (username,))
    data = cursor.fetchone()
    cursor.close()

    if data:
        error = "This user already exists"
        return render_template('staffRegister.html', error=error)
    else:
        # kiểm tra airline có tồn tại không
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM airline WHERE name = %s', (name,))
        airline_data = cursor.fetchone()
        cursor.close()

        if airline_data:
            # thêm nhân viên mới
            cursor = conn.cursor()
            insert_query = 'INSERT INTO airline_staff (username, password, name) VALUES (%s, %s, %s)'
            cursor.execute(insert_query, (username, password, name))
            conn.commit()
            cursor.close()

            message = f"Airline Staff '{username}' successfully created!"
            return render_template('index.html', message=message)
        else:
            error = "This airline does not exist"
            return render_template('staffRegister.html', error=error)
