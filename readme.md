<div align="center">
  <img width="750" src="https://raw.githubusercontent.com/kurwjan/LanisAPI/rewrite/header.svg">
</div>

## Work in progress
Diese Branch enthält noch nicht alle alten Features und kein Wiki, aber sie
werden bald kommen. Aktuell implementiert ist:
+ Grundstruktur `LanisClient`
  + Applets _(Verfügbare, Unterstützung)_
  + Client und Initialisierung entkoppelt _(→ core/initialization/types.py)_
    + Cookie-Initialisierung
    + Account-Initialisierung mit Schul-Id
+ Modularer Modulaufbau _(auch Custom Module)_
  + Vertretungsplan-Modul

## Installation
Jede Version ab **0.5.0** sind von der rewrite branch, sie sind auch immer als Pre-Release markiert.

### Erste Methode (Git)
+ Habe Python 3.11
+ Downloade den Source-Code (z. B. `git clone https://github.com/kurwjan/LanisAPI.git`)
+ Führe `pip install .` im Root-Ordner _("LanisAPI")_ aus.

### Zweite Methode (Pip)
+ Habe Python 3.11
+ Führe `pip install lanisapi==VERSION` aus um die spezifische Prerelease-Version downloaden zu können.
  + Liste aller Prerelease- und Release-Versionen findest du hier: [Github](https://github.com/kurwjan/LanisAPI/releases) und [PyPi](https://pypi.org/project/lanisapi/#history).