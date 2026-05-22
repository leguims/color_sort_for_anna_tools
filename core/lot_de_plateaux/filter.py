import copy
import datetime

from .model import LotDePlateaux
from .generator import (
    construire_les_permutations_de_jetons,
    construire_les_permutations_de_colonnes
)
from core.plateau import Plateau

def effacer_plateaux_valides(lot_de_plateaux: LotDePlateaux, set_plateaux_a_effacer: set, prefixe_log: str, plateau_courant: Plateau) -> None:
    if set_plateaux_a_effacer:
        plateau = Plateau(lot_de_plateaux._plateau_courant.nb_colonnes, lot_de_plateaux._plateau_courant.nb_lignes, lot_de_plateaux._plateau_courant.nb_colonnes_vides)
        for iter_plateau_a_effacer in set_plateaux_a_effacer:
            if iter_plateau_a_effacer in lot_de_plateaux.plateaux_valides:
                lot_de_plateaux.plateaux_valides.remove(iter_plateau_a_effacer)
                plateau.clear()
                plateau.plateau_ligne_texte = iter_plateau_a_effacer
                lot_de_plateaux.logger.debug(f"{prefixe_log} '{plateau.plateau_ligne_texte_universel}' : en doublon avec '{plateau_courant.plateau_ligne_texte_universel}'")
                # Reduire la liste des plateaux valides enregistrés
                lot_de_plateaux._export_json.exporter(lot_de_plateaux)

def filtrer_plateaux_invalides_ou_ininteressants(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 1 : Valider les plateaux au sens de la classe 'Plateau.est_valide'"""
    prefixe_log = "filtrer plateaux invalides ou ininteressants :"
    if lot_de_plateaux.est_filtre_plateaux_invalides_ou_ininteressants:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._filtrer_dernier_plateau_traite is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._plateau_courant.nb_colonnes,
                              lot_de_plateaux._plateau_courant.nb_lignes,
                              lot_de_plateaux._plateau_courant.nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._filtrer_dernier_plateau_traite:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        # Traiter les doublons si le plateau courant est toujours dans la liste des plateaux valides (=non élagué)
        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._filtrer_dernier_plateau_traite = plateau_courant.plateau_ligne_texte_universel

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

    lot_de_plateaux._filtrer_dernier_plateau_traite = None
    lot_de_plateaux._filtrer_plateaux_invalides_ou_ininteressants = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

def filtrer_doublons_permutation_jetons(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 2 : Chercher les doublons (permutations de jetons)"""
    prefixe_log = "filtrer doublons permutation jetons :"
    if not lot_de_plateaux.est_filtre_plateaux_invalides_ou_ininteressants:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
        return

    if lot_de_plateaux.est_filtre_doublons_permutation_jetons:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._filtrer_dernier_plateau_traite is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._plateau_courant.nb_colonnes,
                              lot_de_plateaux._plateau_courant.nb_lignes,
                              lot_de_plateaux._plateau_courant.nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._filtrer_dernier_plateau_traite:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        # Traiter les doublons si le plateau courant est toujours dans la liste des plateaux valides (=non élagué)
        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._filtrer_dernier_plateau_traite = plateau_courant.plateau_ligne_texte_universel

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

    lot_de_plateaux._filtrer_dernier_plateau_traite = None
    lot_de_plateaux._filtrer_doublons_permutation_jetons = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

def filtrer_doublons_permutation_piles(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 3 : Chercher les doublons (permutations de piles)"""
    prefixe_log = "Filtrer doublons permutations piles :"
    if not lot_de_plateaux.est_filtre_plateaux_invalides_ou_ininteressants:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
        return

    if not lot_de_plateaux.est_filtre_doublons_permutation_jetons:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 2 n'est pas terminee")
        return

    if lot_de_plateaux.est_filtre_doublons_permutation_piles:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._filtrer_dernier_plateau_traite is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._plateau_courant.nb_colonnes,
                              lot_de_plateaux._plateau_courant.nb_lignes,
                              lot_de_plateaux._plateau_courant.nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._filtrer_dernier_plateau_traite:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._filtrer_dernier_plateau_traite = plateau_courant.plateau_ligne_texte_universel

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

    lot_de_plateaux._filtrer_dernier_plateau_traite = None
    lot_de_plateaux._filtrer_doublons_permutation_piles = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

def filtrer_doublons_permutation_jetons_piles(lot_de_plateaux: LotDePlateaux, periode_affichage: float) -> None:
    """Phase 4 : Chercher les doublons (permutations de jetons des permutations de piles)"""
    prefixe_log = "Filtrer doublons permutations jetons et piles :"
    if not lot_de_plateaux.est_filtre_plateaux_invalides_ou_ininteressants:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
        return

    if not lot_de_plateaux.est_filtre_doublons_permutation_jetons:
        lot_de_plateaux.logger.error(f"{prefixe_log} la phase 2 n'est pas terminee")
        return

    if not lot_de_plateaux.est_filtre_doublons_permutation_piles:
        lot_de_plateaux ._logger.error(f"{prefixe_log} la phase 3 n'est pas terminee")
        return

    if lot_de_plateaux.est_filtre_doublons_permutation_jetons_piles:
        lot_de_plateaux.logger.info(f"{prefixe_log} deja terminee")
        return

    lot_de_plateaux.logger.info(f"{prefixe_log} debut")
    reprendre_au_dernier_plateau = lot_de_plateaux._filtrer_dernier_plateau_traite is not None
    if reprendre_au_dernier_plateau:
        lot_de_plateaux.logger.info(f"{prefixe_log} Reprendre au dernier plateau")

    dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
    nb_plateaux_a_valider = lot_de_plateaux.nb_plateaux_valides
    lot_de_plateaux.logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
    # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
    copie_plateaux_valides = copy.deepcopy(lot_de_plateaux.plateaux_valides)

    plateau_courant = Plateau(lot_de_plateaux._plateau_courant.nb_colonnes,
                              lot_de_plateaux._plateau_courant.nb_lignes,
                              lot_de_plateaux._plateau_courant.nb_colonnes_vides)
    for iter_plateau_ligne_texte in copie_plateaux_valides:
        plateau_courant.clear()
        plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

        if reprendre_au_dernier_plateau:
            if plateau_courant.plateau_ligne_texte_universel == lot_de_plateaux._filtrer_dernier_plateau_traite:
                reprendre_au_dernier_plateau = False
                lot_de_plateaux.logger.info(f"{prefixe_log} Fin de reprise")
            nb_plateaux_a_valider -= 1
            continue

        if iter_plateau_ligne_texte in lot_de_plateaux.plateaux_valides:
            # Enregistrement du plateau courant pour une eventuelle reprise.
            lot_de_plateaux._filtrer_dernier_plateau_traite = plateau_courant.plateau_ligne_texte_universel

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

    lot_de_plateaux._filtrer_dernier_plateau_traite = None
    lot_de_plateaux._filtrer_doublons_permutation_jetons_piles = True
    lot_de_plateaux._export_json.forcer_export(lot_de_plateaux)
    lot_de_plateaux.logger.info(f"{prefixe_log} terminee")

