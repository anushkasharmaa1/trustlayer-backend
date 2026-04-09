"""
simulation_engine.py
--------------------
Applies hypothetical behavioral changes to a user's transaction history
and returns a simulated Trust Score without persisting any changes.

Supports:
  - increase_savings: adds a synthetic monthly credit entry
  - reduce_spending_percent: scales down all debit amounts by a given percentage
"""

import copy
from datetime import date

from models.transaction_model import SimulationRequest
from models.response_model import SimulationResponse
from services.feature_engineering import extract_features
from services.scoring_engine import compute_trust_score


def _apply_increase_savings(
    transactions: list[dict], extra_monthly_savings: float
) -> list[dict]:
    """
    Simulate saving more by injecting an extra credit entry per month
    that appears in the transaction history.
    """
    if extra_monthly_savings <= 0:
        return transactions

    # Find the set of months already present
    months_present = {t["date"][:7] for t in transactions}

    synthetic = []
    for month in months_present:
        # Place synthetic entry on the 28th of each month (always valid)
        synthetic.append({
            "amount": extra_monthly_savings,
            "type": "credit",
            "date": f"{month}-28",
        })

    return transactions + synthetic


def _apply_reduce_spending(
    transactions: list[dict], reduce_percent: float
) -> list[dict]:
    """
    Simulate reducing discretionary spending by scaling all debit amounts down.
    """
    if reduce_percent <= 0:
        return transactions

    factor = 1.0 - (reduce_percent / 100.0)
    adjusted = []
    for txn in transactions:
        if txn["type"] == "debit":
            adjusted.append({**txn, "amount": round(txn["amount"] * factor, 2)})
        else:
            adjusted.append(txn)
    return adjusted


def simulate_score(
    original_transactions: list[dict],
    request: SimulationRequest,
) -> SimulationResponse:
    """
    Apply hypothetical changes to the transaction list and compute
    a new Trust Score without modifying stored data.

    Args:
        original_transactions: Current stored transactions for the user.
        request: SimulationRequest containing the hypothetical parameters.

    Returns:
        SimulationResponse with original score, simulated score, and delta.
    """
    # Step 1: compute baseline score from original data
    original_features = extract_features(original_transactions)
    original_result   = compute_trust_score(original_features)

    # Step 2: apply hypothetical changes to a copy
    simulated = copy.deepcopy(original_transactions)
    simulated = _apply_increase_savings(simulated, request.increase_savings)
    simulated = _apply_reduce_spending(simulated, request.reduce_spending_percent)

    # Step 3: compute simulated score
    sim_features = extract_features(simulated)
    sim_result   = compute_trust_score(sim_features)

    return SimulationResponse(
        trust_score=sim_result.trust_score,
        risk_level=sim_result.risk_level,
        features=sim_result.features,
        explanation=sim_result.explanation,
        original_score=original_result.trust_score,
        score_delta=sim_result.trust_score - original_result.trust_score,
    )
