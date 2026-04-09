"""
build_training_dataset.py
--------------------------
Processes raw UPI transaction datasets into behavioral features for ML training.

This script:
1. Loads and standardizes transaction data from multiple sources
2. Aggregates features by user (using Receiver UPI ID as user_id)
3. Generates proxy risk labels based on behavioral patterns
4. Outputs clean training dataset for XGBoost model

Features generated:
- transaction_frequency: Total transactions per user
- income_source_count: Number of distinct income sources
- avg_income: Average incoming transaction amount
- income_variance: Variance in incoming amounts (lower = more regular)
- essential_spend_ratio: Ratio of essential expenses (set to 0.5 as proxy since no categories)
- cash_withdrawal_ratio: Ratio of cash withdrawals (set to 0 since no ATM data)
- risk_label: Proxy label (1 = high risk, 0 = low risk) based on variance
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Dataset paths
DATA_DIR = Path(__file__).parent.parent / "datasets"
OUTPUT_FILE = DATA_DIR / "trustlayer_training_data.csv"

def load_and_standardize_data():
    """Load transaction datasets and standardize column names."""
    # Load main transaction dataset
    df = pd.read_csv(DATA_DIR / "transactions.csv")

    # Standardize column names
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('@', '')

    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Filter successful transactions only
    df = df[df['status'] == 'SUCCESS'].copy()

    return df

def aggregate_user_features(df):
    """Aggregate behavioral features by user (Receiver UPI ID)."""
    users = []

    # Get unique users (receivers)
    unique_users = df['receiver_upi_id'].unique()

    for user_id in unique_users:
        # Transactions where user is receiver (income)
        income_txns = df[df['receiver_upi_id'] == user_id]

        # Transactions where user is sender (expenses)
        expense_txns = df[df['sender_upi_id'] == user_id]

        # Skip users with no income data
        if len(income_txns) == 0:
            continue

        # Calculate features
        transaction_frequency = len(income_txns) + len(expense_txns)
        income_source_count = income_txns['sender_upi_id'].nunique()
        avg_income = income_txns['amount_inr'].mean()
        income_variance = income_txns['amount_inr'].var() if len(income_txns) > 1 else 0

        # Proxy values since no merchant categories or cash withdrawal data
        essential_spend_ratio = 0.5  # Assume 50% of expenses are essential
        cash_withdrawal_ratio = 0.0  # No cash withdrawal data in UPI

        # Create proxy risk label
        # High risk if low average income or few income sources
        risk_label = 1 if (avg_income < 3000 or income_source_count < 1) else 0

        users.append({
            'user_id': user_id,
            'transaction_frequency': transaction_frequency,
            'income_source_count': income_source_count,
            'avg_income': avg_income,
            'income_variance': income_variance,
            'essential_spend_ratio': essential_spend_ratio,
            'cash_withdrawal_ratio': cash_withdrawal_ratio,
            'risk_label': risk_label
        })

    return pd.DataFrame(users)

def main():
    """Main pipeline to build training dataset."""
    print("Loading and standardizing transaction data...")
    df = load_and_standardize_data()

    print(f"Loaded {len(df)} transactions")
    print(f"Unique users: {df['receiver_upi_id'].nunique()}")

    print("Aggregating user features...")
    training_df = aggregate_user_features(df)

    print(f"Generated training data for {len(training_df)} users")
    print(f"Risk distribution: {training_df['risk_label'].value_counts().to_dict()}")

    # Save to CSV
    training_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Training dataset saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()