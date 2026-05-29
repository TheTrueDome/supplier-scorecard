import pandas as pd
import fpdf
from fpdf import FPDF
import os

FONT_DIR = fpdf.__path__[0] + "/fonts/"


# ── Konfiguration ─────────────────────────────────────────────────────────────
EXCEL_FILE  = "suppliers.xlsx"
OUTPUT_DIR  = "output"
LOGO_TEXT   = "Supplier Scorecard"   # Platzhalter bis echtes Logo vorhanden

# Schwellenwerte für Ampelbewertung
THRESHOLDS = {
    "Liefertreue_%":       {"gruen": 95, "gelb": 85},
    "Qualitaetsrate_%":    {"gruen": 98, "gelb": 94},
    "Reklamationsquote_%": {"gruen": 1.0, "gelb": 3.0},   # niedriger = besser
    "Reaktionszeit_Tage":  {"gruen": 3,   "gelb": 7},     # niedriger = besser
}

INVERTIERT = {"Reklamationsquote_%", "Reaktionszeit_Tage"}  # niedriger = besser

# ── Ampelfarbe berechnen ──────────────────────────────────────────────────────
def ampel(wert, metrik):
    g = THRESHOLDS[metrik]["gruen"]
    y = THRESHOLDS[metrik]["gelb"]
    if metrik in INVERTIERT:
        if wert <= g:  return "GRÜN",  (0, 180, 0)
        if wert <= y:  return "GELB",  (220, 180, 0)
        return             "ROT",   (200, 0, 0)
    else:
        if wert >= g:  return "GRÜN",  (0, 180, 0)
        if wert >= y:  return "GELB",  (220, 180, 0)
        return             "ROT",   (200, 0, 0)

# ── Gesamtscore berechnen (0–100) ─────────────────────────────────────────────
def gesamtscore(row):
    scores = []
    for metrik, thresh in THRESHOLDS.items():
        wert = row[metrik]
        g, y = thresh["gruen"], thresh["gelb"]
        if metrik in INVERTIERT:
            if wert <= g:    scores.append(100)
            elif wert <= y:  scores.append(60)
            else:            scores.append(20)
        else:
            if wert >= g:    scores.append(100)
            elif wert >= y:  scores.append(60)
            else:            scores.append(20)
    return round(sum(scores) / len(scores))

# ── PDF-Klasse ────────────────────────────────────────────────────────────────
class ScorecardPDF(FPDF):

    def setup_font(self):
        self.add_font("DejaVu", "",  "fonts/DejaVuSans.ttf")
        self.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf")

    def header(self):
        self.set_fill_color(46, 95, 163)
        self.rect(0, 0, 210, 28, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 18)
        self.set_xy(10, 8)
        self.cell(0, 12, LOGO_TEXT,
                  new_x="LMARGIN", new_y="NEXT")

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10,
                f"Seite {self.page_no()}  ·  Vertraulich – nur für internen Gebrauch",
                align="C")

    def scorecard(self, row, score):
        self.setup_font()
        self.add_page()

        # ── Lieferanteninfo ───────────────────────────────────────────────────
        self.set_xy(10, 35)
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(26, 26, 26)
        self.cell(0, 8, row["Lieferant"],
                  new_x="LMARGIN", new_y="NEXT")

        self.set_font("DejaVu", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6,
                  f"Lieferantennummer: {row['Lieferantennummer']}   |   Bewertungszeitraum: {row['Bewertungszeitraum']}",
                  new_x="LMARGIN", new_y="NEXT")

        # ── Gesamtscore-Box ───────────────────────────────────────────────────
        if score >= 80:    box_color = (0, 180, 0)
        elif score >= 50:  box_color = (220, 180, 0)
        else:              box_color = (200, 0, 0)

        self.set_xy(140, 33)
        self.set_fill_color(*box_color)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 28)
        self.cell(58, 18, f"{score}/100",
                  align="C", fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_xy(140, 51)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(58, 5, "Gesamtbewertung",
                  align="C",
                  new_x="LMARGIN", new_y="NEXT")

        # ── Trennlinie ────────────────────────────────────────────────────────
        self.set_draw_color(200, 200, 200)
        self.line(10, 60, 200, 60)

        # ── Metriken-Tabelle ──────────────────────────────────────────────────
        self.set_xy(10, 65)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(26, 26, 26)
        self.set_font("DejaVu", "B", 10)
        self.cell(80, 8, "Metrik",             fill=True)
        self.cell(35, 8, "Wert",     align="C", fill=True)
        self.cell(35, 8, "Zielwert", align="C", fill=True)
        self.cell(35, 8, "Bewertung",align="C", fill=True)
        self.ln()

        
        metriken = {
            "Liefertreue_%":       ("Liefertreue",
                                    f">= {THRESHOLDS['Liefertreue_%']['gruen']} %",
                                    f"{row['Liefertreue_%']} %"),
            "Qualitaetsrate_%":    ("Qualitätsrate",
                                    f">= {THRESHOLDS['Qualitaetsrate_%']['gruen']} %",
                                    f"{row['Qualitaetsrate_%']} %"),
            "Reklamationsquote_%": ("Reklamationsquote",
                                    f"<= {THRESHOLDS['Reklamationsquote_%']['gruen']} %",
                                    f"{row['Reklamationsquote_%']} %"),
            "Reaktionszeit_Tage":  ("Reaktionszeit",
                                    f"<= {THRESHOLDS['Reaktionszeit_Tage']['gruen']} Tage",
                                    f"{row['Reaktionszeit_Tage']} Tage"),
}

        self.set_font("DejaVu", "", 10)
        for metrik, (label, ziel, anzeige) in metriken.items():
            status, farbe = ampel(row[metrik], metrik)
            self.set_fill_color(255, 255, 255)
            self.set_text_color(26, 26, 26)
            self.cell(80, 9, label)
            self.cell(35, 9, anzeige,  align="C")
            self.cell(35, 9, ziel,     align="C")
            self.set_fill_color(*farbe)
            self.set_text_color(255, 255, 255)
            self.cell(35, 9, status, align="C", fill=True)
            self.ln()
            self.set_draw_color(220, 220, 220)
            self.line(10, self.get_y(), 200, self.get_y())

        # ── Handlungsempfehlung ───────────────────────────────────────────────
        self.set_xy(10, self.get_y() + 10)
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(26, 26, 26)
        self.cell(0, 8, "Handlungsempfehlung", new_x="LMARGIN", new_y="NEXT")
        self.set_font("DejaVu", "", 10)
        self.set_text_color(80, 80, 80)

        if score >= 80:
            empfehlung = "Lieferant erfüllt alle Qualitätsanforderungen. Fortsetzung der Zusammenarbeit empfohlen."
        elif score >= 50:
            empfehlung = "Lieferant zeigt Verbesserungsbedarf. Maßnahmenplan innerhalb von 30 Tagen anfordern."
        else:
            empfehlung = "Kritische Abweichungen festgestellt. Sofortmaßnahmen erforderlich – Eskalation an Einkaufsleitung."

        self.multi_cell(0, 7, empfehlung)
    
def create_summary_pdf(ergebnisse):
    from datetime import date

    # Nach Score absteigend sortieren
    sortiert = sorted(ergebnisse, key=lambda x: x["Score"], reverse=True)
    zeitraum = sortiert[0]["Bewertungszeitraum"] if sortiert else "–"

    pdf = ScorecardPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.setup_font()
    pdf.add_page()

# ── Titel ─────────────────────────────────────────────────────────────────
    pdf.set_xy(10, 35)
    pdf.set_font("DejaVu", "B", 14)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 8, f"Lieferantenübersicht – {zeitraum}",
            new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Erstellt am: {date.today().strftime('%d.%m.%Y')}  ·  {len(sortiert)} Lieferanten bewertet",
            new_x="LMARGIN", new_y="NEXT")

# ── Trennlinie ────────────────────────────────────────────────────────────
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y() + 3, 200, pdf.get_y() + 3)
    pdf.ln(8)

# ── Tabellenkopf ──────────────────────────────────────────────────────────
    pdf.set_fill_color(240, 240, 240)
    pdf.set_text_color(26, 26, 26)
    pdf.set_font("DejaVu", "B", 10)
    pdf.cell(15,  8, "Rang",           fill=True)
    pdf.cell(65,  8, "Lieferant",      fill=True)
    pdf.cell(30,  8, "Nr.",            fill=True, align="C")
    pdf.cell(35,  8, "Score",          fill=True, align="C")
    pdf.cell(45,  8, "Bewertung",      fill=True, align="C")
    pdf.ln()

# ── Tabellenzeilen ────────────────────────────────────────────────────────
    pdf.set_font("DejaVu", "", 10)
    rang = 1
    for i, e in enumerate(sortiert):
        # Gleicher Score = gleicher Rang
        if i > 0 and e["Score"] < sortiert[i-1]["Score"]:
            rang = i + 1

        if e["Score"] >= 80:    farbe = (0, 180, 0);    status = "GRÜN"
        elif e["Score"] >= 50:  farbe = (220, 180, 0);  status = "GELB"
        else:                   farbe = (200, 0, 0);    status = "ROT"

        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(26, 26, 26)
        pdf.cell(15,  9, str(rang))
        pdf.cell(65,  9, e["Lieferant"])
        pdf.cell(30,  9, e["Lieferantennummer"], align="C")
        pdf.cell(35,  9, f"{e['Score']}/100",    align="C")
        pdf.set_fill_color(*farbe)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(45,  9, status, align="C", fill=True)
        pdf.ln()
        pdf.set_draw_color(220, 220, 220)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())

# ── KPI-Zusammenfassung ───────────────────────────────────────────────────
    gruen = sum(1 for e in sortiert if e["Score"] >= 80)
    gelb  = sum(1 for e in sortiert if 50 <= e["Score"] < 80)
    rot   = sum(1 for e in sortiert if e["Score"] < 50)

    pdf.ln(10)
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_text_color(26, 26, 26)
    pdf.cell(0, 7, "Zusammenfassung", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(0, 150, 0)
    pdf.cell(0, 6, f"  Freigegeben (GRÜN):         {gruen}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(180, 140, 0)
    pdf.cell(0, 6, f"  Maßnahmenbedarf (GELB):     {gelb}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(180, 0, 0)
    pdf.cell(0, 6, f"  Kritische Lieferanten (ROT): {rot}", new_x="LMARGIN", new_y="NEXT")

    dateiname = f"{OUTPUT_DIR}/Übersicht_{zeitraum.replace(' ', '_')}.pdf"
    pdf.output(dateiname)
    print(f"  📊 Übersicht erstellt           | {dateiname}")
# ── Hauptprogramm ─────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_excel(EXCEL_FILE)
    print(f"📋 {len(df)} Lieferanten geladen – PDFs werden erstellt...\n")

    ergebnisse = []

    for _, row in df.iterrows():
        score = gesamtscore(row)

        pdf = ScorecardPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.scorecard(row, score)

        dateiname = f"{OUTPUT_DIR}/Scorecard_{row['Lieferantennummer']}_{row['Lieferant'].replace(' ', '_')}.pdf"
        pdf.output(dateiname)
        print(f"  ✅ {row['Lieferant']:20s} | Score: {score:3d}/100 | {dateiname}")

        
        ergebnisse.append({
            "Lieferant":          row["Lieferant"],
            "Lieferantennummer":  row["Lieferantennummer"],
            "Bewertungszeitraum": row["Bewertungszeitraum"],
            "Score":              score,
        })

    
    create_summary_pdf(ergebnisse)
    print(f"\n🎉 Fertig – {len(df)} Einzel-PDFs + 1 Übersicht erstellt in /{OUTPUT_DIR}/")

if __name__ == "__main__":
    main()