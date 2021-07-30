from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from supply.config import Config



login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'primary'
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail() 


#Creation of app into a function
def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

    from supply.users.routes import users
    from supply.main.routes import main
    from supply.errors.handlers import errors
    #Register Blueprint
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app