from flask import Flask, render_template, request, session, url_for, redirect, app, Blueprint
import pymysql.cursors
from datetime import datetime
import pandas as pd
from db_config import get_connection