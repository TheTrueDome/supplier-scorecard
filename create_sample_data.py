import pandas as pd

data = {
    "Lieferant":           ["Müller GmbH", "Schmidt AG", "Weber KG", "Fischer GmbH", "Braun Ltd."],
    "Lieferantennummer":   ["L-001", "L-002", "L-003", "L-004", "L-005"],
    "Bewertungszeitraum":  ["Q1 2026"] * 5,
    "Liefertreue_%":       [97.5, 88.0, 95.2, 72.0, 99.1],
    "Qualitaetsrate_%":    [99.2, 96.5, 98.1, 91.0, 99.8],
    "Reklamationsquote_%": [0.8, 2.1, 1.5, 6.2, 0.3],
    "Reaktionszeit_Tage":  [2, 8, 4, 12, 1],
}

df = pd.DataFrame(data)
df.to_excel("suppliers.xlsx", index=False)
print("✅ suppliers.xlsx erstellt")
print(df.to_string(index=False))