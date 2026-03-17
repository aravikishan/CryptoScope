"""Service layer tests for CryptoScope."""

import pytest

from services.portfolio import PortfolioService
from services.market import MarketService


class TestMarketService:
    def test_get_current_price(self, client):
        svc = MarketService()
        price = svc.get_current_price("BTC")
        assert price > 0
        assert isinstance(price, (int, float))

    def test_unknown_token_returns_zero(self, client):
        svc = MarketService()
        price = svc.get_current_price("NONEXISTENT")
        assert price == 0.0

    def test_price_history(self, client):
        svc = MarketService()
        history = svc.get_price_history("ETH", days=10)
        assert len(history) == 10
        assert all("price" in h and "date" in h for h in history)

    def test_gas_price_positive(self, client):
        svc = MarketService()
        gas = svc.get_current_gas_price()
        assert gas >= 5.0

    def test_correlation_matrix(self, client):
        svc = MarketService()
        result = svc.compute_correlation_matrix(["BTC", "ETH"], days=10)
        assert result["matrix"]["BTC"]["BTC"] == 1.0
        assert result["matrix"]["ETH"]["ETH"] == 1.0

    def test_pearson_self_correlation(self, client):
        vals = [1.0, 2.0, 3.0, 4.0, 5.0]
        corr = MarketService._pearson_correlation(vals, vals)
        assert abs(corr - 1.0) < 0.001


class TestPortfolioService:
    def test_create_wallet(self, client, db_session):
        svc = PortfolioService()
        wallet = svc.create_wallet("Test Wallet")
        assert wallet.name == "Test Wallet"
        assert wallet.address.startswith("0x")

    def test_buy_transaction_updates_balance(self, client, db_session):
        svc = PortfolioService()
        wallet = svc.create_wallet("Buy Test")
        svc.execute_transaction(
            wallet.id, "BTC", "buy", 0.5, price_per_unit=60000.0,
        )
        tokens = svc.get_wallet_tokens(wallet.id)
        btc = [t for t in tokens if t["symbol"] == "BTC"]
        assert len(btc) == 1
        assert btc[0]["balance"] == 0.5
        assert btc[0]["avg_buy_price"] == 60000.0
