"""
transaction_model.py
--------------------
Pydantic models for validating incoming transaction payloads.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import date


class Transaction(BaseModel):
    """A single financial transaction."""

    amount: float = Field(
        ...,
        gt=0,
        description="Transaction amount in INR. Must be a positive number.",
    )
    type: Literal["credit", "debit"] = Field(
        ...,
        description="'credit' for money received, 'debit' for money spent.",
    )
    date: str = Field(
        ...,
        description="Transaction date in YYYY-MM-DD format.",
    )
    sender: str | None = Field(
        None,
        description="Sender name for credit transactions (e.g., employer, client).",
    )
    description: str | None = Field(
        None,
        description="Transaction description or memo.",
    )
    category: str | None = Field(
        None,
        description="Transaction category (e.g., 'income', 'rent', 'groceries', 'savings', 'cash_withdrawal').",
    )

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Ensure date is parseable as YYYY-MM-DD."""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format.")
        return v


class TransactionUploadRequest(BaseModel):
    """Payload for POST /upload-transactions."""

    user_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the user.",
    )
    transactions: list[Transaction] = Field(
        ...,
        min_length=1,
        description="List of transactions to store. At least one required.",
    )


class SimulationRequest(BaseModel):
    """Payload for POST /simulate."""

    user_id: str = Field(..., description="User to run the simulation for.")
    increase_savings: float = Field(
        default=0.0,
        ge=0,
        description="Extra monthly savings amount added to the user's profile (INR).",
    )
    reduce_spending_percent: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Percentage by which to reduce debit transactions (0-100).",
    )
