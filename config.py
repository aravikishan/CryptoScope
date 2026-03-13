"""Application configuration for CryptoScope."""

import os

# Server
HOST = "0.0.0.0"
PORT = int(os.environ.get("CRYPTOSCOPE_PORT", 8010))
DEBUG = os.environ.get("CRYPTOSCOPE_DEBUG", "false").lower() == "true"

# Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "cryptoscope.db")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{DATABASE_PATH}"
)

# Supported tokens with realistic base prices (USD)
DEFAULT_TOKENS = {
    "BTC":   {"name": "Bitcoin",       "base_price": 67500.00, "volatility": 0.035},
    "ETH":   {"name": "Ethereum",      "base_price": 3450.00,  "volatility": 0.042},
    "SOL":   {"name": "Solana",        "base_price": 172.00,   "volatility": 0.060},
    "ADA":   {"name": "Cardano",       "base_price": 0.62,     "volatility": 0.055},
    "DOT":   {"name": "Polkadot",      "base_price": 8.40,     "volatility": 0.050},
    "LINK":  {"name": "Chainlink",     "base_price": 18.50,    "volatility": 0.048},
    "AVAX":  {"name": "Avalanche",     "base_price": 42.00,    "volatility": 0.058},
    "MATIC": {"name": "Polygon",       "base_price": 0.88,     "volatility": 0.052},
    "UNI":   {"name": "Uniswap",       "base_price": 12.30,    "volatility": 0.055},
    "ATOM":  {"name": "Cosmos",        "base_price": 11.20,    "volatility": 0.050},
    "XRP":   {"name": "Ripple",        "base_price": 0.58,     "volatility": 0.045},
    "DOGE":  {"name": "Dogecoin",      "base_price": 0.16,     "volatility": 0.070},
}

# Simulation parameters
SIMULATION_DAYS = 365
PRICE_HISTORY_POINTS = 90

# Gas fee simulation (in Gwei for Ethereum-like networks)
GAS_BASE_PRICE = 25.0
GAS_VOLATILITY = 0.40
GAS_SPIKE_PROBABILITY = 0.08
GAS_SPIKE_MULTIPLIER = 4.0

# Correlation matrix parameters
CORRELATION_WINDOW = 30

# Testing
TESTING = False
