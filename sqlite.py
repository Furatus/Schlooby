import sys
import asyncio
import os
import sqlite3 as sqlite

def insert_keepalive_sqlite(userid, starttime, endtime):
    conn = sqlite.connect("schlooby.db")
    c = conn.cursor()
    c.execute(f"INSERT INTO keepalives VALUES ({userid},{starttime},{endtime})")
    conn.commit()
    conn.close()