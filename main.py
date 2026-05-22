"""Wolken Parkour 3D - een lang 3D parkourspel."""

import json
from math import atan2, cos, degrees, pi, radians, sin
from pathlib import Path
from time import perf_counter

from ursina import (
    AmbientLight,
    DirectionalLight,
    Entity,
    Text,
    Ursina,
    Vec3,
    camera,
    color,
    destroy,
    distance,
    held_keys,
    mouse,
    raycast,
    time,
    window,
)
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import unlit_shader

TITEL = "Wolken Parkour 3D"
BAAN_VERSIE = 10
START_PUNT = Vec3(0, 2, 0)
START_SNELHEID = 7
AUTO_OPSLAAN_TIJD = 1.0
OPSLAG_BESTAND = Path(__file__).with_name("savegame.json")
LAAD_HOOGTE_BOVEN = 90
LAAD_HOOGTE_ONDER = 55
LAAD_VERNIEUW_HOOGTE = 14
SPRINGBLOK_INTERVAL = 8
SPRINGBLOK_STAP = 6
SPRINGBLOK_COOLDOWN = 0.7
MUURSPRONG_COOLDOWN = 0.35
SPRINGBLOK_SCHAAL = (1.7, 0.35, 1.7)
OBSTAKEL_MUUR_INTERVAL = 9
OBSTAKEL_MUUR_START_LEVEL = 18
OBSTAKEL_PAD_Z = 5.8
LADDER_STAP = 5
BOOSTPAD_STAP = 4
BOOSTPAD_COOLDOWN = 0.8
BOOSTPAD_SCHAAL = (2.4, 0.2, 2.4)
SPELER_SPRONGHOOGTE = 2.8
COMPUTER_SPELER_AANTAL = 16
COMPUTER_SPELER_SNELHEID = 10.5
COMPUTER_SPELER_SPRONGHOOGTE = SPELER_SPRONGHOOGTE
COMPUTER_SPELER_START_VERTAGING = 1.2
PARCOURS_VOLGORDE = ["springblok", "boost", "ladder", "spiraal", "blokkade", "muurpad"]
TOREN_STRAAL = 18
TOREN_STRAAL_VARIATIE = 5.5
TOREN_HOEK_BASIS = 12.5

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

REGENBOOG_RGB = [
    (255, 90, 90),
    (255, 160, 70),
    (255, 220, 80),
    (120, 235, 110),
    (90, 220, 255),
    (120, 150, 255),
    (220, 120, 255),
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

# Deze hulpgetallen maken de hele toren vriendelijker van begin tot eind.
SPRONG_HULP_BREEDER = 1.22
SPRONG_HULP_KLEINER_GAT = 0.72
SPRONG_HULP_MINDER_HOOGTE = 0.68
SPRONG_HULP_MINDER_ZIJ = 0.86

MOEILIJKHEID_NAMEN = [
    "heel makkelijk",
    "makkelijk",
    "spannend",
    "lastig",
    "superslim",
]

LEVEL_BIJVOEGLIJK = [
    "draaiende",
    "slimme",
    "wilde",
    "zwevende",
    "steile",
    "bochtige",
    "springende",
    "hoge",
    "smalle",
    "gekke",
]

HOOGTE_PATROONEN = [
    [0.0, 0.6, 1.5, 2.6, 3.8, 5.0, 4.0, 2.8, 1.6, 0.6, 1.8, 3.4, 5.3],
    [0.0, -0.8, -1.8, -3.0, -4.3, -3.1, -1.5, 0.3, 1.8, 3.2, 4.8, 3.0, 1.0],
    [0.0, 1.0, 2.3, 3.8, 2.2, 0.3, -1.0, 0.6, 2.6, 4.5, 3.0, 1.2, 0.0],
    [0.0, 1.5, 3.2, 5.0, 3.0, 0.8, -1.2, 1.1, 3.8, 6.0, 4.1, 1.9, 0.0],
]


def vec3_van(positie):
    """Maak van een tuple makkelijk een Vec3."""
    return Vec3(positie[0], positie[1], positie[2])


def normaliseer_richting(x, z):
    """Maak van x en z een nette richting."""
    lengte = (x * x + z * z) ** 0.5
    if lengte == 0:
        return Vec3(1, 0, 0)
    return Vec3(x / lengte, 0, z / lengte)


def kijk_richting():
    """Kijk in welke richting de speler kijkt op de vloer."""
    hoek = radians(player.rotation_y)
    return normaliseer_richting(sin(hoek), cos(hoek))


def zij_richting():
    """Geef de zijrichting van de speler."""
    richting = kijk_richting()
    return normaliseer_richting(richting.z, -richting.x)


def begrens_kleur(waarde):
    """Zorg dat een kleurkanaal netjes tussen 0.0 en 1.0 blijft."""
    return max(0.0, min(1.0, float(waarde)))


def kleurkanaal_uit_255(waarde):
    """Zet een kleur van 0-255 om naar een kleur die Ursina goed begrijpt."""
    return begrens_kleur(waarde / 255)


def maak_rgb_kleur(rgb, helderheid=1.0, alpha=255):
    """Maak van een rgb-tuple een kleur met meer of minder licht."""
    rood, groen, blauw = rgb
    return color.rgba(
        kleurkanaal_uit_255(rood * helderheid),
        kleurkanaal_uit_255(groen * helderheid),
        kleurkanaal_uit_255(blauw * helderheid),
        kleurkanaal_uit_255(alpha),
    )


def kleur_van_level(level_nummer, helderheid=1.0, alpha=255):
    """Geef elk level een kleur uit de regenboog."""
    return maak_rgb_kleur(REGENBOOG_RGB[level_nummer % len(REGENBOOG_RGB)], helderheid, alpha)


def voeg_muren_toe(muur_data, level_nummer, stijl, x, y, breedte, gap, z):
    """Maak muurstukken voor de levels waar je langs muren moet springen."""
    muur_lengte = breedte + gap + 2.5
    muur_kleur = kleur_van_level(level_nummer, 0.62)
    buiten = normaliseer_richting(x, z)
    zijkant = Vec3(-buiten.z, 0, buiten.x)
    muur_afstand = 3.6 + min(2.4, gap)

    if stijl == 5:
        muur_data.append(
            {
                "positie": (x + zijkant.x * muur_afstand, y + 3.4, z + zijkant.z * muur_afstand),
                "schaal": (3.0, 7.0, 3.0),
                "kleur": muur_kleur,
            }
        )
    elif stijl == 6:
        muur_data.append(
            {
                "positie": (x - zijkant.x * muur_afstand, y + 3.4, z - zijkant.z * muur_afstand),
                "schaal": (3.0, 7.0, 3.0),
                "kleur": muur_kleur,
            }
        )
    elif stijl == 7:
        muur_data.append(
            {
                "positie": (x + zijkant.x * muur_afstand, y + 3.7, z + zijkant.z * muur_afstand),
                "schaal": (3.0, 7.4, 3.0),
                "kleur": muur_kleur,
            }
        )
        muur_data.append(
            {
                "positie": (x - zijkant.x * muur_afstand, y + 3.7, z - zijkant.z * muur_afstand),
                "schaal": (3.0, 7.4, 3.0),
                "kleur": muur_kleur,
            }
        )
    elif stijl == 8:
        muur_data.append(
            {
                "positie": (x + buiten.x * (muur_afstand + 1.2), y + 4.0, z + buiten.z * (muur_afstand + 1.2)),
                "schaal": (3.2, 8.0, 3.2),
                "kleur": muur_kleur,
            }
        )
    elif stijl == 9:
        muur_data.append(
            {
                "positie": (x + zijkant.x * muur_afstand, y + 4.2, z + zijkant.z * muur_afstand),
                "schaal": (muur_lengte * 0.35, 8.4, 3.0),
                "kleur": muur_kleur,
            }
        )
        muur_data.append(
            {
                "positie": (x - zijkant.x * muur_afstand, y + 4.2, z - zijkant.z * muur_afstand),
                "schaal": (muur_lengte * 0.35, 8.4, 3.0),
                "kleur": muur_kleur,
            }
        )


def voeg_blokkade_muur_toe(muur_data, vorige_punt, huidig_punt, level_nummer):
    """Maak een muur midden op de route waar je langs moet springen."""
    midden_x = (vorige_punt.x + huidig_punt.x) / 2
    midden_y = (vorige_punt.y + huidig_punt.y) / 2
    midden_z = (vorige_punt.z + huidig_punt.z) / 2
    muur_data.append(
        {
            "positie": (midden_x, midden_y + 4.1, midden_z),
            "schaal": (3.5, 8.2, 3.5),
            "kleur": kleur_van_level(level_nummer, 0.7),
        }
    )


def voeg_muurpad_toe(muur_data, x, y, z, level_nummer):
    """Maak een lange zijmuur waar je langs moet springen."""
    buiten = normaliseer_richting(x, z)
    muur_data.append(
        {
            "positie": (x + buiten.x * 3.4, y + 3.7, z + buiten.z * 3.4),
            "schaal": (3.0, 7.4, 3.0),
            "kleur": kleur_van_level(level_nummer, 0.66),
        }
    )


def kies_parcours_soort(level):
    """Kies welke speciale soort parcours dit level krijgt."""
    if level < 4:
        return "springblok"
    return PARCOURS_VOLGORDE[(level - 4) % len(PARCOURS_VOLGORDE)]


def maak_level_profiel(level, moeilijkheid):
    """Maak voor elk level een eigen patroon, zodat het niet steeds herhaalt."""
    basis_stijl = level % len(STIJL_NAMEN)
    variant = level // len(STIJL_NAMEN)
    parcours_soort = kies_parcours_soort(level)
    z_basis = STIJL_Z_PATROON[basis_stijl]
    z_mix = STIJL_Z_PATROON[(basis_stijl + variant + 3) % len(STIJL_Z_PATROON)]
    y_basis = STIJL_Y_PATROON[(basis_stijl + variant * 2) % len(STIJL_Y_PATROON)]
    hoogte_basis = HOOGTE_PATROONEN[(level + variant) % len(HOOGTE_PATROONEN)]

    draai_z = (level * 3 + variant) % len(z_basis)
    draai_mix = (level + variant * 2) % len(z_mix)
    draai_y = (level * 2 + variant) % len(y_basis)
    draai_hoogte = (level + basis_stijl) % len(hoogte_basis)

    spiegel = variant % 2 == 1
    z_schaal = (0.82 + moeilijkheid * 0.55 + (variant % 4) * 0.08) * SPRONG_HULP_MINDER_ZIJ
    mix_schaal = (0.18 + (variant % 3) * 0.06) * SPRONG_HULP_MINDER_ZIJ
    y_schaal = (1.35 + moeilijkheid * 2.45 + (variant % 3) * 0.3) * SPRONG_HULP_MINDER_HOOGTE
    hoogte_schaal = (0.5 + moeilijkheid * 0.85 + (variant % 4) * 0.14) * SPRONG_HULP_MINDER_HOOGTE

    z_pat = []
    y_pat = []

    for stap in range(SPRONGEN_PER_LEVEL):
        z_waarde = z_basis[(stap + draai_z) % len(z_basis)] * z_schaal
        mix_waarde = z_mix[(stap + draai_mix) % len(z_mix)] * mix_schaal
        if spiegel:
            z_waarde = -z_waarde
        if (stap + level) % 4 == 0:
            mix_waarde *= -1
        z_pat.append(round(z_waarde + mix_waarde, 2))

        y_waarde = y_basis[(stap + draai_y) % len(y_basis)] * y_schaal
        hoogte_waarde = hoogte_basis[(stap + draai_hoogte) % len(hoogte_basis)] * hoogte_schaal
        if variant % 3 == 2 and stap in (2, 6, 10):
            hoogte_waarde += (0.8 + moeilijkheid * 0.9) * SPRONG_HULP_MINDER_HOOGTE
        if variant % 4 == 1 and stap in (4, 8, 11):
            hoogte_waarde -= (0.7 + moeilijkheid * 0.8) * SPRONG_HULP_MINDER_HOOGTE
        y_pat.append(round(y_waarde + hoogte_waarde, 2))

    level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} {STIJL_NAMEN[basis_stijl]}"
    level_kleur = kleur_van_level(level, 1.0)

    if parcours_soort == "spiraal":
        draai = -1 if variant % 2 else 1
        spiraal_z = [0.0, 1.4, 3.0, 4.8, 5.8, 4.8, 3.0, 0.0, -3.0, -4.8, -5.8, -4.8, -3.0]
        klim = (1.2 + moeilijkheid * 0.8) * SPRONG_HULP_MINDER_HOOGTE
        z_pat = [round(waarde * draai * SPRONG_HULP_MINDER_ZIJ, 2) for waarde in spiraal_z]
        y_pat = [
            round(
                stap * klim
                + sin(stap * 0.7) * (0.5 + moeilijkheid * 0.3) * SPRONG_HULP_MINDER_HOOGTE,
                2,
            )
            for stap in range(SPRONGEN_PER_LEVEL)
        ]
        level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} rondje omhoog"
    elif parcours_soort == "ladder":
        z_pat = [0.0, 0.3, 0.8, 0.9, 0.5, 0.2, 0.0, -0.2, -0.5, -0.4, 0.0, 0.4, 0.0]
        y_pat = [0.0, 0.7, 1.3, 1.8, 2.2, 5.0, 6.5, 7.6, 8.6, 9.2, 10.1, 10.9, 11.7]
        y_pat = [round(waarde * (0.75 + moeilijkheid * 0.45) * SPRONG_HULP_MINDER_HOOGTE, 2) for waarde in y_pat]
        level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} ladder klim"
    elif parcours_soort == "boost":
        z_pat = [0.0, 0.8, 1.8, 3.2, 1.6, 0.0, -1.6, -3.2, -1.8, -0.8, 0.0, 1.4, 0.0]
        y_pat = [0.0, 0.4, 1.0, 1.4, 1.0, 0.4, 0.1, 0.8, 1.5, 2.3, 3.0, 2.0, 1.2]
        y_pat = [round(waarde * (0.8 + moeilijkheid * 0.35) * SPRONG_HULP_MINDER_HOOGTE, 2) for waarde in y_pat]
        level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} snelheidsbaan"
    elif parcours_soort == "blokkade":
        level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} muurroute"
    elif parcours_soort == "springblok":
        level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} springblokbaan"
    elif parcours_soort == "muurpad":
        z_pat = [waarde * SPRONG_HULP_MINDER_ZIJ for waarde in [4.6, 5.0, 5.4, 5.8, 5.8, 5.4, 5.0, 4.6, 4.2, 4.6, 5.0, 5.4, 5.8]]
        if variant % 2 == 1:
            z_pat = [-waarde for waarde in z_pat]
        y_pat = [round(waarde * (0.85 + moeilijkheid * 0.4) * SPRONG_HULP_MINDER_HOOGTE, 2) for waarde in y_pat]
        level_naam = f"{LEVEL_BIJVOEGLIJK[(level + variant) % len(LEVEL_BIJVOEGLIJK)]} muurpad"

    return basis_stijl, level_kleur, z_pat, y_pat, level_naam, parcours_soort


def schaal_voor_boostpad(breedte, diepte):
    """Maak een snelheidsvlak dat de hele bovenkant van een blok bedekt."""
    return (breedte, BOOSTPAD_SCHAAL[1], diepte)


def schaal_voor_springblok(breedte, diepte):
    """Maak een springvlak dat de hele bovenkant van een blok bedekt."""
    return (breedte, SPRINGBLOK_SCHAAL[1], diepte)


def bouw_baangegevens():
    """Bouw een toren van levels die steeds hoger wordt."""
    platform_data = [{"positie": (0.0, 0.0, 0.0), "schaal": (STARTPLATFORM_SCHAAL, 1.0, STARTPLATFORM_SCHAAL), "kleur": maak_rgb_kleur((120, 150, 255), 0.95)}]
    muur_data = []
    ladder_data = []
    boostpad_data = [
        {
            "positie": (0.0, 0.65, 0.0),
            "schaal": schaal_voor_boostpad(STARTPLATFORM_SCHAAL, STARTPLATFORM_SCHAAL),
            "kleur": maak_rgb_kleur((90, 220, 255), 1.2),
            "level": 0,
        }
    ]
    springblok_data = []
    checkpoint_data = []
    ster_posities = []
    level_hoogtes = []
    level_kleuren = []
    level_namen = []

    y = 0.0
    vorige_breedte = STARTPLATFORM_SCHAAL
    huidige_hoek = 0.0
    vorig_platform_punt = Vec3(0, 0, 0)

    for level in range(AANTAL_LEVELS):
        moeilijkheid = level / max(1, AANTAL_LEVELS - 1)
        stijl, level_kleur, z_pat, y_pat, level_naam, parcours_soort = maak_level_profiel(level, moeilijkheid)
        heeft_springblok = parcours_soort in ("springblok", "spiraal")
        heeft_blokkade_muur = parcours_soort == "blokkade"
        heeft_ladder = parcours_soort == "ladder"
        heeft_boostpad = parcours_soort == "boost"
        heeft_muurpad = parcours_soort == "muurpad"
        grote_sprong_stappen = 0
        basis_y = level * 7.2 + (level // 6) * 2.2
        basis_breedte = (BEGIN_SCHAAL[0] + (EIND_SCHAAL[0] - BEGIN_SCHAAL[0]) * moeilijkheid) * SPRONG_HULP_BREEDER
        basis_diepte = (BEGIN_SCHAAL[1] + (EIND_SCHAAL[1] - BEGIN_SCHAAL[1]) * moeilijkheid) * SPRONG_HULP_BREEDER
        vorige_positie_in_level = None

        for stap in range(SPRONGEN_PER_LEVEL):
            wereld_stap = level * SPRONGEN_PER_LEVEL + stap + 1

            breedte = max(2.8, basis_breedte - (stap % 4) * 0.06)
            diepte = max(2.9, basis_diepte - (stap % 3) * 0.05)
            gap = (
                BEGIN_GAP + (EIND_GAP - BEGIN_GAP) * moeilijkheid + (stap % 3) * 0.12
            ) * SPRONG_HULP_KLEINER_GAT
            extra_hoogte = 0.0

            if grote_sprong_stappen > 0:
                gap += 0.55
                extra_hoogte = 0.45 if grote_sprong_stappen == 2 else 0.22

            if heeft_boostpad and stap in (BOOSTPAD_STAP + 1, BOOSTPAD_STAP + 2):
                gap += 0.5
            hoek_stap = TOREN_HOEK_BASIS + gap * 2.1
            if heeft_ladder and stap >= LADDER_STAP:
                hoek_stap *= 0.78
            if heeft_muurpad and stap >= 3:
                hoek_stap *= 0.9
            if parcours_soort == "spiraal":
                hoek_stap *= 1.15

            huidige_hoek += hoek_stap
            radius = TOREN_STRAAL + z_pat[stap % len(z_pat)] * 0.85
            x = round(cos(radians(huidige_hoek)) * radius, 2)
            z = round(sin(radians(huidige_hoek)) * radius, 2)
            y = basis_y + y_pat[stap % len(y_pat)] + extra_hoogte

            if heeft_blokkade_muur and stap in (4, 5, 6, 7):
                midden_hoek = radians(huidige_hoek - 8)
                blokkade_radius = TOREN_STRAAL + (2.4 if stap < 6 else -2.0)
                x = round(cos(midden_hoek) * blokkade_radius, 2)
                z = round(sin(midden_hoek) * blokkade_radius, 2)

            if level >= 80 and stap % 11 == 5:
                y += 0.75
            elif level >= 45 and stap % 9 == 4:
                y += 0.5
            elif level >= 20 and stap % 7 == 3:
                y += 0.25

            platform_punt = Vec3(x, y, z)

            platform_data.append(
                {"positie": (x, y, z), "schaal": (breedte, 1.0, diepte), "kleur": level_kleur}
            )
            voeg_muren_toe(muur_data, level, stijl, x, y, breedte, gap, z)
            if heeft_blokkade_muur and stap == 5:
                voeg_blokkade_muur_toe(muur_data, vorig_platform_punt, platform_punt, level)
            if heeft_muurpad and stap in (4, 7, 10):
                voeg_muurpad_toe(muur_data, x, y, z, level)
            if heeft_ladder and stap == LADDER_STAP and vorige_positie_in_level is not None:
                vorige_x, vorige_y, vorige_z = vorige_positie_in_level
                ladder_hoogte = max(4.6, abs(y - vorige_y) + 3.4)
                ladder_data.append(
                    {
                        "positie": ((vorige_x + x) / 2, min(vorige_y, y) + ladder_hoogte / 2 - 0.5, (vorige_z + z) / 2),
                        "schaal": (0.9, ladder_hoogte, 1.1),
                        "kleur": kleur_van_level(level, 0.78),
                    }
                )
            if heeft_boostpad and stap == BOOSTPAD_STAP:
                boostpad_data.append(
                    {
                        "positie": (x, y + 0.65, z),
                        "schaal": schaal_voor_boostpad(breedte, diepte),
                        "kleur": kleur_van_level(level, 1.14),
                        "level": level,
                    }
                )

            if heeft_springblok and stap == SPRINGBLOK_STAP:
                springblok_data.append(
                    {
                        "positie": (x, y + 0.7, z),
                        "schaal": schaal_voor_springblok(breedte, diepte),
                        "kleur": kleur_van_level(level, 1.22),
                        "level": level,
                    }
                )
                grote_sprong_stappen = 2
            elif grote_sprong_stappen > 0:
                grote_sprong_stappen -= 1

            if wereld_stap % CHECKPOINT_INTERVAL == 0:
                checkpoint_data.append({"positie": (x, y + 0.7, z), "kleur": kleur_van_level(level, 0.85), "level": level})

            if (level + 1) % STER_INTERVAL == 0 and stap == SPRONGEN_PER_LEVEL - 1:
                ster_posities.append((x, y + 1.6, z))

            vorige_breedte = breedte
            vorige_positie_in_level = (x, y, z)
            vorig_platform_punt = platform_punt

        level_hoogtes.append(y)
        level_kleuren.append(level_kleur)
        level_namen.append(level_naam)

    finish_radius = TOREN_STRAAL * 0.35
    finish_x = round(cos(radians(huidige_hoek + 35)) * finish_radius, 2)
    finish_y = y + 8.0
    finish_z = round(sin(radians(huidige_hoek + 35)) * finish_radius, 2)
    top_kleur = kleur_van_level(AANTAL_LEVELS - 1, 1.18)

    platform_data.append(
        {"positie": (finish_x, finish_y, finish_z), "schaal": (FINISH_PLATFORM_SCHAAL, 1.0, FINISH_PLATFORM_SCHAAL), "kleur": top_kleur}
    )
    doel_positie = Vec3(finish_x, finish_y + 2.2, finish_z)
    return (
        platform_data,
        muur_data,
        ladder_data,
        boostpad_data,
        springblok_data,
        checkpoint_data,
        ster_posities,
        level_hoogtes,
        level_kleuren,
        level_namen,
        doel_positie,
    )


(
    PLATFORM_DATA,
    MUUR_DATA,
    LADDER_DATA,
    BOOSTPAD_DATA,
    SPRINGBLOK_DATA,
    CHECKPOINT_DATA,
    STER_POSITIES,
    LEVEL_HOOGTES,
    LEVEL_KLEUREN,
    LEVEL_NAMEN,
    DOEL_POSITIE,
) = bouw_baangegevens()
TOTAAL_STERREN = len(STER_POSITIES)
EERSTE_SPRONG_POSITIE = vec3_van(PLATFORM_DATA[1]["positie"])
START_ROTATIE_Y = degrees(atan2(EERSTE_SPRONG_POSITIE.x - START_PUNT.x, EERSTE_SPRONG_POSITIE.z - START_PUNT.z))

app = Ursina()
window.title = TITEL
window.borderless = False
window.color = maak_rgb_kleur((32, 44, 96))
window.exit_button.visible = False
window.fps_counter.enabled = True
camera.fov = 95
camera.clear_color = maak_rgb_kleur((32, 44, 96))

sterren = []
boostpads = []
ladders = []
springblokken = []
checkpoints = []
computer_spelers = []
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
laatste_boostpad_tijd = 0.0
laatste_springblok_tijd = 0.0
laatste_muursprong_tijd = 0.0


def maak_platform(positie, schaal, kleur_blok):
    """Maak een springblok waar de speler op kan landen."""
    blok = Entity(
        model="cube",
        shader=unlit_shader,
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
        shader=unlit_shader,
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )
    muur.is_muur = True
    return muur


def maak_springblok(positie, schaal, kleur_blok):
    """Maak een fel blok dat je extra ver omhoog schiet."""
    blok = Entity(
        model="cube",
        shader=unlit_shader,
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )
    blok.is_muur = False
    return blok


def maak_ladder(positie, schaal, kleur_blok):
    """Maak een ladder waar je omhoog kunt klimmen."""
    ladder = Entity(
        model="cube",
        shader=unlit_shader,
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )
    ladder.is_muur = False
    return ladder


def maak_boostpad(positie, schaal, kleur_blok):
    """Maak een fel snelheidsvlak dat je vooruit duwt."""
    pad = Entity(
        model="cube",
        shader=unlit_shader,
        color=kleur_blok,
        position=vec3_van(positie),
        scale=schaal,
        collider="box",
    )
    pad.is_muur = False
    return pad


def vernieuw_actieve_lijst(bron_data, actieve_lijst, maker, minimum_x, maximum_x):
    """Houd alleen de blokken actief die dicht bij de speler zijn."""
    gewenste_indexen = set()

    for index, data in enumerate(bron_data):
        positie_y = data["positie"][1]
        halve_hoogte = data["schaal"][1] / 2

        if positie_y + halve_hoogte < minimum_x or positie_y - halve_hoogte > maximum_x:
            continue

        gewenste_indexen.add(index)
        if index not in actieve_lijst:
            actieve_lijst[index] = maker(data["positie"], data["schaal"], data["kleur"])

    for index in list(actieve_lijst):
        if index not in gewenste_indexen:
            destroy(actieve_lijst.pop(index))


def vernieuw_actieve_baan(force=False):
    """Laad alleen het stukje toren dat om de speler heen zit."""
    global laatste_laad_x

    if not force and laatste_laad_x is not None:
        if abs(player.y - laatste_laad_x) < LAAD_VERNIEUW_HOOGTE:
            return

    minimum_x = player.y - LAAD_HOOGTE_ONDER
    maximum_x = player.y + LAAD_HOOGTE_BOVEN
    vernieuw_actieve_lijst(PLATFORM_DATA, actieve_platforms, maak_platform, minimum_x, maximum_x)
    vernieuw_actieve_lijst(MUUR_DATA, actieve_muren, maak_muur, minimum_x, maximum_x)
    laatste_laad_x = player.y


class ZwevendeSter(Entity):
    """Een ster draait en zweeft een klein beetje op en neer."""

    def __init__(self, positie, nummer):
        super().__init__(
            model="sphere",
            shader=unlit_shader,
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


class ComputerSpeler(Entity):
    """Een hulp-speler die vanzelf de route voordoet."""

    def __init__(self, pad_punten, start_offset, kleur_rgb, extra_vertaging=0.0):
        super().__init__(
            model="cube",
            shader=unlit_shader,
            color=maak_rgb_kleur(kleur_rgb, 1.1),
            position=pad_punten[0] + start_offset,
            scale=(0.9, 1.5, 0.9),
        )
        self.pad_punten = pad_punten
        self.start_offset = start_offset
        self.start_vertaging = COMPUTER_SPELER_START_VERTAGING + extra_vertaging
        self.segment_start = Vec3(self.position.x, self.position.y, self.position.z)
        self.doel_index = 1
        self.segment_tijd = 0.5
        self.segment_voortgang = 0.0
        self.sprong_hoogte = COMPUTER_SPELER_SPRONGHOOGTE
        self.wacht_tijd = self.start_vertaging
        self.klaar = False
        self.reset()

    def reset(self):
        """Zet de hulp-speler weer netjes terug naar het begin."""
        self.position = self.pad_punten[0] + self.start_offset
        self.segment_start = Vec3(self.position.x, self.position.y, self.position.z)
        self.doel_index = 1
        self.segment_voortgang = 0.0
        self.sprong_hoogte = COMPUTER_SPELER_SPRONGHOOGTE
        self.wacht_tijd = self.start_vertaging
        self.klaar = False
        self.draai_naar(self.pad_punten[self.doel_index])
        self.bereid_volgende_sprong_voor()

    def draai_naar(self, doel):
        """Draai de hulp-speler naar het volgende blok."""
        verschil = doel - self.position
        if abs(verschil.x) > 0.01 or abs(verschil.z) > 0.01:
            self.rotation_y = degrees(atan2(verschil.x, verschil.z))

    def bereid_volgende_sprong_voor(self):
        """Reken uit hoe lang de volgende sprong duurt."""
        if self.doel_index >= len(self.pad_punten):
            self.klaar = True
            self.position = self.pad_punten[-1]
            return

        doel = self.pad_punten[self.doel_index]
        afstand = distance(self.segment_start, doel)
        self.segment_tijd = max(0.2, min(0.68, afstand / COMPUTER_SPELER_SNELHEID))
        self.sprong_hoogte = SPELER_SPRONGHOOGTE
        self.draai_naar(doel)

    def beweeg(self):
        """Laat de hulp-speler van blok naar blok springen."""
        if self.klaar:
            self.y = self.pad_punten[-1].y + 0.18 * sin(perf_counter() * 2.4)
            return

        if self.wacht_tijd > 0:
            self.wacht_tijd = max(0.0, self.wacht_tijd - time.dt)
            return

        doel = self.pad_punten[self.doel_index]
        self.segment_voortgang = min(1.0, self.segment_voortgang + time.dt / self.segment_tijd)
        voortgang = self.segment_voortgang
        basis = self.segment_start + (doel - self.segment_start) * voortgang
        boog = sin(voortgang * pi) * self.sprong_hoogte
        self.position = Vec3(basis.x, basis.y + boog, basis.z)

        if voortgang >= 1.0:
            self.position = doel
            self.segment_start = Vec3(doel.x, doel.y, doel.z)
            self.doel_index += 1
            self.segment_voortgang = 0.0
            self.bereid_volgende_sprong_voor()


def maak_computer_spelers():
    """Maak hulp-spelers die laten zien dat de toren te halen is."""
    global computer_spelers

    pad_punten = [vec3_van(data["positie"]) + Vec3(0, 1.15, 0) for data in PLATFORM_DATA]
    pad_punten.append(Vec3(DOEL_POSITIE.x, DOEL_POSITIE.y + 0.5, DOEL_POSITIE.z))
    start_vakken = [
        Vec3(-3.0, 0, -3.0),
        Vec3(-1.0, 0, -3.0),
        Vec3(1.0, 0, -3.0),
        Vec3(3.0, 0, -3.0),
        Vec3(-3.0, 0, -1.0),
        Vec3(-1.0, 0, -1.0),
        Vec3(1.0, 0, -1.0),
        Vec3(3.0, 0, -1.0),
        Vec3(-3.0, 0, 1.0),
        Vec3(-1.0, 0, 1.0),
        Vec3(1.0, 0, 1.0),
        Vec3(3.0, 0, 1.0),
        Vec3(-3.0, 0, 3.0),
        Vec3(-1.0, 0, 3.0),
        Vec3(1.0, 0, 3.0),
        Vec3(3.0, 0, 3.0),
    ]
    helper_kleuren = [
        (110, 255, 150),
        (90, 220, 255),
        (120, 150, 255),
        (220, 120, 255),
        (255, 220, 80),
        (255, 160, 70),
        (255, 90, 90),
    ]
    computer_spelers = [
        ComputerSpeler(
            pad_punten,
            start_vakken[index],
            helper_kleuren[index % len(helper_kleuren)],
            index * 0.18,
        )
        for index in range(COMPUTER_SPELER_AANTAL)
    ]


def maak_wolken():
    """Maak wolken rondom de toren."""
    return


def maak_wereld():
    """Bouw de hele parkourtoren."""
    AmbientLight(color=maak_rgb_kleur((180, 180, 220), alpha=120))
    DirectionalLight(y=25, z=10, rotation=(45, -35, 0))

    # Dit is de mist onder de baan. Als je daaronder valt, ga je terug.
    Entity(
        model="plane",
        position=(0, -14, 0),
        scale=160,
        color=color.red.tint(-0.15),
    )

    for checkpoint_info in CHECKPOINT_DATA:
        checkpoint = Entity(
            model="cube",
            shader=unlit_shader,
            color=checkpoint_info["kleur"],
            position=vec3_van(checkpoint_info["positie"]),
            scale=(2.8, 0.3, 2.8),
            collider="box",
        )
        checkpoint.actief = False
        checkpoint.level_index = checkpoint_info["level"]
        checkpoint.basis_kleur = checkpoint_info["kleur"]
        checkpoint.actieve_kleur = kleur_van_level(checkpoint.level_index, 1.25)
        checkpoints.append(checkpoint)

    for ladder_info in LADDER_DATA:
        ladders.append(maak_ladder(ladder_info["positie"], ladder_info["schaal"], ladder_info["kleur"]))

    for boostpad_info in BOOSTPAD_DATA:
        boostpads.append(maak_boostpad(boostpad_info["positie"], boostpad_info["schaal"], boostpad_info["kleur"]))

    for springblok_info in SPRINGBLOK_DATA:
        springblokken.append(maak_springblok(springblok_info["positie"], springblok_info["schaal"], springblok_info["kleur"]))

    # Deze vlag laat zien waar het einde van de toren is.
    Entity(
        model="cube",
        shader=unlit_shader,
        position=(DOEL_POSITIE.x, DOEL_POSITIE.y + 1.0, DOEL_POSITIE.z),
        scale=(0.25, 7, 0.25),
        color=kleur_van_level(AANTAL_LEVELS - 1, 0.78),
    )
    Entity(
        model="cube",
        shader=unlit_shader,
        position=(DOEL_POSITIE.x + 1.1, DOEL_POSITIE.y + 3.6, DOEL_POSITIE.z),
        scale=(2.4, 1.4, 0.15),
        color=kleur_van_level(AANTAL_LEVELS - 1, 1.25),
    )
    Entity(model="sphere", shader=unlit_shader, position=DOEL_POSITIE, scale=1.7, color=kleur_van_level(AANTAL_LEVELS - 1, 1.35))

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


def lees_heel_getal(waarde, standaard):
    """Lees een heel getal uit het opslagbestand."""
    try:
        return int(waarde)
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
    actieve_checkpoint_nummers = [nummer for nummer, checkpoint in enumerate(checkpoints) if checkpoint.actief]
    laatste_checkpoint = actieve_checkpoint_nummers[-1] if actieve_checkpoint_nummers else -1
    opslag = {
        "baan_versie": BAAN_VERSIE,
        "speler_positie": vec3_naar_lijst(speler_punt),
        "rotatie_y": player.rotation_y,
        "kijk_x": player.camera_pivot.rotation_x,
        "spawn_punt": vec3_naar_lijst(spawn_punt),
        "verzamelde_sterren": sorted(verzamelde_sterren),
        "actieve_checkpoints": [checkpoint.actief for checkpoint in checkpoints],
        "laatste_checkpoint": laatste_checkpoint,
        "huidig_level": huidige_level_nummer(),
        "verstreken_tijd": verstreken_tijd,
    }

    try:
        OPSLAG_BESTAND.write_text(json.dumps(opslag, indent=2), encoding="utf-8")
        laatste_opslag_tijd = perf_counter()
    except OSError:
        print("Opslaan lukte niet.")


def checkpoint_nummer_uit_lijst(checkpoint_lijst):
    """Zoek het laatste checkpoint dat al gehaald was."""
    laatste_checkpoint = -1

    for nummer, actief in enumerate(checkpoint_lijst):
        if bool(actief):
            laatste_checkpoint = nummer

    return laatste_checkpoint


def spawn_punt_van_checkpoint(checkpoint_nummer):
    """Maak een veilig spawn-punt bij een checkpoint."""
    if 0 <= checkpoint_nummer < len(checkpoints):
        checkpoint = checkpoints[checkpoint_nummer]
        return Vec3(checkpoint.x, checkpoint.y + 2, checkpoint.z)

    return Vec3(START_PUNT.x, START_PUNT.y, START_PUNT.z)


def zet_checkpoint_status(checkpoint_lijst):
    """Zet checkpoints aan of uit op basis van de opslag."""
    for nummer, checkpoint in enumerate(checkpoints):
        checkpoint.actief = nummer < len(checkpoint_lijst) and bool(checkpoint_lijst[nummer])
        checkpoint.color = checkpoint.actieve_kleur if checkpoint.actief else checkpoint.basis_kleur


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

    oude_baan = opslag.get("baan_versie") != BAAN_VERSIE
    laatste_checkpoint = lees_heel_getal(opslag.get("laatste_checkpoint"), checkpoint_nummer_uit_lijst(checkpoint_lijst))
    laatste_checkpoint = max(-1, min(len(checkpoints) - 1, laatste_checkpoint))

    zet_checkpoint_status(checkpoint_lijst)
    spawn_punt = spawn_punt_van_checkpoint(laatste_checkpoint)

    if oude_baan:
        speler_punt = Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)
    else:
        oude_spawn = lijst_naar_vec3(opslag.get("spawn_punt"), spawn_punt)
        speler_punt = lijst_naar_vec3(opslag.get("speler_positie"), oude_spawn)
        if speler_punt.y < -6:
            speler_punt = Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)

    player.position = speler_punt
    player.rotation_y = lees_getal(opslag.get("rotatie_y"), START_ROTATIE_Y)
    if laatste_checkpoint < 0 and distance(player.position, START_PUNT) < 4:
        player.rotation_y = START_ROTATIE_Y
    player.camera_pivot.rotation_x = lees_getal(opslag.get("kijk_x"), 0.0)
    player.air_time = 0
    vernieuw_actieve_baan(force=True)

    maak_sterren_opnieuw()

    verstreken_tijd = max(0.0, lees_getal(opslag.get("verstreken_tijd"), 0.0))
    start_tijd = perf_counter() - verstreken_tijd
    laatste_opslag_tijd = perf_counter()

    if oude_baan:
        toon_melding("Je ging verder vanaf je laatste checkpoint!")
    else:
        toon_melding("Je vorige potje is geladen!")

    return True


def toon_melding(tekst, duur=2.4):
    """Laat even een korte boodschap zien."""
    global melding_tijd

    melding_tekst.text = tekst
    melding_tekst.color = kleur_van_level(huidige_level_nummer() - 1, 1.28)
    melding_tijd = duur


def speler_staat_op_vlak(speler_punt, vlak, marge=0.2):
    """Kijk of de speler ergens op het speciale vlak staat."""
    return (
        abs(speler_punt.x - vlak.x) <= vlak.scale_x / 2 + marge
        and abs(speler_punt.z - vlak.z) <= vlak.scale_z / 2 + marge
        and abs(speler_punt.y - vlak.y) <= 1.5
    )


def gebruik_springblok():
    """Schiet de speler omhoog en vooruit vanaf een fel blok."""
    global laatste_springblok_tijd

    speler_hoogte = player.position + Vec3(0, 1.0, 0)
    nu = perf_counter()

    if nu - laatste_springblok_tijd < SPRINGBLOK_COOLDOWN or not player.grounded:
        return

    for springblok in springblokken:
        if speler_staat_op_vlak(speler_hoogte, springblok):
            richting = kijk_richting()
            player.position = player.position + Vec3(richting.x * 5.0, 4.2, richting.z * 5.0)
            player.air_time = 0
            laatste_springblok_tijd = nu
            vernieuw_actieve_baan(force=True)
            toon_melding("Boing! Super sprong!")
            return


def gebruik_boostpad():
    """Duw de speler vooruit over een fel snelheidsvlak."""
    global laatste_boostpad_tijd

    speler_hoogte = player.position + Vec3(0, 1.0, 0)
    nu = perf_counter()

    if nu - laatste_boostpad_tijd < BOOSTPAD_COOLDOWN or not player.grounded:
        return

    for boostpad in boostpads:
        if speler_staat_op_vlak(speler_hoogte, boostpad):
            richting = kijk_richting()
            player.position = player.position + Vec3(richting.x * 7.5, 1.0, richting.z * 7.5)
            player.air_time = 0
            laatste_boostpad_tijd = nu
            vernieuw_actieve_baan(force=True)
            toon_melding("Zoef! Snelheidsvlak!")
            return


def klim_ladder():
    """Laat de speler omhoog klimmen als hij bij een ladder is."""
    speler_midden = player.position + Vec3(0, 0.8, 0)

    for ladder in ladders:
        if distance(speler_midden, ladder.position) >= 1.6:
            continue

        if held_keys["w"]:
            player.x = ladder.x
            player.z = ladder.z
            player.position = player.position + Vec3(0, 5.6 * time.dt, 0)
            player.air_time = 0
            vernieuw_actieve_baan(force=True)
            return True

        if held_keys["s"]:
            player.x = ladder.x
            player.z = ladder.z
            player.position = player.position + Vec3(0, -3.8 * time.dt, 0)
            player.air_time = 0
            vernieuw_actieve_baan(force=True)
            return True

    return False


def vind_muursprong():
    """Kijk of er vlak naast de speler een muur zit voor een muursprong."""
    startpunt = player.position + Vec3(0, 1.1, 0)
    rechts = zij_richting()
    richtingen = [
        (rechts, Vec3(-rechts.x * 2.8, 2.3, -rechts.z * 2.8)),
        (Vec3(-rechts.x, 0, -rechts.z), Vec3(rechts.x * 2.8, 2.3, rechts.z * 2.8)),
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


def level_nummer_bij_hoogte(hoogte):
    """Zoek welk level bij een hoogte hoort."""
    for nummer, eind_y in enumerate(LEVEL_HOOGTES, start=1):
        if hoogte <= eind_y:
            return nummer
    return AANTAL_LEVELS


def huidige_level_nummer():
    """Kijk in welk level van de baan je ongeveer bent."""
    return level_nummer_bij_hoogte(player.y)


def moeilijkheid_tekst(level_nummer):
    """Geef een kort woord voor hoe moeilijk het nu is."""
    stap = (level_nummer - 1) / max(1, AANTAL_LEVELS - 1)
    index = min(len(MOEILIJKHEID_NAMEN) - 1, int(stap * len(MOEILIJKHEID_NAMEN)))
    return MOEILIJKHEID_NAMEN[index]


def zet_speler_terug(tekst):
    """Zet de speler terug op het laatste veilige punt."""
    player.position = Vec3(spawn_punt.x, spawn_punt.y, spawn_punt.z)
    player.rotation_y = START_ROTATIE_Y
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
        checkpoint.color = checkpoint.basis_kleur

    for computer_speler in computer_spelers:
        computer_speler.reset()

    maak_sterren_opnieuw()
    zet_speler_terug("Nieuw potje! Klaar voor de superlange baan?")
    bewaar_voortgang()


def update_status():
    """Werk de tekst linksboven bij met score, tijd en level."""
    huidig_einde = eind_tijd if eind_tijd is not None else perf_counter()
    voortgang = int(max(0, min(100, (player.y / DOEL_POSITIE.y) * 100)))
    level_nummer = huidige_level_nummer()
    status_tekst.color = LEVEL_KLEUREN[level_nummer - 1]
    status_tekst.text = (
        f"Sterren: {gehaalde_sterren}/{TOTAAL_STERREN}\n"
        f"Tijd: {maak_tijd_tekst(huidig_einde - start_tijd)}\n"
        f"Voortgang: {voortgang}%\n"
        f"Level {level_nummer}/{AANTAL_LEVELS}: {LEVEL_NAMEN[level_nummer - 1]}\n"
        f"Moeilijkheid: {moeilijkheid_tekst(level_nummer)}"
    )


maak_wereld()

# De speler kijkt in first person, alsof je zelf in het spel staat.
player = FirstPersonController(position=START_PUNT)
player.rotation_y = START_ROTATIE_Y
player.speed = START_SNELHEID
player.jump_height = SPELER_SPRONGHOOGTE
player.jump_up_duration = 0.42
player.gravity = 1
player.cursor.color = color.black
vernieuw_actieve_baan(force=True)
maak_computer_spelers()

uitleg_tekst = Text(
    parent=camera.ui,
    text=(
        "Wolken Parkour 3D\n"
        "Toren van 100 levels\n"
        "1300 sprongen omhoog\n"
        "Rondje omhoog en ladders\n"
        "Fel vlak = snelheidsboost\n"
        "Fel blok = super sprong\n"
        "Helpers laten de route zien\n"
        "Spatie langs muur = muursprong\n"
        "Klim helemaal naar boven\n"
        "WASD + muis + spatie\n"
        "R = opnieuw"
    ),
    x=-0.86,
    y=0.38,
    scale=1.05,
    color=kleur_van_level(0, 1.12),
)

status_tekst = Text(parent=camera.ui, x=-0.86, y=0.08, scale=1.05, color=kleur_van_level(0, 1.0))
melding_tekst = Text(parent=camera.ui, y=0.38, origin=(0, 0), scale=1.8, color=kleur_van_level(0, 1.28))
einde_tekst = Text(parent=camera.ui, y=0.08, origin=(0, 0), scale=2.0, color=kleur_van_level(AANTAL_LEVELS - 1, 1.35))

maak_sterren_opnieuw()
if not laad_voortgang():
    toon_melding("Klim helemaal naar de top van de toren!")


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
    for computer_speler in computer_spelers:
        computer_speler.beweeg()
    klim_ladder()
    gebruik_boostpad()
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
            checkpoint.color = checkpoint.actieve_kleur
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
                "Je hebt de hele toren gehaald!\n"
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
