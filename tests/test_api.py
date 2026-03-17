"""API endpoint tests for CryptoScope."""

import json
import pytest


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["service"] == "CryptoScope"


class TestWalletEndpoints:
    def test_create_wallet(self, client):
        resp = client.post(
            "/api/wallets",
            data=json.dumps({"name": "Test Wallet", "network": "ethereum"}),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Test Wallet"
        assert data["network"] == "ethereum"
        assert data["address"].startswith("0x")

    def test_list_wallets(self, client):
        client.post(
            "/api/wallets",
            data=json.dumps({"name": "Wallet A"}),
            content_type="application/json",
        )
        resp = client.get("/api/wallets")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_wallet_not_found(self, client):
        resp = client.get("/api/wallets/9999")
        assert resp.status_code == 404


class TestMarketEndpoints:
    def test_market_prices(self, client):
        resp = client.get("/api/market/prices")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "BTC" in data
        assert "price" in data["BTC"]

    def test_token_price_history(self, client):
        resp = client.get("/api/market/history/BTC?days=10")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["symbol"] == "BTC"
        assert len(data["history"]) == 10

    def test_correlation_matrix(self, client):
        resp = client.get("/api/market/correlation?days=10")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "symbols" in data
        assert "matrix" in data


class TestGasEndpoints:
    def test_current_gas(self, client):
        resp = client.get("/api/gas/current")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "gas_price_gwei" in data
        assert data["gas_price_gwei"] > 0

    def test_gas_history(self, client):
        resp = client.get("/api/gas/history?days=7")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["history"]) == 7
