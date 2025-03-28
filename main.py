import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

keep_alive()

API_KEY = "0d84e9f68e344ecb814a4d752f19e3ab"

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

@bot.command()
async def proyecto(ctx, *, mensaje):
    await ctx.message.delete()
    partes = [x.strip() for x in mensaje.split("|")]
    if len(partes) < 4:
        await ctx.send("❌ Usa el formato: `!proyecto Título|Descripción|Tecnologías|Enlace`")
        return

    titulo, descripcion, tecnologias, enlace = partes[:4]

    imagen = (
        f"https://api.apiflash.com/v1/urltoimage"
        f"?access_key={API_KEY}"
        f"&url={enlace}"
        f"&wait_until=page_loaded"
        f"&delay=4"
        f"&format=jpeg"
    )

    embed = discord.Embed(
        title=f" {titulo}",
        description=f"💡 {descripcion}\n🛠️ {tecnologias}\n🔗 [Ver proyecto]({enlace})",
        color=0x00b7ff
    )
    embed.set_footer(text=f"Publicado por {ctx.author}")
    embed.set_image(url=imagen)

    await ctx.send(embed=embed)
    await mensaje.add_reaction("👍")
    await mensaje.add_reaction("🔥")

@bot.command(name="ayuda")
async def mostrar_ayuda(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📌 Cómo publicar tu proyecto en el showroom",
        description=(
            "**Usa el comando:**\n"
            "`!proyecto Título|Descripción|Tecnologías|Enlace`\n\n"
            "**Ejemplo:**\n"
            "`!proyecto Mi App|Gestor de tareas|React, Node.js|https://github.com/usuario/app`\n\n"
            "**Resultado:**\n"
            "> 🚀 Mi App\n"
            "> 💡 Gestor de tareas\n"
            "> 🛠️ React, Node.js\n"
            "> 🔗 Ver proyecto\n"
            "> 👤 Publicado por el autor\n\n"
            "⚠️ Asegúrate de usar `|` como separador entre cada parte.\n"
            "🖼️ La imagen se genera automáticamente desde la URL del proyecto."
        ),
        color=0x3498db
    )
    await ctx.send(embed=embed)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("❌ No se encontró DISCORD_TOKEN en el archivo .env")

bot.run(token)
