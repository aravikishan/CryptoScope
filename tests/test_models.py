"""Model tests for CryptoScope."""

import pytest

from models.schemas import Wallet, Token, Transaction, GasFee, PriceHistory
from models.database import db


class TestWalletModel:
    def test_wallet_creation(self, client, db_session):
        wallet = Wallet(name="Test", address="0xabc123", network="ethereum")
        db.session.add(wallet)
        db.session.flush()
        assert wallet.id is not None
        assert wallet.name == "Test"
        assert wallet.is_active is True

    def test_wallet_to_dict(self, client, db_session):
        wallet = Wallet(name="Dict Test", address="0xdef456", network="polygon")
        db.session.add(wallet)
        db.session.flush()
        d = wallet.to_dict()
        assert d["name"] == "Dict Test"
        assert d["network"] == "polygon"


class TestTokenModel:
    def test_token_defaults(self, client, db_session):
        wallet = Wallet(name="TW", address="0xtok111", network="ethereum")
        db.session.add(wallet)
        db.session.flush()
        token = Token(wallet_id=wallet.id, symbol="BTC", name="Bitcoin")
        db.session.add(token)
        db.session.flush()
        assert token.balance == 0.0
        assert token.cost_basis == 0.0
        assert token.realized_pnl == 0.0


class TestTransactionModel:
    def test_transaction_to_dict(self, client, db_session):
        wallet = Wallet(name="TxW", address="0xtx222", network="ethereum")
        db.session.add(wallet)
        db.session.flush()
        tx = Transaction(
            wallet_id=wallet.id, symbol="ETH", tx_type="buy",
            quantity=1.5, price_per_unit=3400.0, total_value=5100.0,
            gas_fee=2.50, gas_price_gwei=30.0, tx_hash="0xhash123",
        )
        db.session.add(tx)
        db.session.flush()
        d = tx.to_dict()
        assert d["symbol"] == "ETH"
        assert d["tx_type"] == "buy"
        assert d["quantity"] == 1.5
