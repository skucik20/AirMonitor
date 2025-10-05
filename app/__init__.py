from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # baza danych i migracje
    db.init_app(app)  # powiązanie db z aplikacją
    migrate.init_app(app, db)

    from app.routes.station_routes import station_bp
    app.register_blueprint(station_bp)
    return app
