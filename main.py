import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv
import aiohttp
import json
from datetime import datetime
from commands import register_commands 

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

keep_alive()

API_KEY = "0d84e9f68e344ecb814a4d752f19e3ab"
proyectos = {}

async def obtener_imagen_valida(enlace):
    url_imagen = (
        f"https://api.apiflash.com/v1/urltoimage"
        f"?access_key={API_KEY}"
        f"&url={enlace}"
        f"&wait_until=page_loaded"
        f"&delay=4"
        f"&format=jpeg"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_imagen) as resp:
                if resp.status == 200:
                    return url_imagen
    except:
        pass

    fallback = (
        f"https://api.apiflash.com/v1/urltoimage"
        f"?access_key={API_KEY}"
        f"&url=https://github.com"
        f"&wait_until=page_loaded"
        f"&delay=4"
        f"&format=jpeg"
    )
    return fallback

@bot.command(name="ayuda")
async def mostrar_ayuda(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📌 Cómo publicar tu proyecto en el showroom",
        description=(
            "**Usa `/proyecto` para abrir un formulario que te guíe en el proceso.\n\n"
            "**Resultado:**\n"
            "> =>  Mi App\n"
            "> 💡Gestor de tareas\n"
            "> 🖠️ React, Node.js\n"
            "> 🔗 Ver proyecto\n"
            "> 👤 Publicado por el autor\n\n"
            "**Comandos adicionales:**\n"
            "↪️ `/editar` para modificar tu último proyecto.\n"
            "🗑️ `/borrar` para eliminar tu último proyecto.\n\n"
            "🖼️ La imagen se genera automáticamente desde la URL del proyecto."
        ),
        color=0x3498db
    )
    await ctx.send(embed=embed)

@bot.event
async def on_guild_join(guild):
    data = {
        "nombre": guild.name,
        "id": guild.id,
        "owner_id": guild.owner_id,
        "fecha": datetime.utcnow().isoformat()
    }

    try:
        with open("servers.json", "r") as f:
            servidores = json.load(f)
    except FileNotFoundError:
        servidores = []

    if not any(s["id"] == guild.id for s in servidores):
        servidores.append(data)
        with open("servers.json", "w") as f:
            json.dump(servidores, f, indent=4)
        print(f"🟢 Registrado: {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    print(f"🔴 El bot ha sido eliminado del servidor: {guild.name} (ID: {guild.id})")
    try:
        with open("servers.json", "r") as f:
            servidores = json.load(f)
    except FileNotFoundError:
        servidores = []

    servidores = [s for s in servidores if s["id"] != guild.id]

    with open("servers.json", "w") as f:
        json.dump(servidores, f, indent=4)
    print(f"🗑️ Eliminado del registro: {guild.name} (ID: {guild.id})")

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')

    try:
        with open("servers.json", "r") as f:
            servidores = json.load(f)
    except FileNotFoundError:
        servidores = []

    nuevos = 0
    for guild in bot.guilds:
        if not any(s["id"] == guild.id for s in servidores):
            servidores.append({
                "nombre": guild.name,
                "id": guild.id,
                "owner_id": guild.owner_id,
                "fecha": datetime.utcnow().isoformat()
            })
            nuevos += 1

    if nuevos > 0:
        with open("servers.json", "w") as f:
            json.dump(servidores, f, indent=4)
        print(f"🗂️ Se añadieron {nuevos} servidores al log.")

    for guild in bot.guilds:
        try:
            synced = await bot.tree.sync()
            print(f"🔁 Comandos globales sincronizados: {len(synced)}")
        except Exception as e:
            print(f"❌ Error al sincronizar comandos globales: {e}")
register_commands(bot)  

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("❌ No se encontró DISCORD_TOKEN en el archivo .env")

bot.run(token)