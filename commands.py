# commands.py

from discord import app_commands, Interaction
import json

def register_commands(bot):

    @bot.tree.command(name="panel", description="Muestra los servidores registrados por el bot")
    async def mostrar_panel(interaction: Interaction):
        try:
            with open("servers.json", "r") as f:
                servidores = json.load(f)
        except FileNotFoundError:
            servidores = []

        if not servidores:
            await interaction.response.send_message("ℹ️ Aún no hay servidores registrados.", ephemeral=True)
            return

        mensaje = "\n".join([
            f"• {s['nombre']} (ID: {s['id']}) - Owner ID: {s['owner_id']} - {s['fecha'][:10]}"
            for s in servidores
        ])

        if len(mensaje) > 1900:
            mensaje = mensaje[:1900] + "\n... (truncado)"

        await interaction.response.send_message(
            f"📋 Servidores registrados:\n```{mensaje}```",
            ephemeral=True
        )
