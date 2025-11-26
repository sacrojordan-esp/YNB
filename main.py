import os
import random
import discord
from discord import app_commands
from discord.ui import View, Select
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- Configuración del bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# --- Variables globales ---
jugadores_lista = []
jugadores_restantes = []

# --- Slash Commands ---

@tree.command(name="pc", description="Decide Sí o No según un porcentaje dado.")
@app_commands.describe(porcentaje="Número entre 0 y 100")
async def porcentaje(interaction: discord.Interaction, porcentaje: int):
    if porcentaje < 0 or porcentaje > 100:
        await interaction.response.send_message("⚠️ El porcentaje debe estar entre 0 y 100.")
        return

    azar = random.randint(1, 100)
    if azar <= porcentaje+10:
        await interaction.response.send_message(f"✅ **Sí**   (*{porcentaje}*%)")
    else:
        await interaction.response.send_message(f"❌ **No**   (*{porcentaje}*%)")

@tree.command(name="dado", description="Otorga un numero aleatorio entre dos valores.")
@app_commands.describe(a="Valor de tu perk", b="Valor mínimo del rango", c="Valor máximo del rango", armor_enemy="(Opcional) Armadura del enemigo")
async def numero(interaction: discord.Interaction, a: int, b: int, c: int, armor_enemy:int=0):
    if b < 0 or c > 100:
        await interaction.response.send_message("⚠️ El numero debe estar entre 0 y 100.")
        return

    azar1 = random.randint(1, a)
    azar = random.randint(b, c)
    total = azar1 + azar - armor_enemy
    if armor_enemy != 0:
        await interaction.response.send_message(f"1d{a}: {azar1}  |  Rango({b}-{c}): {azar}  |  DEF: {armor_enemy} \n*{azar1}+{azar}-{armor_enemy}* → **🎲{total}**")
    else:
        await interaction.response.send_message(f"1d{a}: {azar1}  |  Rango({b}-{c}): {azar} \n*{azar1}+{azar}* → **🎲{total}**   ")

@tree.command(name="multidado", description="Otorga un numero aleatorio entre dos valores.")
@app_commands.describe(a="Valor de tu perk", b="Valor mínimo del rango", c="Valor máximo del rango",d="Numero de disparos", armor_enemy="(Opcional) Armadura del enemigo")
async def multidado(interaction: discord.Interaction, a: int, b: int, c: int, d:int, armor_enemy:int=0):
    rafaga = []
    daño = 0
    if b < 0 or c > 100:
        await interaction.response.send_message("⚠️ El numero debe estar entre 0 y 100.")
        return
    for disparo in range(0,d):
        azar1 = random.randint(1, a)    
        azar = random.randint(b, c)
        tiro = azar1 + azar - armor_enemy
        rafaga.append(tiro)
        daño += tiro

    daño_total = daño - armor_enemy
    daño_total_armor = daño -armor_enemy * d

    if armor_enemy != 0:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{a}({b}~{c}) | DEF: {armor_enemy}*\n"
    f"Resultados: {rafaga}\n"
    f"DEF: {armor_enemy} x {d} = -{armor_enemy*d}\n"
    f"**🎲 {daño_total_armor}**"
)
    else:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{a}({b}~{c}) *\n"
    f"Resultados: {rafaga}\n"
    f"**🎲 {daño_total}**"
)
# ---------------------------

@tree.command(name="jugadores", description="Registra una lista de jugadores.")
@app_commands.describe(nombres="Nombres separados por espacios (ej: Ana Luis Pedro)")
async def jugadores(interaction: discord.Interaction, nombres: str):
    global jugadores_lista, jugadores_restantes
    jugadores_lista = nombres.split()
    jugadores_restantes = jugadores_lista.copy()
    await interaction.response.send_message(f"✅ Jugadores registrados: {' '.join(jugadores_lista)}")

# ---------------------------

@tree.command(name="objetivo", description="Muestra un orden aleatorio de los jugadores.")
async def objetivo(interaction: discord.Interaction):
    global jugadores_lista
    if not jugadores_lista:
        await interaction.response.send_message("⚠️ Primero debes registrar jugadores con /jugadores.")
        return

    lista_m = jugadores_lista.copy()
    random.shuffle(lista_m)
    nombres = ", ".join(f"**{x}**" for x in lista_m)
    await interaction.response.send_message(f"🎯 **Orden de objetivos:**\n{nombres}")

# ---------------------------

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")
    print("Slash commands sincronizados con Discord.")

bot.run(TOKEN)
