from app.backend.db import Async_Session

async def get_db():
    async with Async_Session() as session:
        yield session  # session будет закрыта автоматически