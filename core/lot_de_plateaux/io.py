from .model import LotDePlateaux

from io_utils.export_json import ExportJSON
from core.plateau import Plateau

DELAI_ENREGISTRER_LOT_DE_PLATEAUX = 30*60
TAILLE_ENREGISTRER_LOT_DE_PLATEAUX = 100_000

def init_export_json(lot_de_plateaux: LotDePlateaux) -> None:
    nom = f"Plateaux_{lot_de_plateaux._nb_colonnes}x{lot_de_plateaux._nb_lignes}"
    lot_de_plateaux._export_json = ExportJSON(delai=DELAI_ENREGISTRER_LOT_DE_PLATEAUX,
                                    longueur=TAILLE_ENREGISTRER_LOT_DE_PLATEAUX,
                                    nom_plateau=nom, nom_export=nom,
                                    repertoire=lot_de_plateaux._repertoire_export_json)

def arret_des_enregistrements(lot_de_plateaux: LotDePlateaux) -> None:
    "Methode qui finalise la recherche de plateaux"
    lot_de_plateaux._ensemble_des_plateaux_a_ignorer.clear()
    lot_de_plateaux._recherche_terminee = True
    lot_de_plateaux._recherche_dernier_plateau = None
    # Forcer l'enregistrement, car c'est l'arret et il n'y aura plus d'enregistrements.
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)

def exporter_fichier_json(lot_de_plateaux: LotDePlateaux) -> None:
    """Enregistre un fichier JSON avec les plateaux valides"""
    if lot_de_plateaux.nb_plateaux_valides > 0 and lot_de_plateaux._a_change:
        lot_de_plateaux._a_change = lot_de_plateaux._a_change \
            and not lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)

def importer_fichier_json(lot_de_plateaux: LotDePlateaux) -> None:
    """Lit l'enregistrement JSON s'il existe"""
    data_json = lot_de_plateaux._export_json.importer()
    if "colonnes" in data_json:
        lot_de_plateaux._nb_colonnes = data_json["colonnes"]
    if "lignes" in data_json:
        lot_de_plateaux._nb_lignes = data_json["lignes"]
    if "colonnes vides" in data_json:
        lot_de_plateaux._nb_colonnes_vides = data_json["colonnes vides"]

    if "recherche terminee" in data_json:
        lot_de_plateaux._recherche_terminee = data_json["recherche terminee"]
    if lot_de_plateaux._recherche_terminee:
        lot_de_plateaux._recherche_dernier_plateau = None
        if "revalidation phase 1 terminee" in data_json:
            lot_de_plateaux._revalidation_phase_1_terminee = data_json["revalidation phase 1 terminee"]
        if "revalidation phase 2 terminee" in data_json:
            lot_de_plateaux._revalidation_phase_2_terminee = data_json["revalidation phase 2 terminee"]
        if "revalidation phase 3 terminee" in data_json:
            lot_de_plateaux._revalidation_phase_3_terminee = data_json["revalidation phase 3 terminee"]
        if "revalidation phase 4 terminee" in data_json:
            lot_de_plateaux._revalidation_phase_4_terminee = data_json["revalidation phase 4 terminee"]
        if "dernier plateau revalide" in data_json:
            lot_de_plateaux._revalidation_dernier_plateau = data_json["dernier plateau revalide"]
    else:
        if "dernier plateau recherche" in data_json:
            lot_de_plateaux._recherche_dernier_plateau = data_json["dernier plateau recherche"]
        lot_de_plateaux._revalidation_phase_1_terminee = False
        lot_de_plateaux._revalidation_phase_2_terminee = False
        lot_de_plateaux._revalidation_phase_3_terminee = False
        lot_de_plateaux._revalidation_phase_4_terminee = False
        lot_de_plateaux._revalidation_dernier_plateau = None

    # Rejouer les plateaux deja trouves
    if 'nombre plateaux' in data_json \
        and data_json['nombre plateaux'] > 0:
        # Recuperation des plateaux valides que la recherche soit terminee ou non
        # pas d'optilmisation identifiee pour accelerer la poursuite de la recherche
        plateau = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
        for plateau_valide in data_json['liste plateaux']:
            # 'self.est_ignore()' n'est pas utilise, car il va modifier le fichier
            #  d'export quand des plateaux valides sont ajoutes. Dans notre cas, il
            #  faut ajouter les plateaux depuis l'export en considerant qu'il sont fiables.
            plateau.clear()
            plateau.plateau_ligne_texte_universel = plateau_valide
            lot_de_plateaux._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
    lot_de_plateaux._nombre_de_plateaux_valides_courant = len(lot_de_plateaux._ensemble_des_plateaux_valides)

    # Solutions
    if 'liste difficulte des plateaux' in data_json and data_json['liste difficulte des plateaux']:
        # Convertir 'difficulte' et 'nb_coups' en entiers
        plateau = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
        for difficulte_str, dico_nb_coups in data_json['liste difficulte des plateaux'].items():
            if difficulte_str == 'null':
                difficulte = None
            else:
                difficulte = int(difficulte_str)
            for nb_coups_str, liste_plateaux in dico_nb_coups.items():
                if nb_coups_str == 'null':
                    nb_coups = None
                else:
                    nb_coups = int(nb_coups_str)
                if difficulte not in lot_de_plateaux._ensemble_des_difficultes_de_plateaux:
                    lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte] = {}
                if nb_coups not in lot_de_plateaux._ensemble_des_difficultes_de_plateaux.get(difficulte):
                    lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups] = []
                for plateau_txt in liste_plateaux:
                    plateau.clear()
                    plateau.plateau_ligne_texte_universel = plateau_txt
                    lot_de_plateaux._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups].append(plateau.plateau_ligne_texte)

def to_dict(lot_de_plateaux: LotDePlateaux) -> dict:
    dict_lot_de_plateaux = {}
    
    # Ajouter les informations de colonnes et lignes si disponibles
    if lot_de_plateaux._nb_colonnes is not None:
        dict_lot_de_plateaux['colonnes'] = lot_de_plateaux._nb_colonnes
        dict_lot_de_plateaux['lignes'] = lot_de_plateaux._nb_lignes
        dict_lot_de_plateaux['colonnes vides'] = lot_de_plateaux._nb_colonnes_vides

    # Indiquer si la recherche est terminee
    dict_lot_de_plateaux['recherche terminee'] = lot_de_plateaux._recherche_terminee
    dict_lot_de_plateaux['dernier plateau recherche'] = lot_de_plateaux._recherche_dernier_plateau
    dict_lot_de_plateaux['revalidation phase 1 terminee'] = lot_de_plateaux._revalidation_phase_1_terminee
    dict_lot_de_plateaux['revalidation phase 2 terminee'] = lot_de_plateaux._revalidation_phase_2_terminee
    dict_lot_de_plateaux['revalidation phase 3 terminee'] = lot_de_plateaux._revalidation_phase_3_terminee
    dict_lot_de_plateaux['revalidation phase 4 terminee'] = lot_de_plateaux._revalidation_phase_4_terminee
    dict_lot_de_plateaux['dernier plateau revalide'] = lot_de_plateaux._revalidation_dernier_plateau

    # Ajouter le nombre de plateaux et la liste des plateaux valides
    dict_lot_de_plateaux['nombre plateaux'] = len(lot_de_plateaux.plateaux_valides)
    liste_plateaux_universelle = []
    plateau = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
    for plateau_txt in lot_de_plateaux.plateaux_valides:
        plateau.clear()
        plateau.plateau_ligne_texte = plateau_txt
        liste_plateaux_universelle.append(plateau.plateau_ligne_texte_universel)
    liste_plateaux_universelle.sort()
    dict_lot_de_plateaux['liste plateaux'] = liste_plateaux_universelle

    # La difficulte est un entier, mais est enregistree comme une chaine de caracteres dans le JSON. Surement car c'est une cle.
    liste_difficultes_universelles = {}
    plateau = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
    for difficulte, dico_nb_coups in lot_de_plateaux._ensemble_des_difficultes_de_plateaux.items():
        liste_difficultes_universelles[difficulte] = {}
        for nb_coups, liste_plateaux in dico_nb_coups.items():
            liste_difficultes_universelles[difficulte][nb_coups] = []
            for plateau_txt in liste_plateaux:
                plateau.clear()
                plateau.plateau_ligne_texte = plateau_txt
                liste_difficultes_universelles[difficulte][nb_coups].append(plateau.plateau_ligne_texte_universel)
            liste_difficultes_universelles[difficulte][nb_coups].sort()
    dict_lot_de_plateaux['liste difficulte des plateaux']= liste_difficultes_universelles

    return dict_lot_de_plateaux

