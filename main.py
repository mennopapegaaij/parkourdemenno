"""Wolken Parkour 3D - een simpel 3D parkourspel."""

import json
from math import sin
from pathlib import Path
from time import perf_counter

from ursina import (
    AmbientLight,
    DirectionalLight,
    Entity,
    Sky,
    Text,
    Ursina,
    Vec3,
    camera,
    color,
    destroy,
    distance,
    mouse,
    time,
    window,
)
from ursina.prefabs.first_person_controller import FirstPersonController

TITEL = "Wolken Parkour 3D"
START_PUNT = Vec3(0, 2, 0)
START_SNELHEID = 7
TOTAAL_STERREN = 3
AUTO_OPSLAAN_TIJD = 1.0
OPSLAG_BESTAND = Path(__file__).with_name("savegame.json")

PLATFORMS = [
    {"positie": (0, 0, 0), "schaal": (6, 1, 6), "kleur": color.azure},
    {"positie": (7, 1, 0), "schaal": (4, 1, 4), "kleur": color.orange},
    {"positie": (13, 2, 2), "schaal": (4, 1, 4), "kleur": color.lime},
    {"positie": (19, 3, -1), "schaal": (2, 1, 8), "kleur": color.gray},
    {"positie": (25, 4, -4), "schaal": (3, 1, 3), "kleur": color.cyan},
    {"positie": (31, 5, -4), "schaal": (4, 1, 4), "kleur": color.violet},
    {"positie": (37, 6, 0), "schaal": (3, 1, 3), "kleur": color.orange},
    {"positie": (43, 7, 4), "schaal": (3, 1, 3), "kleur": color.lime},
    {"positie": (49, 8, 0), "schaal": (3, 1, 3), "kleur": color.azure},
    {"positie": (55, 9, -4), "schaal": (3, 1, 3), "kleur": color.cyan},
    {"positie": (61, 10, -4), "schaal": (4, 1, 4), "kleur": color.violet},
    {"positie": (67, 11, 0), "schaal": (3, 1, 3), "kleur": color.orange},
    {"positie": (73, 12, 0), "schaal": (8, 1, 8), "kleur": color.gold},
]

STER_POSITIES = [
    (13, 3.3, 2),
    (31, 6.3, -4),
    (61, 11.3, -4),
]

CHECKPOINT_POSITIES = [
    (31, 5.65, -4),
    (61, 10.65, -4),
]

DOEL_POSITIE = Vec3(73, 14.2, 0)

app = Ursina()
window.title = TITEL
window.borderless = False
window.color = color.rgb(145, 205, 255)
window.exit_button.visible = False
window.fps_counter.enabled = True
camera.fov = 95

sterren = []
checkpoints = []
verzamelde_sterren = set()
spawn_punt = Vec3(START_PUNT.x, START_PUNT.y, START_PUNT.z)
gehaalde_sterren = 0
gewonnen = False
start_tijd = perf_counter()
eind_tijd = None
melding_tijd = 0.0
laatste_opslag_tijd = 0.0


def vec3_van(positie):
    """Maak van een tuple makkelijk een Vec3."""
    return Vec3(positie[0], positie[1], positie[2])


def maak_platform(positie, schaal, kleur_blok):
    """Maak een springblok waar de speler op kan landen."""
    return Entity(
        model="cube",
        texture="white_cube",
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )


class ZwevendeSter(Entity):
    """Een ster draait en zweeft een klein beetje op en neer."""

    def __init__(self, positie, nummer):
        super().__init__(
            model="sphere",
            color=color.yellow,
            position=vec3_van(positie),
            scale=0.7,
            collider="sphere",
        )
        self.nummer = nummer
        self.basis_y = self.y
        self.fase = (self.x + self.z) * 0.12

    def update(self):
        self.rotation_y += 140 * time.dt
        self.y = self.basis_y + sin(perf_counter() * 3 + self.fase) * 0.15


def maak_wolken():
    """Maak wat wolken zodat de baan hoog in de lucht lijkt."""
    wolk_data = [
        (-20, 18, 15, (10, 3, 6)),
        (18, 23, -18, (12, 4, 7)),
        (55, 20, 18, (14, 4, 8)),
        (85, 24, -10, (11, 3, 6)),
    ]

    for x, y, z, schaal in wolk_data:
        Entity(
            model="sphere",
            color=color.rgba(255, 255, 255, 180),
            position=(x, y, z),
            scale=schaal,
        )


def maak_wereld():
    """Bouw de hele parkourbaan en de omgeving."""
    Sky()
    AmbientLight(color=color.rgba(180, 180, 220, 120))
    DirectionalLight(y=25, z=10, rotation=(45, -35, 0))

    # Dit is de rode mist onder de baan. Als je daaronder valt, ga je terug.
    Entity(model="plane", position=(35, -12, 0), scale=220, color=color.red.tint(-0.1))

    for blok in PLATFORMS:
        maak_platform(blok["positie"], blok["schaal"], blok["kleur"])

    for positie in CHECKPOINT_POSITIES:
        checkpoint = Entity(
            model="cube",
            texture="white_cube",
            color=color.rgb(100, 140, 255),
            position=vec3_van(positie),
            scale=(2.6, 0.3, 2.6),
            collider="box",
        )
        checkpoint.actief = False
        checkpoints.append(checkpoint)

    # Een simpele vlag laat zien waar de finish is.
    Entity(model="cube", position=(73, 15.2, 0), scale=(0.25, 6, 0.25), color=color.white)
    Entity(model="cube", position=(74, 16.8, 0), scale=(2.2, 1.2, 0.15), color=color.red)
    Entity(model="sphere", position=DOEL_POSITIE, scale=1.4, color=color.yellow)

    maak_wolken()


def maak_sterren_opnieuw():
    """Zet alle sterren terug voor een nieuw potje."""
    global sterren

    for ster in sterren:
        destroy(ster)

    sterren = [
        ZwevendeSter(positie, nummer)
        for nummer, positie in enumerate(STER_POSITIES)
        if nummer not in verzamelde_sterren
    ]


def vec3_naar_lijst(waarde):
    """Maak van een Vec3 een gewone lijst voor het opslagbestand."""
    return [waarde.x, waarde.y, waarde.z]


def lijst_naar_vec3(waarde, standaard):
    """Maak van een lijst weer een Vec3."""
    if not isinstance(waarde, list) or len(waarde) != 3:
        return Vec3(standaard.x, standaard.y, standaard.z)

    try:
        return Vec3(float(waarde[0]), float(waarde[1]), float(waarde[2]))
    except (TypeError, ValueError):
        return Vec3(standaard.x, standaard.y, standaard.z)


def lees_getal(waarde, standaard):
    """Lees een getal uit het opslagbestand."""
    try:
        return float(waarde)
    except (TypeError, ValueError):
        return standaard


def veilig_speler_punt():
    """Bewaar geen plek midden in een val, maar een veilige plek."""
    if player.y < -6:
        return Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)
    return Vec3(player.x, player.y, player.z)


def wis_opslag():
    """Verwijder het opslagbestand als een potje klaar is."""
    if OPSLAG_BESTAND.exists():
        try:
            OPSLAG_BESTAND.unlink()
        except OSError:
            print("Het lukte niet om het opslagbestand weg te halen.")


def bewaar_voortgang():
    """Sla op waar de speler nu is."""
    global laatste_opslag_tijd

    if gewonnen:
        wis_opslag()
        return

    verstreken_tijd = max(0.0, perf_counter() - start_tijd)
    speler_punt = veilig_speler_punt()
    opslag = {
        "speler_positie": vec3_naar_lijst(speler_punt),
        "rotatie_y": player.rotation_y,
        "kijk_x": player.camera_pivot.rotation_x,
        "spawn_punt": vec3_naar_lijst(spawn_punt),
        "verzamelde_sterren": sorted(verzamelde_sterren),
        "actieve_checkpoints": [checkpoint.actief for checkpoint in checkpoints],
        "verstreken_tijd": verstreken_tijd,
    }

    try:
        OPSLAG_BESTAND.write_text(json.dumps(opslag, indent=2), encoding="utf-8")
        laatste_opslag_tijd = perf_counter()
    except OSError:
        print("Opslaan lukte niet.")


def laad_voortgang():
    """Laad het vorige potje als er een opslagbestand is."""
    global spawn_punt, gehaalde_sterren, start_tijd, verzamelde_sterren, laatste_opslag_tijd

    if not OPSLAG_BESTAND.exists():
        return False

    try:
        opslag = json.loads(OPSLAG_BESTAND.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("Het opslagbestand is niet goed. Het spel begint opnieuw.")
        return False
    except OSError:
        print("Het opslagbestand kon niet gelezen worden. Het spel begint opnieuw.")
        return False

    verzamelde_lijst = opslag.get("verzamelde_sterren", [])
    checkpoint_lijst = opslag.get("actieve_checkpoints", [])

    if not isinstance(verzamelde_lijst, list) or not isinstance(checkpoint_lijst, list):
        print("Er missen dingen in het opslagbestand. Het spel begint opnieuw.")
        return False

    nieuwe_sterren = set()
    for waarde in verzamelde_lijst:
        try:
            nummer = int(waarde)
        except (TypeError, ValueError):
            continue

        if 0 <= nummer < len(STER_POSITIES):
            nieuwe_sterren.add(nummer)

    verzamelde_sterren = nieuwe_sterren
    gehaalde_sterren = len(verzamelde_sterren)

    spawn_punt = lijst_naar_vec3(opslag.get("spawn_punt"), START_PUNT)
    speler_punt = lijst_naar_vec3(opslag.get("speler_positie"), spawn_punt)
    if speler_punt.y < -6:
        speler_punt = Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)

    player.position = speler_punt
    player.rotation_y = lees_getal(opslag.get("rotatie_y"), 0.0)
    player.camera_pivot.rotation_x = lees_getal(opslag.get("kijk_x"), 0.0)

    for nummer, checkpoint in enumerate(checkpoints):
        checkpoint.actief = nummer < len(checkpoint_lijst) and bool(checkpoint_lijst[nummer])
        checkpoint.color = color.lime if checkpoint.actief else color.rgb(100, 140, 255)

    maak_sterren_opnieuw()

    verstreken_tijd = max(0.0, lees_getal(opslag.get("verstreken_tijd"), 0.0))
    start_tijd = perf_counter() - verstreken_tijd
    laatste_opslag_tijd = perf_counter()
    toon_melding("Je vorige potje is geladen!")
    return True


def toon_melding(tekst, duur=2.0):
    """Laat even een korte boodschap zien."""
    global melding_tijd

    melding_tekst.text = tekst
    melding_tijd = duur


def maak_tijd_tekst(seconden):
    """Zet seconden om naar minuten en seconden."""
    hele_seconden = int(seconden)
    minuten = hele_seconden // 60
    rest_seconden = hele_seconden % 60
    return f"{minuten}:{rest_seconden:02d}"


def zet_speler_terug(tekst):
    """Zet de speler terug op het laatste veilige punt."""
    player.position = Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)
    player.rotation_y = 0
    player.camera_pivot.rotation_x = 0
    player.air_time = 0
    toon_melding(tekst)


def herstart_spel():
    """Begin helemaal opnieuw vanaf het eerste blok."""
    global spawn_punt, gehaalde_sterren, gewonnen, start_tijd, eind_tijd, verzamelde_sterren

    spawn_punt = Vec3(START_PUNT.x, START_PUNT.y, START_PUNT.z)
    gehaalde_sterren = 0
    verzamelde_sterren = set()
    gewonnen = False
    start_tijd = perf_counter()
    eind_tijd = None
    player.speed = START_SNELHEID
    mouse.locked = True
    einde_tekst.text = ""

    for checkpoint in checkpoints:
        checkpoint.actief = False
        checkpoint.color = color.rgb(100, 140, 255)

    maak_sterren_opnieuw()
    zet_speler_terug("Nieuw potje! Pak alle 3 de sterren.")
    bewaar_voortgang()


def update_status():
    """Werk de tekst linksboven bij met score en tijd."""
    huidig_einde = eind_tijd if eind_tijd is not None else perf_counter()
    status_tekst.text = (
        f"Sterren: {gehaalde_sterren}/{TOTAAL_STERREN}\n"
        f"Tijd: {maak_tijd_tekst(huidig_einde - start_tijd)}"
    )


maak_wereld()

# De speler kijkt in first person, alsof je zelf in het spel staat.
player = FirstPersonController(position=START_PUNT)
player.speed = START_SNELHEID
player.jump_height = 2.2
player.jump_up_duration = 0.35
player.gravity = 1
player.cursor.color = color.black

uitleg_tekst = Text(
    parent=camera.ui,
    text=(
        "Wolken Parkour 3D\n"
        "WASD = lopen\n"
        "Muis = kijken\n"
        "Spatie = springen\n"
        "R = opnieuw"
    ),
    x=-0.86,
    y=0.45,
    scale=1.1,
)

status_tekst = Text(parent=camera.ui, x=-0.86, y=0.2, scale=1.1)
melding_tekst = Text(parent=camera.ui, y=0.38, origin=(0, 0), scale=1.8, color=color.white)
einde_tekst = Text(parent=camera.ui, y=0.08, origin=(0, 0), scale=2.2, color=color.yellow)

maak_sterren_opnieuw()
if not laad_voortgang():
    toon_melding("Spring van blok naar blok en pak 3 sterren!")


def input(key):
    """Luister naar toetsen die iets speciaals moeten doen."""
    if key == "r":
        herstart_spel()


def update():
    """Deze functie draait steeds opnieuw terwijl het spel loopt."""
    global gehaalde_sterren, spawn_punt, gewonnen, eind_tijd, melding_tijd

    if melding_tijd > 0:
        melding_tijd -= time.dt
        if melding_tijd <= 0 and not gewonnen:
            melding_tekst.text = ""

    if not gewonnen and player.y < -8:
        zet_speler_terug("Oeps! Je viel naar beneden.")

    for ster in list(sterren):
        if distance(player, ster) < 1.4:
            destroy(ster)
            sterren.remove(ster)
            verzamelde_sterren.add(ster.nummer)
            gehaalde_sterren += 1
            toon_melding(f"Goed gedaan! Ster {gehaalde_sterren} gepakt.")
            bewaar_voortgang()

    for nummer, checkpoint in enumerate(checkpoints, start=1):
        if not checkpoint.actief and distance(player.position, checkpoint.position + Vec3(0, 1.2, 0)) < 1.8:
            checkpoint.actief = True
            checkpoint.color = color.lime
            spawn_punt = Vec3(checkpoint.x, checkpoint.y + 2, checkpoint.z)
            toon_melding(f"Checkpoint {nummer} gehaald!")
            bewaar_voortgang()

    if not gewonnen and distance(player.position, DOEL_POSITIE) < 2.5:
        if gehaalde_sterren == TOTAAL_STERREN:
            gewonnen = True
            eind_tijd = perf_counter()
            player.speed = 0
            mouse.locked = False
            melding_tekst.text = ""
            einde_tekst.text = (
                "Jij hebt gewonnen!\n"
                f"Tijd: {maak_tijd_tekst(eind_tijd - start_tijd)}\n"
                "Druk op R voor een nieuw potje."
            )
            wis_opslag()
        elif melding_tijd <= 0:
            toon_melding("Pak eerst alle sterren voor je naar de finish gaat!")

    if not gewonnen and perf_counter() - laatste_opslag_tijd >= AUTO_OPSLAAN_TIJD:
        bewaar_voortgang()

    update_status()


if __name__ == "__main__":
    app.run()
