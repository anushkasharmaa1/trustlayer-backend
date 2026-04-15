"""
response_model.py
-----------------
Pydantic models that define the structured JSON shape of every API response.
All endpoints return one of these models — never raw dicts.
"""

from pydantic import BaseModel, Field
from typing import Literal


class FeatureBreakdown(BaseModel):
    """Computed behavioral features used to derive the Trust Score."""

    income_stability: float = Field(
        ..., description="Coefficient of variation of income (lower = more stable)."
    )
    spending_consistency: float = Field(
        ..., description="Coefficient of variation of spending (lower = more consistent)."
    )
    savings_ratio: float = Field(
        ..., description="Net savings as a fraction of total income (higher = better)."
    )
    transaction_frequency: float = Field(
        ..., description="Average number of transactions per month."
    )
    avg_monthly_income: float = Field(
        ..., description="Mean monthly credit (income) in INR."
    )
    avg_monthly_spending: float = Field(
        ..., description="Mean monthly debit (spending) in INR."
    )
    income_regular_day_variance: float = Field(
        ..., description="Variance in income payment days (lower = more regular)."
    )
    income_source_count: int = Field(
        ..., description="Number of distinct income sources."
    )
    essential_spend_ratio: float = Field(
        ..., description="Ratio of spending on essentials (rent, utilities, etc.) to total spending."
    )
    savings_transfer_frequency: float = Field(
        ..., description="Frequency of transfers to savings/investment accounts per month."
    )
    cash_withdrawal_ratio: float = Field(
        ..., description="Ratio of cash withdrawals to total spending."
    )


class TrustScoreResponse(BaseModel):
    """Standard Trust Score response returned by /get-score and /simulate."""

    trust_score: int = Field(
        ..., ge=0, le=1000, description="Composite behavioral credit score (0-1000)."
    )
    risk_level: Literal["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"] = Field(
        ..., description="Derived risk classification based on trust_score."
    )
    top_positive_signals: list[str] = Field(
        ..., description="Key positive behavioral signals contributing to the score."
    )
    risk_signals: list[str] = Field(
        ..., description="Key risk signals that may lower the score."
    )
    features: FeatureBreakdown
    explanation: list[str] = Field(
        ..., description="Human-readable summary of factors driving the score."
    )


class UploadResponse(BaseModel):
    """Returned after a successful transaction upload."""

    message: str
    user_id: str
    transactions_stored: int


class SimulationResponse(TrustScoreResponse):
    """Extends TrustScoreResponse with simulation delta metadata."""

    original_score: int = Field(..., description="Score before applying hypothetical changes.")
    score_delta: int = Field(..., description="Difference: simulated_score - original_score.")
