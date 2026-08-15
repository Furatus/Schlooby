import sys
import asyncio
import os
from paramiko import SSHClient, MissingHostKeyPolicy, WarningPolicy
import paramiko


async def ssh_client_init():
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(os.getenv('SERVER_IP'),22,os.getenv('SSH_USERNAME'),os.getenv('SSH_PASSWORD'))

    return ssh_client

async def logs_container_docker():

    ssh_client = await ssh_client_init()
    
    stdin, stdout, stderr = ssh_client.exec_command(f"docker logs {os.getenv('CONTAINER_NAME')}")

    output_string = stdout.read()

    ssh_client.close()

    return output_string

async def stop_container_docker():

    ssh_client = await ssh_client_init()

    stdin, stdout, stderr = ssh_client.exec_command(f"cd {os.getenv('COMPOSE_FOLDER')} && docker compose down")

    errlines = stderr.readlines()

    ssh_client.close()

    if len(errlines) == 0 :
        return True
    else :
        return False

async def start_container_docker():

    ssh_client = await ssh_client_init()

    stdin, stdout, stderr = ssh_client.exec_command(f"cd {os.getenv('COMPOSE_FOLDER')} && docker compose up -d")

    errlines = stderr.readlines()

    ssh_client.close()

    if len(errlines) == 0 :
        return True
    else :
        return False

async def restart_container_docker():

    ssh_client = await ssh_client_init()

    stdin, stdout, stderr = ssh_client.exec_command(f"docker restart {os.getenv('CONTAINER_NAME')}")

    errlines = stderr.readlines()

    ssh_client.close()

    if len(errlines) == 0 :
        return True
    else :
        return False

async def health_container_docker():

    ssh_client = await ssh_client_init()
    
    stdin, stdout, stderr = ssh_client.exec_command(f"docker stats --no-stream")

    output_string = stdout.read().decode('unicode-escape')

    ssh_client.close()

    if output_string.find(f"{os.getenv('CONTAINER_NAME')}") != -1 :
        return True
    else :
        return False

async def sleep_server():

    ssh_client = await ssh_client_init()
    
    stdin, stdout, stderr = ssh_client.exec_command("sudo /usr/bin/systemctl suspend")

    print(stderr.readlines())

    ssh_client.close()

    if len(stderr.readlines()) == 0 :
        return True
    else :
        return False

async def shutdown_server():

    ssh_client = await ssh_client_init()
    
    stdin, stdout, stderr = ssh_client.exec_command("sudo /usr/sbin/shutdown now")

    print(stderr.readlines())

    ssh_client.close()

    if len(stderr.readlines()) == 0 :
        return True
    else :
        return False

async def reboot_server():
    ssh_client = await ssh_client_init()
    
    stdin, stdout, stderr = ssh_client.exec_command("sudo /usr/sbin/reboot")

    print(stderr.readlines())

    ssh_client.close()

    if len(stderr.readlines()) == 0 :
        return True
    else :
        return False

async def pull_container_docker():

    ssh_client = await ssh_client_init()
    
    stdin, stdout, stderr = ssh_client.exec_command(f"cd {os.getenv('COMPOSE_FOLDER')} && docker compose pull")
    
    errlines = stderr.readlines()
    
    ssh_client.close()
    
    if len(errlines) == 0 :
        return True
    else :
        return False