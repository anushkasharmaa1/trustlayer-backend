"""
memory_store.py
---------------
Simple in-memory key-value store used when PostgreSQL is unavailable.
Data is lost on server restart — suitable for development and demos.

Thread-safety: uses a plain dict. FastAPI runs in a single async event loop,
so concurrent coroutines are safe. For true multi-threaded use, wrap with asyncio.Lock.
"""

from collections import defaultdict


class MemoryStore:
    """Stores transactions keyed by user_id."""

    def __init__(self):
        # { user_id: [{"amount": ..., "type": ..., "date": ...}, ...] }
        self._store: dict[str, list[dict]] = defaultdict(list)

    def save_transactions(self, user_id: str, transactions: list[dict]) -> None:
        """
        Append transactions for a user.
        Calling this multiple times accumulates history (does not overwrite).
        """
        self._store[user_id].extend(transactions)

    def load_transactions(self, user_id: str) -> list[dict]:
        """Return all stored transactions for a user, or an empty list."""
        return list(self._store.get(user_id, []))

    def clear(self, user_id: str) -> None:
        """Remove all transactions for a user (useful in tests)."""
        self._store.pop(user_id, None)

    def user_exists(self, user_id: str) -> bool:
        return user_id in self._store and len(self._store[user_id]) > 0
