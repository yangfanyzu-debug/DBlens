import unittest

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db


class DatabaseSessionFactoryTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_get_db_yields_async_session(self):
        db_gen = get_db()

        session = await anext(db_gen)
        self.assertIsInstance(session, AsyncSession)

        await db_gen.aclose()


if __name__ == "__main__":
    unittest.main()
