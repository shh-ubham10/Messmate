from flask import Flask
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from .routes.encode_routes import encode_bp
# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.debug = True 
    CORS(app)
    bcrypt = Bcrypt(app)
    app.register_blueprint(encode_bp, url_prefix='/encode')


    app.config['bcrypt'] = bcrypt




    return app
