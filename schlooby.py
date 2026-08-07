import discord
from discord.ext import commands
from discord import app_commands
import sys
import os
import asyncio
import gameserver
from env import load_env
from enum import Enum
import datetime
from ConfirmShutdownView import ConfirmShutdownView
from IgnoreHealthView import IgnoreHealthView
import ssh_docker
import wakeonlan_server

load_env()
guild_id = int(os.getenv('GUILD_ID'))
discord_guild = discord.Object(guild_id)

class MyClient(discord.Client):
    # Suppress error on the User attribute being None since it fills up later
    user: discord.ClientUser

    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=discord_guild)
        await self.tree.sync(guild=discord_guild)


client = MyClient()

@client.tree.command(name="announce")
@app_commands.describe(message="Message to be sent in the gameserver")
async def announce(interaction: discord.Interaction, message: str = ""):
    """Envoie un message global dans le serveur de jeu"""
    if message == None or message == "" : 
        await interaction.response.send_message("Le message ne peut pas être vide ! Demande annulée.")
        return

    await interaction.response.defer()  # réserve plus de temps
    
    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    alive = await gameserver.health_game_server()
    
    if alive == False :
        await msg.edit(content="Le serveur ne répond pas ou est fermé. considérez la commande `/start` ou `/restart` pour résoudre le problème ?")
        await msg.clear_reaction("⌛")
        await msg.add_reaction("⚠️")
        return

    await gameserver.announce_game_server(message)

    await msg.edit(content=f"Message envoyé : {message}")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="listplayers")
async def list_players(interaction : discord.Interaction) :
    """Liste tous les joueurs actuellement connectés sur le serveur de jeu"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    alive = await gameserver.health_game_server()
    
    if alive == False :
        await msg.edit(content="Le serveur ne répond pas ou est fermé. considérez la commande `/start` ou `/restart` pour résoudre le problème ?")
        await msg.clear_reaction("⌛")
        await msg.add_reaction("⚠️")
        return

    players = await gameserver.get_players_from_game_server()['players']

    playeramount = len(players)

    if playeramount > 25 : 
        overflow = playeramount - 24
        players = players[0:23]

    embed = discord.Embed(title="Liste des Joueurs actuellement connectés sur le serveur")

    if playeramount == 0 :
        embed.add_field(name="Aucun joueur connecté !", value="")

    for player in players :
        embed.add_field(name=f"{player['name']}", value=f"id : {player['accountName']} | ping : {round(player['ping'])}")
    embed.set_footer(text=f"{playeramount} Joueur(s) Connectés")

    await msg.edit(content="",embed=embed)
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="save")
async def save(interaction : discord.Interaction) :
    """Force la sauvegarde du monde sur le serveur"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    alive = await gameserver.health_game_server()
    
    if alive == False :
        await msg.edit(content="Le serveur ne répond pas ou est fermé. considérez la commande `/start` ou `/restart` pour résoudre le problème ?")
        await msg.clear_reaction("⌛")
        await msg.add_reaction("⚠️")
        return

    await gameserver.save_game_server()

    await msg.edit(content="Partie sauvegardée !")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="info")
async def server_info(interaction : discord.Interaction) :
    """Affiche les informations générales du serveur de jeu"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    alive = await gameserver.health_game_server()

    if alive == False :
        await msg.edit(content="Le serveur ne répond pas ou est fermé. considérez la commande `/start` ou `/restart` pour résoudre le problème ?")
        await msg.clear_reaction("⌛")
        await msg.add_reaction("⚠️")
        return

    server_info = await gameserver.info_game_server()

    embed = discord.Embed(title="Informations du serveur")

    embed.add_field(name="Nom du serveur", value=f"{server_info['servername']}")
    embed.add_field(name="Description", value=f"{server_info['description']}")
    embed.add_field(name="GUID du monde", value=f"{server_info['worldguid']}")

    embed.set_footer(text=f"Version du serveur : {server_info['version']}")

    await msg.edit(content="",embed=embed)
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

class statustype(Enum) :
    gameserver = 0
    container = 1
    host = 2
    schlooby = 3

@client.tree.command(name="status")
@app_commands.describe(type= "Catégorie/type du serveur duquel afficher l'état")
async def status(interaction : discord.Interaction, type : statustype) :
    """Affiche le statut du service choisi (en fonction du type)"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    match type.value:
        case 0:
            alive = await gameserver.health_game_server()

            if alive == False :
                await msg.edit(content="Le serveur ne répond pas ou est fermé. considérez la commande `/start` ou `/restart` pour résoudre le problème ?")
                await msg.clear_reaction("⌛")
                await msg.add_reaction("⚠️")
                return

            server_info = await gameserver.metrics_game_server()

            embed = discord.Embed(title="État du serveur")

            embed.add_field(name="FPS Serveur | Temps de cycle", value=f"{server_info['serverfps']} fps | {round(server_info['serverframetime'])} ms")
            embed.add_field(name="Nombre de joueurs / Capacité maximale", value=f"{server_info['currentplayernum']}/{server_info['maxplayernum']}")
            embed.add_field(name="Temps de fonctionnement", value=f"{str(datetime.timedelta(seconds=int(server_info['uptime'])))} (hh:mm:ss)")
            embed.add_field(name="Nombre de bases", value=f"{server_info['basecampnum']}")
            embed.add_field(name="Jours écoulés (en jeu)", value=f"{server_info['days']}")

            await msg.edit(content="",embed=embed)
            await msg.clear_reaction("⌛")
            await msg.add_reaction("✅")

        case 1:
            await msg.edit(content='Pas encore implémenté')
            await msg.clear_reaction("⌛")

        case 2:
            await msg.edit(content='Pas encore implémenté')
            await msg.clear_reaction("⌛")

        case 3:
            embed = discord.Embed(title="État de Schlooby", description=" Statut : En ligne")
            
            embed.add_field(name="Description", value=f"Bonjour 👋, je suis Schlooby (Schloobs pour les intimes) ! \n J'aide mon créateur à piloter des serveurs de jeu :) \n\n Un bug ? une question ? Je ne fonctionne pas correctement ? \n Contactez mon développeur <@270595136466059264>, il pourra sûrement vous aider. \n Vous pouvez aussi trouver mon code source sur github : https://github.com/Furatus/Schlooby")

            embed.set_footer(text=f"Version {os.getenv('SCHLOOBY_VERSION')}")

            await msg.edit(content="",embed=embed)
            await msg.clear_reaction("⌛")

        case _:
            await msg.edit(content='Type Inconnu, utilisez le sélecteur de type')
            await msg.clear_reaction("⌛")
            await msg.add_reaction("⚠️")

@client.tree.command(name="delayedstop")
@app_commands.describe(delai="temps en secondes avant la fermeture du serveur (entre 30 secondes et 20 minutes)")
@app_commands.describe(message="Message à envoyer aux personnes sur le serveur")
async def delayedstop(interaction : discord.Interaction, delai: app_commands.Range[int,30,1200], message: str = "") :
    """Arrêter le serveur de jeu (depuis le serveur, pas le conteneur)"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    alive = await gameserver.health_game_server()

    if alive == False :
        await msg.edit(content="Le serveur ne répond pas ou est fermé.")
        await msg.clear_reaction("⌛")
        await msg.add_reaction("⚠️")
        return

    players = await gameserver.get_players_from_game_server()['players']
    
    playeramount = len(players)

    if playeramount != 0:
        embed = discord.Embed(
            title=f"⚠️ Attention, il y a encore {playeramount} joueur(s) sur le serveur",
            description="Confirmer l'extinction ?"
        )
        view = ConfirmShutdownView()

        await msg.edit(embed=embed, view=view)

        # attendre que l'utilisateur clique (ou que ça timeout)
        await view.wait()

        if view.value ==  False:
            return
        

    await gameserver.shutdown_game_server(delai, f"Attention, fermeture du serveur dans : {str(datetime.timedelta(seconds=int(delai)))}, message : {message}")

    await msg.edit(content=f"Fermeture envoyée au serveur. Le serveur fermera dans {delai} secondes")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="stop")
async def stop(interaction : discord.Interaction) :
    """Arrêter le serveur de jeu (conteneur)"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))

    if ping == False :
            await msg.edit(content="Le serveur ne répond pas au ping. Impossible d'arrêter le conteneur. Considérez la commande `/start` ou `/hostwakeup` pour démarrer le serveur ou la machine.")
            return

    alive = await ssh_docker.health_container_docker()

    if alive == False :
        ignore_view = IgnoreHealthView()

        await msg.edit(content="Le conteneur ne répond pas ou est fermé. Continuer quand même ?", view=ignore_view)
        await msg.clear_reaction("⌛")

        await ignore_view.wait()

        ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))

        if ping == False :
            msg.edit(content="Le serveur ne répond pas au ping. Impossible d'arrêter.")
            return

        if ignore_view.value == False:
            return

    if alive == True:
        players = await gameserver.get_players_from_game_server()['players']
    
        playeramount = len(players)

        if playeramount != 0:
            embed = discord.Embed(
                title=f"⚠️ Attention, il y a encore {playeramount} joueur(s) sur le serveur",
                description="Confirmer l'extinction ?"
            )
            shutdown_view = ConfirmShutdownView()

            await msg.edit(embed=embed, view=shutdown_view)

            # attendre que l'utilisateur clique (ou que ça timeout)
            await shutdown_view.wait()

            if shutdown_view.value ==  False:
                return
        

    await ssh_docker.stop_container_docker()

    await msg.edit(content=f"Le serveur a été éteint.")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

class logstype(Enum) :
    gameserver = 0
    schlooby = 1

@client.tree.command(name="logs")
@app_commands.describe(type= "Affiche les journeaux du type choisi")
async def logs(interaction : discord.Interaction, type : logstype) :
    """Affiche le statut du service choisi (en fonction du type)"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    match type.value:
        case 0:
            ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))

            if ping == False :
                await msg.edit(content="Le serveur ne répond pas au ping. Considérez la commande `/start` pour démarrer le serveur")
                return
        
            alive = await ssh_docker.health_container_docker()

            if alive == False :
                await msg.edit(content="Le conteneur ne répond pas ou est fermé. considérez la commande `/start`")
                await msg.clear_reaction("⌛")
                await msg.add_reaction("⚠️")
                return

            logs = await ssh_docker.logs_container_docker().decode('unicode-escape')
            lastest_logs = logs[-1800:] if len(logs) > 1800 else logs

            await msg.edit(content=f"### Logs brutes du serveur \n``` {lastest_logs} ```")
            await msg.clear_reaction("⌛")
            await msg.add_reaction("✅")

        case 1:
            await msg.edit(content='Pas encore implémenté')
            await msg.clear_reaction("⌛")

        case _:
            await msg.edit(content='Type Inconnu, utilisez le sélecteur de type')
            await msg.clear_reaction("⌛")
            await msg.add_reaction("⚠️")

@client.tree.command(name="restart")
async def restart(interaction : discord.Interaction) :
    """Redémarrer le serveur de jeu (conteneur)"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))

    if ping == False :
            await msg.edit(content="Le serveur ne répond pas au ping. Impossible de redémarrer le conteneur. Considérez la commande `/start` pour démarrer le serveur")
            await msg.clear_reaction("⌛")
            return

    alive = await ssh_docker.health_container_docker()

    if alive == False :
        await msg.edit(content="Le conteneur ne répond pas ou est fermé. \n Impossible de redémarrer. Essayez la commande /stop puis /start")
        await msg.clear_reaction("⌛")
        return

    if alive == True:
        players = await gameserver.get_players_from_game_server()['players']
    
        playeramount = len(players)

        if playeramount != 0:
            embed = discord.Embed(
                title=f"⚠️ Attention, il y a encore {playeramount} joueur(s) sur le serveur",
                description="Confirmer le redémarrage ?"
            )
            shutdown_view = ConfirmShutdownView()

            await msg.edit(embed=embed, view=shutdown_view)

            # attendre que l'utilisateur clique (ou que ça timeout)
            await shutdown_view.wait()

            if shutdown_view.value ==  False:
                return
        

    await ssh_docker.restart_container_docker()

    await msg.edit(content=f"Le serveur a été redémarré.")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="hostsleep")
async def hostleep(interaction : discord.Interaction) :
    """Mise en veille de la machine"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))

    if ping == False :
            await msg.edit(content="Le serveur ne répond pas au ping. Impossible de mettre en veille, probalement déjà éteinte.")
            await msg.clear_reaction("⌛")
            return

    server_alive = await ssh_docker.health_container_docker()

    if server_alive == True:
        players = await gameserver.get_players_from_game_server()['players']
    
        playeramount = len(players)

        if playeramount == None : playeramount = 0

        embed = discord.Embed(
            title=f"⚠️ Attention le serveur est encore allumé et il y a encore {playeramount} joueur(s) sur le serveur",
            description="Il faut impérativement éteindre le serveur pour mettre l'ordinateur en veille. Confirmer la mise en veille ?"
        )
        shutdown_view = ConfirmShutdownView()

        await msg.edit(embed=embed, view=shutdown_view)

        # attendre que l'utilisateur clique (ou que ça timeout)
        await shutdown_view.wait()

        if shutdown_view.value ==  False:
            return

        await ssh_docker.stop_container_docker()

    await ssh_docker.sleep_server()

    await msg.edit(content=f"La machine a été mise en veille.")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="hostwakeup")
async def hostwakeup(interaction : discord.Interaction) :
    """Envoie un signal de réveil à la machine (en veille ou éteinte)."""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))
        
    if ping == True :
        await msg.edit(content="Le serveur est déjà allumé. il n'est pas nécessaire d'envoyer un paquet.")
        return

    await wakeonlan_server.wake_server()

    await msg.edit(content=f"Signal envoyé")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="hostreboot")
async def hostreboot(interaction : discord.Interaction) :
    """Redémarre la machine"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))

    if ping == False :
            await msg.edit(content="Le serveur ne répond pas au ping. Impossible de redémarrer la machine, probalement éteinte.")
            await msg.clear_reaction("⌛")
            return

    server_alive = await ssh_docker.health_container_docker()

    if server_alive == True:
        players = await gameserver.get_players_from_game_server()['players']
    
        playeramount = len(players)

        embed = discord.Embed(
            title=f"⚠️ Attention le serveur est encore allumé et il y a encore {playeramount} joueur(s) sur le serveur",
            description="Il faut impérativement éteindre le serveur pour arrêter l'ordinateur. Confirmer l'extinction ?"
        )
        shutdown_view = ConfirmShutdownView()

        await msg.edit(embed=embed, view=shutdown_view)

        # attendre que l'utilisateur clique (ou que ça timeout)
        await shutdown_view.wait()

        if shutdown_view.value ==  False:
            return

        await ssh_docker.stop_container_docker()

    await ssh_docker.reboot_server()

    await msg.edit(content=f"La machine a été redémarrée.")
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")


@client.tree.command(name="connect")
async def connect_info(interaction : discord.Interaction) :
    """Affiche les informations de connexion à entrer dans le jeu"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")

    alive = await gameserver.health_game_server()
    embed = discord.Embed(title="Informations de connexion",description=f"Jeu : {os.getenv('CONNECT_GAME')}")

    embed.add_field(name="Adresse du serveur", value=f"{os.getenv('CONNECT_DNS')}")
    embed.add_field(name="Mot de passe, si existant", value=f"{os.getenv('CONNECT_PASSWORD')}")

    if alive == False :
        embed.set_footer(text=f"Attention, le serveur ne répond pas ou est fermé, il sera impossible de rejoindre sans résoudre le problème, ou le démarrer")

    else:
        embed.set_footer(text="Le serveur est en marche, prêt à recevoir la connexion.")
    
    await msg.edit(content="",embed=embed)
    await msg.clear_reaction("⌛")
    await msg.add_reaction("✅")

@client.tree.command(name="start")
async def start(interaction : discord.Interaction) :
    """Démarre le serveur de jeu, et la machine si elle est éteinte"""
    await interaction.response.defer()

    msg = await interaction.followup.send("Traitement en cours, toutes les autres commandes seront IGNORÉES jusqu'à la résolution de celle-ci...", wait=True)
    await msg.add_reaction("⌛")
    
    ping = await wakeonlan_server.ping(os.getenv('SERVER_IP'))
    
    if ping == False :
        await msg.edit(content="L'ordinateur est éteint, Tentative d'allumage")
        await wakeonlan_server.wake_server()
        await msg.edit(content="Signal envoyé, patientez ~3 min pour le démarrage (cela peut demander plus, ou moins de temps)")
        for i in range(0,60,1) :
            alive = await wakeonlan_server.ping(os.getenv('SERVER_IP'))
            if alive == False and i == 60 :
                await msg.edit("Le serveur ne répond pas, ou n'a pas l'air d'avoir démarré. Impossible de démarrer le conteneur ou le serveur de jeu.")
                await msg.clear_reaction("⌛")
                return
            
            if alive == True :
                await msg.edit(content="Réponse reçue du serveur, la séquence va continuer.")
                break

            await asyncio.sleep(10)
            await wakeonlan_server.wake_server()
            await msg.edit(content=f"Ping : Tentative n°{i}/60, 10s attente (maximum 10 minutes, on considère que l'ordinateur n'a pas démarré au delà)...")

        await msg.edit(content="Attente de 30 secondes, le temps que le serveur s'initialise correctement...")
        await asyncio.sleep(30)
    
    alive = await ssh_docker.health_container_docker()

    if alive == False :
        await msg.edit(content="Le conteneur docker n'est pas initialisé. Fermeture par mesure de sûreté, si le compose a mal été fermé...")
        await ssh_docker.stop_container_docker()

        await msg.edit(content="Lancement du conteneur... En cas de mise à jour du serveur, cette étape peut durer jusqu'à ~5 minutes...")
        await ssh_docker.start_container_docker()

    if alive == True :
            await msg.edit(content="Le conteneur est déjà en marche. Si le serveur ne fonctionne plus, ou n'est plus accessible, utiliser la commande `/restart` OU `/stop` puis `/start` à nouveau")
            return
    
    await msg.edit(content="Serveur démarré. Il devrait être accessible sous peu. Vérification de l'état/santé du serveur post démarrage dans 1 minute. (Vous pouvez ignorer)")

    await asyncio.sleep(60)
    gameserver_alive = await gameserver.health_game_server()

    if gameserver_alive == True :
        await msg.edit(content="Serveur démarré, vérification réussie !")

    else :
        await msg.edit(content="Le serveur semble démarré, mais la vérification a échoué. si il n'est pas accessible, utiliser la commande `/restart` OU `/stop` puis `/start` à nouveau")

    await msg.clear_reaction("⌛")    
    await msg.add_reaction("✅")

client.run(os.getenv('DISCORD_BOT_TOKEN'))