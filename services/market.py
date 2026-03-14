"""Simulated market data, gas fees, and correlation analysis."""

import hashlib
import math
import random
from datetime import datetime, timedelta, timezone

from models.database import db
from models.schemas import GasFee, PriceHistory


# Default token configuration used when config is not importable in tests
_DEFAULT_TOKENS = {
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


def _get_tokens():
    """Load token config, falling back to defaults."""
    try:
        from config import DEFAULT_TOKENS
        return DEFAULT_TOKENS
    except ImportError:
        return _DEFAULT_TOKENS


class MarketService:
    """Provides simulated price data, gas fees, and correlation analysis."""

    def __init__(self):
        self._price_cache = {}
        self._history_cache = {}

    # ------------------------------------------------------------------
    # Price simulation
    # ------------------------------------------------------------------

    def _simulate_price(self, base_price, volatility, seed, days_offset=0):
        """Generate a deterministic but realistic price using random walk."""
        rng = random.Random(seed + days_offset)
        price = base_price
        steps = max(1, abs(days_offset))
        for _ in range(steps):
            drift = 0.0002
            shock = rng.gauss(0, 1) * volatility
            daily_return = drift + shock
            price *= (1 + daily_return)
            price = max(price * 0.01, price)
        return round(price, 8 if base_price < 1.0 else 2)

    def get_current_price(self, symbol):
        """Get current simulated price for a token."""
        tokens = _get_tokens()
        if symbol not in tokens:
            return 0.0
        if symbol in self._price_cache:
            return self._price_cache[symbol]

        token_info = tokens[symbol]
        seed_val = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
        day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
        price = self._simulate_price(
            token_info["base_price"],
            token_info["volatility"],
            seed_val,
            day_of_year,
        )
        self._price_cache[symbol] = price
        return price

    def get_all_current_prices(self):
        """Get current prices and 24h change for all tokens."""
        tokens = _get_tokens()
        result = {}
        for symbol, info in tokens.items():
            current = self.get_current_price(symbol)
            seed_val = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
            day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
            prev = self._simulate_price(
                info["base_price"], info["volatility"],
                seed_val, day_of_year - 1,
            )
            change_24h = ((current - prev) / prev * 100) if prev > 0 else 0.0
            volume = current * random.Random(seed_val + day_of_year).randint(
                500_000, 50_000_000
            )
            market_cap = current * random.Random(seed_val).randint(
                10_000_000, 500_000_000_000
            )
            result[symbol] = {
                "symbol": symbol,
                "name": info["name"],
                "price": current,
                "change_24h": round(change_24h, 2),
                "volume_24h": round(volume, 2),
                "market_cap": round(market_cap, 2),
            }
        return result

    def get_price_history(self, symbol, days=90):
        """Generate simulated price history for a token."""
        cache_key = f"{symbol}_{days}"
        if cache_key in self._history_cache:
            return self._history_cache[cache_key]

        tokens = _get_tokens()
        if symbol not in tokens:
            return []

        info = tokens[symbol]
        seed_val = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
        now = datetime.now(timezone.utc)
        history = []
        price = info["base_price"]
        rng = random.Random(seed_val)

        for i in range(days):
            drift = 0.0002
            shock = rng.gauss(0, 1) * info["volatility"]
            daily_return = drift + shock
            price *= (1 + daily_return)
            price = max(price * 0.01, price)

            ts = now - timedelta(days=days - i)
            volume = price * rng.randint(500_000, 50_000_000)
            history.append({
                "date": ts.strftime("%Y-%m-%d"),
                "price": round(price, 8 if info["base_price"] < 1.0 else 2),
                "volume": round(volume, 2),
            })

        self._history_cache[cache_key] = history
        return history

    # ------------------------------------------------------------------
    # Gas fee simulation
    # ------------------------------------------------------------------

    def get_current_gas_price(self):
        """Simulate current gas price in Gwei."""
        base = 25.0
        hour = datetime.now(timezone.utc).hour
        time_factor = 1.0 + 0.3 * math.sin(math.pi * hour / 12)
        rng = random.Random(int(datetime.now(timezone.utc).timestamp()) // 60)
        noise = rng.gauss(0, 0.15)
        is_spike = rng.random() < 0.08
        spike = 3.5 if is_spike else 1.0
        gas_price = base * time_factor * (1 + noise) * spike
        return round(max(5.0, gas_price), 2)

    def calculate_gas_fee_usd(self, gas_price_gwei, gas_used=21000):
        """Convert gas price from Gwei to USD using current ETH price."""
        eth_price = self.get_current_price("ETH")
        gas_fee_eth = (gas_price_gwei * gas_used) / 1e9
        return round(gas_fee_eth * eth_price, 4)

    def get_gas_history(self, days=30):
        """Generate simulated gas price history."""
        now = datetime.now(timezone.utc)
        history = []
        rng = random.Random(42)
        base = 25.0

        for d in range(days):
            day_prices = []
            for h in range(24):
                time_factor = 1.0 + 0.3 * math.sin(math.pi * h / 12)
                noise = rng.gauss(0, 0.2)
                is_spike = rng.random() < 0.08
                spike = rng.uniform(3.0, 6.0) if is_spike else 1.0
                gp = base * time_factor * (1 + noise) * spike
                day_prices.append(max(5.0, gp))

            ts = now - timedelta(days=days - d)
            avg_gas = sum(day_prices) / len(day_prices)
            min_gas = min(day_prices)
            max_gas = max(day_prices)
            eth_price = self.get_current_price("ETH")
            avg_fee_usd = (avg_gas * 21000) / 1e9 * eth_price

            history.append({
                "date": ts.strftime("%Y-%m-%d"),
                "avg_gas_gwei": round(avg_gas, 2),
                "min_gas_gwei": round(min_gas, 2),
                "max_gas_gwei": round(max_gas, 2),
                "avg_fee_usd": round(avg_fee_usd, 4),
            })
        return history

    def record_gas_fee(self, gas_price_gwei, fee_usd, network="ethereum"):
        """Record a gas fee to the database."""
        rng = random.Random(int(datetime.now(timezone.utc).timestamp()))
        record = GasFee(
            network=network,
            gas_price_gwei=gas_price_gwei,
            gas_used=21000,
            fee_usd=fee_usd,
            block_number=rng.randint(18_000_000, 20_000_000),
        )
        db.session.add(record)
        return record

    def get_gas_stats(self):
        """Get aggregate gas fee statistics."""
        from sqlalchemy import func
        total_fees = db.session.query(func.sum(GasFee.fee_usd)).scalar() or 0.0
        avg_gas = db.session.query(
            func.avg(GasFee.gas_price_gwei)
        ).scalar() or 0.0
        max_gas = db.session.query(
            func.max(GasFee.gas_price_gwei)
        ).scalar() or 0.0
        min_gas = db.session.query(
            func.min(GasFee.gas_price_gwei)
        ).scalar() or 0.0
        count = db.session.query(func.count(GasFee.id)).scalar() or 0

        return {
            "total_fees_usd": round(total_fees, 4),
            "avg_gas_gwei": round(avg_gas, 2),
            "max_gas_gwei": round(max_gas, 2),
            "min_gas_gwei": round(min_gas, 2),
            "total_transactions": count,
            "current_gas_gwei": self.get_current_gas_price(),
            "current_fee_usd": self.calculate_gas_fee_usd(
                self.get_current_gas_price()
            ),
        }

    # ------------------------------------------------------------------
    # Correlation analysis
    # ------------------------------------------------------------------

    def compute_correlation_matrix(self, symbols=None, days=30):
        """Compute price correlation matrix between tokens."""
        tokens = _get_tokens()
        if symbols is None:
            symbols = list(tokens.keys())[:8]

        returns = {}
        for sym in symbols:
            hist = self.get_price_history(sym, days)
            prices = [h["price"] for h in hist]
            daily_returns = []
            for i in range(1, len(prices)):
                if prices[i - 1] > 0:
                    ret = (prices[i] - prices[i - 1]) / prices[i - 1]
                    daily_returns.append(ret)
                else:
                    daily_returns.append(0.0)
            returns[sym] = daily_returns

        matrix = {}
        for sym_a in symbols:
            matrix[sym_a] = {}
            for sym_b in symbols:
                if sym_a == sym_b:
                    matrix[sym_a][sym_b] = 1.0
                else:
                    corr = self._pearson_correlation(
                        returns.get(sym_a, []),
                        returns.get(sym_b, []),
                    )
                    matrix[sym_a][sym_b] = round(corr, 4)
        return {"symbols": symbols, "matrix": matrix}

    @staticmethod
    def _pearson_correlation(x, y):
        """Calculate Pearson correlation coefficient."""
        n = min(len(x), len(y))
        if n < 2:
            return 0.0
        x = x[:n]
        y = y[:n]
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        if std_x == 0 or std_y == 0:
            return 0.0
        return cov / (std_x * std_y)

    # ------------------------------------------------------------------
    # Seed data loading
    # ------------------------------------------------------------------

    def seed_from_json(self, data, portfolio_service):
        """Load seed data from parsed JSON."""
        for w_data in data.get("wallets", []):
            wallet = portfolio_service.create_wallet(
                name=w_data["name"],
                network=w_data.get("network", "ethereum"),
            )
            for t_data in w_data.get("tokens", []):
                portfolio_service.add_token_to_wallet(
                    wallet.id, t_data["symbol"], t_data.get("name"),
                )
            for tx_data in w_data.get("transactions", []):
                portfolio_service.execute_transaction(
                    wallet_id=wallet.id,
                    symbol=tx_data["symbol"],
                    tx_type=tx_data["tx_type"],
                    quantity=tx_data["quantity"],
                    price_per_unit=tx_data.get("price_per_unit"),
                    notes=tx_data.get("notes"),
                )
