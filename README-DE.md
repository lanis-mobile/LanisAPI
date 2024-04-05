[[README DE](https://github.com/kurwjan/LanisAPI/blob/master/README-DE.md)]  [[README EN](https://github.com/kurwjan/LanisAPI/blob/master/README.md)]

# LanisAPI

> ## ⚠ Aktueller Rework
> **[Siehe #32](https://github.com/kurwjan/LanisAPI/issues/32)** und die **[Rewrite-Branch](https://github.com/kurwjan/LanisAPI/tree/rewrite)**.
> 
> *Jetzt kannst du einfach v0.4.1 benutzen.*

## Was ist das?

Eine inoffizielle Python-Bibliothek für das Schulportal Hessen. Auch auf [PyPi](https://pypi.org/project/lanisapi/) verfügbar.

## Features

+ Hausaufgaben oder andere Aufgaben bekommen.
+ Vertretungsplan bekommen.
+ Kalenderereignisse bekommen.
+ Unterhaltungen bekommen.
+ Alle Schulen die Lanis haben bekommen.
+ Alle Online-Apps mit ihren Links bekommen.

**Übersicht von zukünftigen Features, Probleme und anderes [hier](https://github.com/users/kurwjan/projects/2)**

## App für das Schulportal Hessen
Du möchtest eine App? Benutze [lanis-mobile](https://github.com/alessioC42/lanis-mobile)!

[<img src="https://github.com/alessioC42/lanis-mobile/assets/84250128/19d30436-32f7-4cbe-b78e-f2fee3583c28" width="25%">](https://github.com/alessioC42/lanis-mobile)

Lanis-mobile ist offen für neue Contributors!

## Wie installiere ich das?

```sh
pip install lanisapi
```

Vorausgesetzt wird Python 3.11. *(ältere Versionen gehen wahrscheinlich nicht, habe es nicht getestet)*

## Beispiel

Dieses Beispiel gibt dir den Vertretungsplan.

```python
from lanisapi import LanisClient

def main():
    client = LanisClient(LanisAccount("school id", "name.lastname", "password"))
        or: client = LanisClient(LanisAccount(School("school", "city"), "name.lastname", "password"))
        or: client = LanisClient(LanisCookie("school id", "session id"))
    print(client.get_substitution_plan())
    client.close()
    
if __name__ == "__main__":
    main()
```

Mehr Infos bei der [Wiki](https://lanisapi.readthedocs.io/en/latest/first_steps.html).

## Wie kann ich mithelfen

1. Du kannst bei *Issues* Probleme die du findest melden.
2. Du kannst bei *Issues* Ideenvorschläge machen.
3. **Beim Programmieren beitragen**: Mehr Infos [hier](https://docs.github.com/en/get-started/quickstart/contributing-to-projects), falls du neu bist und es gibt auch Hilfe über dieses Projekt [hier](https://lanisapi.readthedocs.io/en/latest/contributing/programming_help.html).

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
