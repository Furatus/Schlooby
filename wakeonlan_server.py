import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import wakeonlan
import sys
import asyncio
import os


async def wake_server():
    try :
        wakeonlan.wake(os.getenv('SERVER_MAC_ADDRESS'))
        return True

    except Exception as e:
        print(f"Error sending Wake-on-LAN packet: {e}")
        return False

async def ping(host): # Found on StackOverflow from ePi272314 and Benjamin L.
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['fping', param, '1', '-t', '300', host]

    return subprocess.call(command) == 0