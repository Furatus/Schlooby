import discord

class ConfirmShutdownView(discord.ui.View):
    def __init__(self, *, timeout=60):
        super().__init__(timeout=timeout)
        self.value = None  # pour stocker le résultat si besoin ailleurs

    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.edit_message(content="OK, Extinction confirmée, Traitement en cours...", embed=None, view=None)
        self.stop()  # arrête d'écouter les clics sur cette vue

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.edit_message(content="Extinction annulée.", embed=None, view=None)
        self.stop()

    async def on_timeout(self):
        # appelé automatiquement si personne ne clique dans le délai
        self.value = False