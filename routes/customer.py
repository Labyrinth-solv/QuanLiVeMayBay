from db_config import get_connection
from routes import Flask, render_template, request, session, url_for, redirect, app, get_connection,Blueprint
import pymysql.cursors

customer_bp=Blueprint("customer", __name__)
conn = get_connection()

# display customerLogin page
@customer_bp.route('/customerLogin')
def customerLogin():
    return render_template('customerLogin.html')


# authenticate customerLogin
@customer_bp.route('/customerLoginAuth', methods=['GET', 'POST'])
def customerLoginAuth():
    # grabs information from the forms
    email = request.form['email']
    password = request.form['password']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM Customer WHERE email = %s and password =%s'
    cursor.execute(query, (email, password))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    # check if the customer data was found
    if (data):
        # creates a session for the the user
        # session is a built in
        session['email'] = email
        return redirect(url_for('customerHome.customerHome'))
    else:
        # returns an error message to the html page
        error = 'Invalid login'
        return render_template('customerLogin.html', error=error)

# display customerRegister page
@customer_bp.route('/customerRegister')
def customerRegister():
    return render_template('customerRegister.html')

# authenticates customerRegister
@customer_bp.route('/customerRegisterAuth', methods=['GET', 'POST'])
def customerRegisterAuth():
    # grabs information from the forms
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']
    date_of_birth = request.form['date_of_birth']

    # cursor used to send queries
    cursor = conn.cursor()
    # executes query
    query = 'SELECT * FROM Customer WHERE email = %s'
    cursor.execute(query, (email,))
    # stores the results in a variable
    data = cursor.fetchone()
    # use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None

    # check if the customer already exists
    if (data):
        # If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('customerRegister.html', error=error)
    else:
        # add customer to system
        cursor = conn.cursor()
        ins = 'INSERT INTO Customer (email, name, password, date_of_birth) VALUES (%s, %s, %s, %s)'
        cursor.execute(ins,
                       (email, name, password, date_of_birth))
        conn.commit()
        cursor.close()

        # send success message to index
        message = "Customer " + email + " successfully created!"
        return render_template('customerRegister.html', message=message)



# allow customers to log out
@customer_bp.route('/customerLogout')
def customerLogout():
	email = session['email']
	session.pop('email')
	message= email+" has been successfully logged out"
	return render_template('index.html', message = message)
