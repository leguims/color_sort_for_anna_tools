"Module pour creer, resoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations
import datetime
import copy
import logging

from plateau import Plateau
from export_json import ExportJSON

DELAI_ENREGISTRER_LOT_DE_PLATEAUX = 30*60
TAILLE_ENREGISTRER_LOT_DE_PLATEAUX = 100_000
DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX = 5*60

# TODO : reprendre l'enregistrement a partir du fichier. => Pas d'amelioration, essayer de comprendre.

class LotDePlateaux:
    """Classe qui gere les lots de plateaux pour parcourir l'immensite des plateaux existants.
Le chanmps nb_plateaux_max designe la memoire allouee pour optimiser la recherche."""
    def __init__(self, dim_plateau, repertoire_export_json, nb_plateaux_max = 1_000_000):
        # Plateau de base
        self._nb_colonnes = dim_plateau[0]
        self._nb_lignes = dim_plateau[1]
        self._nb_colonnes_vides = dim_plateau[2]
        self._plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)

        # Gestion du lot de plateau
        self._ensemble_des_plateaux_valides = set() # Plateaux valides collectés dans la recherche.
        self._ensemble_des_plateaux_a_ignorer = set() # Plateaux invalides collectés dans la recherche.
        self._ensemble_des_permutations_de_nombres = None # Ensemble constant utilisé pour les permutations de jetons
        self._iter_index = 0  # Initialisation de l'index de l'itérateur
        self._nb_plateaux_max = nb_plateaux_max # Limite memoire pour la recherche (plateaux à ignorer)
        self._export_json = None
        self._ensemble_des_difficultes_de_plateaux = {} # Ensemble des plateaux classés par difficulté et profondeur
        self._a_change = False # Indique si les données de la classe ont changé.
        self._logger = logging.getLogger(f"{self._nb_colonnes}.{self._nb_lignes}.{LotDePlateaux.__name__}")
        self._recherche_terminee = False # Indique si la recherche de plateaux valides est terminee (exhaustive)
        self._recherche_dernier_plateau = None # Dernier plateau traité en recherche pour reprise
        self._revalidation_phase_1_terminee = False # Indique si la phase 1 de revalidation est terminee
        self._revalidation_phase_2_terminee = False # Indique si la phase 2 de revalidation est terminee
        self._revalidation_phase_3_terminee = False # Indique si la phase 3 de revalidation est terminee
        self._revalidation_phase_4_terminee = False # Indique si la phase 4 de revalidation est terminee
        self._revalidation_dernier_plateau = None # Dernier plateau traité en revalidation pour reprise

        # Reprise de la recherche
        self._repertoire_export_json = repertoire_export_json
        self.__init_export_json()
        self.__importer_fichier_json()

    # Iterateur avec : __iter__ et __next__
    def __iter__(self):
        if self.est_deja_termine():
            self._logger.debug(f"__iter__ : est_deja_termine.")
            # Parcourir les plateaux valides
            self._iter_index = 0  # Réinitialisation de l'index de l'itérateur
            self._iter_index_max = len(self.plateaux_valides_liste_classee)
            self._iter_list = self.plateaux_valides_liste_classee
        else:
            self._logger.debug(f"__iter__ : NOT est_deja_termine.")
            # Poursuivre la recherche de plateaux valides
            self._iter_permutation_optimisee = self.creer_plateau_initial_optimisation_permutation()
            # Initialisation : commencer les permutations avec le dernier plateau valide
            self._iter_iterateur = permutations(self._iter_permutation_optimisee)
        return self

    def __next__(self):
        if self.est_deja_termine():
            self._logger.debug(f"__next__ : est_deja_termine.")
            # Parcourir les plateaux valides
            if self._iter_index < self._iter_index_max:
                self._iter_index += 1
                self._plateau_courant.clear()
                self._plateau_courant.plateau_ligne_texte = self._iter_list[self._iter_index - 1]
                return self._plateau_courant.plateau_ligne_texte_universel
        else:
            self._logger.debug(f"__next__ : NOT est_deja_termine.")
            dernier_affichage  = datetime.datetime.now().timestamp() - DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX
            while True:
                # Itérer avec les permutations
                self._iter_permutation = next(self._iter_iterateur)
                # Ultime optimisation :
                #  - Si la colonne 1 n'a pas de 'A' => FIN des permutations.
                nb_A_sur_colonne_1 = self._iter_permutation[0:self._nb_lignes].count('A')
                if nb_A_sur_colonne_1 == 0:
                    break
                # Astuce d'optimisation : ignorer la permutation ...
                #  - Si la colonne 1 est remplie de 'A'.
                if nb_A_sur_colonne_1 == self._nb_lignes:
                    continue
                # Astuce identique avec la dernière colonne et la case vide ' '
                #  - Si la colonne N n'a pas de ' '.
                nb_VIDE_sur_colonne_N = self._iter_permutation[-self._nb_lignes:].count(' ')
                if nb_VIDE_sur_colonne_N == 0:
                    continue
                est_ignore = self.est_ignore(''.join(self._iter_permutation))
                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._recherche_dernier_plateau = self._plateau_courant.plateau_ligne_texte_universel
                self._export_json.exporter(self)
                # Log pour suivre l'avancement.
                if datetime.datetime.now().timestamp() - dernier_affichage > DELAI_AFFICHER_ITER_LOT_DE_PLATEAUX:
                    self._logger.info(f"self._recherche_dernier_plateau='{self._recherche_dernier_plateau}'")
                    dernier_affichage  = datetime.datetime.now().timestamp()
                if est_ignore:
                    self._logger.debug(f"__next__ : Plateau ignore. '{self._plateau_courant.plateau_ligne_texte_universel}'")
                else:
                    # Retourner le plateau valide
                    self._logger.debug(f"__next__ : Plateau valide. '{self._plateau_courant.plateau_ligne_texte_universel}'")
                    return self._plateau_courant.plateau_ligne_texte_universel
        self.arret_des_enregistrements()
        raise StopIteration

    def __len__(self):
        return self.nb_plateaux_valides

    def to_dict(self):
        dict_lot_de_plateaux = {}
        
        # Ajouter les informations de colonnes et lignes si disponibles
        if self._nb_colonnes is not None:
            dict_lot_de_plateaux['colonnes'] = self._nb_colonnes
            dict_lot_de_plateaux['lignes'] = self._nb_lignes
            dict_lot_de_plateaux['colonnes vides'] = self._nb_colonnes_vides

        # Indiquer si la recherche est terminee
        dict_lot_de_plateaux['recherche terminee'] = self._recherche_terminee
        dict_lot_de_plateaux['dernier plateau recherche'] = self._recherche_dernier_plateau
        dict_lot_de_plateaux['revalidation phase 1 terminee'] = self._revalidation_phase_1_terminee
        dict_lot_de_plateaux['revalidation phase 2 terminee'] = self._revalidation_phase_2_terminee
        dict_lot_de_plateaux['revalidation phase 3 terminee'] = self._revalidation_phase_3_terminee
        dict_lot_de_plateaux['revalidation phase 4 terminee'] = self._revalidation_phase_4_terminee
        dict_lot_de_plateaux['dernier plateau revalide'] = self._revalidation_dernier_plateau

        # Ajouter le nombre de plateaux et la liste des plateaux valides
        dict_lot_de_plateaux['nombre plateaux'] = len(self.plateaux_valides)
        liste_plateaux_universelle = []
        plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for plateau_txt in self.plateaux_valides:
            plateau.clear()
            plateau.plateau_ligne_texte = plateau_txt
            liste_plateaux_universelle.append(plateau.plateau_ligne_texte_universel)
        liste_plateaux_universelle.sort()
        dict_lot_de_plateaux['liste plateaux'] = liste_plateaux_universelle

        # La difficulte est un entier, mais est enregistree comme une chaine de caracteres dans le JSON. Surement car c'est une cle.
        liste_difficultes_universelles = {}
        plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for difficulte, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items():
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

    def creer_plateau_initial_optimisation_permutation(self):
        """"Reprendre au plateau valide le plus avancé dans les permutations
        ou créer le plateau de permutations initial."""
        if self._recherche_dernier_plateau is not None:
            self._logger.info("Recherche : Reprendre au dernier plateau")
            self._plateau_courant.clear()
            self._plateau_courant.plateau_ligne_texte_universel = self._recherche_dernier_plateau
            return self._plateau_courant.pour_permutations

        # TODO : Vérifier que ce code est obsolète
        #if self.plateaux_valides:
        #    # Reprendre au premier plateau valide classé (c'est le plus avancé dans les permutations)
        #    # 'A   ' est plus loin que 'AAA ' dans les permutations
        #    return [i for i in self.plateaux_valides_liste_classee[0]]

        # Sinon, calculer le plateau initial de permutations
        self._plateau_courant.creer_plateau_permutation_initial()
        return self._plateau_courant.pour_permutations

    def arret_des_enregistrements(self):
        "Methode qui finalise la recherche de plateaux"
        self._ensemble_des_plateaux_a_ignorer.clear()
        self._recherche_terminee = True
        self._recherche_dernier_plateau = None
        # Forcer l'enregistrement, car c'est l'arret et il n'y aura plus d'enregistrements.
        self._export_json.forcer_export(self)

    def est_ignore(self, permutation_plateau):
        "Retourne 'True' si le plateau est deja connu"
        if permutation_plateau not in self._ensemble_des_plateaux_valides \
            and permutation_plateau not in self._ensemble_des_plateaux_a_ignorer:
            self._plateau_courant.clear()
            self._plateau_courant.plateau_ligne_texte = permutation_plateau
            # self._logger.info(plateau)
            # Verifier que la plateau est valide
            if self._plateau_courant.est_valide and self._plateau_courant.est_interessant:
                # Enregistrer la permutation courante qui est un nouveau plateau valide
                self.__ajouter_le_plateau(self._plateau_courant)
                return False
            else:
                # Nouveau Plateau invalide ou initeressant, on l'ignore
                self.__ignorer_le_plateau(self._plateau_courant)
        return True

    def mettre_a_jour_les_plateaux_valides(self, periode_affichage):
        "Verifie la liste des plateaux valides car les regles ont change ou des regles de lots de plateaux sont a appliquer."
        #if not self._recherche_terminee:
        #    self._logger.error("mettre_a_jour_les_plateaux_valides() : la recherche de plateaux n'est pas terminee")
        #    return

        if self._revalidation_phase_1_terminee \
            and self._revalidation_phase_2_terminee \
            and self._revalidation_phase_3_terminee \
            and self._revalidation_phase_4_terminee:
            self._logger.info("mettre_a_jour_les_plateaux_valides() : deja terminee")
            return

        self.__mettre_a_jour_les_plateaux_valides_phase_1(periode_affichage)
        self.__mettre_a_jour_les_plateaux_valides_phase_2(periode_affichage)
        self.__mettre_a_jour_les_plateaux_valides_phase_3(periode_affichage)
        self.__mettre_a_jour_les_plateaux_valides_phase_4(periode_affichage)

    def __effacer_plateaux_valides(self, set_plateaux_a_effacer, prefixe_log, plateau_courant):
        if set_plateaux_a_effacer:
            plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            for iter_plateau_a_effacer in set_plateaux_a_effacer:
                if iter_plateau_a_effacer in self.plateaux_valides:
                    self.plateaux_valides.remove(iter_plateau_a_effacer)
                    plateau.clear()
                    plateau.plateau_ligne_texte = iter_plateau_a_effacer
                    self._logger.debug(f"{prefixe_log} '{plateau.plateau_ligne_texte_universel}' : en doublon avec '{plateau_courant.plateau_ligne_texte_universel}'")
                    # Reduire la liste des plateaux valides enregistrés
                    self._export_json.exporter(self)

    def __mettre_a_jour_les_plateaux_valides_phase_1(self, periode_affichage):
        """Phase 1 : Valider les plateaux au sens de la classe 'Plateau.est_valide'"""
        prefixe_log = "Phase 1 :"
        if self._revalidation_phase_1_terminee:
            self._logger.info(f"{prefixe_log} deja terminee")
            return

        self._logger.info(f"{prefixe_log} debut")
        reprendre_au_dernier_plateau = self._revalidation_dernier_plateau is not None
        if reprendre_au_dernier_plateau:
            self._logger.info(f"{prefixe_log} Reprendre au dernier plateau")

        dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
        nb_plateaux_a_valider = self.nb_plateaux_valides
        self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
        # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
        copie_plateaux_valides = copy.deepcopy(self.plateaux_valides)

        plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_ligne_texte in copie_plateaux_valides:
            plateau_courant.clear()
            plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

            if reprendre_au_dernier_plateau:
                if plateau_courant.plateau_ligne_texte_universel == self._revalidation_dernier_plateau:
                    reprendre_au_dernier_plateau = False
                    self._logger.info(f"{prefixe_log} Fin de reprise")
                nb_plateaux_a_valider -= 1
                continue

            # Traiter les doublons si le plateau courant est toujours dans la liste des plateaux valides (=non élagué)
            if iter_plateau_ligne_texte in self.plateaux_valides:
                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

                if not plateau_courant.est_valide:
                    self._logger.debug(f"{prefixe_log} '{plateau_courant.plateau_ligne_texte_universel}' : invalide a supprimer")
                    self.plateaux_valides.remove(iter_plateau_ligne_texte)
                    # Reduire la liste des plateaux valides enregistrés
                    self._export_json.exporter(self)
                elif not plateau_courant.est_interessant:
                    self._logger.debug(f"{prefixe_log} '{plateau_courant.plateau_ligne_texte_universel}' : ininteressant a supprimer")
                    self.plateaux_valides.remove(iter_plateau_ligne_texte)
                    # Reduire la liste des plateaux valides enregistrés
                    self._export_json.exporter(self)
            nb_plateaux_a_valider -= 1

            # Log pour l'avancement du traitement
            if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                dernier_affichage  = datetime.datetime.now().timestamp()

        self._revalidation_dernier_plateau = None
        self._revalidation_phase_1_terminee = True
        self._export_json.forcer_export(self)
        self._logger.info(f"{prefixe_log} terminee")

    def __mettre_a_jour_les_plateaux_valides_phase_2(self, periode_affichage):
        """Phase 2 : Chercher les doublons (permutations de jetons)"""
        prefixe_log = "Phase 2 :"
        if not self._revalidation_phase_1_terminee:
            self._logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
            return

        if self._revalidation_phase_2_terminee:
            self._logger.info(f"{prefixe_log} deja terminee")
            return

        self._logger.info(f"{prefixe_log} debut")
        reprendre_au_dernier_plateau = self._revalidation_dernier_plateau is not None
        if reprendre_au_dernier_plateau:
            self._logger.info(f"{prefixe_log} Reprendre au dernier plateau")

        dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
        nb_plateaux_a_valider = self.nb_plateaux_valides
        self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
        # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
        copie_plateaux_valides = copy.deepcopy(self.plateaux_valides)

        plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_ligne_texte in copie_plateaux_valides:
            plateau_courant.clear()
            plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

            if reprendre_au_dernier_plateau:
                if plateau_courant.plateau_ligne_texte_universel == self._revalidation_dernier_plateau:
                    reprendre_au_dernier_plateau = False
                    self._logger.info(f"{prefixe_log} Fin de reprise")
                nb_plateaux_a_valider -= 1
                continue

            # Traiter les doublons si le plateau courant est toujours dans la liste des plateaux valides (=non élagué)
            if iter_plateau_ligne_texte in self.plateaux_valides:
                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

                # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
                # Construire les permutations de jetons, rationnaliser et parcourir
                liste_permutations = self.__construire_les_permutations_de_jetons(plateau_courant)
                # Eliminer les doublons et le plateau courant
                liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
                liste_permutations.clear()
                # Ne surtout pas effacer le plateau courant, on cherche les doublons.
                liste_permutations_texte.discard(iter_plateau_ligne_texte)
                # self._logger.debug(f"{prefixe_log} taille des permutations de doublons = {len(liste_permutations_texte)}")

                self.__effacer_plateaux_valides(liste_permutations_texte, prefixe_log, plateau_courant)
                nb_plateaux_a_valider -= 1

                # Log pour l'avancement du traitement
                if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                    self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                    dernier_affichage  = datetime.datetime.now().timestamp()

        self._revalidation_dernier_plateau = None
        self._revalidation_phase_2_terminee = True
        self._export_json.forcer_export(self)
        self._logger.info(f"{prefixe_log} terminee")

    def __mettre_a_jour_les_plateaux_valides_phase_3(self, periode_affichage):
        """Phase 3 : Chercher les doublons (permutations de piles)"""
        prefixe_log = "Phase 3 :"
        if not self._revalidation_phase_1_terminee:
            self._logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
            return

        if not self._revalidation_phase_2_terminee:
            self._logger.error(f"{prefixe_log} la phase 2 n'est pas terminee")
            return

        if self._revalidation_phase_3_terminee:
            self._logger.info(f"{prefixe_log} deja terminee")
            return

        self._logger.info(f"{prefixe_log} debut")
        reprendre_au_dernier_plateau = self._revalidation_dernier_plateau is not None
        if reprendre_au_dernier_plateau:
            self._logger.info(f"{prefixe_log} Reprendre au dernier plateau")

        dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
        nb_plateaux_a_valider = self.nb_plateaux_valides
        self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
        # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
        copie_plateaux_valides = copy.deepcopy(self.plateaux_valides)

        plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_ligne_texte in copie_plateaux_valides:
            plateau_courant.clear()
            plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

            if reprendre_au_dernier_plateau:
                if plateau_courant.plateau_ligne_texte_universel == self._revalidation_dernier_plateau:
                    reprendre_au_dernier_plateau = False
                    self._logger.info(f"{prefixe_log} Fin de reprise")
                nb_plateaux_a_valider -= 1
                continue

            if iter_plateau_ligne_texte in self.plateaux_valides:
                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

                # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
                # Construire les permutations de colonnes, rationnaliser et parcourir
                liste_permutations = self.__construire_les_permutations_de_colonnes(plateau_courant)
                # Eliminer les doublons et le plateau courant
                liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
                liste_permutations.clear()
                # Ne surtout pas effacer le plateau courant, on cherche les doublons.
                liste_permutations_texte.discard(iter_plateau_ligne_texte)
                self._logger.debug(f"{prefixe_log} taille des permutations de colonnes = {len(liste_permutations_texte)}")

                self.__effacer_plateaux_valides(liste_permutations_texte, prefixe_log, plateau_courant)

                nb_plateaux_a_valider -= 1

                if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                    self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                    dernier_affichage  = datetime.datetime.now().timestamp()

        self._revalidation_dernier_plateau = None
        self._revalidation_phase_3_terminee = True
        self._export_json.forcer_export(self)
        self._logger.info(f"{prefixe_log} terminee")

    def __mettre_a_jour_les_plateaux_valides_phase_4(self, periode_affichage):
        """Phase 4 : Chercher les doublons (permutations de jetons des permutations de piles)"""
        prefixe_log = "Phase 4 :"
        if not self._revalidation_phase_1_terminee:
            self._logger.error(f"{prefixe_log} la phase 1 n'est pas terminee")
            return

        if not self._revalidation_phase_2_terminee:
            self._logger.error(f"{prefixe_log} la phase 2 n'est pas terminee")
            return

        if not self._revalidation_phase_3_terminee:
            self._logger.error(f"{prefixe_log} la phase 3 n'est pas terminee")
            return

        if self._revalidation_phase_4_terminee:
            self._logger.info(f"{prefixe_log} deja terminee")
            return

        self._logger.info(f"{prefixe_log} debut")
        reprendre_au_dernier_plateau = self._revalidation_dernier_plateau is not None
        if reprendre_au_dernier_plateau:
            self._logger.info(f"{prefixe_log} Reprendre au dernier plateau")

        dernier_affichage  = datetime.datetime.now().timestamp() - periode_affichage
        nb_plateaux_a_valider = self.nb_plateaux_valides
        self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
        # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
        copie_plateaux_valides = copy.deepcopy(self.plateaux_valides)

        plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_ligne_texte in copie_plateaux_valides:
            plateau_courant.clear()
            plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

            if reprendre_au_dernier_plateau:
                if plateau_courant.plateau_ligne_texte_universel == self._revalidation_dernier_plateau:
                    reprendre_au_dernier_plateau = False
                    self._logger.info(f"{prefixe_log} Fin de reprise")
                nb_plateaux_a_valider -= 1
                continue

            if iter_plateau_ligne_texte in self.plateaux_valides:
                # Enregistrement du plateau courant pour une eventuelle reprise.
                self._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel

                # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
                # Pour chaque permutation de colonne, realiser la permutation de jeton correspondante
                nb_permutations_jetons = 0
                liste_permutations_colonnes = self.__construire_les_permutations_de_colonnes(plateau_courant)
                for plateau_permutation_de_colonne in liste_permutations_colonnes:
                    nb_permutations_jetons += 1
                    liste_permutations = self.__construire_les_permutations_de_jetons(plateau_permutation_de_colonne)
                    # Eliminer les doublons et le plateau courant
                    liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
                    liste_permutations.clear()
                    # Ne surtout pas effacer le plateau courant, on cherche les doublons.
                    liste_permutations_texte.discard(iter_plateau_ligne_texte)
                    if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                        self._logger.debug(f"{prefixe_log} Permutations de jetons numero {nb_permutations_jetons} / {len(liste_permutations_colonnes)}")
                        dernier_affichage  = datetime.datetime.now().timestamp()

                    self.__effacer_plateaux_valides(liste_permutations_texte, prefixe_log, plateau_courant)

                nb_plateaux_a_valider -= 1

                if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                    self._logger.info(f"{prefixe_log} Il reste {nb_plateaux_a_valider} plateaux a valider")
                    dernier_affichage  = datetime.datetime.now().timestamp()

        self._revalidation_dernier_plateau = None
        self._revalidation_phase_4_terminee = True
        self._export_json.forcer_export(self)
        self._logger.info(f"{prefixe_log} terminee")

    @property
    def dernier_plateau_valide(self):
        "Ensemble des plateaux valides"
        liste_plateau_valide = list(self._ensemble_des_plateaux_valides)
        liste_plateau_valide.sort()
        return liste_plateau_valide[-1]

    @property
    def plateaux_valides(self):
        "Ensemble des plateaux valides"
        return self._ensemble_des_plateaux_valides

    @property
    def plateaux_valides_liste_classee(self):
        "Liste classee des plateaux valides"
        liste_classee = list(self._ensemble_des_plateaux_valides)
        liste_classee.sort()
        return liste_classee

    @property
    def nb_plateaux_valides(self):
        "Nombre de plateaux valides"
        return len(self._ensemble_des_plateaux_valides)

    @property
    def nb_plateaux_ignores(self):
        "Nombre de plateaux ignores"
        return len(self._ensemble_des_plateaux_a_ignorer)

    def __ajouter_le_plateau(self, plateau: Plateau):
        "Memorise un plateau deja traite"
        # La recherche de doublons et de permutations est réalisée lors de la phase de 'revalidation'
        # afin d'accelerer la recherche de plateaux valides.
        # Voir la méthode 'mettre_a_jour_les_plateaux_valides()'

        self._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
        self._a_change = True
        # Si l'export n'est pas réalisé, conserver le changement à appliquer
        # _a_change | exporter() || _a_change
        # ===================================
        #   False   |   False    ||  False
        #   False   |   True     ||  False
        #   True    |   False    ||  True
        #   True    |   True     ||  False
        self._a_change = self._a_change and not self._export_json.exporter(self)

    def __construire_les_permutations_de_colonnes(self, plateau: Plateau):
        """Methode qui construit les permutations de colonnes d'un plateau.
Le plateau lui-meme n'est pas dans les permutations."""
        liste_permutations_de_colonnes = []
        # 'set()' est utilise pour eliminer les permutations identiques
        for permutation_courante in set(permutations(plateau.plateau_rectangle_texte)):
            plateau_a_ignorer = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            plateau_a_ignorer.plateau_rectangle_texte = permutation_courante

            # Ignorer toutes les permutations
            if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                liste_permutations_de_colonnes.append(plateau_a_ignorer)
        return liste_permutations_de_colonnes

    def __construire_les_permutations_de_jetons(self, plateau: Plateau):
        """Methode qui construit les permutations de jetons d'un plateau.
Par exemple, ces deux plateaux sont equivalents pour un humain : 'ABC.CBA' ==(A devient B)== 'BAC.CAB'
Le plateau lui-meme n'est pas dans les permutations."""
        # Liste des permutations 'nombre'
        if self._ensemble_des_permutations_de_nombres is None:
            self._ensemble_des_permutations_de_nombres = set(permutations(range(self._plateau_courant.nb_familles)))

        case_vide = ' '
        liste_permutations_de_jetons = []
        for permutation_nombre_courante in self._ensemble_des_permutations_de_nombres:
            # Pour chaque permutation, transposer le plateau
            permutation_jeton_courante = []
            for jeton in plateau.plateau_ligne:
                if jeton != case_vide:
                    # Pour chaque jeton (sauf case vide), appliquer sa transposition
                    indice_jeton = ord(jeton) - ord(self._plateau_courant._liste_familles[0])
                    nouvel_indice_jeton = permutation_nombre_courante[indice_jeton]
                    nouveau_jeton = self._plateau_courant._liste_familles[nouvel_indice_jeton]
                else:
                    nouveau_jeton = case_vide
                # Creation de la transposition jeton apres jeton
                permutation_jeton_courante.append(nouveau_jeton)
            # Le plateau transpose est le plateau a ingorer
            plateau_a_ignorer = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            plateau_a_ignorer.plateau_ligne = permutation_jeton_courante
            if plateau_a_ignorer.plateau_ligne_texte != plateau.plateau_ligne_texte:
                liste_permutations_de_jetons.append(plateau_a_ignorer)
        return liste_permutations_de_jetons


    def __ignorer_le_plateau(self, plateau_a_ignorer: Plateau):
        "Ignore un plateau et met a jour les ensembles et compteurs"
        # Ignorer le plateau
        self._ensemble_des_plateaux_a_ignorer.add(plateau_a_ignorer.plateau_ligne_texte)
        # Optimiser la memoire
        self.__reduire_memoire()

    def __reduire_memoire(self):
        "Optimisation memoire quand la memoire maximum est atteinte"
        if len(self._ensemble_des_plateaux_a_ignorer) > self._nb_plateaux_max:
            self._logger.info('Reduction memoire.')
            # Vider les memoires et compteurs
            self._ensemble_des_plateaux_a_ignorer.clear()

    def fixer_taille_memoire_max(self, nb_plateaux_max):
        "Fixe le nombre maximum de plateau a memoriser"
        if nb_plateaux_max > 0:
            self._nb_plateaux_max = nb_plateaux_max
        self.__reduire_memoire()

    def __init_export_json(self):
        nom = f"Plateaux_{self._nb_colonnes}x{self._nb_lignes}"
        self._export_json = ExportJSON(delai=DELAI_ENREGISTRER_LOT_DE_PLATEAUX,
                                       longueur=TAILLE_ENREGISTRER_LOT_DE_PLATEAUX,
                                       nom_plateau=nom, nom_export=nom,
                                       repertoire=self._repertoire_export_json)

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les plateaux valides"""
        # Enregistrement des donnees dans un fichier JSON
        if self.nb_plateaux_valides > 0 and self._a_change:
            self._a_change = self._a_change and not self._export_json.forcer_export(self)

    def __importer_fichier_json(self):
        """Lit l'enregistrement JSON s'il existe"""
        data_json = self._export_json.importer()
        if "colonnes" in data_json:
            self._nb_colonnes = data_json["colonnes"]
        if "lignes" in data_json:
            self._nb_lignes = data_json["lignes"]
        if "colonnes vides" in data_json:
            self._nb_colonnes_vides = data_json["colonnes vides"]

        if "recherche terminee" in data_json:
            self._recherche_terminee = data_json["recherche terminee"]
        if self._recherche_terminee:
            self._recherche_dernier_plateau = None
            if "revalidation phase 1 terminee" in data_json:
                self._revalidation_phase_1_terminee = data_json["revalidation phase 1 terminee"]
            if "revalidation phase 2 terminee" in data_json:
                self._revalidation_phase_2_terminee = data_json["revalidation phase 2 terminee"]
            if "revalidation phase 3 terminee" in data_json:
                self._revalidation_phase_3_terminee = data_json["revalidation phase 3 terminee"]
            if "revalidation phase 4 terminee" in data_json:
                self._revalidation_phase_4_terminee = data_json["revalidation phase 4 terminee"]
            if "dernier plateau revalide" in data_json:
                self._revalidation_dernier_plateau = data_json["dernier plateau revalide"]
        else:
            if "dernier plateau recherche" in data_json:
                self._recherche_dernier_plateau = data_json["dernier plateau recherche"]
            self._revalidation_phase_1_terminee = False
            self._revalidation_phase_2_terminee = False
            self._revalidation_phase_3_terminee = False
            self._revalidation_phase_4_terminee = False
            self._revalidation_dernier_plateau = None

        # Rejouer les plateaux deja trouves
        if 'nombre plateaux' in data_json \
            and data_json['nombre plateaux'] > 0:
            # Recuperation des plateaux valides que la recherche soit terminee ou non
            # pas d'optilmisation identifiee pour accelerer la poursuite de la recherche
            plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
            for plateau_valide in data_json['liste plateaux']:
                # 'self.est_ignore()' n'est pas utilise, car il va modifier le fichier
                #  d'export quand des plateaux valides sont ajoutes. Dans notre cas, il
                #  faut ajouter les plateaux depuis l'export en considerant qu'il sont fiables.
                plateau.clear()
                plateau.plateau_ligne_texte_universel = plateau_valide
                self._ensemble_des_plateaux_valides.add(plateau.plateau_ligne_texte)
        self._nombre_de_plateaux_valides_courant = len(self._ensemble_des_plateaux_valides)

        # Solutions
        if 'liste difficulte des plateaux' in data_json and data_json['liste difficulte des plateaux']:
            # Convertir 'difficulte' et 'nb_coups' en entiers
            plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
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
                    if difficulte not in self._ensemble_des_difficultes_de_plateaux:
                        self._ensemble_des_difficultes_de_plateaux[difficulte] = {}
                    if nb_coups not in self._ensemble_des_difficultes_de_plateaux.get(difficulte):
                        self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups] = []
                    for plateau_txt in liste_plateaux:
                        plateau.clear()
                        plateau.plateau_ligne_texte_universel = plateau_txt
                        self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups].append(plateau.plateau_ligne_texte)

    def est_deja_termine(self):
        return self._recherche_terminee
    
    def est_deja_connu_difficulte_plateau(self, plateau: Plateau):
        "Methode qui verifie si le plateau est deja resolu"
        est_connu = False
        for difficulte in self._ensemble_des_difficultes_de_plateaux.keys():
            if plateau.plateau_ligne_texte in self._ensemble_des_difficultes_de_plateaux[difficulte]:
                est_connu = True
                break
        return est_connu

    def definir_difficulte_plateau(self, plateau: Plateau, difficulte, nb_coups):
        "Methode qui enregistre les difficultes des plateaux et la profondeur de leur solution"
        if difficulte not in self._ensemble_des_difficultes_de_plateaux:
            self._ensemble_des_difficultes_de_plateaux[difficulte] = {}
        if nb_coups not in self._ensemble_des_difficultes_de_plateaux[difficulte]:
            self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups] = []
        if plateau.plateau_ligne_texte not in self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups]:
            self._ensemble_des_difficultes_de_plateaux[difficulte][nb_coups].append(plateau.plateau_ligne_texte)
            self._a_change = True

    def effacer_difficulte_plateau(self):
        "Methode qui enregistre les difficultes des plateaux et la profondeur de leur solution"
        self._ensemble_des_difficultes_de_plateaux.clear()
        self._a_change = True

    def arret_des_enregistrements_de_difficultes_plateaux(self):
        "Methode qui finalise l'arret des enregistrements des difficultes de plateaux"
        # Classement des difficultes
        cles_difficulte = list(self._ensemble_des_difficultes_de_plateaux.keys())
        if None in cles_difficulte:
            cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
        cles_difficulte_classees = copy.deepcopy(cles_difficulte)
        cles_difficulte_classees.sort()
        if cles_difficulte != cles_difficulte_classees:
            # Ordonner l'ensemble par difficulte croissante
            dico_difficulte_classe = {k: self._ensemble_des_difficultes_de_plateaux.get(k) for k in cles_difficulte_classees}
            if None in self._ensemble_des_difficultes_de_plateaux:
                dico_difficulte_classe[None] = self._ensemble_des_difficultes_de_plateaux.get(None)
            self._ensemble_des_difficultes_de_plateaux = copy.deepcopy(dico_difficulte_classe)
        
        # Classement du nombre de coups
        for difficulte, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items():
            cles_nb_coups = list(dico_nb_coups.keys())
            if None in cles_nb_coups:
                cles_nb_coups.remove(None) # None est inclassable avec 'list().sort()'
            cles_nb_coups_classees = copy.deepcopy(cles_nb_coups)
            cles_nb_coups_classees.sort()
            if cles_nb_coups != cles_nb_coups_classees:
                # Ordonner l'ensemble par nombre de coups croissant
                dico_nb_coups_classe = {k: dico_nb_coups.get(k) for k in cles_nb_coups_classees}
                if None in self._ensemble_des_difficultes_de_plateaux.get(difficulte):
                    dico_nb_coups_classe[None] = self._ensemble_des_difficultes_de_plateaux.get(difficulte).get(None)
                self._ensemble_des_difficultes_de_plateaux[difficulte] = copy.deepcopy(dico_nb_coups_classe)
        self.exporter_fichier_json()

    @property
    def difficulte_plateaux(self):
        "Ensemble des difficultes de plateaux resolus"
        return self._ensemble_des_difficultes_de_plateaux

    @property
    def nb_plateaux_solutionnes(self):
        "Nombre de plateaux valides"
        return sum([len(liste_plateaux) for difficulte, dico_nb_coups in self._ensemble_des_difficultes_de_plateaux.items() for nb_coups, liste_plateaux in dico_nb_coups.items()])
