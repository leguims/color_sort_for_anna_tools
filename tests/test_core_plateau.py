import json
from core.plateau import Plateau

def test_plateau_creation_minimal():
    p = Plateau(2,2)
    assert p is not None
    assert p.nb_colonnes == 2
    assert p.nb_lignes == 2
    assert p.nb_colonnes_vides == 1

def test_plateau_creation_different_dimensions():
    p = Plateau(3, 4)
    assert p.nb_colonnes == 3
    assert p.nb_lignes == 4
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

def test_plateau_vide_est_valide():
    p = Plateau(2, 2)
    p.plateau_ligne_texte_universel = "    "  # Plateau vide
    assert p.est_valide == True

def test_plateau_plein_est_valide():
    p = Plateau(2, 2)
    p.plateau_ligne_texte_universel = "AA.BB"  # Plateau plein
    assert p.est_valide == True

def test_plateau_invalide():
    p = Plateau(2, 2)
    p.plateau_ligne_texte_universel = "AA.AB"  # Trop de A
    assert not p.est_valide

def test_plateau_colonnes_vides():
    p = Plateau(3, 3)
    p.plateau_ligne_texte_universel = "AA .BB .CC "  # Une colonne vide
    assert p.nb_colonnes_vides == 1
