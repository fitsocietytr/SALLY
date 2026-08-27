from flask import Flask
from flask_cors import CORS
from config import Config
from app.database import init_db

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)
    app.config.from_object(Config)

    # Veritabanını ilklendir
    with app.app_context():
        init_db()

    # Rotaları kaydet
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
