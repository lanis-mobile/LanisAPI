[[README DE](https://github.com/kurwjan/LanisAPI/blob/master/README-DE.md)]  [[README EN](https://github.com/kurwjan/LanisAPI/blob/master/README.md)]

# LanisAPI

> # ⚠ Hinweis
> **Da das Schulportal Hessen sich schnell ändert und fragmentiert ist, *(ungerfähr wie die Backwards-Compability bei Linux-Bibliotheken)* können einige Funktionen bei bestimmten Schulen oder nach einer Zeit nicht mehr funktionieren.**

## Was ist das?
Eine unoffiziele Pythonbibliothek für das Schulportal Hessen. Auch auf [PyPi](https://pypi.org/project/lanisapi/) verfügbar.

## Wie installiere ich das?
```
$ pip install lanisapi
```
Vorrausgesetzt wird Python 3.11. *(ältere Versionen gehen bestimmt auch, habe es nicht getestet)*

## Beispiel
Dieses Beispiel gibt dir den Vertretungsplan.
```python
from lanisapi import LanisClient

def main():
    client = LanisClient("schulid", "name.nachname", "passwort")
    client.authenticate()
    print(client.get_substitution_plan())
    client.logout()
    
if __name__ == "__main__":
    main()
```
Mehr Infos bei der Wiki.

## Übersicht von zukünftigen Features, Probleme und anderes [hier](https://github.com/users/kurwjan/projects/2).

## Wie kann ich mithelfen
1. Du kannst bei *Issues* Probleme die du findest melden.
2. Du kannst bei *Issues* Ideenvorschläge machen.
3. **Super duper**: Mithelfen beim programmieren. Mehr Infos [hier](https://docs.github.com/en/get-started/quickstart/contributing-to-projects), falls du neu bist.

## Credits
Das Javascript-Projekt [SPHclient](https://github.com/alessioC42/SPHclient) von [@alessioC42](https://github.com/alessioC42) hat mir geholfen um das Monstrum *Schulportal Hessen* zu verstehen.

Die Android-App [sph-planner](https://github.com/koenidv/sph-planner) *(wenn du Kotlin kannst, kannst du dieser App mal helfen)* von [@koenidv](https://github.com/koenidv) hat mir beim Verstehen der Level 2 Verschlüsselung geholfen.

Andere Projekte die mir nicht unbedingt geholfen haben, aber trotzdem cool sind:

* Flutter Android App [SPH-Vertretungsplan](https://github.com/alessioC42/SPH-vertretungsplan) auch von [@alessioC42](https://github.com/alessioC42)
* Javascript App [SchulportalApp](https://github.com/DerOwnerHD/SchulportalApp) von [DerOwnerHD](https://github.com/DerOwnerHD)
* Flutter Android App [lkwslr-sphplaner](https://github.com/flutter-preview/lkwslr-sphplaner) von [flutter-preview](https://github.com/flutter-preview)
* TypeScript Bibliothek [Maria](https://github.com/elderguardian/maria) von [Elderguardian](https://github.com/elderguardian/)

## Hinweis
Das Projekt ist nicht offiziel mit dem Schulportal Hessen verbunden. Es ist nur eine unoffiziele Bibliothek, unterstützt durch die Community.
