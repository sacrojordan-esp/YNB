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
    description="Realiza un ataque con un arma y calcula el daño."
    )
@app_commands.describe(
    stat="Atributo: FU, PE, RE, CA, IN, AG, SU", 
    arma="Nombre del arma", 
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
    rarity = arma_data["rareza"]

    rarity_factor = {
    "Comun": 1,
    "Poco comun": 2,
    "Raro": 3,
    "Unico": 4
    }.get(rarity)

    randstat = random.randint(1, stat)
    daño = random.randint(mini, maxi)
    daño_final = max(0, (daño + randstat) * rarity_factor - armor_enemy)

    await interaction.response.send_message(
        f"1d{stat}: {randstat}  |  {arma}({rarity}) ({mini}-{maxi}) : {daño}  |  DEF: {armor_enemy}\n"
        f"*({randstat} + {daño}) x {rarity_factor} - {armor_enemy}* → **🎲{daño_final}**"
    )

#/ataque_en_rafaga------------------------------------------------------
@tree.command(
    name="ataque_multiple", 
    description="Realiza un ataque con múltiples disparos y calcula el daño."
    )
@app_commands.describe(
    stat="Atributo: FU, PE, RE, CA, IN, AG, SU", 
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
    rarity = arma_data["rareza"]

    rarity_factor = {
    "Comun": 4,
    "Poco comun": 3,
    "Raro": 2,
    "Unico": 1
    }.get(rarity)

    rafaga = []
    rafaga_temp = []
    resultante = []
    daño = 0

    for _ in range(0,d):
        tiro = (random.randint(1, stat) + random.randint(mini, maxi))
        rafaga_temp.append(tiro)
        tiro = tiro / rarity_factor
        rafaga.append(round(tiro))

        daño_resultante = max(round(tiro) - armor_enemy,0)  #Elimina negativos
        if daño_resultante:
            resultante.append(daño_resultante)
            daño += daño_resultante

    if armor_enemy != 0:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{stat} : {arma} ({mini}~{maxi})*\n"
    f"Rafaga: {rafaga_temp}\n"
    f"Rafaga({rarity}/{rarity_factor}): {rafaga}\n"
    f"Resultado - DEF{armor_enemy}: {resultante}\n"
    f"**🎲 {daño}**"
)
    else:
        await interaction.response.send_message(
    f"*Disparos: {d} x 1d{stat} : {arma} ({mini}~{maxi})*\n"
    f"Rafaga: {rafaga_temp}\n"
    f"Rafaga({rarity}/{rarity_factor}): {rafaga}\n"
    f"**🎲 {daño}**"
)

#/enemy_atack------------------------------------------------------
@tree.command(
    name="enemy_atack", 
    description="El enemigo realiza un ataque."
    )
@app_commands.describe(
    enemy="Nombre del enemigo", 
    )
@app_commands.autocomplete(enemy=enemigo_autocomplete)  #🔹Conexion a autocompletado

async def enemy_atack(
    interaction: discord.Interaction,
    enemy: str,
    ):

    enemy_data = ENEMIGOS.get(enemy)
    if not enemy_data:
        await interaction.response.send_message("❌ Enemigo no encontrado.")
        return
    
    damage = enemy_data["damage"]

    await interaction.response.send_message(
        f"**{enemy}** Inflinge **{damage} de daño**"
    )

# ---------------------------

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")
    print("Slash commands sincronizados con Discord.")

bot.run(TOKEN)
