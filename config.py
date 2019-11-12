from flask_sqlalchemy import SQLAlchemy		
from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key="itsasecrettoeverybody"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devs_and_orgs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
password_reg = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,}$")
bcrypt = Bcrypt(app)