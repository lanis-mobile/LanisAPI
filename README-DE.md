[[README DE](https://github.com/kurwjan/LanisAPI/blob/master/README-DE.md)]  [[README EN](https://github.com/kurwjan/LanisAPI/blob/master/README.md)]

# LanisAPI

> ## ⚠ Hinweis
> **Da das Schulportal Hessen sich schnell ändert und fragmentiert ist, können einige Funktionen bei bestimmten Schulen oder nach einer Zeit nicht mehr funktionieren.**

## Was ist das?

Eine inoffizielle Python-Bibliothek für das Schulportal Hessen. Auch auf [PyPi](https://pypi.org/project/lanisapi/) verfügbar.

## Features

+ Hausaufgaben oder andere Aufgaben bekommen.
+ Vertretungsplan bekommen.
+ Kalenderereignisse bekommen.
+ Unterhaltungen bekommen.
+ Alle Schulen die Lanis haben bekommen.

**Übersicht von zukünftigen Features, Probleme und anderes [hier](https://github.com/users/kurwjan/projects/2)**

## Wie installiere ich das?

```sh
pip install lanisapi
```

Vorausgesetzt wird Python 3.11. *(ältere Versionen gehen bestimmt auch, habe es nicht getestet)*

## Beispiel

Dieses Beispiel gibt dir den Vertretungsplan.

```python
from lanisapi import LanisClient

def main():
    client = LanisClient("schulid", "name.nachname", "passwort")
        or: client = LanisClient(School("school", "city"), "password")
    client.authenticate()
    print(client.get_substitution_plan())
    client.close()
    
if __name__ == "__main__":
    main()
```

Mehr Infos bei der [Wiki](https://lanisapi.readthedocs.io/en/latest/first_steps.html).

## Wie kann ich mithelfen

1. Du kannst bei *Issues* Probleme die du findest melden.
2. Du kannst bei *Issues* Ideenvorschläge machen.
3. **Beim Programmieren beitragen**: Mehr Infos [hier](https://docs.github.com/en/get-started/quickstart/contributing-to-projects), falls du neu bist.

*Übrigens, wenn dir dieses Projekt gefällt, kannst du es auch einen Stern geben.*

## Creditss

Das Javascript-Projekt [SPHclient](https://github.com/alessioC42/SPHclient) von [@alessioC42](https://github.com/alessioC42) hat mir geholfen um das *Schulportal Hessen* zu verstehen.

Die Android-App [sph-planner](https://github.com/koenidv/sph-planner) von [@koenidv](https://github.com/koenidv) hat mir beim Verstehen der Level 2 Verschlüsselung geholfen.

Andere Projekte die mir nicht unbedingt geholfen haben, aber trotzdem cool sind:

+ **Gute TypeScript Bibliothek [Maria](https://github.com/elderguardian/maria) von [Elderguardian](https://github.com/elderguardian/)**
+ Flutter Android App [SPH-Vertretungsplan](https://github.com/alessioC42/SPH-vertretungsplan) auch von [@alessioC42](https://github.com/alessioC42)
+ Javascript App [SchulportalApp](https://github.com/DerOwnerHD/SchulportalApp) von [DerOwnerHD](https://github.com/DerOwnerHD)
+ Flutter Android App [lkwslr-sphplaner](https://github.com/flutter-preview/lkwslr-sphplaner) von [flutter-preview](https://github.com/flutter-preview)

## Hinweis

Das Projekt ist nicht offiziell mit dem Schulportal Hessen verbunden. Es ist nur eine inoffizielle Bibliothek, unterstützt durch die Community.
