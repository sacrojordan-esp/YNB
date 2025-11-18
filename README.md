¿Qué hace este proyecto?
YNBalancer es un bot ligero para Discord diseñado para apoyar juegos de rol de mesa como Dungeons & Dragons o cualquier sistema que utilice decisiones basadas en probabilidad.
Proporciona resultados aleatorios rápidos, tiradas personalizadas basadas en habilidades y herramientas simples para la gestión de jugadores, facilitando el desarrollo de las partidas.
YNBalancer ayuda a los directores de juego y jugadores a automatizar tareas repetitivas típicas de las sesiones de rol.

Funciones actuales

-----Comandos de Aleatoriedad y Dados-----

/pc 76 — Devuelve “Sí” o “No” según el porcentaje indicado.

/dado 7 20 30 — Realiza una tirada personalizada usando:

valor de habilidad (por ejemplo: 7)
/ rango mínimo (por ejemplo: 20)
/ rango máximo (por ejemplo: 30)

-----Comandos de Gestión de Jugadores-----

/jugadores Juan Maria — Registra una lista de nombres de jugadores.

/objetivo — Genera y muestra un orden aleatorio usando los jugadores registrados.

¿COMO USAR EL PROYECTO?

A partir de este punto si no tienes conocimiento sobre python ve al archivo llamado: "Iniciando el bot sin saber como iniciarlo"



Si sabes utilizar python sigue con estos pasos:

1 Descarga este repositorio en ZIP y extraelo en tu escritorio en una carpeta llamada YNB

2 Accede al archivo .env y agrega tu token entre las comillas: DISCORD_TOKEN='tu_token_aquí'

3 Instala las dependencias requeridas: pip install -r requirements.txt

4 Ejecuta el bot: python main.py
