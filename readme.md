<hr style="margin-top: 3em">
<div align="center" style="margin-bottom: 3em">
    <h1 style="margin-top: 1em; margin-bottom: 0; padding-top: 0">LanisAPI</h1>
    <h4 style="margin-top: 0">rewrite branch</h4>
</div>
<hr> <!-- Absolutely disgusting code -->

### Work in progress
Diese Branch enthält noch nicht alle alten Features und kein Wiki, aber sie
werden bald kommen. Aktuell implementiert ist:
+ Grundstruktur `LanisClient`
  + Applets _(Verfügbare, Unterstützung)_
  + Client und Initialisierung entkoppelt _(→ core/initialization/types.py)_
    + Cookie-Initialisierung
    + Account-Initialisierung mit Schul-Id
+ Modularer Modulaufbau _(auch Custom Module)_
  + Vertretungsplan-Modul