from flask import Flask
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from .routes.user_routes import user_bp
from .routes.auth_routes import auth_bp
from .routes.inventory_routes import inventory_bp
from .routes.menu_routes import menu_bp
from .routes.plan_routes import plan_bp
from .routes.user_plan_routes import user_plan_bp
from .routes.statistical_routes import stats_bp
# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.debug = True 
    bcrypt = Bcrypt(app)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(menu_bp, url_prefix='/menu')
    app.register_blueprint(plan_bp, url_prefix='/plan')
    app.register_blueprint(user_plan_bp, url_prefix='/userplan')
    app.register_blueprint(stats_bp, url_prefix='/stats')


    app.config['bcrypt'] = bcrypt




    return app
