import sys
import asyncio
import os
import sqlite3 as sqlite
import glob
import calendar
import time


async def init_db():
    """Inits the sqlite file, database and tables if not existing"""

    if os.path.exists(os.getenv('SQLITE_DB_FILE')) == False :
        with open(os.getenv('SQLITE_DB_FILE'), 'w') as fp:
            pass

    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS serverstatus (server_id BIGINT PRIMARY KEY, game TEXT, first_empty_time BIGINT, first_down_time BIGINT, message_id BIGINT);")
    conn.commit()

    c.execute(f"CREATE TABLE IF NOT EXISTS keepalives(user_id BIGINT, starttime BIGINT, endtime BIGINT);")
    conn.commit()

    conn.close()

async def insert_keepalive(userid, starttime, endtime):
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
    c.execute(f"INSERT INTO keepalives VALUES ({userid},{starttime},{endtime})")
    conn.commit()
    conn.close()

async def check_first_empty_time():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()

    c.execute(f"SELECT first_empty_time FROM serverstatus WHERE game = '{os.getenv('GAME')}'")
    output = c.fetchone()

    conn.commit()
    conn.close()

    return output[0]

async def insert_first_empty_time():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()

    current_timestamp = calendar.timegm(time.gmtime())

    c.execute(f"UPDATE serverstatus SET first_empty_time = {current_timestamp} WHERE game = '{os.getenv('GAME')}'")


    conn.commit()
    conn.close()

async def check_first_down_time():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()

    c.execute(f"SELECT first_down_time FROM serverstatus WHERE game = '{os.getenv('GAME')}'")
    output = c.fetchone()

    conn.commit()
    conn.close()

    return output[0]

async def insert_first_down_time():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()

    current_timestamp = calendar.timegm(time.gmtime())

    c.execute(f"UPDATE serverstatus SET first_down_time = {current_timestamp} WHERE game = '{os.getenv('GAME')}'")

    conn.commit()
    conn.close()

async def clear_times():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()

    c.execute(f"UPDATE serverstatus SET first_empty_time = NULL, first_down_time = NULL WHERE game = '{os.getenv('GAME')}'")

    conn.commit()

    conn.close()

async def get_current_keepalive_count():

    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()

    current_timestamp = calendar.timegm(time.gmtime())
    
    c.execute(f"SELECT COUNT(*) FROM keepalives WHERE starttime <= {current_timestamp} AND endtime >= {current_timestamp}")
    count = c.fetchone()
    
    conn.commit()
    conn.close()
    
    return count[0]


async def remove_my_keepalives(userid):

    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
            
    c.execute(f"DELETE FROM keepalives WHERE user_id = {userid}")
            
    conn.commit()
            
    conn.close()

async def remove_all_keepalives():

    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
                
    c.execute(f"DELETE FROM keepalives WHERE user_id != 0")
                
    conn.commit()
                
    conn.close()

async def get_message_id():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
    
    c.execute(f"SELECT message_id FROM serverstatus WHERE game = '{os.getenv('GAME')}'")
    output = c.fetchone()
    
    
    conn.commit()
    conn.close()
    
    return output[0]

async def insert_message_id(messageid):
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
    
    c.execute(f"UPDATE serverstatus SET message_id = {messageid} WHERE game = '{os.getenv('GAME')}'")
    
    conn.commit()
    conn.close()

async def clear_message_id():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
        
    c.execute(f"UPDATE serverstatus SET message_id = NULL WHERE game = '{os.getenv('GAME')}'")
        
    conn.commit()
    conn.close()

async def clear_first_empty_time():
    conn = sqlite.connect(os.getenv('SQLITE_DB_FILE'))
    c = conn.cursor()
            
    c.execute(f"UPDATE serverstatus SET first_empty_time = NULL WHERE game = '{os.getenv('GAME')}'")
            
    conn.commit()
    conn.close()