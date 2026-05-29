# Supplier Scorecard Automation

Automatische Generierung von Lieferantenbewertungs-PDFs aus Excel-Rohdaten.

## Was das Projekt macht

Dieses Skript liest eine Excel-Tabelle mit Lieferantenkennzahlen ein und erstellt automatisch eine formatierte PDF-Scorecard pro Lieferant. Jede Scorecard enthält:

- Lieferantenname, Nummer und Bewertungszeitraum
- Gesamtscore (0–100) mit farbiger Bewertungsbox
- Metriken-Tabelle mit Ampelbewertung (GRÜN / GELB / ROT)
- Automatische Handlungsempfehlung basierend auf dem Gesamtscore

![Beispiel-Scorecard](docs/scorecard_preview.png)

## Bewertungsmetriken

| Metrik | GRÜN | GELB | ROT |
|---|---|---|---|
| Liefertreue | >= 95 % | >= 85 % | < 85 % |
| Qualitätsrate | >= 98 % | >= 94 % | < 94 % |
| Reklamationsquote | <= 1,0 % | <= 3,0 % | > 3,0 % |
| Reaktionszeit | <= 3 Tage | <= 7 Tage | > 7 Tage |

## Voraussetzungen

```bash
conda create -n scorecard python=3.11 -y
conda activate scorecard
pip install openpyxl fpdf2 pandas
```

## Verwendung

**1. Testdaten erstellen:**
```bash
python create_sample_data.py
```

**2. Scorecards generieren:**
```bash
python generate_scorecards.py
```

Die PDFs werden im Ordner `output/` gespeichert – eine Datei pro Lieferant.

## Eingabeformat (suppliers.xlsx)

| Spalte | Beschreibung | Beispiel |
|---|---|---|
| Lieferant | Name des Lieferanten | Müller GmbH |
| Lieferantennummer | Eindeutige ID | L-001 |
| Bewertungszeitraum | Quartal/Zeitraum | Q1 2026 |
| Liefertreue_% | Liefertreue in Prozent | 97.5 |
| Qualitaetsrate_% | Qualitätsrate in Prozent | 99.2 |
| Reklamationsquote_% | Reklamationsquote in Prozent | 0.8 |
| Reaktionszeit_Tage | Reaktionszeit in Tagen | 2 |

## Projektstruktur

```
supplier-scorecard/
├── generate_scorecards.py   # Hauptskript
├── create_sample_data.py    # Hilfsskript für Testdaten
├── suppliers.xlsx           # Eingabedaten
├── output/                  # Generierte PDFs (nicht versioniert)
├── start.sh                 # Startet VS Code in der richtigen Umgebung
└── git_push.sh              # Commit und Push mit Commit-Nachricht
```

## Schwellenwerte anpassen

Die Ampelgrenzen sind zentral in `generate_scorecards.py` konfiguriert:

```python
THRESHOLDS = {
    "Liefertreue_%":       {"gruen": 95, "gelb": 85},
    "Qualitaetsrate_%":    {"gruen": 98, "gelb": 94},
    "Reklamationsquote_%": {"gruen": 1.0, "gelb": 3.0},
    "Reaktionszeit_Tage":  {"gruen": 3,   "gelb": 7},
}
```

## Geplante Erweiterungen

- Zusammenfassungs-PDF mit Ranking aller Lieferanten
- Trendanalyse über mehrere Bewertungszeiträume
- Kommandozeilenargument für einzelne Lieferanten

## Hintergrund

Dieses Projekt entstand als praktische Umsetzung von Erfahrungen aus dem Lieferantenqualitätsmanagement in der Medizintechnik. Ziel war die Automatisierung eines wiederkehrenden manuellen Reporting-Prozesses.

---

*Entwickelt mit Python, pandas und fpdf2*
