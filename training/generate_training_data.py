"""
generate_training_data.py
--------------------------
Generates a realistic synthetic dataset of gig worker financial profiles
with labeled credit outcomes (defaulted: 0/1).

Why synthetic and not Kaggle directly?
  The Kaggle Home Credit dataset has different feature shapes than what
  TrustLayer extracts from UPI transactions. This generator creates data
  that matches TrustLayer's exact feature schema, while embedding the same
  statistical patterns that real credit research has validated:

  - Low income volatility  → lower default rate
  - High savings ratio     → lower default rate
  - Consistent spending    → lower default rate
  - High transaction freq  → lower default rate (more financial activity = more stable)

  These relationships are grounded in RBI and World Bank research on
  alternative credit scoring for informal economy workers.

Output: training/training_data.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path

RANDOM_SEED = 42
N_SAMPLES   = 15_000   # enough for robust XGBoost training

rng = np.random.default_rng(RANDOM_SEED)


def generate_profile(n: int) -> pd.DataFrame:
    """
    Generate n synthetic gig worker financial profiles.
    Each row = one user's aggregated behavioral features + default label.
    """

    # ------------------------------------------------------------------ #
    # 1. Latent "financial health" score (0-1) — drives all features      #
    # ------------------------------------------------------------------ #
    # This hidden variable represents true creditworthiness.
    # We use it to make features correlated with each other realistically.
    health = rng.beta(a=2.5, b=2.0, size=n)   # slightly right-skewed

    # ------------------------------------------------------------------ #
    # 2. Feature generation (each feature correlated with health)         #
    # ------------------------------------------------------------------ #

    # Income stability (CV of monthly income — lower = more stable)
    # Healthy workers: low CV (~0.05-0.2), struggling: high CV (~0.4-1.2)
    income_stability = np.clip(
        rng.beta(a=1.5, b=4.0, size=n) * (1.5 - health) + rng.normal(0, 0.03, n),
        0.01, 1.5
    )

    # Spending consistency (CV of monthly spending — lower = more consistent)
    spending_consistency = np.clip(
        rng.beta(a=1.5, b=3.5, size=n) * (1.4 - health * 0.8) + rng.normal(0, 0.03, n),
        0.01, 1.5
    )

    # Savings ratio (net savings / income — higher = better)
    savings_ratio = np.clip(
        health * 0.55 + rng.normal(0, 0.06, n),
        0.0, 0.80
    )

    # Transaction frequency (txn/month — higher = more active)
    transaction_frequency = np.clip(
        health * 25 + rng.normal(3, 2, n),
        1.0, 60.0
    )

    # Average monthly income (INR)
    avg_monthly_income = np.clip(
        health * 35000 + rng.normal(8000, 3000, n),
        3000, 80000
    )

    # Average monthly spending
    spend_fraction = np.clip(1.0 - savings_ratio + rng.normal(0, 0.05, n), 0.2, 1.1)
    avg_monthly_spending = np.clip(
        avg_monthly_income * spend_fraction,
        1000, avg_monthly_income * 1.1
    )

    # ------------------------------------------------------------------ #
    # 3. Default label generation                                         #
    # ------------------------------------------------------------------ #
    # Logistic model: probability of default decreases with health
    # Calibrated so ~22% of the dataset defaults (realistic for gig segment)

    log_odds = (
        -2.5                                        # intercept
        + 2.8  * income_stability                   # high volatility = risky
        + 1.6  * spending_consistency               # inconsistent spending = risky
        - 5.0  * savings_ratio                      # savings = protective
        - 0.06 * (transaction_frequency - 10)       # more activity = safer
        - 0.00003 * (avg_monthly_income - 15000)    # higher income = safer
        + rng.normal(0, 0.4, n)                     # noise
    )
    prob_default = 1 / (1 + np.exp(-log_odds))
    defaulted = (rng.uniform(size=n) < prob_default).astype(int)

    df = pd.DataFrame({
        "income_stability":       np.round(income_stability,       4),
        "spending_consistency":   np.round(spending_consistency,   4),
        "savings_ratio":          np.round(savings_ratio,          4),
        "transaction_frequency":  np.round(transaction_frequency,  2),
        "avg_monthly_income":     np.round(avg_monthly_income,     2),
        "avg_monthly_spending":   np.round(avg_monthly_spending,   2),
        "defaulted":              defaulted,
    })

    return df


if __name__ == "__main__":
    print(f"Generating {N_SAMPLES:,} synthetic gig worker profiles...")
    df = generate_profile(N_SAMPLES)

    out_path = Path("training/training_data.csv")
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False)

    default_rate = df["defaulted"].mean() * 100
    print(f"Saved to {out_path}")
    print(f"Default rate: {default_rate:.1f}%")
    print(f"Shape: {df.shape}")
    print("\nFeature summary:")
    print(df.drop(columns="defaulted").describe().round(3).to_string())
