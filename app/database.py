"""
database.py
-----------
Provides a unified async database interface.

Strategy:
  - If DATABASE_URL is set in config, connect to PostgreSQL via `databases`.
  - Otherwise fall back to the in-memory store transparently.

All route code interacts only with the `db` object exported at the bottom,
so swapping storage backends requires zero changes outside this file.
"""

from app.config import get_settings
from storage.memory_store import MemoryStore

settings = get_settings()

# ---------------------------------------------------------------------------
# PostgreSQL path (requires DATABASE_URL in env)
# ---------------------------------------------------------------------------
_postgres_available = False
database = None  # databases.Database instance when PG is active

if settings.database_url:
    try:
        import databases
        import sqlalchemy

        database = databases.Database(settings.database_url)

        metadata = sqlalchemy.MetaData()

        transactions_table = sqlalchemy.Table(
            "transactions",
            metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column("user_id", sqlalchemy.String, nullable=False),
            sqlalchemy.Column("amount", sqlalchemy.Float, nullable=False),
            sqlalchemy.Column("type", sqlalchemy.String, nullable=False),
            sqlalchemy.Column("date", sqlalchemy.String, nullable=False),
        )

        engine = sqlalchemy.create_engine(settings.database_url)

        async def startup_db():
            metadata.create_all(engine)
            await database.connect()

        async def shutdown_db():
            await database.disconnect()

        async def save_transactions(user_id: str, transactions: list[dict]):
            """Persist a list of transaction dicts to PostgreSQL."""
            query = transactions_table.insert()
            rows = [{"user_id": user_id, **t} for t in transactions]
            await database.execute_many(query=query, values=rows)

        async def load_transactions(user_id: str) -> list[dict]:
            """Fetch all transactions for a user from PostgreSQL."""
            query = transactions_table.select().where(
                transactions_table.c.user_id == user_id
            )
            rows = await database.fetch_all(query)
            return [dict(r) for r in rows]

        _postgres_available = True

    except Exception as e:
        print(f"[TrustLayer] PostgreSQL unavailable ({e}). Using in-memory store.")


# ---------------------------------------------------------------------------
# In-memory fallback path
# ---------------------------------------------------------------------------
_memory_store = MemoryStore()


if not _postgres_available:
    # Stub lifecycle hooks so main.py can call them unconditionally
    async def startup_db():
        pass

    async def shutdown_db():
        pass

    async def save_transactions(user_id: str, transactions: list[dict]):
        _memory_store.save_transactions(user_id, transactions)

    async def load_transactions(user_id: str) -> list[dict]:
        return _memory_store.load_transactions(user_id)
