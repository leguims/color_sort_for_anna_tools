"""Formate le JSON pour l'exportation et l'importation des données du plateau
 - plateau: "A  .BAA.BB ",
 - recherche terminee: true/false,
 - dico des longueurs de solutions: {
        longueur solution: nombre de solutions de cette longueur
        ...
    },
 - dico des longueurs de blocages: {
        longueur blocage: nombre de blocages de cette longueur
        ...
    },
 - difficulte: entier représentant la difficulté du plateau
 - solution: Liste des coups d'une solution la plus courte
"""

from .model import ResoudrePlateau

def exporter_fichier_json(resoudre_plateau: ResoudrePlateau) -> None:
    """Enregistre un fichier JSON avec les solutions et les statistiques du plateau"""
    resoudre_plateau._export_json_solutions.forcer_export(resoudre_plateau)

def importer_fichier_json(resoudre_plateau: ResoudrePlateau) -> None:
    """Lit l'enregistrement JSON de la solution s'il existe"""
    data_json = resoudre_plateau._export_json_solutions.importer()
    if 'recherche terminee' in data_json:
        resoudre_plateau._recherche_terminee = data_json.get('recherche terminee', False)
    if 'dico des longueurs de solutions' in data_json:
        resoudre_plateau._dico_des_longueurs_de_solutions = data_json.get('dico des longueurs de solutions', {})
    if 'dico des longueurs de blocages' in data_json:
        resoudre_plateau._dico_des_longueurs_de_blocages = data_json.get('dico des longueurs de blocages', {})
    if 'difficulte_classique' in data_json:
        resoudre_plateau._difficulte_classique = data_json.get('difficulte_classique', -1)
    if 'difficulte_qui_perd_gagne' in data_json:
        resoudre_plateau._difficulte_qui_perd_gagne = data_json.get('difficulte_qui_perd_gagne', -1)
    if 'solution' in data_json:
        resoudre_plateau._solution = data_json['solution']

def to_dict(resoudre_plateau: ResoudrePlateau) -> dict:
    dict_resoudre_plateau = {
        'plateau': resoudre_plateau._plateau_initial.plateau_ligne_texte_universel,
        'recherche terminee': resoudre_plateau._recherche_terminee,
        'dico des longueurs de solutions': resoudre_plateau._dico_des_longueurs_de_solutions,
        'dico des longueurs de blocages': resoudre_plateau._dico_des_longueurs_de_blocages,
        'difficulte_classique': resoudre_plateau._difficulte_classique if resoudre_plateau._difficulte_classique else 0,
        'difficulte_qui_perd_gagne': resoudre_plateau._difficulte_qui_perd_gagne if resoudre_plateau._difficulte_qui_perd_gagne else 0,
        'solution': resoudre_plateau._solution
    }
    return dict_resoudre_plateau
