<div align="center">

# CryptoScope

[![CI](https://github.com/ravikishan/cryptoscope/actions/workflows/ci.yml/badge.svg)](https://github.com/ravikishan/cryptoscope/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A cryptocurrency portfolio tracker with P&L calculations, gas fee analysis,
and market correlation charts.**

[Features](#features) |
[Quick Start](#quick-start) |
[API Reference](#api-reference) |
[Screenshots](#screenshots) |
[Architecture](#architecture) |
[Contributing](#contributing)

</div>

---

## Features

- **Portfolio Dashboard** -- Real-time portfolio value, 24h change, and allocation donut chart
- **Multi-Wallet Support** -- Track holdings across multiple wallets and networks
- **P&L Calculations** -- Cost basis tracking, unrealized/realized gains per token
- **Transaction Tracking** -- Log buy/sell/transfer transactions with automatic cost basis updates
- **Gas Fee Analysis** -- Historical gas price monitoring with gauge visualization
- **Market Overview** -- Live prices, 24h changes, and volume for 12+ tokens
- **Price Charts** -- 90-day price history with gradient line charts
- **Correlation Matrix** -- Visual heatmap showing price correlations between tokens
- **REST API** -- Full-featured JSON API for all operations
- **Dark Crypto Theme** -- Purple/blue gradients with neon accents

## Supported Tokens

| Token | Name        | Token | Name      |
|-------|-------------|-------|-----------|
| BTC   | Bitcoin     | UNI   | Uniswap   |
| ETH   | Ethereum    | ATOM  | Cosmos    |
| SOL   | Solana      | XRP   | Ripple    |
| ADA   | Cardano     | DOGE  | Dogecoin  |
| DOT   | Polkadot    | AVAX  | Avalanche |
| LINK  | Chainlink   | MATIC | Polygon   |

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/ravikishan/cryptoscope.git
cd cryptoscope

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will be available at `http://localhost:8010`

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t cryptoscope .
docker run -p 8010:8010 cryptoscope
```

### Using the start script

```bash
chmod +x start.sh
./start.sh
```

## API Reference

### Wallets

| Method   | Endpoint                         | Description            |
|----------|----------------------------------|------------------------|
| `GET`    | `/api/wallets`                   | List all wallets       |
| `POST`   | `/api/wallets`                   | Create a new wallet    |
| `GET`    | `/api/wallets/:id`               | Get wallet details     |
| `DELETE` | `/api/wallets/:id`               | Delete a wallet        |
| `POST`   | `/api/wallets/:id/tokens`        | Add token to wallet    |
| `GET`    | `/api/wallets/:id/tokens`        | List wallet tokens     |

### Transactions

| Method | Endpoint                              | Description            |
|--------|---------------------------------------|------------------------|
| `POST` | `/api/transactions`                   | Execute a transaction  |
| `GET`  | `/api/wallets/:id/transactions`       | List wallet transactions |

### Portfolio

| Method | Endpoint                        | Description            |
|--------|---------------------------------|------------------------|
| `GET`  | `/api/portfolio/summary`        | Portfolio summary      |
| `GET`  | `/api/portfolio/top-performers` | Top performing tokens  |

### Market

| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| `GET`  | `/api/market/prices`              | All token prices         |
| `GET`  | `/api/market/prices/:symbol`      | Single token price       |
| `GET`  | `/api/market/history/:symbol`     | Price history            |
| `GET`  | `/api/market/correlation`         | Correlation matrix       |

### Gas Fees

| Method | Endpoint             | Description            |
|--------|----------------------|------------------------|
| `GET`  | `/api/gas/current`   | Current gas price      |
| `GET`  | `/api/gas/history`   | Gas price history      |
| `GET`  | `/api/gas/stats`     | Gas fee statistics     |

### Example Requests

```bash
# Create a wallet
curl -X POST http://localhost:8010/api/wallets \
  -H "Content-Type: application/json" \
  -d '{"name": "My Wallet", "network": "ethereum"}'

# Execute a buy transaction
curl -X POST http://localhost:8010/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"wallet_id": 1, "symbol": "BTC", "tx_type": "buy", "quantity": 0.5}'

# Get portfolio summary
curl http://localhost:8010/api/portfolio/summary

# Get correlation matrix
curl http://localhost:8010/api/market/correlation?symbols=BTC,ETH,SOL&days=30
```

## Architecture

```
cryptoscope/
+-- app.py                          # Flask entry point
+-- config.py                       # Configuration
+-- requirements.txt                # Dependencies
+-- models/
|   +-- database.py                 # SQLite/SQLAlchemy setup
|   +-- schemas.py                  # ORM models (Wallet, Token, Transaction, etc.)
+-- routes/
|   +-- api.py                      # REST API endpoints
|   +-- views.py                    # HTML template routes
+-- services/
|   +-- portfolio.py                # Portfolio tracking & P&L
|   +-- market.py                   # Price simulation & correlation
+-- templates/                      # Jinja2 HTML templates
+-- static/
|   +-- css/style.css               # Dark crypto theme
|   +-- js/main.js                  # Chart.js visualizations
+-- tests/                          # pytest test suite
+-- seed_data/data.json             # Sample data
```

### Key Design Decisions

- **Simulated Data**: Prices are deterministically generated using seeded
  random walks, providing realistic but reproducible data without external
  API dependencies.
- **Cost Basis Tracking**: Uses average cost method for calculating
  unrealized gains and per-trade realized P&L.
- **Pearson Correlation**: Custom implementation of Pearson's r for the
  correlation matrix -- no NumPy dependency required.
- **Gas Fee Model**: Simulates Ethereum-like gas pricing with time-of-day
  variation and random congestion spikes.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py -v
```

## Screenshots

### Portfolio Dashboard
The main dashboard shows total portfolio value, P&L metrics, allocation
donut chart, top performers table, and a live price ticker strip.

### Market Overview
Browse all supported tokens with price, 24h change, volume, market cap,
sparkline mini-charts, full price chart, and correlation heatmap.

### Gas Fee Tracker
Monitor current gas prices with an animated gauge, 30-day gas history
chart showing min/avg/max, and a daily summary table.

## Environment Variables

| Variable            | Default | Description             |
|---------------------|---------|-------------------------|
| `CRYPTOSCOPE_PORT`  | `8010`  | Server port             |
| `CRYPTOSCOPE_DEBUG` | `false` | Enable debug mode       |
| `DATABASE_URL`      | SQLite  | Database connection URI |
| `SECRET_KEY`        | dev-key | Flask secret key        |

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License -- see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with Flask, Chart.js, and SQLAlchemy</sub>
</div>
