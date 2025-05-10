from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receipts.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    from .routes import receipt_routes
    app.register_blueprint(receipt_routes)

    migrate = Migrate(app, db)

    return app