import sys
import asyncio
import os
import sqlite3 as sqlite

async def insert_keepalive_sqlite(userid, starttime, endtime):
    conn = await sqlite.connect("schlooby.db")
    c = conn.cursor()
    await c.execute(f"INSERT INTO keepalives VALUES ({userid},{starttime},{endtime})")
    conn.commit()
    conn.close()