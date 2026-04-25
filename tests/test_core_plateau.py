import json
from core.plateau import Plateau

def test_plateau_creation_minimal():
    p = Plateau(2,2)
    assert p is not None
    assert p.nb_colonnes == 2
    assert p.nb_lignes == 2
    assert p.nb_colonnes_vides == 1

def test_plateau_est_valide():
    p = Plateau(2,2)
    p.plateau_ligne_texte_universel = "AAB.BB .A  "
    assert p.est_valide == True

def test_plateau_est_valide():
    p = Plateau(2,2)
    p.plateau_ligne_texte_universel = "AA .BB .B A"
    assert not p.est_valide
    p.plateau_ligne_texte_universel = "AAAA.BB .B  "
    assert not p.est_valide
