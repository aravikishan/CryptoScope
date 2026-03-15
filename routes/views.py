"""HTML-serving view routes for CryptoScope."""

from flask import Blueprint, render_template

from services.portfolio import PortfolioService
from services.market import MarketService

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    """Portfolio dashboard."""
    svc = PortfolioService()
    market = MarketService()
    summary = svc.get_portfolio_summary()
    prices = market.get_all_current_prices()
    top = svc.get_top_performers()
    gas_stats = market.get_gas_stats()
    return render_template(
        "index.html",
        summary=summary,
        prices=prices,
        top_performers=top,
        gas_stats=gas_stats,
    )


@views_bp.route("/wallet/<int:wallet_id>")
def wallet_detail(wallet_id):
    """Wallet detail page."""
    svc = PortfolioService()
    wallet = svc.get_wallet(wallet_id)
    if not wallet:
        return render_template("index.html", error="Wallet not found"), 404
    tokens = svc.get_wallet_tokens(wallet_id)
    transactions = svc.get_wallet_transactions(wallet_id)
    return render_template(
        "wallet.html",
        wallet=wallet,
        tokens=tokens,
        transactions=transactions,
    )


@views_bp.route("/wallets")
def wallets_list():
    """List all wallets."""
    svc = PortfolioService()
    wallets = svc.get_all_wallets()
    return render_template("wallet.html", wallets=wallets, wallet=None, tokens=[], transactions=[])


@views_bp.route("/market")
def market_overview():
    """Market overview page."""
    market = MarketService()
    prices = market.get_all_current_prices()
    sorted_prices = sorted(prices.values(), key=lambda x: x["market_cap"], reverse=True)
    correlation = market.compute_correlation_matrix()
    return render_template(
        "market.html",
        prices=sorted_prices,
        correlation=correlation,
    )


@views_bp.route("/gas")
def gas_tracker():
    """Gas fee tracker page."""
    market = MarketService()
    gas_stats = market.get_gas_stats()
    gas_history = market.get_gas_history(30)
    return render_template(
        "gas.html",
        gas_stats=gas_stats,
        gas_history=gas_history,
    )


@views_bp.route("/about")
def about():
    """About page."""
    return render_template("about.html")
