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

proyectos = {}
formulario_estado = {}

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")

@bot.command()
async def proyecto(ctx):
    await ctx.message.delete()
    formulario_estado[ctx.author.id] = {'estado': 'titulo'}
    await ctx.send("✏️ ¿Cuál es el **título** de tu proyecto?")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot:
        return

    user_id = message.author.id
    if user_id not in formulario_estado:
        return

    estado = formulario_estado[user_id]['estado']

    if estado == 'titulo':
        formulario_estado[user_id]['titulo'] = message.content
        formulario_estado[user_id]['estado'] = 'descripcion'
        await message.channel.send("📝 ¿Cuál es la **descripción** de tu proyecto?")

    elif estado == 'descripcion':
        formulario_estado[user_id]['descripcion'] = message.content
        formulario_estado[user_id]['estado'] = 'tecnologias'
        await message.channel.send("⚙️ ¿Qué **tecnologías** utilizaste?")

    elif estado == 'tecnologias':
        formulario_estado[user_id]['tecnologias'] = message.content
        formulario_estado[user_id]['estado'] = 'enlace'
        await message.channel.send("🔗 ¿Cuál es el **enlace** a tu proyecto?")

    elif estado == 'enlace':
        formulario_estado[user_id]['enlace'] = message.content
        datos = formulario_estado.pop(user_id)

        titulo = datos['titulo']
        descripcion = datos['descripcion']
        tecnologias = datos['tecnologias']
        enlace = datos['enlace']

        imagen = (
            f"https://api.apiflash.com/v1/urltoimage"
            f"?access_key={API_KEY}"
            f"&url={enlace}"
            f"&wait_until=page_loaded"
            f"&delay=4"
            f"&format=jpeg"
        )

        embed = discord.Embed(
            title=f"🚀 {titulo}",
            description=f"💡 {descripcion}\n🛠️ {tecnologias}\n🔗 [Ver proyecto]({enlace})",
            color=0x00b7ff
        )
        embed.set_footer(text=f"Publicado por {message.author}")
        embed.set_image(url=imagen)

        mensaje_enviado = await message.channel.send(embed=embed)
        await mensaje_enviado.add_reaction("👍")
        await mensaje_enviado.add_reaction("🔥")
        proyectos[user_id] = mensaje_enviado

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
            "**Comienza escribiendo:** `!proyecto`\n"
            "Te guiaré paso a paso para completar la publicación.\n\n"
            "**Comandos adicionales:**\n"
            "🔁 `!editar Título|Descripción|Tecnologías|Enlace` para modificar tu proyecto.\n"
            "🗑️ `!borrar` para eliminar tu proyecto.\n\n"
            "⚠️ Usa `|` como separador solo para `!editar`.\n"
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
