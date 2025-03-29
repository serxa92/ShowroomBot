import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

keep_alive()

API_KEY = "0d84e9f68e344ecb814a4d752f19e3ab"

proyectos = {}

class ProyectoModal(discord.ui.Modal, title="📌 Publicar Proyecto"):
    titulo = discord.ui.TextInput(label="Título del proyecto", placeholder="Mi increíble app", max_length=100)
    descripcion = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.paragraph, max_length=300)
    tecnologias = discord.ui.TextInput(label="Tecnologías usadas", placeholder="Python, React, etc.")
    enlace = discord.ui.TextInput(label="Enlace del proyecto", placeholder="https://github.com/usuario/proyecto")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"🚀 {self.titulo}",
            description=f"💡 {self.descripcion}\n🛠️ {self.tecnologias}\n🔗 [Ver proyecto]({self.enlace})",
            color=0x00b7ff
        )
        embed.set_footer(text=f"Publicado por {interaction.user}")

        imagen = (
            f"https://api.apiflash.com/v1/urltoimage"
            f"?access_key={API_KEY}"
            f"&url={self.enlace}"
            f"&wait_until=page_loaded"
            f"&delay=4"
            f"&format=jpeg"
        )
        embed.set_image(url=imagen)

        mensaje = await interaction.channel.send(embed=embed)
        await mensaje.add_reaction("👍")
        await mensaje.add_reaction("🔥")
        proyectos[interaction.user.id] = mensaje
        await interaction.response.send_message("✅ Proyecto publicado correctamente.", ephemeral=True)

@tree.command(name="proyecto", description="Publica un proyecto en el showroom")
async def slash_proyecto(interaction: discord.Interaction):
    await interaction.response.send_modal(ProyectoModal())

@bot.command(name="editar")
async def editar_proyecto(ctx, *, mensaje):
    await ctx.message.delete()
    if ctx.author.id not in proyectos:
        await ctx.send("❌ No tienes ningún proyecto publicado para editar.")
        return

    partes = [x.strip() for x in mensaje.split("|")]
    if len(partes) < 4:
        await ctx.send("❌ Usa el formato: `!editar Título|Descripción|Tecnologías|Enlace`")
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

    nuevo_embed = discord.Embed(
        title=f"🚀 {titulo}",
        description=f"💡 {descripcion}\n🛠️ {tecnologias}\n🔗 [Ver proyecto]({enlace})",
        color=0x00b7ff
    )
    nuevo_embed.set_footer(text=f"Publicado por {ctx.author}")
    nuevo_embed.set_image(url=imagen)

    try:
        mensaje_original = proyectos[ctx.author.id]
        await mensaje_original.edit(embed=nuevo_embed)
    except Exception as e:
        await ctx.send("❌ No se pudo editar el mensaje. Puede que haya sido eliminado.")

@bot.command(name="borrar")
async def borrar_proyecto(ctx):
    await ctx.message.delete()
    if ctx.author.id not in proyectos:
        await ctx.send("❌ No tienes ningún proyecto publicado para borrar.")
        return

    try:
        mensaje_original = proyectos[ctx.author.id]
        await mensaje_original.delete()
        del proyectos[ctx.author.id]
        await ctx.send("🗑️ Proyecto borrado correctamente.")
    except Exception as e:
        await ctx.send("❌ No se pudo borrar el mensaje. Puede que ya no exista.")

@bot.command(name="ayuda")
async def mostrar_ayuda(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="📌 Cómo publicar tu proyecto en el showroom",
        description=(
            "**Comando nuevo:** Usa `/proyecto` para abrir un formulario moderno.\n\n"
            "**Comandos adicionales:**\n"
            "🔁 `!editar Título|Descripción|Tecnologías|Enlace` para modificar tu proyecto.\n"
            "🗑️ `!borrar` para eliminar tu proyecto.\n\n"
            "🖼️ La imagen se genera automáticamente desde la URL del proyecto."
        ),
        color=0x3498db
    )
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
if token is None:
    raise ValueError("❌ No se encontró DISCORD_TOKEN en el archivo .env")

bot.run(token)
