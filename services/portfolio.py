"""Portfolio tracking, P&L calculations, and allocation analysis."""

import hashlib
import time
from datetime import datetime, timezone

from models.database import db
from models.schemas import Wallet, Token, Transaction
from services.market import MarketService


class PortfolioService:
    """Handles portfolio operations, cost basis tracking, and P&L."""

    def __init__(self):
        self.market = MarketService()

    # ------------------------------------------------------------------
    # Wallet operations
    # ------------------------------------------------------------------

    def create_wallet(self, name, network="ethereum"):
        """Create a new wallet with a deterministic address."""
        seed = f"{name}-{network}-{time.time()}"
        address = "0x" + hashlib.sha256(seed.encode()).hexdigest()[:40]
        wallet = Wallet(name=name, address=address, network=network)
        db.session.add(wallet)
        db.session.commit()
        return wallet

    def get_wallet(self, wallet_id):
        """Retrieve a wallet by ID."""
        return db.session.get(Wallet, wallet_id)

    def get_all_wallets(self):
        """Retrieve all active wallets."""
        return Wallet.query.filter_by(is_active=True).all()

    def delete_wallet(self, wallet_id):
        """Soft-delete a wallet."""
        wallet = db.session.get(Wallet, wallet_id)
        if wallet:
            wallet.is_active = False
            db.session.commit()
            return True
        return False

    # ------------------------------------------------------------------
    # Token operations
    # ------------------------------------------------------------------

    def add_token_to_wallet(self, wallet_id, symbol, name=None):
        """Add a token tracking entry to a wallet."""
        if name is None:
            name = symbol
        existing = Token.query.filter_by(
            wallet_id=wallet_id, symbol=symbol
        ).first()
        if existing:
            return existing
        token = Token(wallet_id=wallet_id, symbol=symbol, name=name)
        db.session.add(token)
        db.session.commit()
        return token

    def get_wallet_tokens(self, wallet_id):
        """Get all tokens in a wallet with current values."""
        tokens = Token.query.filter_by(wallet_id=wallet_id).all()
        result = []
        for token in tokens:
            current_price = self.market.get_current_price(token.symbol)
            current_value = token.balance * current_price
            unrealized_pnl = current_value - token.cost_basis
            pnl_percent = (
                (unrealized_pnl / token.cost_basis * 100)
                if token.cost_basis > 0 else 0.0
            )
            result.append({
                **token.to_dict(),
                "current_price": current_price,
                "current_value": current_value,
                "unrealized_pnl": unrealized_pnl,
                "pnl_percent": pnl_percent,
                "total_pnl": unrealized_pnl + token.realized_pnl,
            })
        return result

    # ------------------------------------------------------------------
    # Transaction processing
    # ------------------------------------------------------------------

    def execute_transaction(self, wallet_id, symbol, tx_type, quantity,
                            price_per_unit=None, notes=None):
        """Execute a buy/sell/transfer transaction with gas fee."""
        if price_per_unit is None:
            price_per_unit = self.market.get_current_price(symbol)

        total_value = quantity * price_per_unit
        gas_price_gwei = self.market.get_current_gas_price()
        gas_fee = self.market.calculate_gas_fee_usd(gas_price_gwei)

        tx_seed = f"{wallet_id}-{symbol}-{tx_type}-{time.time()}"
        tx_hash = "0x" + hashlib.sha256(tx_seed.encode()).hexdigest()[:64]

        transaction = Transaction(
            wallet_id=wallet_id,
            symbol=symbol,
            tx_type=tx_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            total_value=total_value,
            gas_fee=gas_fee,
            gas_price_gwei=gas_price_gwei,
            tx_hash=tx_hash,
            notes=notes,
        )
        db.session.add(transaction)

        token = Token.query.filter_by(
            wallet_id=wallet_id, symbol=symbol
        ).first()
        if token is None:
            token = self.add_token_to_wallet(wallet_id, symbol)

        if tx_type == "buy":
            new_cost_basis = token.cost_basis + total_value
            new_balance = token.balance + quantity
            token.avg_buy_price = (
                new_cost_basis / new_balance if new_balance > 0 else 0.0
            )
            token.balance = new_balance
            token.cost_basis = new_cost_basis
            token.total_invested += total_value
        elif tx_type == "sell":
            if quantity > token.balance:
                quantity = token.balance
            cost_of_sold = token.avg_buy_price * quantity
            realized = (price_per_unit - token.avg_buy_price) * quantity
            token.realized_pnl += realized
            token.balance -= quantity
            token.cost_basis -= cost_of_sold
            token.total_sold += total_value
            if token.cost_basis < 0:
                token.cost_basis = 0.0

        self.market.record_gas_fee(gas_price_gwei, gas_fee)
        db.session.commit()
        return transaction

    def get_wallet_transactions(self, wallet_id, limit=50):
        """Get recent transactions for a wallet."""
        return (
            Transaction.query
            .filter_by(wallet_id=wallet_id)
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------
    # Portfolio analytics
    # ------------------------------------------------------------------

    def get_portfolio_summary(self):
        """Calculate aggregate portfolio metrics across all wallets."""
        wallets = self.get_all_wallets()
        total_value = 0.0
        total_cost_basis = 0.0
        total_realized_pnl = 0.0
        total_invested = 0.0
        allocation = {}
        token_details = []

        for wallet in wallets:
            tokens = self.get_wallet_tokens(wallet.id)
            for t in tokens:
                total_value += t["current_value"]
                total_cost_basis += t["cost_basis"]
                total_realized_pnl += t["realized_pnl"]
                total_invested += t["total_invested"]

                if t["symbol"] in allocation:
                    allocation[t["symbol"]] += t["current_value"]
                else:
                    allocation[t["symbol"]] = t["current_value"]

                token_details.append(t)

        unrealized_pnl = total_value - total_cost_basis
        total_pnl = unrealized_pnl + total_realized_pnl
        pnl_percent = (
            (total_pnl / total_invested * 100)
            if total_invested > 0 else 0.0
        )

        allocation_pct = {}
        for symbol, value in allocation.items():
            allocation_pct[symbol] = (
                (value / total_value * 100) if total_value > 0 else 0.0
            )

        price_data = self.market.get_all_current_prices()
        change_24h = sum(
            price_data.get(s, {}).get("change_24h", 0.0) *
            (allocation_pct.get(s, 0.0) / 100.0)
            for s in allocation_pct
        )

        return {
            "total_value": total_value,
            "total_cost_basis": total_cost_basis,
            "total_invested": total_invested,
            "unrealized_pnl": unrealized_pnl,
            "realized_pnl": total_realized_pnl,
            "total_pnl": total_pnl,
            "pnl_percent": pnl_percent,
            "change_24h": change_24h,
            "allocation": allocation,
            "allocation_pct": allocation_pct,
            "wallet_count": len(wallets),
            "token_count": len(token_details),
        }

    def get_top_performers(self, limit=5):
        """Return tokens sorted by P&L performance."""
        all_tokens = []
        for wallet in self.get_all_wallets():
            all_tokens.extend(self.get_wallet_tokens(wallet.id))

        aggregated = {}
        for t in all_tokens:
            sym = t["symbol"]
            if sym not in aggregated:
                aggregated[sym] = {
                    "symbol": sym,
                    "total_pnl": 0.0,
                    "pnl_percent": 0.0,
                    "current_value": 0.0,
                }
            aggregated[sym]["total_pnl"] += t["total_pnl"]
            aggregated[sym]["current_value"] += t["current_value"]

        for sym in aggregated:
            entry = aggregated[sym]
            if entry["current_value"] > 0:
                entry["pnl_percent"] = (
                    entry["total_pnl"] / entry["current_value"] * 100
                )

        sorted_tokens = sorted(
            aggregated.values(), key=lambda x: x["total_pnl"], reverse=True
        )
        return sorted_tokens[:limit]

    def get_total_gas_spent(self):
        """Calculate total gas fees spent across all transactions."""
        from sqlalchemy import func
        result = db.session.query(func.sum(Transaction.gas_fee)).scalar()
        return result or 0.0
