from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
app.config['SECRET_KEY'] = '233'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'+'?check_same_thread=False'  # relative path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'email'
app.config['MAIL_PASSWORD'] = 'password'
mail = Mail(app)


from flaskwebapp.users.routes import users
from flaskwebapp.post.routes import posts
from flaskwebapp.main.routes import main

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
