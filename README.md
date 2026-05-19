# Wolken Parkour 3D

Een vrolijk 3D parkourspel in Python met `ursina`.

## Wat doe je in het spel?

- Spring van blok naar blok hoog in de lucht
- Pak 3 gele sterren
- Raak checkpoints zodat je niet helemaal opnieuw hoeft
- Haal de vlag om te winnen
- Val je naar beneden? Dan ga je terug naar je laatste checkpoint
- Het spel slaat automatisch op waar je bent gebleven

## Starten

```bash
pip install -r requirements.txt
python main.py
```

## Besturing

- `WASD` = lopen
- Muis = kijken
- `Spatie` = springen
- `R` = opnieuw beginnen
- `Esc` = stoppen

## Opslaan

Het spel bewaart automatisch:

- je plek
- je sterren
- je checkpoints
- je tijd

Als je later terugkomt en `python main.py` weer start, ga je verder waar je was.
