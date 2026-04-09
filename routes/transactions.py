"""
routes/transactions.py
----------------------
POST /upload-transactions
Accepts a list of financial transactions and persists them for a given user_id.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import verify_api_key
from app.database import save_transactions
from models.transaction_model import TransactionUploadRequest
from models.response_model import UploadResponse

router = APIRouter()


@router.post(
    "/upload-transactions",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload financial transactions for a user",
)
async def upload_transactions(
    payload: TransactionUploadRequest,
    _: str = Depends(verify_api_key),
):
    """
    Store a batch of transactions for the specified user_id.

    - Transactions are appended to any existing history (not replaced).
    - Requires a valid X-API-KEY header.
    """
    txn_dicts = [t.model_dump() for t in payload.transactions]

    try:
        await save_transactions(payload.user_id, txn_dicts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store transactions: {str(e)}",
        )

    return UploadResponse(
        message="Transactions stored successfully.",
        user_id=payload.user_id,
        transactions_stored=len(txn_dicts),
    )
