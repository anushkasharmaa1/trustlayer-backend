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


def detect_anomalies(transactions: list[dict]) -> list[str]:
    """
    Basic anomaly detection for anti-gaming.
    
    Returns a list of warning messages if suspicious patterns are detected.
    """
    warnings = []
    
    if not transactions:
        return warnings
    
    amounts = [txn["amount"] for txn in transactions]
    
    # Check for round numbers
    round_count = sum(1 for amt in amounts if amt % 100 == 0)
    if round_count / len(amounts) > 0.8:
        warnings.append("High proportion of round number transactions detected")
    
    # Check for weekend transactions
    weekend_txns = 0
    total_txns = len(transactions)
    for txn in transactions:
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(txn["date"])
            if dt.weekday() >= 5:  # Saturday=5, Sunday=6
                weekend_txns += 1
        except:
            pass
    if weekend_txns == 0 and total_txns > 10:
        warnings.append("No weekend transactions detected")
    
    # Check for identical income values
    credits = [txn["amount"] for txn in transactions if txn["type"] == "credit"]
    if len(credits) > 1 and len(set(credits)) == 1:
        warnings.append("All income transactions have identical amounts")
    
    return warnings


def extract_features(transactions: list[dict]) -> FeatureBreakdown:
    """
    Derive behavioral financial features from a flat list of transactions.

    Args:
        transactions: list of dicts with keys: amount, type, date, sender?, description?, category?

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
            income_regular_day_variance=1.0,
            income_source_count=0,
            essential_spend_ratio=0.0,
            savings_transfer_frequency=0.0,
            cash_withdrawal_ratio=0.0,
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

    # New features
    # Income regularity: variance in payment days
    income_days = [int(txn["date"][-2:]) for txn in transactions if txn["type"] == "credit"]
    income_regular_day_variance = float(np.var(income_days)) if income_days else 1.0

    # Income source diversity: distinct senders
    senders = [txn.get("sender", f"unknown_{txn['amount']}") for txn in transactions if txn["type"] == "credit"]
    income_source_count = len(set(senders))

    # Essential spending ratio
    essential_categories = {"rent", "utilities", "telecom", "insurance", "loan_payment"}
    essential_spending = sum(txn["amount"] for txn in transactions 
                           if txn["type"] == "debit" and txn.get("category") in essential_categories)
    essential_spend_ratio = essential_spending / total_spending if total_spending > 0 else 0.0

    # Savings transfer frequency
    savings_txns = [txn for txn in transactions if txn["type"] == "debit" and txn.get("category") == "savings"]
    savings_transfer_frequency = len(savings_txns) / num_months

    # Cash withdrawal ratio
    cash_withdrawals = sum(txn["amount"] for txn in transactions 
                          if txn["type"] == "debit" and txn.get("category") == "cash_withdrawal")
    cash_withdrawal_ratio = cash_withdrawals / total_spending if total_spending > 0 else 0.0

    return FeatureBreakdown(
        income_stability=round(income_stability, 4),
        spending_consistency=round(spending_consistency, 4),
        savings_ratio=round(savings_ratio, 4),
        transaction_frequency=round(transaction_frequency, 2),
        avg_monthly_income=round(avg_income, 2),
        avg_monthly_spending=round(avg_spending, 2),
        income_regular_day_variance=round(income_regular_day_variance, 4),
        income_source_count=income_source_count,
        essential_spend_ratio=round(essential_spend_ratio, 4),
        savings_transfer_frequency=round(savings_transfer_frequency, 2),
        cash_withdrawal_ratio=round(cash_withdrawal_ratio, 4),
    )
