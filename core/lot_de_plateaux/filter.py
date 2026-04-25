import copy
import datetime

from .model import LotDePlateaux
from .generator import (
    construire_les_permutations_de_jetons,
    construire_les_permutations_de_colonnes
)
from core.plateau import Plateau

def plateau_est_ignore(lot_de_plateaux: LotDePlateaux, permutation_plateau: str) -> bool:
    "Retourne 'True' si le plateau est deja connu"
    if permutation_plateau not in lot_de_plateaux._ensemble_des_plateaux_valides \
        and permutation_plateau not in lot_de_plateaux._ensemble_des_plateaux_a_ignorer:
        lot_de_plateaux._plateau_courant.clear()
        lot_de_plateaux._plateau_courant.plateau_ligne_texte = permutation_plateau
        # lot_de_plateaux.logger.info(plateau)
        # Verifier que la plateau est valide
        if lot_de_plateaux._plateau_courant.est_valide and lot_de_plateaux._plateau_courant.est_interessant:
            # Enregistrer la permutation courante qui est un nouveau plateau valide
            ajouter_le_plateau(lot_de_plateaux, lot_de_plateaux._plateau_courant)
            return False
        else:
            # Nouveau Plateau invalide ou initeressant, on l'ignore
            ignorer_le_plateau(lot_de_plateaux, lot_de_plateaux._plateau_courant)
    return True

def ajouter_le_plateau(lot_de_plateaux: LotDePlateaux, plateau: Plateau) -> None:
    "Memorise un plateau deja traite"
    # La recherche de doublons et de permutations est réalisée lors de la phase de 'revalidation'
    # afin d'accelerer la recherche de plateaux valides.
    # Voir la méthode 'mettre_a_jour_les_plateaux_valides()'

    lot_de_plateaux._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
    lot_de_plateaux._a_change = True
    # Si l'export n'est pas réalisé, conserver le changement à appliquer
    # _a_change | exporter() || _a_change
    # ===================================
    #   False   |   False    ||  False
    #   False   |   True     ||  False
    #   True    |   False    ||  True
    #   True    |   True     ||  False
    lot_de_plateaux._a_change = lot_de_plateaux._a_change \
        and not lot_de_plateaux._export_json.exporter(lot_de_plateaux)

def ignorer_le_plateau(lot_de_plateaux: LotDePlateaux, plateau_a_ignorer: Plateau) -> None:
    "Ignore un plateau et met a jour les ensembles et compteurs"
    # Ignorer le plateau
    lot_de_plateaux._ensemble_des_plateaux_a_ignorer.add(plateau_a_ignorer.plateau_ligne_texte)
    # Optimiser la memoire
    reduire_memoire(lot_de_plateaux)

def fixer_taille_memoire_max(lot_de_plateaux: LotDePlateaux, nb_plateaux_max: int) -> None:
    "Fixe le nombre maximum de plateau a memoriser"
    if nb_plateaux_max > 0:
        lot_de_plateaux._nb_plateaux_max = nb_plateaux_max
    reduire_memoire(lot_de_plateaux)

def reduire_memoire(lot_de_plateaux: LotDePlateaux) -> None:
    "Optimisation memoire quand la memoire maximum est atteinte"
    if len(lot_de_plateaux._ensemble_des_plateaux_a_ignorer) > lot_de_plateaux._nb_plateaux_max:
        lot_de_plateaux.logger.info('Reduction memoire.')
        # Vider les memoires et compteurs
        lot_de_plateaux._ensemble_des_plateaux_a_ignorer.clear()

def effacer_plateaux_valides(lot_de_plateaux: LotDePlateaux, set_plateaux_a_effacer: set, prefixe_log: str, plateau_courant: Plateau) -> None:
    if set_plateaux_a_effacer:
        plateau = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
        for iter_plateau_a_effacer in set_plateaux_a_effacer:
            if iter_plateau_a_effacer in lot_de_plateaux.plateaux_valides:
                lot_de_plateaux.plateaux_valides.remove(iter_plateau_a_effacer)
                plateau.clear()
                plateau.plateau_ligne_texte = iter_plateau_a_effacer
                lot_de_plateaux.logger.debug(f"{prefixe_log} '{plateau.plateau_ligne_texte_universel}' : en doublon avec '{plateau_courant.plateau_ligne_texte_universel}'")
                # Reduire la liste des plateaux valides enregistrés
                lot_de_plateaux._export_json.exporter(lot_de_plateaux)

def mettre_a_jour_les_plateaux_valides(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    "Verifie la liste des plateaux valides car les regles ont change ou des regles de lots de plateaux sont a appliquer."
    #if not self._recherche_terminee:
    #    self._logger.error("mettre_a_jour_les_plateaux_valides() : la recherche de plateaux n'est pas terminee")
    #    return

    if lot_de_plateaux._revalidation_phase_1_terminee \
        and lot_de_plateaux._revalidation_phase_2_terminee \
        and lot_de_plateaux._revalidation_phase_3_terminee \
        and lot_de_plateaux._revalidation_phase_4_terminee:
        lot_de_plateaux.logger.info("mettre_a_jour_les_plateaux_valides() : deja terminee")
        return

    mettre_a_jour_les_plateaux_valides_phase_1(lot_de_plateaux, periode_affichage)
    mettre_a_jour_les_plateaux_valides_phase_2(lot_de_plateaux, periode_affichage)
    mettre_a_jour_les_plateaux_valides_phase_3(lot_de_plateaux, periode_affichage)
    mettre_a_jour_les_plateaux_valides_phase_4(lot_de_plateaux, periode_affichage)

def mettre_a_jour_les_plateaux_valides_phase_1(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 1 : Valider les plateaux au sens de la classe 'Plateau.est_valide'"""
    prefixe_log = "Phase 1 :"
    if lot_de_plateaux._revalidation_phase_1_terminee:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._revalidation_dernier_plateau is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._revalidation_dernier_plateau:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        # Traiter les doublons si le plateau courant est toujours dans la liste des plateaux valides (=non élagué)
        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

            if not plateau_courant.est_valide:
                lot_de_plateaux.logger.debug(f"{prefixe_log} '{plateau_courant.plateau_ligne_texte_universel}' : invalide a supprimer")
                lot_de_plateaux.plateaux_valides.remove(iter_plateau_ligne_texte)
                # Reduire la liste des plateaux valides enregistrés
                lot_de_plateaux._export_json.exporter(lot_de_plateaux)
            elif not plateau_courant.est_interessant:
                lot_de_plateaux.logger.debug(f"{prefixe_log} '{plateau_courant.plateau_ligne_texte_universel}' : ininteressant a supprimer")
                lot_de_plateaux.plateaux_valides.remove(iter_plateau_ligne_texte)
                # Reduire la liste des plateaux valides enregistrés
                lot_de_plateaux._export_json.exporter(lot_de_plateaux)
        nb_plateaux_a_valider -= 1

        # Log pour l'avancement du traitement
        if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
            lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
            dernier_affichage  = datetime.datetime.now().timestamp()

    lot_de_plateaux._revalidation_dernier_plateau = None
    lot_de_plateaux._revalidation_phase_1_terminee = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

def mettre_a_jour_les_plateaux_valides_phase_2(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 2 : Chercher les doublons (permutations de jetons)"""
    prefixe_log = "Phase 2 :"
    if not lot_de_plateaux._revalidation_phase_1_terminee:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
        return

    if lot_de_plateaux._revalidation_phase_2_terminee:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._revalidation_dernier_plateau is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._revalidation_dernier_plateau:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        # Traiter les doublons si le plateau courant est toujours dans la liste des plateaux valides (=non élagué)
        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

            # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
            # Construire les permutations de jetons, rationnaliser et parcourir
            liste_permutations = construire_les_permutations_de_jetons(lot_de_plateaux, plateau_courant)
            # Eliminer les doublons et le plateau courant
            liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
            liste_permutations.clear()
            # Ne surtout pas effacer le plateau courant, on cherche les doublons.
            liste_permutations_texte.discard(iter_plateau_ligne_texte)
            # lot_de_plateaux.logger.debug(f"{prefixe_log} taille des permutations de doublons = {len(liste_permutations_texte)}")

            effacer_plateaux_valides(lot_de_plateaux, liste_permutations_texte, prefixe_log, plateau_courant)
            nb_plateaux_a_valider -= 1

            # Log pour l'avancement du traitement
            if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                dernier_affichage  = datetime.datetime.now().timestamp()

    lot_de_plateaux._revalidation_dernier_plateau = None
    lot_de_plateaux._revalidation_phase_2_terminee = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

def mettre_a_jour_les_plateaux_valides_phase_3(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 3 : Chercher les doublons (permutations de piles)"""
    prefixe_log = "Phase 3 :"
    if not lot_de_plateaux._revalidation_phase_1_terminee:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
        return

    if not lot_de_plateaux._revalidation_phase_2_terminee:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 2 n'est pas terminee")
        return

    if lot_de_plateaux._revalidation_phase_3_terminee:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._revalidation_dernier_plateau is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._revalidation_dernier_plateau:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

            # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
            # Construire les permutations de colonnes, rationnaliser et parcourir
            liste_permutations = construire_les_permutations_de_colonnes(lot_de_plateaux, plateau_courant)
            # Eliminer les doublons et le plateau courant
            liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
            liste_permutations.clear()
            # Ne surtout pas effacer le plateau courant, on cherche les doublons.
            liste_permutations_texte.discard(iter_plateau_ligne_texte)
            lot_de_plateaux.logger.debug(f"{prefixe_log} taille des permutations de colonnes = {len(liste_permutations_texte)}")

            effacer_plateaux_valides(lot_de_plateaux, liste_permutations_texte, prefixe_log, plateau_courant)

            nb_plateaux_a_valider -= 1

            if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                dernier_affichage  = datetime.datetime.now().timestamp()

    lot_de_plateaux._revalidation_dernier_plateau = None
    lot_de_plateaux._revalidation_phase_3_terminee = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

def mettre_a_jour_les_plateaux_valides_phase_4(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 4 : Chercher les doublons (permutations de jetons des permutations de piles)"""
    prefixe_log = "Phase 4 :"
    if not lot_de_plateaux._revalidation_phase_1_terminee:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
        return

    if not lot_de_plateaux._revalidation_phase_2_terminee:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 2 n'est pas terminee")
        return

    if not lot_de_plateaux._revalidation_phase_3_terminee:
        lot_de_plateaux ._logger.error(f"{prefixe_log} la phase 3 n'est pas terminee")
        return

    if lot_de_plateaux._revalidation_phase_4_terminee:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._revalidation_dernier_plateau is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._nb_colonnes, lot_de_plateaux._nb_lignes, lot_de_plateaux._nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._revalidation_dernier_plateau:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

            # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
            # Pour chaque permutation de colonne, realiser la permutation de jeton correspondante
            nb_permutations_jetons = 0
            liste_permutations_colonnes = construire_les_permutations_de_colonnes(lot_de_plateaux, plateau_courant)
            for plateau_permutation_de_colonne in liste_permutations_colonnes:
                nb_permutations_jetons += 1
                liste_permutations = construire_les_permutations_de_jetons(lot_de_plateaux, plateau_permutation_de_colonne)
                # Eliminer les doublons et le plateau courant
                liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
                liste_permutations.clear()
                # Ne surtout pas effacer le plateau courant, on cherche les doublons.
                liste_permutations_texte.discard(iter_plateau_ligne_texte)
                if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                    lot_de_plateaux.logger.debug(f"{prefixe_log} Permutations de jetons numero {nb_permutations_jetons} / {len(liste_permutations_colonnes)}")
                    dernier_affichage  = datetime.datetime.now().timestamp()

                effacer_plateaux_valides(lot_de_plateaux, liste_permutations_texte, prefixe_log, plateau_courant)

            nb_plateaux_a_valider -= 1

            if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                dernier_affichage  = datetime.datetime.now().timestamp()

    lot_de_plateaux._revalidation_dernier_plateau = None
    lot_de_plateaux._revalidation_phase_4_terminee = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

