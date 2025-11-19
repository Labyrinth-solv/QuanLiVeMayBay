#Import packages
from flask import Flask, render_template, request, session, url_for, redirect, Blueprint
import pymysql.cursors
from datetime import datetime
import pandas as pd
from db_config import get_connection
import routes.customer
from routes import customer, staff, search, customerHome, staffHome

#Initialize the app from Flask
app = Flask(__name__, template_folder="templates")
conn=get_connection()

app.register_blueprint(customer.customer_bp)
app.register_blueprint(staff.staff_bp)
app.register_blueprint(search.search_bp)
app.register_blueprint(customerHome.customerHome_bp)
app.register_blueprint(staffHome.staffHome_bp)


# display index page
@app.route('/')
def hello():
	return render_template('index.html')


app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION


if __name__ == "__main__":
	app.run(debug=True)
