from flask import Flask, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from rgz import rgz  

app = Flask(__name__)




@app.errorhandler(404)
def not_found(err):
    return "Нет такой страницы", 404

app.secret_key = '123'
user_db = "anastasia_udodova"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "doska_obyavleni"
password = "0123456789"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



app.register_blueprint(rgz)