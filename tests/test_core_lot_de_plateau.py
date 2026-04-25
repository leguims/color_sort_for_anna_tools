import json
from core.lot_de_plateaux import LotDePlateaux
from core.plateau import Plateau

def test_lot_creation(tmp_path):
    lot = LotDePlateaux([2,2,1], tmp_path)
    assert len(lot) == 0

def test_lot_ajout_et_filtrage(tmp_path):
    lot = LotDePlateaux([2,2,1], tmp_path)
    p = Plateau(2,2)
    p.plateau_ligne_texte_universel = "AAB.BB .A  "
    lot.ajouter_le_plateau(p)
    assert lot.nb_plateaux_valides >= 1

def test_lot_memoire_max(tmp_path):
    lot = LotDePlateaux([2,2,1], tmp_path)
    lot.fixer_taille_memoire_max(1)

    p1 = Plateau(2,2)
    p1.plateau_ligne_texte_universel = "AAB.BB .A  "
    p2 = Plateau(2,2)
    p2.plateau_ligne_texte_universel = "CCC.DD .D  "
    p3 = Plateau(2,2)
    p3.plateau_ligne_texte_universel = "EEE.FF .F  "

    lot.ajouter_le_plateau(p1)
    lot.ajouter_le_plateau(p2)
    lot.ajouter_le_plateau(p3)

    assert lot.nb_plateaux_valides <= 1
