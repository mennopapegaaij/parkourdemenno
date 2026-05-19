"""Wolken Parkour 3D - een lang 3D parkourspel."""

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
BAAN_VERSIE = 2
START_PUNT = Vec3(0, 2, 0)
START_SNELHEID = 7
AUTO_OPSLAAN_TIJD = 1.0
OPSLAG_BESTAND = Path(__file__).with_name("savegame.json")

AANTAL_FASES = 10
SPRONGEN_PER_FASE = 130
TOTAAL_SPRONGEN = AANTAL_FASES * SPRONGEN_PER_FASE
CHECKPOINT_INTERVAL = 50

FASE_NAMEN = [
    "makkelijke start",
    "zachte bochten",
    "trap omhoog",
    "smalle zigzag",
    "grote bochten",
    "muur links",
    "muur rechts",
    "muren slalom",
    "hoge slinger",
    "eindbaas",
]

FASE_KLEUREN = [
    color.azure,
    color.lime,
    color.orange,
    color.cyan,
    color.violet,
    color.rgb(255, 170, 80),
    color.rgb(120, 220, 255),
    color.rgb(255, 110, 160),
    color.rgb(255, 215, 110),
    color.rgb(255, 100, 100),
]

FASE_SCHALEN = [
    (6.8, 6.8),
    (6.2, 6.0),
    (5.8, 5.6),
    (5.0, 4.8),
    (4.5, 4.4),
    (3.4, 3.2),
    (3.2, 3.0),
    (2.8, 2.8),
    (2.5, 2.5),
    (2.3, 2.4),
]

FASE_GAPS = [1.8, 1.95, 2.1, 2.25, 2.4, 2.55, 2.7, 2.85, 3.0, 3.1]

FASE_Z_PATROON = [
    [0.0, 0.4, 0.0, -0.4],
    [0.0, 1.0, 1.8, 1.0, 0.0, -1.0, -1.8, -1.0],
    [0.0, 0.8, 1.6, 2.4, 1.6, 0.8, 0.0, -0.8, -1.6, -2.4, -1.6, -0.8],
    [0.0, 1.6, 3.0, 1.6, 0.0, -1.6, -3.0, -1.6],
    [0.0, 2.2, 4.2, 2.2, 0.0, -2.2, -4.2, -2.2],
    [3.6, 4.2, 5.0, 5.6, 5.0, 4.2],
    [-3.6, -4.2, -5.0, -5.6, -5.0, -4.2],
    [4.2, 5.1, 4.2, 2.0, 0.0, -2.0, -4.2, -5.1, -4.2, -2.0, 0.0, 2.0],
    [0.0, 2.8, 5.0, 2.8, 0.0, -2.8, -5.0, -2.8],
    [0.0, 2.4, 4.8, 6.0, 4.8, 2.4, 0.0, -2.4, -4.8, -6.0, -4.8, -2.4],
]

FASE_Y_PATROON = [
    [0.0, 0.0, 0.1, 0.1],
    [0.0, 0.1, 0.2, 0.1, 0.0, 0.1, 0.2, 0.1],
    [0.0, 0.15, 0.3, 0.45, 0.6, 0.45, 0.3, 0.15],
    [0.0, 0.2, 0.4, 0.2, 0.0, 0.2, 0.4, 0.2],
    [0.1, 0.3, 0.5, 0.3, 0.1, 0.3, 0.5, 0.3],
    [0.0, 0.1, 0.25, 0.4, 0.25, 0.1],
    [0.0, 0.1, 0.25, 0.4, 0.25, 0.1],
    [0.2, 0.35, 0.5, 0.35, 0.2, 0.35, 0.5, 0.35, 0.2, 0.35, 0.5, 0.35],
    [0.0, 0.2, 0.45, 0.7, 0.45, 0.2, -0.1, 0.2],
    [0.1, 0.35, 0.6, 0.85, 0.6, 0.35, 0.1, 0.35, 0.6, 0.85, 0.6, 0.35],
]


def vec3_van(positie):
    """Maak van een tuple makkelijk een Vec3."""
    return Vec3(positie[0], positie[1], positie[2])


def voeg_muren_toe(muur_data, fase, x, y, breedte, gap, z):
    """Maak muurstukken voor de fases waar je langs muren moet springen."""
    muur_lengte = breedte + gap + 2.5
    muur_kleur = color.rgba(235, 235, 255, 170)

    if fase == 5:
        muur_data.append(
            {"positie": (x, y + 3.4, 7.2), "schaal": (muur_lengte, 7.0, 1.2), "kleur": muur_kleur}
        )
    elif fase == 6:
        muur_data.append(
            {"positie": (x, y + 3.4, -7.2), "schaal": (muur_lengte, 7.0, 1.2), "kleur": muur_kleur}
        )
    elif fase == 7:
        muur_data.append(
            {"positie": (x, y + 3.7, 7.4), "schaal": (muur_lengte, 7.4, 1.2), "kleur": muur_kleur}
        )
        muur_data.append(
            {"positie": (x, y + 3.7, -7.4), "schaal": (muur_lengte, 7.4, 1.2), "kleur": muur_kleur}
        )
    elif fase == 8:
        actieve_kant = 7.5 if z >= 0 else -7.5
        muur_data.append(
            {"positie": (x, y + 4.0, actieve_kant), "schaal": (muur_lengte, 8.0, 1.2), "kleur": muur_kleur}
        )
    elif fase == 9:
        muur_data.append(
            {"positie": (x, y + 4.2, 7.8), "schaal": (muur_lengte, 8.4, 1.2), "kleur": muur_kleur}
        )
        muur_data.append(
            {"positie": (x, y + 4.2, -7.8), "schaal": (muur_lengte, 8.4, 1.2), "kleur": muur_kleur}
        )


def bouw_baangegevens():
    """Bouw een baan die van makkelijk naar moeilijk gaat en 100 keer zo lang is."""
    platform_data = [{"positie": (0.0, 0.0, 0.0), "schaal": (9.0, 1.0, 9.0), "kleur": color.azure}]
    muur_data = []
    checkpoint_posities = []
    ster_posities = []
    fase_eindes = []

    x = 0.0
    y = 0.0
    z = 0.0
    vorige_breedte = 9.0

    for fase in range(AANTAL_FASES):
        basis_y = fase * 2.2
        basis_breedte, basis_diepte = FASE_SCHALEN[fase]
        z_pat = FASE_Z_PATROON[fase]
        y_pat = FASE_Y_PATROON[fase]

        for stap in range(SPRONGEN_PER_FASE):
            wereld_stap = fase * SPRONGEN_PER_FASE + stap + 1

            breedte = max(2.1, basis_breedte - (stap % 4) * 0.08)
            diepte = max(2.2, basis_diepte - (stap % 3) * 0.06)
            gap = FASE_GAPS[fase] + (stap % 3) * 0.12

            x += vorige_breedte / 2 + gap + breedte / 2
            y = basis_y + y_pat[stap % len(y_pat)]
            z = z_pat[stap % len(z_pat)]

            if fase >= 8 and stap % 11 == 5:
                y += 0.2

            platform_data.append(
                {"positie": (x, y, z), "schaal": (breedte, 1.0, diepte), "kleur": FASE_KLEUREN[fase]}
            )
            voeg_muren_toe(muur_data, fase, x, y, breedte, gap, z)

            if wereld_stap % CHECKPOINT_INTERVAL == 0:
                checkpoint_posities.append((x, y + 0.7, z))

            if stap == SPRONGEN_PER_FASE - 1:
                ster_posities.append((x, y + 1.6, z))

            vorige_breedte = breedte

        fase_eindes.append(x)

    finish_x = x + vorige_breedte / 2 + 8.0
    finish_y = y + 0.3
    finish_z = z

    platform_data.append({"positie": (finish_x, finish_y, finish_z), "schaal": (12.0, 1.0, 12.0), "kleur": color.gold})
    doel_positie = Vec3(finish_x, finish_y + 2.2, finish_z)
    return platform_data, muur_data, checkpoint_posities, ster_posities, fase_eindes, doel_positie


PLATFORM_DATA, MUUR_DATA, CHECKPOINT_POSITIES, STER_POSITIES, FASE_EINDES, DOEL_POSITIE = bouw_baangegevens()
TOTAAL_STERREN = len(STER_POSITIES)

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


def maak_muur(positie, schaal, kleur_blok):
    """Maak een hoge muur langs de springroute."""
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
            scale=0.8,
            collider="sphere",
        )
        self.nummer = nummer
        self.basis_y = self.y
        self.fase = nummer * 0.4

    def update(self):
        self.rotation_y += 140 * time.dt
        self.y = self.basis_y + 0.18 * sin(perf_counter() * 3 + self.fase)


def maak_wolken():
    """Maak wolken langs de hele lange baan."""
    wolk_kleur = color.rgba(255, 255, 255, 170)
    wolk_x = -60

    while wolk_x <= DOEL_POSITIE.x + 120:
        z_basis = 16 if int(wolk_x / 220) % 2 == 0 else -16
        Entity(model="sphere", color=wolk_kleur, position=(wolk_x, 18, z_basis), scale=(12, 4, 7))
        Entity(model="sphere", color=wolk_kleur, position=(wolk_x + 8, 20, z_basis + 3), scale=(10, 3, 6))
        Entity(model="sphere", color=wolk_kleur, position=(wolk_x - 6, 19, z_basis - 4), scale=(9, 3, 5))
        wolk_x += 220


def maak_wereld():
    """Bouw de hele parkourwereld."""
    Sky()
    AmbientLight(color=color.rgba(180, 180, 220, 120))
    DirectionalLight(y=25, z=10, rotation=(45, -35, 0))

    # Dit is de mist onder de baan. Als je daaronder valt, ga je terug.
    Entity(
        model="plane",
        position=(DOEL_POSITIE.x / 2, -14, 0),
        scale=DOEL_POSITIE.x * 2.4,
        color=color.red.tint(-0.15),
    )

    for blok in PLATFORM_DATA:
        maak_platform(blok["positie"], blok["schaal"], blok["kleur"])

    for muur in MUUR_DATA:
        maak_muur(muur["positie"], muur["schaal"], muur["kleur"])

    for positie in CHECKPOINT_POSITIES:
        checkpoint = Entity(
            model="cube",
            texture="white_cube",
            color=color.rgb(100, 140, 255),
            position=vec3_van(positie),
            scale=(2.8, 0.3, 2.8),
            collider="box",
        )
        checkpoint.actief = False
        checkpoints.append(checkpoint)

    # Deze vlag laat zien waar het einde van de baan is.
    Entity(model="cube", position=(DOEL_POSITIE.x, DOEL_POSITIE.y + 1.0, DOEL_POSITIE.z), scale=(0.25, 7, 0.25), color=color.white)
    Entity(model="cube", position=(DOEL_POSITIE.x + 1.1, DOEL_POSITIE.y + 3.6, DOEL_POSITIE.z), scale=(2.4, 1.4, 0.15), color=color.red)
    Entity(model="sphere", position=DOEL_POSITIE, scale=1.7, color=color.yellow)

    maak_wolken()


def maak_sterren_opnieuw():
    """Zet alle sterren terug die nog niet gepakt zijn."""
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
        "baan_versie": BAAN_VERSIE,
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
        wis_opslag()
        print("Het opslagbestand was stuk. Het spel begint opnieuw.")
        return False
    except OSError:
        print("Het opslagbestand kon niet gelezen worden. Het spel begint opnieuw.")
        return False

    if opslag.get("baan_versie") != BAAN_VERSIE:
        wis_opslag()
        print("Er is een nieuwe baan. Je begint opnieuw op het eerste blok.")
        return False

    verzamelde_lijst = opslag.get("verzamelde_sterren", [])
    checkpoint_lijst = opslag.get("actieve_checkpoints", [])

    if not isinstance(verzamelde_lijst, list) or not isinstance(checkpoint_lijst, list):
        wis_opslag()
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
    player.air_time = 0

    for nummer, checkpoint in enumerate(checkpoints):
        checkpoint.actief = nummer < len(checkpoint_lijst) and bool(checkpoint_lijst[nummer])
        checkpoint.color = color.lime if checkpoint.actief else color.rgb(100, 140, 255)

    maak_sterren_opnieuw()

    verstreken_tijd = max(0.0, lees_getal(opslag.get("verstreken_tijd"), 0.0))
    start_tijd = perf_counter() - verstreken_tijd
    laatste_opslag_tijd = perf_counter()
    toon_melding("Je vorige potje is geladen!")
    return True


def toon_melding(tekst, duur=2.4):
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


def huidige_fase_nummer():
    """Kijk in welk stuk van de baan je ongeveer bent."""
    for nummer, eind_x in enumerate(FASE_EINDES, start=1):
        if player.x <= eind_x:
            return nummer
    return AANTAL_FASES


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
    zet_speler_terug("Nieuw potje! Klaar voor de superlange baan?")
    bewaar_voortgang()


def update_status():
    """Werk de tekst linksboven bij met score, tijd en voortgang."""
    huidig_einde = eind_tijd if eind_tijd is not None else perf_counter()
    voortgang = int(max(0, min(100, (player.x / DOEL_POSITIE.x) * 100)))
    fase_nummer = huidige_fase_nummer()
    status_tekst.text = (
        f"Sterren: {gehaalde_sterren}/{TOTAAL_STERREN}\n"
        f"Tijd: {maak_tijd_tekst(huidig_einde - start_tijd)}\n"
        f"Voortgang: {voortgang}%\n"
        f"Fase {fase_nummer}/{AANTAL_FASES}: {FASE_NAMEN[fase_nummer - 1]}"
    )


maak_wereld()

# De speler kijkt in first person, alsof je zelf in het spel staat.
player = FirstPersonController(position=START_PUNT)
player.speed = START_SNELHEID
player.jump_height = 2.25
player.jump_up_duration = 0.35
player.gravity = 1
player.cursor.color = color.black

uitleg_tekst = Text(
    parent=camera.ui,
    text=(
        "Wolken Parkour 3D\n"
        "1300 sprongen\n"
        "Van makkelijk naar moeilijk\n"
        "Ook langs muren springen\n"
        "WASD + muis + spatie\n"
        "R = opnieuw"
    ),
    x=-0.86,
    y=0.38,
    scale=1.05,
)

status_tekst = Text(parent=camera.ui, x=-0.86, y=0.08, scale=1.05)
melding_tekst = Text(parent=camera.ui, y=0.38, origin=(0, 0), scale=1.8, color=color.white)
einde_tekst = Text(parent=camera.ui, y=0.08, origin=(0, 0), scale=2.0, color=color.yellow)

maak_sterren_opnieuw()
if not laad_voortgang():
    toon_melding("Deze baan is nu 100 keer zo lang. Succes!")


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
        if distance(player, ster) < 1.5:
            destroy(ster)
            sterren.remove(ster)
            verzamelde_sterren.add(ster.nummer)
            gehaalde_sterren += 1
            toon_melding(f"Goed gedaan! Ster {gehaalde_sterren} gepakt.")
            bewaar_voortgang()

    for nummer, checkpoint in enumerate(checkpoints, start=1):
        if not checkpoint.actief and distance(player.position, checkpoint.position + Vec3(0, 1.2, 0)) < 1.9:
            checkpoint.actief = True
            checkpoint.color = color.lime
            spawn_punt = Vec3(checkpoint.x, checkpoint.y + 2, checkpoint.z)
            toon_melding(f"Checkpoint {nummer} gehaald!")
            bewaar_voortgang()

    if not gewonnen and distance(player.position, DOEL_POSITIE) < 3.0:
        if gehaalde_sterren == TOTAAL_STERREN:
            gewonnen = True
            eind_tijd = perf_counter()
            player.speed = 0
            mouse.locked = False
            melding_tekst.text = ""
            einde_tekst.text = (
                "Jij hebt gewonnen!\n"
                f"Tijd: {maak_tijd_tekst(eind_tijd - start_tijd)}\n"
                "Je hebt de 100x lange baan gehaald!\n"
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
