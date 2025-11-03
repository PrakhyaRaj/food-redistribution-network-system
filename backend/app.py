from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    

    # Import and register routes
    from routes.user_routes import user_bp
    from routes.food_routes import food_bp
    from routes.transaction_routes import transaction_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(food_bp)
    app.register_blueprint(transaction_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
