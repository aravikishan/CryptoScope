"""REST API endpoints for CryptoScope."""

from flask import Blueprint, jsonify, request

from services.portfolio import PortfolioService
from services.market import MarketService

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _portfolio():
    return PortfolioService()


def _market():
    return MarketService()


# ------------------------------------------------------------------
# Wallet endpoints
# ------------------------------------------------------------------

@api_bp.route("/wallets", methods=["GET"])
def list_wallets():
    """List all active wallets."""
    svc = _portfolio()
    wallets = svc.get_all_wallets()
    return jsonify([w.to_dict() for w in wallets])


@api_bp.route("/wallets", methods=["POST"])
def create_wallet():
    """Create a new wallet."""
    data = request.get_json(force=True)
    name = data.get("name", "My Wallet")
    network = data.get("network", "ethereum")
    svc = _portfolio()
    wallet = svc.create_wallet(name, network)
    return jsonify(wallet.to_dict()), 201


@api_bp.route("/wallets/<int:wallet_id>", methods=["GET"])
def get_wallet(wallet_id):
    """Get wallet details with token holdings."""
    svc = _portfolio()
    wallet = svc.get_wallet(wallet_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    tokens = svc.get_wallet_tokens(wallet_id)
    result = wallet.to_dict()
    result["tokens"] = tokens
    return jsonify(result)


@api_bp.route("/wallets/<int:wallet_id>", methods=["DELETE"])
def delete_wallet(wallet_id):
    """Delete a wallet."""
    svc = _portfolio()
    success = svc.delete_wallet(wallet_id)
    if success:
        return jsonify({"message": "Wallet deleted"}), 200
    return jsonify({"error": "Wallet not found"}), 404


# ------------------------------------------------------------------
# Token endpoints
# ------------------------------------------------------------------

@api_bp.route("/wallets/<int:wallet_id>/tokens", methods=["POST"])
def add_token(wallet_id):
    """Add a token to a wallet."""
    data = request.get_json(force=True)
    symbol = data.get("symbol", "").upper()
    name = data.get("name", symbol)
    if not symbol:
        return jsonify({"error": "Symbol is required"}), 400
    svc = _portfolio()
    token = svc.add_token_to_wallet(wallet_id, symbol, name)
    return jsonify(token.to_dict()), 201


@api_bp.route("/wallets/<int:wallet_id>/tokens", methods=["GET"])
def list_tokens(wallet_id):
    """List tokens in a wallet with current values."""
    svc = _portfolio()
    tokens = svc.get_wallet_tokens(wallet_id)
    return jsonify(tokens)


# ------------------------------------------------------------------
# Transaction endpoints
# ------------------------------------------------------------------

@api_bp.route("/transactions", methods=["POST"])
def create_transaction():
    """Execute a buy/sell/transfer transaction."""
    data = request.get_json(force=True)
    wallet_id = data.get("wallet_id")
    symbol = data.get("symbol", "").upper()
    tx_type = data.get("tx_type", "buy")
    quantity = float(data.get("quantity", 0))
    price = data.get("price_per_unit")
    notes = data.get("notes")

    if not wallet_id or not symbol or quantity <= 0:
        return jsonify({"error": "wallet_id, symbol, and positive quantity required"}), 400
    if tx_type not in ("buy", "sell", "transfer"):
        return jsonify({"error": "tx_type must be buy, sell, or transfer"}), 400

    svc = _portfolio()
    price_float = float(price) if price is not None else None
    tx = svc.execute_transaction(
        wallet_id, symbol, tx_type, quantity, price_float, notes,
    )
    return jsonify(tx.to_dict()), 201


@api_bp.route("/wallets/<int:wallet_id>/transactions", methods=["GET"])
def list_transactions(wallet_id):
    """List transactions for a wallet."""
    limit = request.args.get("limit", 50, type=int)
    svc = _portfolio()
    txs = svc.get_wallet_transactions(wallet_id, limit)
    return jsonify([tx.to_dict() for tx in txs])


# ------------------------------------------------------------------
# Portfolio endpoints
# ------------------------------------------------------------------

@api_bp.route("/portfolio/summary", methods=["GET"])
def portfolio_summary():
    """Get overall portfolio summary with P&L."""
    svc = _portfolio()
    summary = svc.get_portfolio_summary()
    return jsonify(summary)


@api_bp.route("/portfolio/top-performers", methods=["GET"])
def top_performers():
    """Get top performing tokens by P&L."""
    limit = request.args.get("limit", 5, type=int)
    svc = _portfolio()
    performers = svc.get_top_performers(limit)
    return jsonify(performers)


# ------------------------------------------------------------------
# Market endpoints
# ------------------------------------------------------------------

@api_bp.route("/market/prices", methods=["GET"])
def market_prices():
    """Get current prices for all tokens."""
    svc = _market()
    prices = svc.get_all_current_prices()
    return jsonify(prices)


@api_bp.route("/market/prices/<symbol>", methods=["GET"])
def token_price(symbol):
    """Get current price for a specific token."""
    svc = _market()
    price = svc.get_current_price(symbol.upper())
    if price == 0.0:
        return jsonify({"error": "Token not found"}), 404
    all_prices = svc.get_all_current_prices()
    data = all_prices.get(symbol.upper(), {"symbol": symbol.upper(), "price": price})
    return jsonify(data)


@api_bp.route("/market/history/<symbol>", methods=["GET"])
def price_history(symbol):
    """Get price history for a token."""
    days = request.args.get("days", 90, type=int)
    svc = _market()
    history = svc.get_price_history(symbol.upper(), days)
    if not history:
        return jsonify({"error": "Token not found"}), 404
    return jsonify({"symbol": symbol.upper(), "days": days, "history": history})


@api_bp.route("/market/correlation", methods=["GET"])
def correlation_matrix():
    """Get token correlation matrix."""
    symbols_param = request.args.get("symbols", "")
    days = request.args.get("days", 30, type=int)
    symbols = (
        [s.strip().upper() for s in symbols_param.split(",") if s.strip()]
        if symbols_param else None
    )
    svc = _market()
    matrix = svc.compute_correlation_matrix(symbols, days)
    return jsonify(matrix)


# ------------------------------------------------------------------
# Gas fee endpoints
# ------------------------------------------------------------------

@api_bp.route("/gas/current", methods=["GET"])
def current_gas():
    """Get current gas price."""
    svc = _market()
    gas_gwei = svc.get_current_gas_price()
    fee_usd = svc.calculate_gas_fee_usd(gas_gwei)
    return jsonify({
        "gas_price_gwei": gas_gwei,
        "fee_usd": fee_usd,
        "network": "ethereum",
    })


@api_bp.route("/gas/history", methods=["GET"])
def gas_history():
    """Get gas price history."""
    days = request.args.get("days", 30, type=int)
    svc = _market()
    history = svc.get_gas_history(days)
    return jsonify({"days": days, "history": history})


@api_bp.route("/gas/stats", methods=["GET"])
def gas_stats():
    """Get aggregate gas fee statistics."""
    svc = _market()
    stats = svc.get_gas_stats()
    return jsonify(stats)


# ------------------------------------------------------------------
# Health check
# ------------------------------------------------------------------

@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "CryptoScope"})
