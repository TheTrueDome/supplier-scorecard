# Python Lernreferenz – Supplier Scorecard
*Nur neue Konzepte – Quality-Dashboard-Inhalte sind in der separaten Referenz dokumentiert*

---

## 1. Klassen und Vererbung

Das Herzstück des Projekts ist eine eigene PDF-Klasse die von `FPDF` erbt:

```python
from fpdf import FPDF

class ScorecardPDF(FPDF):
    def header(self):
        ...
    def footer(self):
        ...
    def scorecard(self, row, score):
        ...
```

### Was Vererbung bedeutet
`class ScorecardPDF(FPDF)` bedeutet: ScorecardPDF ist eine FPDF plus eigene Erweiterungen.
Die Klasse bekommt alle Methoden von FPDF kostenlos dazu (`add_page`, `cell`, `set_font` usw.)
und kann eigene Methoden hinzufügen oder bestehende überschreiben.

### Methoden überschreiben (Override)
`header()` und `footer()` sind in FPDF bereits definiert – als leere Platzhalter.
Indem wir sie in `ScorecardPDF` neu definieren, ersetzen wir die leeren Versionen
durch unsere eigene Implementierung. FPDF ruft sie automatisch bei jeder neuen Seite auf.

### self
`self` ist die Referenz auf die aktuelle Instanz der Klasse.
Jeder Methodenaufruf innerhalb der Klasse geht über `self`:

```python
self.set_font("DejaVu", "B", 14)   # ruft set_font auf diesem Objekt auf
self.set_xy(10, 35)                 # setzt Position auf diesem Objekt
```

---

## 2. Klasse instanziieren und verwenden

```python
pdf = ScorecardPDF()                          # Objekt erstellen
pdf.set_auto_page_break(auto=True, margin=20) # Seitenumbruch konfigurieren
pdf.scorecard(row, score)                     # eigene Methode aufrufen
pdf.output("datei.pdf")                       # PDF speichern
```

`set_auto_page_break(auto=True, margin=20)` sagt fpdf2: Wenn der Inhalt
bis auf 20mm an den unteren Rand kommt, automatisch eine neue Seite beginnen.

---

## 3. fpdf2 – PDF-Layout-Methoden

### Koordinatensystem
fpdf2 arbeitet in Millimetern. Ursprung (0,0) ist oben links.
A4-Seite: 210mm breit, 297mm hoch.

```python
self.set_xy(10, 35)        # Cursor auf x=10mm, y=35mm setzen
self.get_y()               # aktuelle Y-Position abfragen (dynamisch)
```

`get_y()` ist wichtig wenn du nicht weißt wie hoch der vorherige Inhalt war –
z. B. nach einer Tabelle mit variabler Zeilenzahl.

### Rechtecke und Linien
```python
self.rect(0, 0, 210, 28, 'F')              # gefülltes Rechteck (x, y, breite, höhe)
self.line(10, 60, 200, 60)                 # Linie von (x1,y1) nach (x2,y2)
```

`'F'` = Fill (gefüllt), `'D'` = Draw (nur Rahmen), `'FD'` = beides.

### Farben setzen
```python
self.set_fill_color(46, 95, 163)     # RGB für Füllfarbe
self.set_text_color(255, 255, 255)   # RGB für Textfarbe
self.set_draw_color(200, 200, 200)   # RGB für Linienfarbe
```

Alle Farbmethoden erwarten RGB-Werte (0–255). Die Farbe gilt ab dem Aufruf
für alle folgenden Elemente bis sie wieder geändert wird.

### Zellen – cell() und multi_cell()
```python
self.cell(breite, höhe, "Text", align="C", fill=True,
          new_x="LMARGIN", new_y="NEXT")

self.multi_cell(0, 7, "Langer Text der umgebrochen wird")
```

| Parameter | Bedeutung |
|---|---|
| `breite=0` | 0 = volle Seitenbreite bis zum rechten Rand |
| `fill=True` | Hintergrund mit `set_fill_color` füllen |
| `align="C"` | Zentriert – L=links, R=rechts, C=zentriert |
| `new_x="LMARGIN"` | Nach der Zelle zurück zum linken Rand |
| `new_y="NEXT"` | Nach der Zelle eine Zeile nach unten |
| `multi_cell` | Bricht automatisch um wenn Text zu lang – kein new_x/new_y nötig |

### Schriftart laden und setzen
```python
self.add_font("DejaVu", "",  "/usr/share/fonts/TTF/DejaVuSans.ttf")
self.add_font("DejaVu", "B", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf")
self.set_font("DejaVu", "B", 14)   # Familie, Stil (""=normal, "B"=fett), Größe
```

`add_font` muss vor dem ersten `set_font`-Aufruf mit dieser Schriftart stehen.
Ab fpdf2 v2.5 kein `uni=True` mehr nötig – alle TTF-Fonts sind automatisch Unicode-fähig.

---

## 4. Modulsystem – `__path__` und Importe

```python
import fpdf
from fpdf import FPDF

FONT_DIR = fpdf.__path__[0] + "/fonts/"
```

`import fpdf` importiert das gesamte Modul – gibt Zugriff auf `fpdf.__path__`
`from fpdf import FPDF` importiert nur die Klasse – für die direkte Verwendung

`__path__` ist ein spezielles Attribut jedes Python-Pakets das den
Installationspfad auf dem Dateisystem enthält. `[0]` weil es eine Liste ist.

---

## 5. Sets und Mengenoperationen

```python
INVERTIERT = {"Reklamationsquote_%", "Reaktionszeit_Tage"}

if metrik in INVERTIERT:
    # gilt für Metriken wo niedriger = besser
```

`{}` mit Werten aber ohne Schlüssel ist ein **Set** (Menge) – keine Duplikate,
sehr schnelle Mitgliedsprüfung mit `in`. Gut geeignet wenn du nur prüfen willst
ob ein Wert in einer Gruppe von Werten enthalten ist.

---

## 6. Dictionary of Dictionaries

```python
THRESHOLDS = {
    "Liefertreue_%": {"gruen": 95, "gelb": 85},
    "Qualitaetsrate_%": {"gruen": 98, "gelb": 94},
}

# Zugriff:
g = THRESHOLDS["Liefertreue_%"]["gruen"]   # → 95
```

Verschachtelte Dictionaries sind nützlich um strukturierte Konfiguration
zentral zu halten. Änderst du einen Schwellenwert, gilt das überall.

---

## 7. Funktionen mit mehreren Rückgabewerten

```python
def ampel(wert, metrik):
    if wert >= g:
        return "GRÜN", (0, 180, 0)    # gibt zwei Werte zurück: String + Tuple
    ...

# Aufruf:
status, farbe = ampel(row[metrik], metrik)   # Tuple unpacking
self.set_fill_color(*farbe)                   # * entpackt Tuple in Argumente
```

Python-Funktionen können mehrere Werte als Tuple zurückgeben.
`*farbe` entpackt `(0, 180, 0)` in drei separate Argumente für `set_fill_color`.

---

## 8. DataFrame-Iteration mit iterrows()

```python
for _, row in df.iterrows():
    score = gesamtscore(row)
    pdf = ScorecardPDF()
    pdf.scorecard(row, score)
```

`iterrows()` gibt für jede Zeile ein Tupel `(index, row)` zurück.
Der `_` ist Konvention für „dieser Wert wird nicht gebraucht" (der Index).
`row` ist eine pandas Series – Zugriff auf Werte per Spaltenname: `row["Lieferant"]`.

---

## 9. f-String Formatierung mit Padding

```python
print(f"  ✅ {row['Lieferant']:20s} | Score: {score:3d}/100")
```

| Format | Bedeutung | Beispiel |
|---|---|---|
| `:20s` | String auf 20 Zeichen auffüllen (linksbündig) | `"Müller GmbH        "` |
| `:3d` | Integer auf 3 Stellen auffüllen | `" 20"` |

Nützlich für sauber ausgerichtete Terminal-Ausgaben.

---

## 10. Hilfsmuster – Verzeichnis sicherstellen

```python
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

Erstellt den Ordner `output/` falls er nicht existiert.
`exist_ok=True` verhindert einen Fehler wenn der Ordner bereits vorhanden ist.
Ohne diesen Parameter würde das Skript abstürzen wenn `output/` schon da ist.

---

## 11. if __name__ == "__main__"

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

Dieser Block läuft nur wenn die Datei direkt ausgeführt wird (`python generate_scorecards.py`).
Wird die Datei als Modul importiert (`import generate_scorecards`), läuft `main()` nicht automatisch.
Best Practice für alle Python-Skripte mit einer Hauptfunktion.

---

## 12. Projektstruktur – Rückblick

```
supplier-scorecard/
├── generate_scorecards.py   # Klasse + Logik + main()
├── create_sample_data.py    # einmaliges Hilfsskript
├── suppliers.xlsx           # Eingabe (binär, nicht in VS Code öffnen)
└── output/                  # generierte PDFs (.gitignore)
```

**Wichtige Erkenntnis:** `.xlsx`-Dateien sind binäre Dateien – kein Texteditor
kann sie sinnvoll anzeigen. Zur Kontrolle immer `pd.read_excel()` nutzen
oder mit `xdg-open` in einem nativen Programm öffnen.

---

## 13. Nächste mögliche Schritte

| Erweiterung | Neue Konzepte |
|---|---|
| Zusammenfassungs-PDF (Ranking aller Lieferanten) | Mehrere Seiten, Tabellen mit dynamischer Länge |
| Trendanalyse (Q1 vs Q2) | Mehrere Excel-Sheets, `pd.merge`, Vergleichslogik |
| Kommandozeilenargument | `argparse` Modul |
| Automatischer E-Mail-Versand | `smtplib`, `email.mime` |
