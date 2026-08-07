import requests
import sys
import asyncio
import os

async def get_players_from_game_server():
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}/players"
        headers = {
            "Authorization": os.getenv('GAMESERVER_API_BASIC_AUTH')
        }

        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            return r.json()  # Assuming the response is in JSON format
        else:
            print(f"Failed to fetch players. Status code: {r.status_code}, Response: {r.text}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching players: {e}")
        return None

async def save_game_server():
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}/save"
        headers = {
            "Authorization": os.getenv('GAMESERVER_API_BASIC_AUTH')
        }

        r = requests.post(url, headers=headers)

        if r.status_code == 200:
            return True
        else:
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while saving: {e}")
        return False

async def info_game_server():
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}/info"
        headers = {
            "Authorization": os.getenv('GAMESERVER_API_BASIC_AUTH')
        }
    
        r = requests.get(url, headers=headers)
    
        if r.status_code == 200:
            return r.json()  # Assuming the response is in JSON format
        else:
            print(f"Failed to fetch Server Data. Status code: {r.status_code}, Response: {r.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while saving: {e}")
        return False

async def metrics_game_server():
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}/metrics"
        headers = {
            "Authorization": os.getenv('GAMESERVER_API_BASIC_AUTH')
        }
    
        r = requests.get(url, headers=headers)
    
        if r.status_code == 200:
            return r.json()  # Assuming the response is in JSON format
        else:
            print(f"Failed to fetch Server Data. Status code: {r.status_code}, Response: {r.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while saving: {e}")
        return False

async def shutdown_game_server(waittime, message):
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}/shutdown"
        headers = {
            "Authorization": os.getenv('GAMESERVER_API_BASIC_AUTH')
        }
        payload = {
            "waittime": waittime,
            "message": message
        }

        r = requests.post(url, headers=headers, json=payload)

        if r.status_code == 200:
            return True
        else:
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while saving: {e}")
        return False

async def announce_game_server(message):
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}/announce"
        headers = {
            "Authorization": os.getenv('GAMESERVER_API_BASIC_AUTH')
        }
        payload = {
            "message": message
        }

        r = requests.post(url, headers=headers, json=payload)

        if r.status_code == 200:
            return True
        else:
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while saving: {e}")
        return False

async def health_game_server():
    try:
        url = f"{os.getenv('GAMESERVER_API_URL')}"
    
        r = requests.get(url)
    
        if r.status_code:
            return True
        else:
            return False
            
    except requests.exceptions.RequestException as e:
        return False

