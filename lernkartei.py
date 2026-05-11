"""
lernkartei.py – Lernkartei-System für die Musikklausur
======================================================
Algorithmus:
  Liste 1  →  zufällige Frage ausgeben
            →  Antwort anzeigen lassen
            →  Richtig? → Liste 2
            →  Falsch?  → bleibt in Liste 1
  Liste 1 leer? → Liste 2 → Liste 1 kopieren, neu starten
"""

import random
import os
import json

# Fragen aus separater Datei importieren
from fragen import FRAGEN

# ──────────────────────────────────────────────
#  Hilfsfunktionen
# ──────────────────────────────────────────────

SAVE_FILE = "fortschritt.json"


def lade_paare(rohliste: list) -> list[tuple]:
    """Wandelt [F, A, F, A, ...] in [(F, A), (F, A), ...] um."""
    if len(rohliste) % 2 != 0:
        raise ValueError("FRAGEN-Liste hat eine ungerade Anzahl an Einträgen! "
                         "Jede Frage braucht genau eine Antwort.")
    return [(rohliste[i], rohliste[i + 1]) for i in range(0, len(rohliste), 2)]


def speichere_fortschritt(liste1: list, liste2: list):
    """Speichert den aktuellen Stand in eine JSON-Datei."""
    daten = {
        "liste1": liste1,
        "liste2": liste2,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)


def lade_fortschritt() -> tuple[list, list] | None:
    """Lädt gespeicherten Fortschritt, falls vorhanden."""
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        daten = json.load(f)
    return daten["liste1"], daten["liste2"]


def loesche_fortschritt():
    """Löscht die Speicherdatei."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def clear():
    """Konsole leeren (plattformübergreifend)."""
    os.system("cls" if os.name == "nt" else "clear")


def trennlinie():
    print("─" * 55)


def eingabe(prompt: str, erlaubt: list[str]) -> str:
    """Liest eine Eingabe und validiert sie."""
    while True:
        antwort = input(prompt).strip().lower()
        if antwort in erlaubt:
            return antwort
        print(f"  Bitte nur eingeben: {' / '.join(erlaubt)}")


# ──────────────────────────────────────────────
#  Hauptprogramm
# ──────────────────────────────────────────────

def starte_lernkartei():
    clear()
    print("╔═══════════════════════════════════════════════╗")
    print("║          🎵  MUSIK-LERNKARTEI  🎵             ║")
    print("╚═══════════════════════════════════════════════╝")
    print()

    alle_paare = lade_paare(FRAGEN)

    # Gespeicherten Fortschritt anbieten
    gespeichert = lade_fortschritt()
    if gespeichert:
        liste1, liste2 = gespeichert
        print(f"  💾  Gespeicherter Fortschritt gefunden:")
        print(f"      Liste 1 (noch zu lernen): {len(liste1)} Karten")
        print(f"      Liste 2 (bereits richtig): {len(liste2)} Karten")
        print()
        wahl = eingabe("  Fortsetzen? [j/n]: ", ["j", "n"])
        if wahl == "n":
            loesche_fortschritt()
            liste1 = [list(p) for p in alle_paare]
            liste2 = []
    else:
        liste1 = [list(p) for p in alle_paare]
        liste2 = []

    runde = 1
    gesamt_richtig = 0
    gesamt_falsch = 0

    # ── Haupt-Schleife ──────────────────────────────
    while True:
        clear()
        trennlinie()
        print(f"  Runde {runde}  |  "
              f"Noch zu lernen: {len(liste1)}  |  "
              f"Bereits richtig: {len(liste2)}")
        trennlinie()

        # ── Liste 1 ist leer → Runde abgeschlossen ─
        if len(liste1) == 0:
            print()
            print("  ✅  Super! Alle Karten dieser Runde richtig beantwortet!")
            print(f"      Runde {runde} abgeschlossen.")
            print()
            trennlinie()
            wahl = eingabe("  Neue Runde starten? [j/n]: ", ["j", "n"])
            if wahl == "n":
                break
            # Liste 2 → Liste 1, Liste 2 leeren
            liste1 = [p[:] for p in liste2]
            liste2 = []
            runde += 1
            loesche_fortschritt()
            continue

        # ── Zufällige Karte aus Liste 1 ─────────────
        index = random.randrange(len(liste1))
        paar = liste1[index]
        frage, antwort = paar[0], paar[1]

        print()
        print(f"  Karte {len(liste2) + 1} von {len(liste1) + len(liste2)}")
        print()
        print("  ❓ FRAGE:")
        print(f"  {frage}")
        print()

        eingabe("  [Enter] → Antwort anzeigen", [""])

        print()
        trennlinie()
        print("  💡 ANTWORT:")
        print(f"  {antwort}")
        trennlinie()
        print()

        wahl = eingabe("  Richtig oder Falsch?  [r/f]  |  Beenden: [b]: ",
                       ["r", "f", "b"])

        if wahl == "b":
            speichere_fortschritt(liste1, liste2)
            print()
            print("  💾  Fortschritt gespeichert. Bis zum nächsten Mal!")
            print()
            break
        elif wahl == "r":
            liste1.pop(index)
            liste2.append(paar)
            gesamt_richtig += 1
            print("  ✅  Richtig! Karte wandert in Liste 2.")
        else:
            gesamt_falsch += 1
            print("  ❌  Falsch. Karte bleibt in Liste 1.")

        input("  [Enter] → Weiter")

    # ── Abschluss-Statistik ─────────────────────────
    clear()
    trennlinie()
    print("  📊  STATISTIK DIESER SITZUNG")
    trennlinie()
    print(f"  Richtig beantwortet : {gesamt_richtig}")
    print(f"  Falsch beantwortet  : {gesamt_falsch}")
    gesamt = gesamt_richtig + gesamt_falsch
    if gesamt > 0:
        quote = round(gesamt_richtig / gesamt * 100)
        print(f"  Trefferquote        : {quote} %")
    trennlinie()
    print()
    print("  Viel Erfolg bei der Klausur! 🎵")
    print()


# ── Entry Point ───────────────────────────────
if __name__ == "__main__":
    starte_lernkartei()
