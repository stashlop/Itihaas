"""Itihaas Coins ledger.

All coin movements happen on the server and are recorded in the
``Transaction`` table, so the balance is always auditable. The browser never
decides how many coins a user earns or spends.
"""
from __future__ import annotations

import math
import uuid

from flask import current_app

from .extensions import db
from .models import ItihaasCoins, Transaction

REWARD = "reward"
PAYMENT = "payment"


def get_wallet(user_id: int) -> ItihaasCoins:
    """Return the user's wallet, creating an empty one if needed (not committed)."""
    wallet = ItihaasCoins.query.filter_by(user_id=user_id).first()
    if wallet is None:
        wallet = ItihaasCoins(user_id=user_id, coins=0)
        db.session.add(wallet)
        db.session.flush()
    return wallet


def _record(user_id: int, amount: int, kind: str, reference: str) -> Transaction:
    txn = Transaction(
        user_id=user_id,
        amount=amount,
        transaction_type=kind,
        transaction_id=f"{reference}-{uuid.uuid4().hex[:8]}",
    )
    db.session.add(txn)
    return txn


def spend(user_id: int, requested: int, max_amount: float, reference: str) -> int:
    """Spend up to ``requested`` coins (capped by balance and ``max_amount``).

    Returns the number of coins actually spent. 1 coin = ₹1.
    """
    wallet = get_wallet(user_id)
    coins = max(0, min(int(requested or 0), wallet.coins, int(math.floor(max_amount))))
    if coins:
        wallet.coins -= coins
        _record(user_id, coins, PAYMENT, reference)
    return coins


def reward_for(amount_paid: float) -> int:
    rate = current_app.config.get("COIN_REWARD_RATE", 0.10)
    return max(0, int(math.floor(amount_paid * rate)))


def award(user_id: int, coins: int, reference: str) -> int:
    if coins <= 0:
        return 0
    wallet = get_wallet(user_id)
    wallet.coins += coins
    _record(user_id, coins, REWARD, reference)
    return coins
