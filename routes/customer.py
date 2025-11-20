from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection,Blueprint
import pymysql.cursors

customer_bp=Blueprint("customer", __name__)
conn = get_connection()

@customer_bp.route('/customerLogin')
def customerLogin():
    return render_template('customerLogin.html')


@customer_bp.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
    email = request.form['email']
    password = request.form['password']

    cursor = conn.cursor()
    query = 'SELECT * FROM Customer WHERE email = %s and password =%s'
    cursor.execute(query, (email, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if (data):
        session['email'] = email
        return redirect(url_for('customerHome.customerHome'))
    else:
        error = 'Invalid login'
        return render_template('customerLogin.html', error=error)

@customer_bp.route('/customerRegister')
def customerRegister():
    return render_template('customerRegister.html')

@customer_bp.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    date_of_birth = request.form['date_of_birth']

    cursor = conn.cursor()
    query = 'SELECT * FROM Customer WHERE email = %s'
    cursor.execute(query, (email,))
    data = cursor.fetchone()
    cursor.close()
    error = None

    if (data):
        error = "This user already exists"
        return render_template('customerRegister.html', error=error)
    else:
        cursor = conn.cursor()
        ins = 'INSERT INTO Customer (email, name, password, date_of_birth) VALUES (%s, %s, %s, %s)'
        cursor.execute(ins,
                       (email, name, password, date_of_birth))
        conn.commit()
        cursor.close()

        message = "Customer " + email + " successfully created!"
        return render_template('customerRegister.html', message=message)



@customer_bp.route('/customerLogout')
def customerLogout():
    email = session['email']
    session.pop('email')
    message= email+" has been successfully logged out"
    return render_template('index.html', message = message)
