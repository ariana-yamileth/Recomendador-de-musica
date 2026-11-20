"""
Carga a MongoDB Atlas un catálogo REAL de artistas y canciones, con usuarios y
reproducciones generados automáticamente.

Uso (desde la raíz del proyecto, con el entorno .venv activado):
    python scripts/generar_datos_reales.py

Usa el MONGO_URI del archivo .env y crea las colecciones con validación de esquema.
OJO: borra y recrea usuarios, artistas, canciones y reproducciones.
"""
import random
from datetime import datetime, timedelta

import _ruta  # noqa: F401  (permite importar app/ desde scripts/)
from faker import Faker
from pymongo import ASCENDING

from app.config import get_db
from app.esquemas import VALIDADORES

fake = Faker("es_MX")
Faker.seed(42)
random.seed(42)

# ---------- Conexión a Atlas y colecciones con validación ----------
db = get_db("admin")
for nombre in ["usuarios", "artistas", "canciones", "reproducciones"]:
    db[nombre].drop()
    if nombre in VALIDADORES:
        db.create_collection(nombre, validator=VALIDADORES[nombre],
                             validationLevel="strict", validationAction="error")
    else:
        db.create_collection(nombre)

CIUDADES = ["Puebla", "CDMX", "Guadalajara", "Monterrey", "Querétaro",
            "Veracruz", "Mérida", "Oaxaca", "Toluca", "Cholula"]

# ---------------------------------------------------------------------
# Catálogo real: (nombre, [géneros], país, oyentes mensuales en millones
# (aproximado), [(canción, año), ...]) -> la primera canción de cada lista
# es la más popular del artista. Cifras y años son aproximados.
# ---------------------------------------------------------------------
CATALOGO = [
    # ---- Pop ----
    ("The Weeknd", ["R&B", "Pop"], "Canadá", 110, [("Blinding Lights", 2019), ("Starboy", 2016), ("Save Your Tears", 2020), ("Die For You", 2016), ("The Hills", 2015)]),
    ("Taylor Swift", ["Pop"], "Estados Unidos", 100, [("Anti-Hero", 2022), ("Cruel Summer", 2019), ("Blank Space", 2014), ("Shake It Off", 2014), ("Love Story", 2008)]),
    ("Ed Sheeran", ["Pop"], "Reino Unido", 90, [("Shape of You", 2017), ("Perfect", 2017), ("Thinking Out Loud", 2014), ("Bad Habits", 2021), ("Photograph", 2014)]),
    ("Dua Lipa", ["Pop"], "Reino Unido", 75, [("Levitating", 2020), ("Don't Start Now", 2019), ("New Rules", 2017), ("Houdini", 2023), ("One Kiss", 2018)]),
    ("Harry Styles", ["Pop"], "Reino Unido", 70, [("As It Was", 2022), ("Watermelon Sugar", 2019), ("Adore You", 2019), ("Sign of the Times", 2017), ("Late Night Talking", 2022)]),
    ("Billie Eilish", ["Pop", "Indie"], "Estados Unidos", 80, [("Birds of a Feather", 2024), ("Bad Guy", 2019), ("Lovely", 2018), ("Ocean Eyes", 2016), ("What Was I Made For?", 2023)]),
    ("Rihanna", ["Pop", "R&B"], "Barbados", 60, [("Umbrella", 2007), ("Diamonds", 2012), ("We Found Love", 2011), ("Work", 2016), ("Stay", 2012)]),
    ("Bruno Mars", ["Pop", "R&B"], "Estados Unidos", 85, [("Die with a Smile", 2024), ("Uptown Funk", 2014), ("Locked Out of Heaven", 2012), ("Just the Way You Are", 2010), ("That's What I Like", 2016)]),
    ("Adele", ["Pop"], "Reino Unido", 55, [("Rolling in the Deep", 2010), ("Someone Like You", 2011), ("Hello", 2015), ("Easy on Me", 2021), ("Set Fire to the Rain", 2011)]),
    ("Michael Jackson", ["Pop"], "Estados Unidos", 50, [("Billie Jean", 1982), ("Beat It", 1982), ("Thriller", 1982), ("Smooth Criminal", 1987), ("Don't Stop 'Til You Get Enough", 1979)]),
    ("Whitney Houston", ["Pop", "R&B"], "Estados Unidos", 30, [("I Wanna Dance with Somebody", 1987), ("I Will Always Love You", 1992), ("How Will I Know", 1985), ("Greatest Love of All", 1985)]),
    ("Shakira", ["Pop"], "Colombia", 70, [("Hips Don't Lie", 2006), ("Waka Waka", 2010), ("Whenever, Wherever", 2001), ("La Tortura", 2005), ("Bzrp Music Sessions, Vol. 53", 2023)]),
    ("Rosalía", ["Pop"], "España", 30, [("Despechá", 2022), ("Saoko", 2022), ("Malamente", 2018), ("Bizcochito", 2022)]),
    ("Enrique Iglesias", ["Pop"], "España", 40, [("Bailando", 2014), ("Súbeme la Radio", 2017), ("Hero", 2001), ("Tonight (I'm Lovin' You)", 2010)]),
    ("Ricky Martin", ["Pop"], "Puerto Rico", 20, [("Livin' la Vida Loca", 1999), ("La Copa de la Vida", 1998), ("Vente Pa' Ca", 2016), ("She Bangs", 2000)]),

    # ---- Rock / Metal / Indie ----
    ("Queen", ["Rock"], "Reino Unido", 50, [("Bohemian Rhapsody", 1975), ("Don't Stop Me Now", 1978), ("Another One Bites the Dust", 1980), ("Under Pressure", 1981), ("We Will Rock You", 1977)]),
    ("Coldplay", ["Rock", "Pop"], "Reino Unido", 80, [("Yellow", 2000), ("Viva la Vida", 2008), ("Fix You", 2005), ("The Scientist", 2002), ("Paradise", 2011)]),
    ("Imagine Dragons", ["Rock", "Pop"], "Estados Unidos", 60, [("Believer", 2017), ("Radioactive", 2012), ("Thunder", 2017), ("Demons", 2013), ("Bones", 2022)]),
    ("Arctic Monkeys", ["Indie", "Rock"], "Reino Unido", 55, [("Do I Wanna Know?", 2013), ("I Wanna Be Yours", 2013), ("R U Mine?", 2012), ("505", 2007), ("I Bet You Look Good on the Dancefloor", 2005)]),
    ("Linkin Park", ["Rock", "Metal"], "Estados Unidos", 50, [("In the End", 2000), ("Numb", 2003), ("Crawling", 2000), ("What I've Done", 2007), ("Somewhere I Belong", 2003)]),
    ("Metallica", ["Metal"], "Estados Unidos", 35, [("Enter Sandman", 1991), ("Nothing Else Matters", 1991), ("One", 1988), ("Master of Puppets", 1986), ("Fade to Black", 1984)]),
    ("Guns N' Roses", ["Rock"], "Estados Unidos", 40, [("Sweet Child o' Mine", 1987), ("November Rain", 1991), ("Welcome to the Jungle", 1987), ("Paradise City", 1987), ("Don't Cry", 1991)]),
    ("Nirvana", ["Rock"], "Estados Unidos", 35, [("Smells Like Teen Spirit", 1991), ("Come as You Are", 1991), ("Lithium", 1991), ("In Bloom", 1991), ("Heart-Shaped Box", 1993)]),
    ("AC/DC", ["Rock"], "Australia", 40, [("Back in Black", 1980), ("Highway to Hell", 1979), ("Thunderstruck", 1990), ("You Shook Me All Night Long", 1980), ("T.N.T.", 1975)]),
    ("Led Zeppelin", ["Rock"], "Reino Unido", 30, [("Stairway to Heaven", 1971), ("Whole Lotta Love", 1969), ("Immigrant Song", 1970), ("Kashmir", 1975), ("Black Dog", 1971)]),
    ("The Beatles", ["Rock", "Pop"], "Reino Unido", 30, [("Here Comes the Sun", 1969), ("Let It Be", 1970), ("Hey Jude", 1968), ("Come Together", 1969), ("Yesterday", 1965)]),
    ("Radiohead", ["Indie", "Rock"], "Reino Unido", 30, [("Creep", 1992), ("Karma Police", 1997), ("No Surprises", 1997), ("Fake Plastic Trees", 1995), ("Paranoid Android", 1997)]),
    ("The Killers", ["Indie", "Rock"], "Estados Unidos", 25, [("Mr. Brightside", 2003), ("Somebody Told Me", 2004), ("When You Were Young", 2006), ("Human", 2008), ("Read My Mind", 2006)]),
    ("Tame Impala", ["Indie"], "Australia", 30, [("The Less I Know the Better", 2015), ("Let It Happen", 2015), ("Borderline", 2019), ("Feels Like We Only Go Backwards", 2012), ("Eventually", 2015)]),
    ("Black Sabbath", ["Metal"], "Reino Unido", 15, [("Paranoid", 1970), ("Iron Man", 1970), ("War Pigs", 1970), ("Black Sabbath", 1970), ("N.I.B.", 1970)]),
    ("Iron Maiden", ["Metal"], "Reino Unido", 15, [("The Trooper", 1983), ("Fear of the Dark", 1992), ("Hallowed Be Thy Name", 1982), ("Run to the Hills", 1982), ("The Number of the Beast", 1982)]),
    ("Rammstein", ["Metal"], "Alemania", 20, [("Du Hast", 1997), ("Sonne", 2001), ("Deutschland", 2019), ("Ich Will", 2001), ("Mein Herz brennt", 2001)]),
    ("Maná", ["Rock"], "México", 10, [("Rayando el Sol", 1990), ("Clavado en un Bar", 1997), ("Corazón Espinado", 1994), ("Oye Mi Amor", 1992), ("En el Muelle de San Blas", 1997)]),
    ("Café Tacvba", ["Rock", "Indie"], "México", 5, [("Eres", 2003), ("La Ingrata", 1992), ("Chilanga Banda", 1994), ("Déjate Caer", 1994)]),
    ("Caifanes", ["Rock"], "México", 5, [("La Negra Tomasa", 1988), ("Afuera", 1994), ("Nubes", 1992), ("No Dejes Que", 1992)]),
    ("Soda Stereo", ["Rock"], "Argentina", 10, [("De Música Ligera", 1990), ("Persiana Americana", 1986), ("Cuando Pase el Temblor", 1985), ("En la Ciudad de la Furia", 1988)]),

    # ---- Hip hop / R&B ----
    ("Drake", ["Hip hop"], "Canadá", 80, [("God's Plan", 2018), ("One Dance", 2016), ("Hotline Bling", 2015), ("Passionfruit", 2017), ("Rich Flex", 2022)]),
    ("Post Malone", ["Hip hop"], "Estados Unidos", 70, [("Circles", 2019), ("Sunflower", 2018), ("Rockstar", 2017), ("Congratulations", 2016), ("White Iverson", 2015)]),
    ("Eminem", ["Hip hop"], "Estados Unidos", 70, [("Lose Yourself", 2002), ("Without Me", 2002), ("The Real Slim Shady", 2000), ("Love the Way You Lie", 2010), ("Mockingbird", 2004)]),
    ("Kendrick Lamar", ["Hip hop"], "Estados Unidos", 60, [("Not Like Us", 2024), ("HUMBLE.", 2017), ("DNA.", 2017), ("Money Trees", 2012), ("Alright", 2015)]),
    ("Travis Scott", ["Hip hop"], "Estados Unidos", 55, [("Sicko Mode", 2018), ("Goosebumps", 2016), ("Highest in the Room", 2019), ("FE!N", 2023), ("Butterfly Effect", 2017)]),
    ("Beyoncé", ["R&B", "Pop"], "Estados Unidos", 40, [("Halo", 2008), ("Crazy in Love", 2003), ("Single Ladies (Put a Ring on It)", 2008), ("Formation", 2016), ("Cuff It", 2022)]),
    ("SZA", ["R&B"], "Estados Unidos", 50, [("Kill Bill", 2022), ("Snooze", 2022), ("Good Days", 2020), ("Saturn", 2024), ("The Weekend", 2017)]),
    ("Frank Ocean", ["R&B", "Indie"], "Estados Unidos", 20, [("Thinkin Bout You", 2012), ("Nights", 2016), ("Pink + White", 2016), ("Novacane", 2011), ("Lost", 2012)]),

    # ---- Reggaeton / Latino urbano ----
    ("Bad Bunny", ["Reggaeton"], "Puerto Rico", 80, [("Me Porto Bonito", 2022), ("Tití Me Preguntó", 2022), ("Ojitos Lindos", 2022), ("Dákiti", 2020), ("Callaita", 2019)]),
    ("Karol G", ["Reggaeton"], "Colombia", 55, [("Tusa", 2019), ("Provenza", 2022), ("Bichota", 2020), ("MAMIII", 2022), ("TQG", 2023)]),
    ("J Balvin", ["Reggaeton"], "Colombia", 40, [("Mi Gente", 2017), ("Ginza", 2015), ("Ay Vamos", 2014), ("Safari", 2016), ("Con Altura", 2019)]),
    ("Daddy Yankee", ["Reggaeton"], "Puerto Rico", 35, [("Gasolina", 2004), ("Dura", 2018), ("Con Calma", 2019), ("Limbo", 2012), ("Shaky Shaky", 2015)]),
    ("Maluma", ["Reggaeton"], "Colombia", 25, [("Felices los 4", 2017), ("Hawái", 2020), ("Corazón", 2017)]),

    # ---- Regional mexicano / Banda ----
    ("Peso Pluma", ["Regional mexicano"], "México", 50, [("Ella Baila Sola", 2023), ("La Bebé", 2023), ("Por Las Noches", 2022), ("El Belicón", 2022), ("PRC", 2023)]),
    ("Grupo Frontera", ["Regional mexicano"], "Estados Unidos", 25, [("Un x100to", 2023), ("No Se Va", 2023), ("El Amor de Su Vida", 2023)]),
    ("Los Tigres del Norte", ["Regional mexicano"], "México", 10, [("La Puerta Negra", 1985), ("Jaula de Oro", 1984), ("La Reina del Sur", 2002), ("Contrabando y Traición", 1974)]),
    ("Vicente Fernández", ["Regional mexicano"], "México", 15, [("Volver, Volver", 1972), ("El Rey", 1971), ("Estos Celos", 1996), ("Mujeres Divinas", 1994)]),
    ("Juan Gabriel", ["Balada", "Regional mexicano"], "México", 15, [("Amor Eterno", 1984), ("Hasta Que Te Conocí", 1986), ("Querida", 1984)]),
    ("Banda MS", ["Banda"], "México", 10, [("Hermosa Experiencia", 2012), ("Te Presumo", 2012)]),

    # ---- Cumbia ----
    ("Selena", ["Cumbia", "Pop"], "Estados Unidos", 12, [("Como la Flor", 1992), ("Bidi Bidi Bom Bom", 1994), ("Amor Prohibido", 1994), ("La Carcacha", 1992), ("No Me Queda Más", 1994)]),
    ("Los Ángeles Azules", ["Cumbia"], "México", 20, [("Cómo Te Voy a Olvidar", 1996), ("Nunca Es Suficiente", 2019), ("17 Años", 1990), ("El Listón de Tu Pelo", 1995)]),

    # ---- Balada ----
    ("Luis Miguel", ["Balada", "Pop"], "México", 15, [("La Incondicional", 1989), ("Ahora Te Puedes Marchar", 1987), ("Hasta Que Me Olvides", 1993), ("La Bikina", 1991)]),

    # ---- Salsa ----
    ("Marc Anthony", ["Salsa"], "Estados Unidos", 15, [("Vivir Mi Vida", 2013), ("Valió la Pena", 2004), ("Flor Pálida", 1993), ("Te Conozco Bien", 2004)]),
    ("Celia Cruz", ["Salsa"], "Cuba", 8, [("La Vida Es un Carnaval", 1998), ("Quimbara", 1974), ("Yo Viviré", 2000)]),
    ("Héctor Lavoe", ["Salsa"], "Puerto Rico", 5, [("El Cantante", 1978), ("Mi Gente", 1975), ("Periódico de Ayer", 1975)]),

    # ---- Electrónica ----
    ("Daft Punk", ["Electrónica"], "Francia", 35, [("Get Lucky", 2013), ("One More Time", 2000), ("Instant Crush", 2013), ("Harder, Better, Faster, Stronger", 2001), ("Around the World", 1997)]),
    ("Calvin Harris", ["Electrónica"], "Reino Unido", 50, [("Summer", 2014), ("Feel So Close", 2011), ("This Is What You Came For", 2016), ("Blame", 2014), ("How Deep Is Your Love", 2015)]),
    ("Avicii", ["Electrónica"], "Suecia", 40, [("Wake Me Up", 2013), ("Levels", 2011), ("Hey Brother", 2013), ("The Nights", 2014), ("Waiting for Love", 2015)]),
    ("David Guetta", ["Electrónica"], "Francia", 50, [("Titanium", 2011), ("Memories", 2010), ("When Love Takes Over", 2009), ("Sexy Bitch", 2009)]),

    # ---- Jazz ----
    ("Miles Davis", ["Jazz"], "Estados Unidos", 6, [("So What", 1959), ("Blue in Green", 1959), ("All Blues", 1959), ("Freddie Freeloader", 1959)]),
    ("Louis Armstrong", ["Jazz"], "Estados Unidos", 8, [("What a Wonderful World", 1967), ("La Vie en Rose", 1950), ("Hello, Dolly!", 1964)]),
    ("Frank Sinatra", ["Jazz"], "Estados Unidos", 20, [("Fly Me to the Moon", 1964), ("My Way", 1969), ("New York, New York", 1979), ("The Way You Look Tonight", 1964), ("I've Got You Under My Skin", 1956)]),

    # ---- Clásica (años de composición, por eso el esquema permite desde 1600) ----
    ("Ludwig van Beethoven", ["Clásica"], "Alemania", 10, [("Für Elise", 1810), ("Claro de Luna (Sonata n.º 14)", 1801), ("Sinfonía n.º 9: Oda a la Alegría", 1824), ("Sinfonía n.º 5", 1808)]),
    ("Wolfgang Amadeus Mozart", ["Clásica"], "Austria", 8, [("Eine kleine Nachtmusik", 1787), ("Réquiem: Lacrimosa", 1791), ("Sonata para piano n.º 11", 1783), ("Sinfonía n.º 40", 1788)]),
    ("Frédéric Chopin", ["Clásica"], "Polonia", 8, [("Nocturno Op. 9 n.º 2", 1832), ("Vals del minuto", 1847), ("Estudio Revolucionario", 1831), ("Balada n.º 1", 1835)]),
    ("Johann Sebastian Bach", ["Clásica"], "Alemania", 7, [("Aria en sol (Suite n.º 3)", 1730), ("Preludio en do mayor", 1722), ("Toccata y fuga en re menor", 1704), ("Suite para violonchelo n.º 1", 1720)]),
]

# ---------- Artistas ----------
artistas = []
for i, (nombre, generos, pais, oyentes_m, _) in enumerate(CATALOGO, start=1):
    artistas.append({
        "_id": i,
        "nombre": nombre,
        "generos": generos,
        "pais": pais,
        "oyentes_mensuales": oyentes_m * 1_000_000,
    })

# ---------- Canciones ----------
canciones = []
pesos = []   # popularidad: artista famoso y posición alta en su lista = más reproducciones
for art, (_, _, _, oyentes_m, temas) in zip(artistas, CATALOGO):
    for pos, (titulo, anio) in enumerate(temas):
        canciones.append({
            "_id": len(canciones) + 1,
            "titulo": titulo,
            "artista_id": art["_id"],
            "artista": art["nombre"],          # desnormalizado a propósito
            "genero": random.choice(art["generos"]),
            "duracion_seg": random.randint(150, 330),
            "anio": anio,
        })
        pesos.append(oyentes_m * (len(temas) - pos))

por_genero = {}
for c, p in zip(canciones, pesos):
    por_genero.setdefault(c["genero"], []).append((c, p))
generos_disponibles = list(por_genero.keys())


def elegir_ponderado(candidatos, k, excluir=()):
    """Elige k canciones distintas; las más populares salen con más frecuencia."""
    elegidas = set()
    objetos = [c for c, _ in candidatos]
    w = [p for _, p in candidatos]
    k = min(k, len(objetos))
    while len(elegidas) < k:
        c = random.choices(objetos, weights=w, k=1)[0]
        if c["_id"] not in excluir:
            elegidas.add(c["_id"])
    return elegidas


todas = list(zip(canciones, pesos))

# ---------- Usuarios (1000) ----------
usuarios = []
for i in range(1, 1001):
    usuarios.append({
        "_id": i,
        "nombre": fake.name(),
        "correo": fake.unique.email(),
        "edad": random.randint(15, 45),
        "ciudad": random.choice(CIUDADES),
        "generos_favoritos": random.sample(generos_disponibles, k=random.randint(1, 3)),
        "fecha_registro": fake.date_time_between(start_date="-3y", end_date="now"),
    })

# ---------- Reproducciones (~30,000) ----------
reproducciones = []
for u in usuarios:
    # ~80% de las canciones vienen de sus géneros favoritos, ~20% son de todo el catálogo
    pool_fav = [par for g in u["generos_favoritos"] for par in por_genero[g]]
    elegidas = elegir_ponderado(pool_fav, 24)
    while len(elegidas) < 30:
        elegidas |= elegir_ponderado(todas, 1, excluir=elegidas)
    for cid in elegidas:
        c = canciones[cid - 1]
        reproducciones.append({
            "usuario_id": u["_id"],
            "cancion_id": cid,
            "artista_id": c["artista_id"],
            "genero": c["genero"],
            "fecha": datetime.now() - timedelta(days=random.randint(0, 365),
                                                minutes=random.randint(0, 1440)),
            "calificacion": random.randint(1, 5),
        })

# ---------- Carga masiva ----------
db.artistas.insert_many(artistas)
db.canciones.insert_many(canciones)
db.usuarios.insert_many(usuarios)
db.reproducciones.insert_many(reproducciones)

# ---------- Índices ----------
db.reproducciones.create_index([("usuario_id", ASCENDING)])
db.reproducciones.create_index([("cancion_id", ASCENDING)])
db.reproducciones.create_index([("artista_id", ASCENDING)])
db.canciones.create_index([("genero", ASCENDING)])
db.usuarios.create_index([("correo", ASCENDING)], unique=True)

total = 0
print("Carga terminada en la base:", db.name)
for c in ["usuarios", "artistas", "canciones", "reproducciones"]:
    n = db[c].count_documents({})
    total += n
    print(f"  {c}: {n}")
print("  TOTAL:", total)