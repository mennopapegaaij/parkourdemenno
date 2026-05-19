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
    raycast,
    time,
    window,
)
from ursina.prefabs.first_person_controller import FirstPersonController

TITEL = "Wolken Parkour 3D"
BAAN_VERSIE = 5
START_PUNT = Vec3(0, 2, 0)
START_SNELHEID = 7
AUTO_OPSLAAN_TIJD = 1.0
OPSLAG_BESTAND = Path(__file__).with_name("savegame.json")
LAAD_AFSTAND_VOORUIT = 180
LAAD_AFSTAND_ACHTERUIT = 110
LAAD_VERNIEUW_AFSTAND = 20
SPRINGBLOK_INTERVAL = 8
SPRINGBLOK_STAP = 6
SPRINGBLOK_COOLDOWN = 0.7
MUURSPRONG_COOLDOWN = 0.35
SPRINGBLOK_SCHAAL = (1.7, 0.35, 1.7)
OBSTAKEL_MUUR_INTERVAL = 9
OBSTAKEL_MUUR_START_LEVEL = 18
OBSTAKEL_PAD_Z = 5.8

STIJL_NAMEN = [
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

STIJL_KLEUREN = [
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

STIJL_Z_PATROON = [
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

STIJL_Y_PATROON = [
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

AANTAL_LEVELS = 100
SPRONGEN_PER_LEVEL = 13
TOTAAL_SPRONGEN = AANTAL_LEVELS * SPRONGEN_PER_LEVEL
CHECKPOINT_INTERVAL = SPRONGEN_PER_LEVEL
STER_INTERVAL = 10

BEGIN_SCHAAL = (6.8, 6.8)
EIND_SCHAAL = (2.3, 2.4)
BEGIN_GAP = 1.8
EIND_GAP = 3.1
STARTPLATFORM_SCHAAL = 9.0
FINISH_PLATFORM_SCHAAL = 12.0

MOEILIJKHEID_NAMEN = [
    "heel makkelijk",
    "makkelijk",
    "spannend",
    "lastig",
    "superslim",
]

HOOGTE_PATROONEN = [
    [0.0, 0.2, 0.6, 1.0, 1.5, 2.0, 1.5, 1.0, 0.6, 0.2, 0.8, 1.4, 2.1],
    [0.0, -0.3, -0.8, -1.2, -1.6, -1.1, -0.5, 0.1, 0.8, 1.4, 1.9, 1.2, 0.4],
    [0.0, 0.6, 1.2, 1.8, 1.0, 0.2, -0.4, 0.4, 1.2, 2.0, 1.4, 0.8, 0.0],
]


def vec3_van(positie):
    """Maak van een tuple makkelijk een Vec3."""
    return Vec3(positie[0], positie[1], positie[2])


def voeg_muren_toe(muur_data, level_nummer, stijl, x, y, breedte, gap, z):
    """Maak muurstukken voor de levels waar je langs muren moet springen."""
    muur_lengte = breedte + gap + 2.5
    muur_kleur = color.rgba(235, 235, 255, 170)

    if level_nummer < 55:
        return

    if stijl == 5:
        muur_data.append(
            {"positie": (x, y + 3.4, 7.2), "schaal": (muur_lengte, 7.0, 1.2), "kleur": muur_kleur}
        )
    elif stijl == 6:
        muur_data.append(
            {"positie": (x, y + 3.4, -7.2), "schaal": (muur_lengte, 7.0, 1.2), "kleur": muur_kleur}
        )
    elif stijl == 7:
        muur_data.append(
            {"positie": (x, y + 3.7, 7.4), "schaal": (muur_lengte, 7.4, 1.2), "kleur": muur_kleur}
        )
        muur_data.append(
            {"positie": (x, y + 3.7, -7.4), "schaal": (muur_lengte, 7.4, 1.2), "kleur": muur_kleur}
        )
    elif stijl == 8:
        actieve_kant = 7.5 if z >= 0 else -7.5
        muur_data.append(
            {"positie": (x, y + 4.0, actieve_kant), "schaal": (muur_lengte, 8.0, 1.2), "kleur": muur_kleur}
        )
    elif stijl == 9:
        muur_data.append(
            {"positie": (x, y + 4.2, 7.8), "schaal": (muur_lengte, 8.4, 1.2), "kleur": muur_kleur}
        )
        muur_data.append(
            {"positie": (x, y + 4.2, -7.8), "schaal": (muur_lengte, 8.4, 1.2), "kleur": muur_kleur}
        )


def voeg_blokkade_muur_toe(muur_data, x, y, gap, breedte):
    """Maak een muur midden op de route waar je langs moet springen."""
    muur_data.append(
        {
            "positie": (x - breedte / 2 - gap / 2, y + 4.1, 0.0),
            "schaal": (1.2, 8.2, 7.2),
            "kleur": color.rgba(255, 245, 210, 190),
        }
    )


def bouw_baangegevens():
    """Bouw een baan met veel korte levels die steeds moeilijker worden."""
    platform_data = [{"positie": (0.0, 0.0, 0.0), "schaal": (STARTPLATFORM_SCHAAL, 1.0, STARTPLATFORM_SCHAAL), "kleur": color.azure}]
    muur_data = []
    springblok_posities = []
    checkpoint_posities = []
    ster_posities = []
    level_eindes = []

    x = 0.0
    y = 0.0
    z = 0.0
    vorige_breedte = STARTPLATFORM_SCHAAL

    for level in range(AANTAL_LEVELS):
        moeilijkheid = level / max(1, AANTAL_LEVELS - 1)
        stijl = level % len(STIJL_NAMEN)
        heeft_springblok = level >= 12 and (level + 1) % SPRINGBLOK_INTERVAL == 0
        heeft_blokkade_muur = level >= OBSTAKEL_MUUR_START_LEVEL and (level + 1) % OBSTAKEL_MUUR_INTERVAL == 0
        blokkade_kant = OBSTAKEL_PAD_Z if (level // OBSTAKEL_MUUR_INTERVAL) % 2 == 0 else -OBSTAKEL_PAD_Z
        grote_sprong_stappen = 0
        basis_y = level * 0.32 + (level // 10) * 0.35
        z_pat = STIJL_Z_PATROON[stijl]
        y_pat = STIJL_Y_PATROON[stijl]
        hoogte_pat = HOOGTE_PATROONEN[level % len(HOOGTE_PATROONEN)]
        hoogte_schaal = 1.0 + moeilijkheid * 1.7
        basis_breedte = BEGIN_SCHAAL[0] + (EIND_SCHAAL[0] - BEGIN_SCHAAL[0]) * moeilijkheid
        basis_diepte = BEGIN_SCHAAL[1] + (EIND_SCHAAL[1] - BEGIN_SCHAAL[1]) * moeilijkheid

        for stap in range(SPRONGEN_PER_LEVEL):
            wereld_stap = level * SPRONGEN_PER_LEVEL + stap + 1

            breedte = max(2.1, basis_breedte - (stap % 4) * 0.08)
            diepte = max(2.2, basis_diepte - (stap % 3) * 0.06)
            gap = BEGIN_GAP + (EIND_GAP - BEGIN_GAP) * moeilijkheid + (stap % 3) * 0.12
            extra_hoogte = 0.0

            if grote_sprong_stappen > 0:
                gap += 1.0
                extra_hoogte = 0.7 if grote_sprong_stappen == 2 else 0.35

            x += vorige_breedte / 2 + gap + breedte / 2
            hoogte_bonus = hoogte_pat[stap % len(hoogte_pat)] * (0.25 + moeilijkheid * 0.35)
            y = basis_y + y_pat[stap % len(y_pat)] * hoogte_schaal + hoogte_bonus + extra_hoogte
            z = z_pat[stap % len(z_pat)]

            if heeft_blokkade_muur and stap in (4, 5, 6):
                z = blokkade_kant + (0.8 if stap == 5 else 0.0)
            elif heeft_blokkade_muur and stap in (7, 8):
                z = blokkade_kant * 0.55

            if level >= 80 and stap % 11 == 5:
                y += 0.55
            elif level >= 45 and stap % 9 == 4:
                y += 0.35

            platform_data.append(
                {"positie": (x, y, z), "schaal": (breedte, 1.0, diepte), "kleur": STIJL_KLEUREN[stijl]}
            )
            voeg_muren_toe(muur_data, level, stijl, x, y, breedte, gap, z)
            if heeft_blokkade_muur and stap == 4:
                voeg_blokkade_muur_toe(muur_data, x, y, gap, breedte)

            if heeft_springblok and stap == SPRINGBLOK_STAP:
                springblok_posities.append((x, y + 0.7, z))
                grote_sprong_stappen = 2
            elif grote_sprong_stappen > 0:
                grote_sprong_stappen -= 1

            if wereld_stap % CHECKPOINT_INTERVAL == 0:
                checkpoint_posities.append((x, y + 0.7, z))

            if (level + 1) % STER_INTERVAL == 0 and stap == SPRONGEN_PER_LEVEL - 1:
                ster_posities.append((x, y + 1.6, z))

            vorige_breedte = breedte

        level_eindes.append(x)

    finish_x = x + vorige_breedte / 2 + 8.0
    finish_y = y + 0.3
    finish_z = z

    platform_data.append(
        {"positie": (finish_x, finish_y, finish_z), "schaal": (FINISH_PLATFORM_SCHAAL, 1.0, FINISH_PLATFORM_SCHAAL), "kleur": color.gold}
    )
    doel_positie = Vec3(finish_x, finish_y + 2.2, finish_z)
    return platform_data, muur_data, springblok_posities, checkpoint_posities, ster_posities, level_eindes, doel_positie


PLATFORM_DATA, MUUR_DATA, SPRINGBLOK_POSITIES, CHECKPOINT_POSITIES, STER_POSITIES, LEVEL_EINDES, DOEL_POSITIE = bouw_baangegevens()
TOTAAL_STERREN = len(STER_POSITIES)

app = Ursina()
window.title = TITEL
window.borderless = False
window.color = color.rgb(145, 205, 255)
window.exit_button.visible = False
window.fps_counter.enabled = True
camera.fov = 95

sterren = []
springblokken = []
checkpoints = []
verzamelde_sterren = set()
actieve_platforms = {}
actieve_muren = {}
spawn_punt = Vec3(START_PUNT.x, START_PUNT.y, START_PUNT.z)
gehaalde_sterren = 0
gewonnen = False
start_tijd = perf_counter()
eind_tijd = None
melding_tijd = 0.0
laatste_opslag_tijd = 0.0
laatste_laad_x = None
laatste_springblok_tijd = 0.0
laatste_muursprong_tijd = 0.0


def maak_platform(positie, schaal, kleur_blok):
    """Maak een springblok waar de speler op kan landen."""
    blok = Entity(
        model="cube",
        texture="white_cube",
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )
    blok.is_muur = False
    return blok


def maak_muur(positie, schaal, kleur_blok):
    """Maak een hoge muur langs de springroute."""
    muur = Entity(
        model="cube",
        texture="white_cube",
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )
    muur.is_muur = True
    return muur


def maak_springblok(positie):
    """Maak een groen blok dat je extra ver omhoog schiet."""
    blok = Entity(
        model="cube",
        texture="white_cube",
        color=color.rgb(80, 255, 120),
        position=vec3_van(positie),
        scale=SPRINGBLOK_SCHAAL,
        collider="box",
    )
    blok.is_muur = False
    return blok


def vernieuw_actieve_lijst(bron_data, actieve_lijst, maker, minimum_x, maximum_x):
    """Houd alleen de blokken actief die dicht bij de speler zijn."""
    gewenste_indexen = set()

    for index, data in enumerate(bron_data):
        positie_x = data["positie"][0]
        halve_breedte = data["schaal"][0] / 2

        if positie_x + halve_breedte < minimum_x or positie_x - halve_breedte > maximum_x:
            continue

        gewenste_indexen.add(index)
        if index not in actieve_lijst:
            actieve_lijst[index] = maker(data["positie"], data["schaal"], data["kleur"])

    for index in list(actieve_lijst):
        if index not in gewenste_indexen:
            destroy(actieve_lijst.pop(index))


def vernieuw_actieve_baan(force=False):
    """Laad alleen het stukje baan dat om de speler heen zit."""
    global laatste_laad_x

    if not force and laatste_laad_x is not None:
        if abs(player.x - laatste_laad_x) < LAAD_VERNIEUW_AFSTAND:
            return

    minimum_x = player.x - LAAD_AFSTAND_ACHTERUIT
    maximum_x = player.x + LAAD_AFSTAND_VOORUIT
    vernieuw_actieve_lijst(PLATFORM_DATA, actieve_platforms, maak_platform, minimum_x, maximum_x)
    vernieuw_actieve_lijst(MUUR_DATA, actieve_muren, maak_muur, minimum_x, maximum_x)
    laatste_laad_x = player.x


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

    for positie in SPRINGBLOK_POSITIES:
        springblokken.append(maak_springblok(positie))

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
    vernieuw_actieve_baan(force=True)

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


def gebruik_springblok():
    """Schiet de speler omhoog en vooruit vanaf een groen blok."""
    global laatste_springblok_tijd

    speler_hoogte = player.position + Vec3(0, 1.0, 0)
    nu = perf_counter()

    if nu - laatste_springblok_tijd < SPRINGBLOK_COOLDOWN or not player.grounded:
        return

    for springblok in springblokken:
        if distance(speler_hoogte, springblok.position) < 1.4:
            player.position = player.position + Vec3(5.0, 4.2, 0)
            player.air_time = 0
            laatste_springblok_tijd = nu
            vernieuw_actieve_baan(force=True)
            toon_melding("Boing! Super sprong!")
            return


def vind_muursprong():
    """Kijk of er vlak naast de speler een muur zit voor een muursprong."""
    startpunt = player.position + Vec3(0, 1.1, 0)
    richtingen = [
        (Vec3(0, 0, 1), Vec3(2.7, 2.3, -2.6)),
        (Vec3(0, 0, -1), Vec3(2.7, 2.3, 2.6)),
    ]

    for richting, sprong in richtingen:
        raak = raycast(startpunt, richting, distance=1.3, ignore=(player,))
        if raak.hit and getattr(raak.entity, "is_muur", False):
            return sprong

    return None


def doe_muursprong():
    """Spring van een muur af als je in de lucht bent en op spatie drukt."""
    global laatste_muursprong_tijd

    nu = perf_counter()
    if player.grounded or nu - laatste_muursprong_tijd < MUURSPRONG_COOLDOWN:
        return False

    sprong = vind_muursprong()
    if sprong is None:
        return False

    player.position = player.position + sprong
    player.air_time = 0
    laatste_muursprong_tijd = nu
    vernieuw_actieve_baan(force=True)
    toon_melding("Muursprong!")
    return True


def maak_tijd_tekst(seconden):
    """Zet seconden om naar minuten en seconden."""
    hele_seconden = int(seconden)
    minuten = hele_seconden // 60
    rest_seconden = hele_seconden % 60
    return f"{minuten}:{rest_seconden:02d}"


def huidige_level_nummer():
    """Kijk in welk level van de baan je ongeveer bent."""
    for nummer, eind_x in enumerate(LEVEL_EINDES, start=1):
        if player.x <= eind_x:
            return nummer
    return AANTAL_LEVELS


def moeilijkheid_tekst(level_nummer):
    """Geef een kort woord voor hoe moeilijk het nu is."""
    stap = (level_nummer - 1) / max(1, AANTAL_LEVELS - 1)
    index = min(len(MOEILIJKHEID_NAMEN) - 1, int(stap * len(MOEILIJKHEID_NAMEN)))
    return MOEILIJKHEID_NAMEN[index]


def zet_speler_terug(tekst):
    """Zet de speler terug op het laatste veilige punt."""
    player.position = Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)
    player.rotation_y = 0
    player.camera_pivot.rotation_x = 0
    player.air_time = 0
    vernieuw_actieve_baan(force=True)
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
    """Werk de tekst linksboven bij met score, tijd en level."""
    huidig_einde = eind_tijd if eind_tijd is not None else perf_counter()
    voortgang = int(max(0, min(100, (player.x / DOEL_POSITIE.x) * 100)))
    level_nummer = huidige_level_nummer()
    stijl_nummer = (level_nummer - 1) % len(STIJL_NAMEN)
    status_tekst.text = (
        f"Sterren: {gehaalde_sterren}/{TOTAAL_STERREN}\n"
        f"Tijd: {maak_tijd_tekst(huidig_einde - start_tijd)}\n"
        f"Voortgang: {voortgang}%\n"
        f"Level {level_nummer}/{AANTAL_LEVELS}: {STIJL_NAMEN[stijl_nummer]}\n"
        f"Moeilijkheid: {moeilijkheid_tekst(level_nummer)}"
    )


maak_wereld()

# De speler kijkt in first person, alsof je zelf in het spel staat.
player = FirstPersonController(position=START_PUNT)
player.speed = START_SNELHEID
player.jump_height = 2.25
player.jump_up_duration = 0.35
player.gravity = 1
player.cursor.color = color.black
vernieuw_actieve_baan(force=True)

uitleg_tekst = Text(
    parent=camera.ui,
    text=(
        "Wolken Parkour 3D\n"
        "100 korte levels\n"
        "1300 sprongen totaal\n"
        "Groen blok = super sprong\n"
        "Spatie langs muur = muursprong\n"
        "Steeds een nieuw stukje\n"
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
    toon_melding("Nu zijn er veel meer korte levels. Succes!")


def input(key):
    """Luister naar toetsen die iets speciaals moeten doen."""
    if key == "r":
        herstart_spel()
    elif key == "space":
        doe_muursprong()


def update():
    """Deze functie draait steeds opnieuw terwijl het spel loopt."""
    global gehaalde_sterren, spawn_punt, gewonnen, eind_tijd, melding_tijd

    vernieuw_actieve_baan()
    gebruik_springblok()

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
