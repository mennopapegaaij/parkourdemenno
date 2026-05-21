# Wolken Parkour 3D

Een vrolijke 3D parkourtoren in Python met `ursina`.

## Wat is er nieuw?

- De baan heeft nu **veel meer korte levels**
- De levels vormen nu samen een **grote toren omhoog**
- Elk level heeft nu zijn eigen **regenboogkleur**
- Elk level is korter, dus je komt sneller in een nieuw stukje
- De levels **herhalen niet steeds opnieuw**
- Elk level heeft nu **sowieso een speciaal ding**
- Het spel gaat nog steeds van **makkelijk naar moeilijk**
- Er zijn nu meerdere soorten parcours, zoals **rondjes omhoog**, **ladders** en **snelheidsbanen**
- De muur-sprongen zitten er nog steeds in
- Er staan nu ook **blokkade-muren** midden in de route waar je langs moet springen
- De baan heeft nu **heel veel meer hoogteverschil**
- Er zijn nu ook **groene springblokken** voor superhoge sprongen
- Er zijn veel meer checkpoints
- Het spel laadt nu alleen het stuk baan dat dicht bij je is, zodat het soepeler loopt
- Het spel slaat automatisch op waar je bent gebleven

## Wat doe je in het spel?

- Klim een superhoge parkourtoren op
- Speel ook rondjes omhoog, ladder-klimmen en snelheidsstukken
- Spring langs muren die midden in de weg staan
- Klim en daal over stukken met heel grote hoogteverschillen
- Gebruik felle snelheidsvlakken voor een extra duw vooruit
- Gebruik felle springblokken voor extra hoge sprongen
- Druk op `Spatie` langs een muur voor een muursprong
- Pak alle sterren
- Haal checkpoints zodat je niet te ver terug hoeft
- Bereik de finishvlag om te winnen

## Starten

```bash
pip install -r requirements.txt
python main.py
```

## Besturing

- `WASD` = lopen
- Muis = kijken
- `W` op een ladder = klimmen
- `Spatie` = springen of muursprong
- `R` = opnieuw beginnen
- `Esc` = stoppen

## Opslaan

Het spel bewaart automatisch:

- je plek
- je sterren
- je checkpoints
- je tijd
- en probeert na nieuwe baan-updates verder te gaan vanaf je checkpoint

Als je later terugkomt en `python main.py` weer start, ga je verder waar je was.
