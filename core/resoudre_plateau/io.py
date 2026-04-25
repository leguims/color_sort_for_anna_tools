from .model import ResoudrePlateau

def exporter_fichier_json(resoudre_plateau: ResoudrePlateau) -> None:
    """Enregistre un fichier JSON avec les solutions et les statistiques du plateau"""
    resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)

def importer_fichier_json(resoudre_plateau: ResoudrePlateau) -> None:
    """Lit l'enregistrement JSON de la solution s'il existe"""
    data_json = resoudre_plateau._export_json_solutions.importer()
    if 'dico des longueurs' in data_json:
        resoudre_plateau._dico_des_longueurs = data_json.get('dico des longueurs')
    if 'recherche terminee' in data_json:
        resoudre_plateau._recherche_terminee = data_json.get('recherche terminee')
    if 'difficulte' in data_json:
        resoudre_plateau._difficulte = data_json.get('difficulte')
    if 'solution' in data_json:
        resoudre_plateau._solution = data_json['solution']

def to_dict(resoudre_plateau: ResoudrePlateau) -> dict:
    dict_resoudre_plateau = {
        'plateau': resoudre_plateau._plateau_initial.plateau_ligne_texte_universel,
        'recherche terminee': resoudre_plateau._recherche_terminee,
        'dico des longueurs': resoudre_plateau._dico_des_longueurs,
        'difficulte': resoudre_plateau._difficulte if resoudre_plateau._difficulte else 0,
        'solution': resoudre_plateau._solution
    }
    return dict_resoudre_plateau
