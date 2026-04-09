"""
feature_engineering.py
-----------------------
Transforms raw transaction records into interpretable behavioral features
used by the scoring engine.

All computations are pure functions with no side effects — easy to test
and deterministic given the same input.
"""

from collections import defaultdict
from datetime import date
import numpy as np
from models.response_model import FeatureBreakdown


def _group_by_month(transactions: list[dict]) -> dict[str, dict]:
    """
    Group transactions by YYYY-MM and separate into credits/debits.

    Returns:
        { "2024-01": {"credits": [amt, ...], "debits": [amt, ...]}, ... }
    """
    monthly: dict[str, dict] = defaultdict(lambda: {"credits": [], "debits": []})

    for txn in transactions:
        month_key = txn["date"][:7]  # "YYYY-MM"
        if txn["type"] == "credit":
            monthly[month_key]["credits"].append(txn["amount"])
        else:
            monthly[month_key]["debits"].append(txn["amount"])

    return dict(monthly)


def _coefficient_of_variation(values: list[float]) -> float:
    """
    Normalized measure of dispersion: std / mean.
    Returns 0 if mean is 0 (to avoid division by zero).
    A lower CV indicates higher consistency.
    """
    if not values or len(values) < 2:
        return 0.0
    arr = np.array(values, dtype=float)
    mean = np.mean(arr)
    if mean == 0:
        return 0.0
    return float(np.std(arr) / mean)


def extract_features(transactions: list[dict]) -> FeatureBreakdown:
    """
    Derive behavioral financial features from a flat list of transactions.

    Args:
        transactions: list of dicts with keys: amount, type, date

    Returns:
        FeatureBreakdown with all computed metrics.
    """
    if not transactions:
        # Return neutral features for empty history
        return FeatureBreakdown(
            income_stability=1.0,
            spending_consistency=1.0,
            savings_ratio=0.0,
            transaction_frequency=0.0,
            avg_monthly_income=0.0,
            avg_monthly_spending=0.0,
        )

    monthly = _group_by_month(transactions)
    months = sorted(monthly.keys())
    num_months = max(len(months), 1)

    # Monthly totals
    monthly_income   = [sum(monthly[m]["credits"]) for m in months]
    monthly_spending = [sum(monthly[m]["debits"])  for m in months]

    avg_income   = float(np.mean(monthly_income))   if monthly_income   else 0.0
    avg_spending = float(np.mean(monthly_spending)) if monthly_spending else 0.0

    # Income stability: CV of monthly income — lower is better
    income_stability = _coefficient_of_variation(monthly_income)

    # Spending consistency: CV of monthly spending — lower is more consistent
    spending_consistency = _coefficient_of_variation(monthly_spending)

    # Savings ratio: (total_income - total_spending) / total_income
    total_income   = sum(monthly_income)
    total_spending = sum(monthly_spending)
    savings_ratio  = max(0.0, (total_income - total_spending) / total_income) if total_income > 0 else 0.0

    # Transaction frequency: average transactions per month
    total_txns           = len(transactions)
    transaction_frequency = total_txns / num_months

    return FeatureBreakdown(
        income_stability=round(income_stability, 4),
        spending_consistency=round(spending_consistency, 4),
        savings_ratio=round(savings_ratio, 4),
        transaction_frequency=round(transaction_frequency, 2),
        avg_monthly_income=round(avg_income, 2),
        avg_monthly_spending=round(avg_spending, 2),
    )
