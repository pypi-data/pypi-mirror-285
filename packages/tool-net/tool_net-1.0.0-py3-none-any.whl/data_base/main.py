import aiomysql
from typing import Optional

db_pool: Optional[aiomysql.Pool] = None

async def init_db_pool(host: str, port: int, user: str, password: str, db: str):
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db,
        autocommit=True
    )

async def close_db_pol():
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()

async def get_db_conn():
    global db_pool
    if db_pool:
       return await db_pool.acquire()
    else:
        raise RuntimeError("Database connection pool is not initialized.")

