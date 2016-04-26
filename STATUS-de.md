## Aktueller Stand 2016-04-26 ##

Hier ein kurzer Überblick über den aktuellen Stand des Fräsenprojektes.

### Überblick über die Maschine ###

Bei der Maschine handelt es sich um eine umgebaute Drehbank. Der Werkzeugschlitten wurde mit zwei Servo-Motoren versehen (X-Achse für Bewegungen normal zur Spindelachse - Z-Achse parallel zur Spindelachse). Die Spindel ist mit einem Indexer versehen. Derzeit verwenden wir LinuxCNC via Parallel-Port um die Maschine zu steuern.

### Was funktioniert schon alles? ###

* Alle Motoren und der Indexer sind in LinuxCNC konfiguriert und lassen sich ansprechen.
* Wir haben einfache Drehkörper erzeugt (inkl. tool-compensation)
* LinuxCNC kann die Spindelgeschwindigkeit (bei uns typischerweise etwa 26 Umdrehungen/min) anzeigen und einfache Bewegungen in relation dazu ausführen (G33).
* Die Beschleunigung und maximale Geschwindigkeit für die X-Achse ist getestet (115mm/s bzw. 1200mm/s²).

### Wie funktioniert G33? ###

`G33` ist der G-Code für spindelsynchronisierte Bewegungen. Die besonderheit dabei ist, dass die Bewegung nicht nur eine bestimmte Form hat (wie bei `G01`) sondern auch in einer bestimmten Zeit bzw. mit einer bestimmten Geschwindigkeit erfolgen muss.

Beispiel (von X=0, Z=0 ausgehend) erzeugt `G33 X4 Z3 K5` eine gleichmäßige Bewegung in X- und Z-Richtung die eine Spindelumdrehung dauert. Es werden 5mm mit K=5mm/Umdrehung zurückgelegt.

Wenn mehrere G33 Befehle mit unterschiedlicher Geschwindigkeit (oder Richtung) hintereinander ausgeführt werden, dann kann die Maschine natürlich nicht sofort Beschleunigen. Dh. es ist völlig normal, dass die Maschine dem theoretischen Weg nicht ganz folgt. Den Weg im Rahmen der Möglichkeiten der Maschine zu planen ist Aufgabe des *Trajectory planner*. Dazu später mehr.

### Unser Testprogramm ###

Bei unserem Test-Programm ([Python script](https://github.com/torotil/caorle/blob/master/ellipse.py) / [generierter G-Code](https://github.com/torotil/caorle/blob/master/ellipse-30.ngc)) handelt es sich um ein einfaches Oval (ausgehend von einem zylindrischem Rohling). Mathematisch:
  
    X = C - A * (1 + sin(2φ)) / 2
    φ … Winkel der Spindel (in Radianten)
    A … Amplitude (20mm)
    C … Der ursprüngliche Durchmesser unseres Werkstückes, wenn X=0 genau die Drehachse der Spindel ist.

Um kein Problem mit den Entry & Exit-Moves zu haben fangen wir immer mit dem äußersten Punkt des Ovals an bzw. hören damit auf. Natürlich kann man mit `G33` keine gekrümmten Pfade zurücklegen, deshalb wird das Oval in 30 Segmente zerlegt.

Warum ausgerechnet das?

* Es ist eine relativ Runde Form. Die auftretenden Beschleunigungen sind also relativ begrenzt (theoretisch wären es weniger als 640mm/s²)
* Es ist relativ leicht zu programmieren.


### Das Ergebnis ###


Die ersten paar Schichten funktionieren: Wir erhalten ein schönes Werkstück mit einem Ovalen Querschnitt. Ab einer bestimmten Schicht verliert dann LinuxCNC gegenüber dem Plan Zeit. Dh. jedes Oval ist im vergleich zu dem Vorher um einen Winkel versetzt. Da wir mit konstantem Z-Vorschub arbeiten entsteht eine Art Spirale. Es handelt sich also nicht um ein isoliertes Problem beim Beginn oder Ende einer Schicht - also liegt es nicht an den Entry- und Exit-Moves.

### Wo liegt das Problem? ###

Bei dem Zeitverlust handelt es sich nicht um eine Differenz zwischen dem (unter Berücksichtigung der Maschinengrenzen) geplanten Weg und der Maschine (follow error) sondern bereits um einen Fehler im „Trajectory planner“. Wir können das Phänomen nämlich bereits bei der Simulation beobachten: Für jede Schicht wird Spiralförmig mit konstantem Z-Vorschub Material abgetragen. Dafür wird immer eine bestimmte Anzahl an Umdrehungen benötigt. Dh. das Abtragen jeder Schicht müsste gleich lange dauern. Tatsächlich dauern die einzelnen Durchgänge ab einer bestimmten Schicht zu lange.

Das Problem steckt also im *trajectory planner* der anstatt einen korrekten Weg zu wählen (oder zu melden, dass ers nicht kann) einfach Zeit liegen lasst. Leider ist der [entsprechende Code](https://github.com/LinuxCNC/linuxcnc/blob/master/src/emc/tp/tp.c) (3000 Zeilen C) nicht gerade leicht nachzuvollziehen. Es gibt [eine relativ gute Erklärung für die nicht-spindelsynchronisierten Modi](http://wiki.linuxcnc.org/cgi-bin/wiki.pl?TrajectoryControl), aber nicht für die Spindelsynchronisierten.

Bis jetzt habe ich es noch nicht geschafft, den Trajectory-Planner direkt(er) mit aufzurufen deshalb gibt es noch keinen einfacheren Test-Case.

### Wie könnten mögliche Lösungen aussehen? ###

* Hardware is cheap: Die Spindelachse zu einer gesteuerten Achse machen und das Problem so umgehen.
* Das Problem in LinuxCNC (oder der Konfiguration) finden und fixen.
* Einen eigenen spezialisierten trajectory planner basteln bzw. die Stepper direkt ansprechen.
