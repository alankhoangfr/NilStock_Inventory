import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail



app = Flask(__name__)
#For Production use prod and for development use dev
ENV = 'prod'

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:'+os.environ.get('POSTGRES_PASS')+'@localhost/stockmanagement'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://auirxajouoquac:2a79c4a80be03451a831bd090ceaba2225cc8b52611a6796311afef45ef9cfa5@ec2-54-198-252-9.compute-1.amazonaws.com:5432/d13729fkjapj1r'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


#Make sure the google gmail account has 2 factor verification
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'mixographics@gmail.com'	
app.config['MAIL_PASSWORD'] = 'qwnledurwgzfqufi'
mail = Mail(app)


from routes.listingRoutes import *
from routes.storageRoutes import *
from routes.supplierRoutes import *
from routes.stocktakeRoutes import *
from routes.transferRoutes import *
from routes.updateBookingRoutes import *
from routes.shoppingRoutes import *
from routes.userRoutes import *
from routes.accountRoutes import *
from routes.homeRoutes import *
from routes.categoryRoutes import *
from routes.accessRoutes import *
from routes.locationRoutes import *
from routes.productRoutes import *
from routes.notificationRoutes import *
from routes.commonRoutes import *

if ENV== 'dev':

	if __name__ == '__main__':
		app.run(debug=True)
else:
	if __name__ == '__main__':
		app.run()