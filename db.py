import aiosqlite

async def run(filename: str, command: str, prepared: iter = ()):
    async with aiosqlite.connect(f"data/{filename}.db") as conn:
        await conn.execute(command, prepared)
        await conn.commit()


async def read(filename: str, command: str, prepared: iter = ()):
    async with aiosqlite.connect(f"data/{filename}.db") as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            cur: aiosqlite.Cursor
            await cur.execute(command, prepared)
            return [dict(x) for x in await cur.fetchall()]