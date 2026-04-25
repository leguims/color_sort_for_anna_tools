import difflib

# Liste à comparer
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

# Comparaison de chaque ligne avec les autres
for i, line1 in enumerate(lines):
    print(f"\nComparaisons pour la ligne {i+1}:       {line1}")
    for j, line2 in enumerate(lines):
        if i != j:
            ratio = difflib.SequenceMatcher(None, line1, line2).ratio()
            print(f"  ↳ avec ligne {j+1:02}: similarité = {100*ratio:.0f}% {line2}")


a = "AAAAB.ABBBB.CDC  .CCC  .DDDD "
b = "AAAAB.ABBBB.CDCCC.C    .DDDD "

matcher1 = difflib.SequenceMatcher(None, a, b, autojunk=False)
matcher2 = difflib.SequenceMatcher(None, b, a, autojunk=False)

print(f"Ratio a→b : {matcher1.ratio():.5f}")
print(f"Ratio b→a : {matcher2.ratio():.5f}")
