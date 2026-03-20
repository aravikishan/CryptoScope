"""CryptoScope -- Cryptocurrency Portfolio Tracker.

Flask entry point: initialises the database, registers blueprints,
seeds sample data on first run, and starts the development server.
"""

import json
import os

from flask import Flask

import config
from models.database import init_db
from routes.api import api_bp
from routes.views import views_bp


# v1.0.1 - Updated for clarity
def create_app(testing=False):
    """Application factory for CryptoScope."""
    app = Flask(__name__)

    # Configuration
    db_uri = config.SQLALCHEMY_DATABASE_URI
    if testing:
        db_uri = "sqlite:///:memory:"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = testing
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cryptoscope-dev-key")

    # Initialise database
    init_db(app)

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(views_bp)

    # Seed data on first run
    if not testing:
        _seed_if_empty(app)

    return app


def _seed_if_empty(app):
    """Load seed data if the database is empty."""
    with app.app_context():
        from models.schemas import Wallet
        if Wallet.query.first() is not None:
            return

        seed_path = os.path.join(app.root_path, "seed_data", "data.json")
        if not os.path.exists(seed_path):
            return

        with open(seed_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        from services.portfolio import PortfolioService
        from services.market import MarketService

        portfolio_svc = PortfolioService()
        market_svc = MarketService()
        market_svc.seed_from_json(data, portfolio_svc)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

if __name__ == "__main__":
    application = create_app()
    application.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
    )
