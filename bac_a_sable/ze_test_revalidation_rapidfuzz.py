from rapidfuzz import fuzz

# Liste de chaînes à comparer
lines = [
    "AAAAB.ABBBB.CDC  .CCC  .DDDD ",
    "AAAAB.ABBBB.CDCCC.C    .DDDD ",
    "AAAAB.ABBBB.CDD  .DDDCC.CC   ",
    "AAAAB.ABBBB.CDDCC.DDD  .CC   ",
    "AAAAB.ABBBB.CDDD .DDC  .CCC  ",
    "AAAAB.ABBBB.CDDD .DDCCC.C    ",
    "AAAAB.ABBBB.CDDDC.DD   .CCC  ",
    "AAAAB.ABBBB.CDDDD.C    .DCCC ",
    "AAAAB.ABBBB.CDDDD.CCC  .DC   ",
    "AAAAB.ABBBB.CDDDD.DCCCC.     "
]

# Score de similarité	Interprétation générale
# 90–100 Presque identiques, probablement des doublons
# 75–89  Très similaires, variantes légères
# 50–74  Moyennement similaires, structure partagée mais différences notables
# 30–49  Faible similarité, quelques motifs communs
# < 30   Très différents, probablement sans lien

# Seuil de similarité (sur 100)
seuil = 30

# Comparaison de chaque ligne avec les autres
for i, line1 in enumerate(lines):
    print(f"\nComparaisons pour la ligne {i+1}:      {line1}")
    for j, line2 in enumerate(lines):
        if i != j:
            score = fuzz.ratio(line1, line2)
            print(f"  ↳ avec ligne {j+1:02}: similarité = {score:.0f}% {line2}")

for line1 in lines:
    print(f"\n{line1}")
    for line2 in lines:
        if line1 != line2:
            score = fuzz.ratio(line1, line2)
            print(f"{line2} similarité = {score:.0f}%")

