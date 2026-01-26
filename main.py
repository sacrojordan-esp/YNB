import os
import random
import discord, json
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

#Extraccion de armas y enemigos
with open("db/armas.json", "r", encoding="utf-8") as f:
    DATA_ARMAS = json.load(f)
ARMAS = {a["name"]: a for a in DATA_ARMAS["armas"]}

with open("db/enemigos.json", "r", encoding="utf-8") as f:
    DATA_ENEMIGOS = json.load(f)
ENEMIGOS = {e["name"]: e for e in DATA_ENEMIGOS["enemigos"]}

# --------------------- SLASH COMANDS ------------------------------------------

#/pc------------------------------------------------------
@tree.command(
    name="pc",
    description="Decide Sí o No según un porcentaje."
    )
@app_commands.describe(
    porcentaje="Número entre 0 y 100"
    )
async def porcentaje(interaction: discord.Interaction, porcentaje: int):
    if porcentaje < 0 or porcentaje > 100:
        await interaction.response.send_message("⚠️ El porcentaje debe estar entre 0 y 100.")
        return

    azar = random.randint(1, 100)
    if azar <= porcentaje+10:
        await interaction.response.send_message(f"✅ **Sí**   (*{porcentaje}*%)")
    else:
        await interaction.response.send_message(f"❌ **No**   (*{porcentaje}*%)")

# Autocompletado de armas y enemigos
async def arma_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=nombre, value=nombre)
        for nombre in ARMAS
        if current.lower() in nombre.lower()
    ][:25]

async def enemigo_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=nombre, value=nombre)
        for nombre in ENEMIGOS
        if current.lower() in nombre.lower()
    ][:25]

#/ataque------------------------------------------------------
@tree.command(
    name="ataque", 
    description="Realiza un ataque con un arma y calcula el daño causado."
    )
@app_commands.describe(
    stat="Atributo special", 
    arma="arma", 
    armor_enemy="Armadura del enemigo (opcional)")
@app_commands.autocomplete(arma=arma_autocomplete)  #🔹Conexion a autocompletado

async def ataque(
    interaction: discord.Interaction,
    stat: int,
    arma: str,
    armor_enemy: int = 0
    ):

    arma_data = ARMAS.get(arma)
    if not arma_data:
        await interaction.response.send_message("❌ Arma no encontrada.")
        return
    mini = arma_data["daño_min"]
    maxi = arma_data["daño_max"]

    randstat = random.randint(1, stat)
    daño = random.randint(mini, maxi)
    daño_final = max(0, daño + randstat - armor_enemy)

    await interaction.response.send_message(
        f"1d{stat}: {randstat}  |  Arma ({mini}-{maxi}): {daño}  |  DEF: {armor_enemy}\n"
        f"*{randstat} + {daño} - {armor_enemy}* → **🎲{daño_final}**"
    )

#/ataque_multiple------------------------------------------------------
@tree.command(
    name="ataque_multiple", 
    description="Realiza un ataque con múltiples disparos y calcula el daño total."
    )
@app_commands.describe(
    stat="Atributo special", 
    arma="arma", 
    d="Numero de disparos", 
    armor_enemy="Armadura del enemigo (opcional)",
    )
@app_commands.autocomplete(arma=arma_autocomplete)

async def ataque_multiple(
    interaction: discord.Interaction,
    stat: int,
    arma: str,
    d:int,
    armor_enemy:int=0
    ):

    arma_data = ARMAS.get(arma)
    if not arma_data:
        await interaction.response.send_message("❌ Arma no encontrada.")
        return
    mini = arma_data["daño_min"]
    maxi = arma_data["daño_max"]

    rafaga = []
    resultante = []
    daño = 0

    for _ in range(0,d):
        tiro = random.randint(1, stat)  + random.randint(mini, maxi)
        rafaga.append(tiro)

        daño_resultante = max(tiro - armor_enemy,0)  #Elimina negativos
        if daño_resultante:
            resultante.append(daño_resultante)
            daño += daño_resultante

    if armor_enemy != 0:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{stat}({mini}~{maxi}) | DEF: {armor_enemy}*\n"
    f"Rafaga: {rafaga}\n"
    f"Resultado - Defensa: {resultante}\n"
    f"**🎲 {daño}**"
)
    else:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{stat}({mini}~{maxi}) *\n"
    f"Rafaga: {rafaga}\n"
    f"**🎲 {daño}**"
)

#/dado
@tree.command(name="dado", description="Realiza un ataque con el rango de daño de un arma.")
@app_commands.describe(a="Atributo special", b="Daño minimo", c="Daño maximo", armor_enemy="Armadura del enemigo(Opcional)")
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

#/multidado
@tree.command(name="multidado", description="Realiza un ataque multiple con el rango del daño del arma.")
@app_commands.describe(a="Atributo special", b="Daño minimo", c="Daño maximo",d="Numero de disparos", armor_enemy="(Opcional) Armadura del enemigo")
async def multidado(interaction: discord.Interaction, a: int, b: int, c: int, d:int, armor_enemy:int=0):
    rafaga = []
    resultante = []
    daño = 0
    if b < 0 or c > 100:
        await interaction.response.send_message("⚠️ El numero debe estar entre 0 y 100.")
        return
    for _ in range(0,d):
        azar1 = random.randint(1, a)    
        azar = random.randint(b, c)
        tiro = azar1 + azar
        rafaga.append(tiro)

        daño_resultante = max(tiro-armor_enemy,0)  #Elimina negativos
        if daño_resultante:
            resultante.append(daño_resultante)
            daño += daño_resultante

    if armor_enemy != 0:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{a}({b}~{c}) | DEF: {armor_enemy}*\n"
    f"Rafaga: {rafaga}\n"
    f"Resultado(-DEF): {resultante}\n"
    f"**🎲 {daño}**"
)
    else:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{a}({b}~{c}) *\n"
    f"Rafaga: {rafaga}\n"
    f"**🎲 {daño}**"
)

# ---------------------------

@tree.command(name="despierta_menta", description="Lanza un electrovibrazo a menta")
@app_commands.describe()
async def despierta(interaction: discord.Interaction):
    await interaction.response.send_message("Menta recibe un electroshock y se viene en la boca del siguiente que escriba")


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")
    print("Slash commands sincronizados con Discord.")

bot.run(TOKEN)
