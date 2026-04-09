"""
routes/simulation.py
--------------------
POST /simulate
Applies hypothetical behavioral changes to a user's transaction history
and returns a simulated Trust Score — without modifying stored data.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_api_key
from app.database import load_transactions
from models.transaction_model import SimulationRequest
from models.response_model import SimulationResponse
from services.simulation_engine import simulate_score

router = APIRouter()


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Simulate Trust Score under hypothetical behavioral changes",
)
async def simulate(
    payload: SimulationRequest,
    _: str = Depends(verify_api_key),
):
    """
    Simulate the impact of behavioral changes on a user's Trust Score.

    Supported parameters:
    - **increase_savings**: Add this amount (INR) as extra monthly income/savings.
    - **reduce_spending_percent**: Reduce all monthly debit amounts by this percentage.

    Changes are NOT persisted. The response includes the original score and delta.
    """
    transactions = await load_transactions(payload.user_id)

    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No transaction history found for user '{payload.user_id}'. "
                   "Upload transactions first via POST /upload-transactions.",
        )

    result = simulate_score(transactions, payload)
    return result
