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
enemigos = {}

# --- Clase Enemigo ---
class Enemigo:
    def __init__(self, nombre, vida):
        self.nombre = nombre
        self.vida = vida

    def recibir_daño(self, daño):
        self.vida -= daño
        if self.vida <= 0:
            self.vida = 0
            return f"💀 {self.nombre} ha sido derrotado."
        else:
            return f"{self.nombre} recibió {daño} de daño. ❤️ Vida restante: {self.vida}"

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
@app_commands.describe(a="Valor de tu perk", b="Valor mínimo del rango (entre 0 y 100)", c="Valor máximo del rango (entre 0 y 100)")
async def numero(interaction: discord.Interaction, a: int, b: int, c: int):
    if b < 0 or c > 100:
        await interaction.response.send_message("⚠️ El numero debe estar entre 0 y 100.")
        return

    azar1 = random.randint(1, a)
    azar = random.randint(b, c)
    await interaction.response.send_message(f"*[1d{a} → {azar1}]* \n*[{b}-{c} → {azar}]*\n🎲 **{azar1 + azar}**")

# ---------------------------

@tree.command(name="jugadores", description="Registra una lista de jugadores.")
@app_commands.describe(nombres="Nombres separados por espacios (ej: Ana Luis Pedro)")
async def jugadores(interaction: discord.Interaction, nombres: str):
    global jugadores_lista, jugadores_restantes
    jugadores_lista = nombres.split()
    jugadores_restantes = jugadores_lista.copy()
    await interaction.response.send_message(f"✅ Jugadores registrados: {', '.join(jugadores_lista)}")

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

@tree.command(name="spawn", description="Crea uno o varios enemigos con la misma vida.")
@app_commands.describe(nombre="Nombre base del enemigo", vida="Puntos de vida", cantidad="Número de enemigos (opcional)")
async def spawn(interaction: discord.Interaction, nombre: str, vida: int, cantidad: int = 1):
    global enemigos

    creados = []

    for i in range(cantidad):
        nombre_final = f"{nombre} {i+1}" if cantidad > 1 else nombre

        if nombre_final in enemigos:
            await interaction.response.send_message(f"⚠️ El enemigo '{nombre_final}' ya existe, omitido.", ephemeral=True)
            continue

        enemigos[nombre_final] = Enemigo(nombre_final, vida)
        creados.append(nombre_final)

    if creados:
        lista = ", ".join(creados)
        await interaction.response.send_message(f"☣️ Spawn: {lista} con 💔 {vida} de vida cada uno.")
    else:
        await interaction.response.send_message("⚠️ No se creó ningún enemigo nuevo.", ephemeral=True)

# ---------------------------

@tree.command(name="atacar", description="Aplica daño a un enemigo existente.")
@app_commands.describe(daño="Cantidad de daño a infligir")
async def atacar(interaction: discord.Interaction, daño: int):
    global enemigos

    # Filtramos solo los enemigos con vida > 0
    enemigos_vivos = {nombre: e for nombre, e in enemigos.items() if e.vida > 0}

    if not enemigos_vivos:
        await interaction.response.send_message("💀 No hay enemigos vivos para atacar.")
        return

    # Crear opciones del menú con los enemigos vivos
    opciones = [
        discord.SelectOption(label=e.nombre, description=f"❤️ Vida: {e.vida}")
        for e in enemigos_vivos.values()
    ]

    opciones = opciones[:25]  # Discord solo permite máximo 25 opciones por menú

    # Clase View con menú desplegable
    class AtacarView(View):
        def __init__(self):
            super().__init__(timeout=30)

            # Crear el menú de selección dentro del View
            self.select = Select(
                placeholder="Selecciona un enemigo para atacar ⚔️",
                options=opciones
            )

            # Asignar el callback del menú
            self.select.callback = self.seleccionar

            # Agregar el select al View
            self.add_item(self.select)

        async def seleccionar(self, interaction2: discord.Interaction):
            enemigo_nombre = self.select.values[0]
            enemigo = enemigos.get(enemigo_nombre)

            if not enemigo or enemigo.vida <= 0:
                await interaction2.response.send_message(
                    f"⚠️ El enemigo '{enemigo_nombre}' ya no está disponible.", ephemeral=True
                )
                return

            resultado = enemigo.recibir_daño(daño)
            await interaction2.response.send_message(f"⚔️ {resultado}")

            # Cierra el menú después de la selección
            self.stop()

    # Crear la vista y mostrar el menú
    view = AtacarView()

    await interaction.response.send_message(
        "🎯 **Selecciona al enemigo que deseas atacar:**",
        view=view
    )
# ---------------------------

@tree.command(name="enemigos", description="Muestra todos los enemigos vivos y sus vidas.")
async def enemigos_lista(interaction: discord.Interaction):
    global enemigos

    # Filtrar solo los que tienen vida > 0
    enemigos_vivos = [e for e in enemigos.values() if e.vida > 0]

    if not enemigos_vivos:
        await interaction.response.send_message("💀 No hay enemigos vivos actualmente.")
        return

    lista_texto = "\n".join(f"☣️  {e.nombre}: 💔 {e.vida}" for e in enemigos_vivos)
    await interaction.response.send_message(f"📜 **Enemigos vivos:**\n{lista_texto}")

@tree.command(name="elimina_enemigos", description="Elimina a todos los enemigos registrados.")
async def limpia_enemigos(interaction: discord.Interaction):
    global enemigos

    if not enemigos:
        await interaction.response.send_message("⚠️ No hay enemigos para eliminar.")
        return

    cantidad = len(enemigos)
    enemigos.clear()  # 🧹 Limpiatodo el diccionario

    await interaction.response.send_message(f"🧨 Todos los enemigos ({cantidad}) fueron eliminados del registro.")

# ---------------------------

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot conectado como {bot.user}")
    print("Slash commands sincronizados con Discord.")

bot.run(TOKEN)