import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv
import aiohttp

intents = discord.Intents.default()
intents.message_content = True

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

    # Imagen por defecto si falla la original
    fallback = (
        f"https://api.apiflash.com/v1/urltoimage"
        f"?access_key={API_KEY}"
        f"&url=https://github.com"
        f"&wait_until=page_loaded"
        f"&delay=4"
        f"&format=jpeg"
    )
    return fallback

class ProyectoModal(discord.ui.Modal, title="📝 Publica tu proyecto"):
    titulo = discord.ui.TextInput(label="Título", placeholder="Nombre del proyecto", max_length=100)
    descripcion = discord.ui.TextInput(label="Descripción", placeholder="¿De qué trata tu proyecto?", style=discord.TextStyle.paragraph)
    tecnologias = discord.ui.TextInput(label="Tecnologías", placeholder="React, Node.js, etc.")
    enlace = discord.ui.TextInput(label="Enlace al proyecto", placeholder="https://...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        autor = interaction.user
        imagen = await obtener_imagen_valida(self.enlace)

        embed = discord.Embed(
            title=f"🚀 {self.titulo}",
            description=f"💡 {self.descripcion}\n🛠️ {self.tecnologias}\n🔗 [Ver proyecto]({self.enlace})",
            color=0x00b7ff
        )
        embed.set_footer(text=f"Publicado por {autor.display_name}")
        embed.set_image(url=imagen)

        mensaje = await interaction.channel.send(embed=embed)
        await mensaje.add_reaction("👍")
        await mensaje.add_reaction("🔥")

        proyectos[autor.id] = mensaje
        await interaction.response.send_message("✅ ¡Proyecto publicado!", ephemeral=True)

class EditarProyectoModal(discord.ui.Modal, title="✏️ Edita tu proyecto"):
    titulo = discord.ui.TextInput(label="Título", max_length=100)
    descripcion = discord.ui.TextInput(label="Descripción", style=discord.TextStyle.paragraph)
    tecnologias = discord.ui.TextInput(label="Tecnologías")
    enlace = discord.ui.TextInput(label="Enlace al proyecto")

    async def on_submit(self, interaction: discord.Interaction):
        autor = interaction.user
        if autor.id not in proyectos:
            await interaction.response.send_message("❌ No tienes ningún proyecto publicado para editar.", ephemeral=True)
            return

        imagen = await obtener_imagen_valida(self.enlace)

        embed = discord.Embed(
            title=f"🚀 {self.titulo}",
            description=f"💡 {self.descripcion}\n🛠️ {self.tecnologias}\n🔗 [Ver proyecto]({self.enlace})",
            color=0x00b7ff
        )
        embed.set_footer(text=f"Publicado por {autor.display_name}")
        embed.set_image(url=imagen)

        mensaje = proyectos[autor.id]
        await mensaje.edit(embed=embed)
        await interaction.response.send_message("✅ Proyecto editado.", ephemeral=True)

@bot.tree.command(name="proyecto", description="Publica un proyecto en el showroom")
async def publicar(interaction: discord.Interaction):
    await interaction.response.send_modal(ProyectoModal())

@bot.tree.command(name="editar", description="Edita tu proyecto publicado")
async def editar(interaction: discord.Interaction):
    await interaction.response.send_modal(EditarProyectoModal())

@bot.tree.command(name="borrar", description="Elimina tu proyecto del showroom")
async def borrar(interaction: discord.Interaction):
    autor = interaction.user
    if autor.id not in proyectos:
        await interaction.response.send_message("❌ No tienes ningún proyecto publicado para borrar.", ephemeral=True)
        return

    mensaje = proyectos[autor.id]
    await mensaje.delete()
    del proyectos[autor.id]
    await interaction.response.send_message("🗑️ Proyecto borrado correctamente.", ephemeral=True)

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
            "> 🛠️ React, Node.js\n"
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
