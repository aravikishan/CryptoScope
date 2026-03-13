"""SQLAlchemy models for CryptoScope cryptocurrency data."""

from datetime import datetime, timezone

from models.database import db


class Wallet(db.Model):
    """Represents a user crypto wallet."""

    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(64), unique=True, nullable=False, index=True)
    network = db.Column(db.String(30), nullable=False, default="ethereum")
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relationships
    tokens = db.relationship("Token", backref="wallet", lazy=True,
                             cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", backref="wallet", lazy=True,
                                   cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "network": self.network,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
            "token_count": len(self.tokens) if self.tokens else 0,
        }


class Token(db.Model):
    """Represents a token holding within a wallet."""

    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False,
                          index=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    cost_basis = db.Column(db.Float, nullable=False, default=0.0)
    avg_buy_price = db.Column(db.Float, nullable=False, default=0.0)
    total_invested = db.Column(db.Float, nullable=False, default=0.0)
    total_sold = db.Column(db.Float, nullable=False, default=0.0)
    realized_pnl = db.Column(db.Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "wallet_id": self.wallet_id,
            "symbol": self.symbol,
            "name": self.name,
            "balance": self.balance,
            "cost_basis": self.cost_basis,
            "avg_buy_price": self.avg_buy_price,
            "total_invested": self.total_invested,
            "total_sold": self.total_sold,
            "realized_pnl": self.realized_pnl,
        }


class Transaction(db.Model):
    """Represents a buy/sell/transfer transaction."""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=False,
                          index=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    tx_type = db.Column(db.String(10), nullable=False)  # buy, sell, transfer
    quantity = db.Column(db.Float, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    total_value = db.Column(db.Float, nullable=False)
    gas_fee = db.Column(db.Float, nullable=False, default=0.0)
    gas_price_gwei = db.Column(db.Float, nullable=False, default=0.0)
    tx_hash = db.Column(db.String(66), unique=True, nullable=False)
    timestamp = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "wallet_id": self.wallet_id,
            "symbol": self.symbol,
            "tx_type": self.tx_type,
            "quantity": self.quantity,
            "price_per_unit": self.price_per_unit,
            "total_value": self.total_value,
            "gas_fee": self.gas_fee,
            "gas_price_gwei": self.gas_price_gwei,
            "tx_hash": self.tx_hash,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "notes": self.notes,
        }


class GasFee(db.Model):
    """Historical gas fee record for network analysis."""

    __tablename__ = "gas_fees"

    id = db.Column(db.Integer, primary_key=True)
    network = db.Column(db.String(30), nullable=False, index=True)
    gas_price_gwei = db.Column(db.Float, nullable=False)
    gas_used = db.Column(db.Integer, nullable=False, default=21000)
    fee_usd = db.Column(db.Float, nullable=False)
    block_number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "network": self.network,
            "gas_price_gwei": self.gas_price_gwei,
            "gas_used": self.gas_used,
            "fee_usd": self.fee_usd,
            "block_number": self.block_number,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class PriceHistory(db.Model):
    """Historical price data for tokens."""

    __tablename__ = "price_history"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    volume_24h = db.Column(db.Float, nullable=False, default=0.0)
    market_cap = db.Column(db.Float, nullable=False, default=0.0)
    change_24h = db.Column(db.Float, nullable=False, default=0.0)
    timestamp = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "volume_24h": self.volume_24h,
            "market_cap": self.market_cap,
            "change_24h": self.change_24h,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
