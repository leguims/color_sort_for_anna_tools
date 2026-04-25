import json

from _pytest.tmpdir import tmp_path
from core.resoudre_plateau import ResoudrePlateau
from core.plateau import Plateau

def test_resoudre_plateau_creation(tmp_path):
    p = Plateau(2,2)
    p.plateau_ligne_texte_universel = "AAB.BB .A  "
    r = ResoudrePlateau(p,tmp_path)
    assert len(r) == 0

def test_resoudre_plateau_export(tmp_path):
    p = Plateau(2,2)
    p.plateau_ligne_texte_universel = "AAB.BB .A  "
    r = ResoudrePlateau(p, tmp_path)

    f = tmp_path / "resoudre.json"
    r.exporter_fichier_json(f)

    data = json.loads(f.read_text())
    assert "plateau" in data

def test_resoudre_plateau_avec_plateau_valide(tmp_path):
    p = Plateau(3, 3)
    p.plateau_ligne_texte_universel = "AA .BB .CC "  # Plateau valide
    r = ResoudrePlateau(p, tmp_path)
    assert len(r) == 0

def test_resoudre_plateau_avec_plateau_invalide(tmp_path):
    p = Plateau(3, 3)
    p.plateau_ligne_texte_universel = "AAA.BBB.CCC"  # Plateau invalide
    r = ResoudrePlateau(p, tmp_path)
    assert len(r) == 0

def test_resoudre_plateau_export_json(tmp_path):
    p = Plateau(3, 3)
    p.plateau_ligne_texte_universel = "AA .BB .CC .ABC"
    r = ResoudrePlateau(p, tmp_path)

    f = tmp_path / "solution.json"
    r.exporter_fichier_json(f)

    data = json.loads(f.read_text())
    assert "plateau" in data
    assert data["plateau"] == "AA .BB .CC "
