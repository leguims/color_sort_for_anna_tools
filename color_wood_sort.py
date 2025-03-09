"Module pour creer, resoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations
import pathlib
import datetime
import json
import copy
from pathlib import Path
from multiprocessing import Pool, cpu_count
import logging

import cProfile
import pstats

REPERTOIRE_SORTIE_RACINE = 'Analyses'
DELAI_ENREGISTRER_LOT_DE_PLATEAUX = 30*60
TAILLE_ENREGISTRER_LOT_DE_PLATEAUX = 100_000

# TODO : reprendre l'enregistrement a partir du fichier. => Pas d'amelioration, essayer de comprendre.

class Plateau:
    "Classe qui implemente un plateau. Son contenu et ses differentes representations."
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides=1):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._est_valide = None
        self._dico_validite_index_vide = {}
        # plateau_ligne : ['A', 'A', 'B', 'B', ' ', ' ']
        self._plateau_ligne = None
        # plateau_ligne_texte : ['AABB  ']
        self._plateau_ligne_texte = None
        # plateau_rectangle : [['A', 'A'], ['B', 'B]', [' ', ' ']]
        self._plateau_rectangle = None
        # plateau_rectangle_texte : ['AA', 'BB', '  ']
        self._plateau_rectangle_texte = None
        self._str_format = ""
        self._nb_familles = nb_colonnes - nb_colonnes_vides
        self._liste_familles = []
        self.__creer_les_familles()

    def clear(self):
        "Efface le plateau pour en ecrire un nouveau"
        self._est_valide = None
        self._plateau_ligne = None
        self._plateau_ligne_texte = None
        self._plateau_ligne_texte_universel = None
        self._plateau_rectangle = None
        self._plateau_rectangle_texte = None
        self._str_format = ""

    def __str__(self):
        if not self._str_format:
            for ligne in self.plateau_rectangle:
                self._str_format += f"{ligne}\n"
        return self._str_format

    def __eq__(self, autre):
        if not isinstance(autre, Plateau):
            # Ne sont pas comparables
            return NotImplemented
        # Comparer taille et contenu
        return (self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides, self._plateau_ligne) == \
            (autre._nb_colonnes, autre._nb_lignes, autre._nb_colonnes_vides, autre._plateau_ligne)

    def __hash__(self):
        return hash((self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides, self._plateau_ligne))

    @property
    def nb_colonnes(self):
        "Nombre de colonnes du plateau"
        return self._nb_colonnes

    @property
    def nb_lignes(self):
        "Nombre de lignes du plateau"
        return self._nb_lignes

    @property
    def nb_colonnes_vides(self):
        "Nombre de colonnes vides du plateau"
        return self._nb_colonnes_vides

    @property
    def plateau_ligne(self):
        "Representation en 1 ligne du plateau (liste)"
        return self._plateau_ligne

    @plateau_ligne.setter
    def plateau_ligne(self, plateau_ligne):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self.clear()
        self._plateau_ligne = tuple(plateau_ligne)

    @property
    def plateau_ligne_texte(self):
        "Representation en 1 ligne du plateau (texte)"
        if not self._plateau_ligne_texte:
            self.__creer_plateau_ligne_texte()
        return self._plateau_ligne_texte

    @plateau_ligne_texte.setter
    def plateau_ligne_texte(self, plateau_ligne_texte):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self.plateau_ligne = [c for c in plateau_ligne_texte] # via setter
        self._plateau_ligne_texte = plateau_ligne_texte

    @property
    def plateau_ligne_texte_universel(self):
        "Representation en 1 ligne du plateau (texte)"
        if not self._plateau_ligne_texte_universel:
            self.__creer_plateau_ligne_texte_universel()
        return self._plateau_ligne_texte_universel

    @plateau_ligne_texte_universel.setter
    def plateau_ligne_texte_universel(self, plateau_ligne_texte_universel):
        # Pas de verification sur la validite,
        # pour pouvoir traiter les plateaux invalides
        # a ignorer.
        self._plateau_ligne_texte = plateau_ligne_texte_universel.replace('.', '')
        self.plateau_ligne = [c for c in self._plateau_ligne_texte] # via setter

    @property
    def plateau_rectangle(self):
        "Representation en rectangle (colonnes et lignes) du plateau (liste)"
        if not self._plateau_rectangle:
            self.__creer_plateau_rectangle()
        return self._plateau_rectangle

    @property
    def plateau_rectangle_texte(self):
        "Representation en rectangle (colonnes et lignes) du plateau (texte)"
        if not self._plateau_rectangle_texte:
            self.__creer_plateau_rectangle_texte()
        return self._plateau_rectangle_texte

    @plateau_rectangle_texte.setter
    def plateau_rectangle_texte(self, plateau_rectangle_texte):
        # Rectangle_texte => plateau_ligne_texte
        plateau_ligne_texte = ''.join(plateau_rectangle_texte)
        # plateau_ligne_texte => plateau_ligne
        self.plateau_ligne = [c for c in plateau_ligne_texte]

    @property
    def pour_permutations(self):
        "Format du plateau utilise pour les permutations"
        return self.plateau_ligne

    def __creer_plateau_ligne_texte(self):
        """['A', 'A', 'B', 'B', ' ', ' '] => ['AABB  ']"""
        if self._plateau_ligne:
            self._plateau_ligne_texte = ''.join(self._plateau_ligne)

    def __creer_plateau_ligne_texte_universel(self):
        """['A', 'A', 'B', 'B', ' ', ' '] => ['AA.BB.  ']"""
        if not self._plateau_rectangle_texte:
            self.__creer_plateau_rectangle_texte()
        if self._plateau_rectangle_texte:
            self._plateau_ligne_texte_universel = '.'.join(self._plateau_rectangle_texte)

    def __creer_plateau_rectangle(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => [['A', 'A'], ['B', 'B'], [' ', ' ']]"""
        if self._plateau_ligne:
            self._plateau_rectangle = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle.append(
                    self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes])

    def __creer_plateau_rectangle_texte(self):
        """"['A', 'A', 'B', 'B', ' ', ' '] => ['AA', 'BB', '  ']"""
        if self._plateau_ligne:
            self._plateau_rectangle_texte = []
            for colonne in range(self._nb_colonnes):
                self._plateau_rectangle_texte.append(''.join(
                    self._plateau_ligne[colonne*self._nb_lignes : (colonne + 1)*self._nb_lignes]))

    @property
    def nb_familles(self):
        "Nombre de familles de couleurs dans le plateau"
        return self._nb_familles

    def __creer_les_familles(self):
        "Creer une liste des familles"
        if not self._liste_familles:
            self._liste_familles = [chr(ord('A')+F) for F in range(self._nb_familles) ]
        return self._liste_familles

    def creer_plateau_initial(self):
        """"Cree un plateau en ligne initial = ['A', 'A', 'B', 'B', ' ', ' ']"""
        if not self._plateau_ligne:
            self.plateau_ligne = tuple(
                [self._liste_familles[famille] for famille in range(self._nb_familles)
                                                 for membre in range(self._nb_lignes)]
                +[' ' for vide in range(self._nb_colonnes_vides)
                         for membre in range(self._nb_lignes)] )

    @property
    def est_valide(self):
        """"Verifie si le plateau en parametre est valide et interessant"""
        if self._plateau_ligne and self._est_valide is None:
            # Est-ce que le plateau est interessant ?
            # Une colonne achevee est sans interet.
            if self.une_colonne_est_pleine_et_monocouleur():
                self._est_valide = False
                return self._est_valide


            # Vérifier la validité du plateau
            # Pour chaque colonne, les cases vides sont sur les dernieres cases
            case_vide = ' '

            # Construction de la position des cases vides
            count = self._plateau_ligne.count(case_vide)
            index_vide = []
            index_courant = -1
            for _ in range(count):
                index_courant = self._plateau_ligne.index(case_vide, index_courant+1)
                index_vide.append(index_courant)
            index_vide = tuple(index_vide) # l'index_vide devient invariable
            
            # Est-ce que cet index est valide ?
            if index_vide in self._dico_validite_index_vide:
                return self._dico_validite_index_vide.get(index_vide)
            
            # Index inconnu, identifier sa validite
            for colonne in range(self._nb_colonnes):
                case_vide_presente = False
                for ligne in range(self._nb_lignes):
                    if not case_vide_presente:
                        # Chercher la premiere case vide de la colonne
                        if (colonne * self._nb_lignes + ligne) in index_vide:
                            case_vide_presente = True
                    else:
                        # Toutes les autres case de la lignes doivent etre vides
                        if (colonne * self._nb_lignes + ligne) not in index_vide:
                            self._est_valide = False
                            self._dico_validite_index_vide[index_vide] = self._est_valide
                            return self._est_valide
            self._est_valide = True
            self._dico_validite_index_vide[index_vide] = self._est_valide

        return self._est_valide

    def la_colonne_est_vide(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        return self.plateau_rectangle_texte[colonne].isspace()

    def la_colonne_est_pleine(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        return self.plateau_rectangle_texte[colonne].count(' ') == 0

    def la_colonne_est_pleine_et_monocouleur(self, colonne):
        est_pleine = self.la_colonne_est_pleine(colonne)
        colonne_texte = self.plateau_rectangle_texte[colonne]
        premiere_case = colonne_texte[0]
        return est_pleine and colonne_texte.count(premiere_case) == self.nb_lignes

    def une_colonne_est_pleine_et_monocouleur(self):
        for colonne in range(self.nb_colonnes):
            if self.la_colonne_est_pleine_et_monocouleur(colonne):
                return True
        return False

    def la_couleur_au_sommet_de_la_colonne(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        colonne_texte = self.plateau_rectangle_texte[colonne]
        derniere_case_non_vide = colonne_texte.strip()[-1]
        return derniere_case_non_vide

    def _compter_les_couleurs_identiques_au_sommet(self, colonne_texte, couleur):
        nb = 0
        colonne_inversee = list(colonne_texte.rstrip())
        colonne_inversee.reverse()
        for case in colonne_inversee:
            if case == couleur:
                nb += 1
            else:
                break
        return nb

    def nombre_de_case_vide_de_la_colonne(self, colonne):
        if colonne >= self.nb_colonnes:
            raise IndexError(f"Le numero de colonne est hors du plateau ({colonne}>={self.nb_colonnes}).")
        colonne_texte = self.plateau_rectangle_texte[colonne]
        return len(colonne_texte) - len(colonne_texte.rstrip())

    def nombre_de_cases_monocouleur_au_sommet_de_la_colonne(self, colonne):
        couleur = self.la_couleur_au_sommet_de_la_colonne(colonne)
        colonne_texte = self.plateau_rectangle_texte[colonne]
        return self._compter_les_couleurs_identiques_au_sommet(colonne_texte, couleur)

    def deplacer_blocs(self, colonne_depart, colonne_arrivee, nombre_blocs = 1):
        if nombre_blocs != self.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(colonne_depart):
            raise ValueError("Le nombre de bloc a deplacer est different a celui du plateau")
        self.annuler_le_deplacer_blocs(colonne_arrivee, colonne_depart, nombre_blocs)

    def annuler_le_deplacer_blocs(self, colonne_depart_a_annuler, colonne_arrivee_a_annuler, nombre_blocs = 1):
        if nombre_blocs > self.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(colonne_arrivee_a_annuler):
            raise ValueError("Le nombre de bloc a deplacer est superieur a celui du plateau")
        if nombre_blocs > self.nombre_de_case_vide_de_la_colonne(colonne_depart_a_annuler):
            raise ValueError("Le nombre de bloc a deplacer est plus grand que ce que la colonne peut recevoir")
        couleur = self.la_couleur_au_sommet_de_la_colonne(colonne_arrivee_a_annuler)
        case_vide = ' '
        plateau = self.plateau_rectangle_texte
        # Inverser la colonne pour remplacer les couleur du haut, puis retablir l'ordre
        # colonne de depart : 'ABAA' => 'AABA' => '  BA' => 'AB  '
        plateau[colonne_arrivee_a_annuler] = plateau[colonne_arrivee_a_annuler][::-1].replace(couleur, case_vide, nombre_blocs)[::-1]
        # colonne d'arrivee : 'C   ' => 'CAA '
        plateau[colonne_depart_a_annuler] = plateau[colonne_depart_a_annuler].replace(case_vide, couleur, nombre_blocs)
        self.plateau_rectangle_texte = plateau

    def a_gagne(self):
        """"Verifie si le plateau actuel est gagnant"""
        return False

class LotDePlateaux:
    """Classe qui gere les lots de plateaux pour parcourir l'immensite des plateaux existants.
Le chanmps nb_plateaux_max designe la memoire allouee pour optimiser la recherche."""
    def __init__(self, dim_plateau, nb_plateaux_max = 1_000_000):
        # Plateau de base
        self._nb_colonnes = dim_plateau[0]
        self._nb_lignes = dim_plateau[1]
        self._nb_colonnes_vides = dim_plateau[2]
        self._plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)

        # Gestion du lot de plateau
        self._ensemble_des_plateaux_valides = set() # Plateaux valides collectés dans la recherche.
        self._ensemble_des_plateaux_a_ignorer = set() # Plateaux invalides collectés dans la recherche.
        self._ensemble_des_permutations_de_nombres = None # Ensemble constant utilisé pour les permutations de jetons
        self._nb_plateaux_max = nb_plateaux_max # Limite memoire pour la recherche (plateaux à ignorer)
        self._export_json = None
        self._ensemble_des_difficultes_de_plateaux = {} # Ensemble des plateaux classés par difficulté et profondeur
        self._a_change = False # Indique si les données de la classe ont changé.
        self._logger = logging.getLogger(f"{self._nb_colonnes}.{self._nb_lignes}.{LotDePlateaux.__name__}")
        self._recherche_terminee = False # Indique si la recherche de plateaux valides est terminee (exhaustive)
        self._revalidation_phase_1_terminee = False # Indique si la phase 1 de revalidation est terminee
        self._revalidation_phase_2_terminee = False # Indique si la phase 2 de revalidation est terminee
        self._revalidation_dernier_plateau = None # Dernier plateau traité en revalidation pour reprise

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
        dict_lot_de_plateaux['revalidation phase 1 terminee'] = self._revalidation_phase_1_terminee
        dict_lot_de_plateaux['revalidation phase 2 terminee'] = self._revalidation_phase_2_terminee
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

    def formater_duree(self, duree):
        """Formater la duree en une chaîne de caracteres lisible."""
        if duree < 0.001:
            return f"{int(duree * 1_000_000)} microsecondes"
        elif duree < 1:
            return f"{int(duree * 1_000)} millisecondes"
        elif duree < 60:
            return f"{int(duree)} secondes"
        else:
            minutes, secondes = divmod(duree, 60)
            heures, minutes = divmod(minutes, 60)
            jours, heures = divmod(heures, 24)
            if jours > 0:
                return f"{int(jours)} jours {int(heures)} heures"
            elif heures > 0:
                return f"{int(heures)} heures {int(minutes)} minutes"
            else:
                return f"{int(minutes)} minutes {int(secondes)} secondes"

    def arret_des_enregistrements(self):
        "Methode qui finalise la recherche de plateaux"
        self._ensemble_des_plateaux_a_ignorer.clear()
        self._recherche_terminee = True
        self.exporter_fichier_json()

    def est_ignore(self, permutation_plateau):
        "Retourne 'True' si le plateau est deja connu"
        if permutation_plateau not in self._ensemble_des_plateaux_valides \
            and permutation_plateau not in self._ensemble_des_plateaux_a_ignorer:
            self._plateau_courant.clear()
            self._plateau_courant.plateau_ligne_texte = permutation_plateau
            # self._logger.info(plateau)
            # Verifier que la plateau est valide
            if self._plateau_courant.est_valide:
                # Enregistrer la permutation courante qui est un nouveau plateau valide
                self.__ajouter_le_plateau(self._plateau_courant)
                return False
            else:
                # Nouveau Plateau invalide, on l'ignore
                self.__ignorer_le_plateau(self._plateau_courant)
        return True

    def mettre_a_jour_les_plateaux_valides(self, periode_affichage):
        "Verifie la liste des plateaux valides car les regles ont change ou des regles de lots de plateaux sont a appliquer."
        if not self._recherche_terminee:
            self._logger.error("mettre_a_jour_les_plateaux_valides() : la recherche de plateaux n'est pas terminee")
            return

        if self._revalidation_phase_1_terminee and self._revalidation_phase_2_terminee:
            self._logger.info("mettre_a_jour_les_plateaux_valides() : deja terminee")
            return

        self.__mettre_a_jour_les_plateaux_valides_phase_1(periode_affichage)
        self.__mettre_a_jour_les_plateaux_valides_phase_2(periode_affichage)

    def __mettre_a_jour_les_plateaux_valides_phase_1(self, periode_affichage):
        # Phase 1 : Validité au sens de la classe 'Plateau.est_valide'
        if self._revalidation_phase_1_terminee:
            self._logger.info("Phase 1 : deja terminee")
            return

        reprendre_au_dernier_plateau = self._revalidation_dernier_plateau is not None
        if reprendre_au_dernier_plateau:
            self._logger.info("Phase 1 : Reprendre au dernier plateau")

        dernier_affichage  = datetime.datetime.now().timestamp()
        nb_plateaux_a_valider = self.nb_plateaux_valides
        # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
        copie_plateaux_valides = copy.deepcopy(self.plateaux_valides)

        plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_ligne_texte in copie_plateaux_valides:
            plateau_courant.clear()
            plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

            if reprendre_au_dernier_plateau:
                if plateau_courant.plateau_ligne_texte_universel == self._revalidation_dernier_plateau:
                    reprendre_au_dernier_plateau = False
                    self._logger.info("Phase 1 : Fin de reprise")
                nb_plateaux_a_valider -= 1
                continue

            if iter_plateau_ligne_texte in self.plateaux_valides:
                if not plateau_courant.est_valide:
                    self._logger.debug(f"Phase 1 : '{plateau_courant.plateau_ligne_texte_universel}' : invalide a supprimer")
                    self.plateaux_valides.remove(iter_plateau_ligne_texte)
            nb_plateaux_a_valider -= 1

            if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                self._logger.info(f"Phase 1 : Il reste {nb_plateaux_a_valider} plateaux a valider")
                dernier_affichage  = datetime.datetime.now().timestamp()
                # Enregistrement du plateau courant pour une eventuelle reprise.
                # + Reduire la liste des plateaux valides
                self._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel
                self._export_json.forcer_export(self)

        self._revalidation_dernier_plateau = None
        self._revalidation_phase_1_terminee = True
        self._export_json.forcer_export(self)
        self._logger.info(f"Phase 1 : terminee")

    def __mettre_a_jour_les_plateaux_valides_phase_2(self, periode_affichage):
        # Phase 2 : Chercher les doublons (permutations de piles et de jetons)
        if not self._revalidation_phase_1_terminee:
            self._logger.error("Phase 2 : la phase 1 n'est pas terminee")
            return

        if self._revalidation_phase_2_terminee:
            self._logger.info("Phase 2 : deja terminee")
            return

        reprendre_au_dernier_plateau = self._revalidation_dernier_plateau is not None
        if reprendre_au_dernier_plateau:
            self._logger.info("Phase 2 : Reprendre au dernier plateau")

        dernier_affichage  = datetime.datetime.now().timestamp()
        nb_plateaux_a_valider = self.nb_plateaux_valides
        # Copie de la liste pour pouvoir effacer des elements au sein de la boucle FOR
        copie_plateaux_valides = copy.deepcopy(self.plateaux_valides)

        plateau_courant = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_ligne_texte in copie_plateaux_valides:
            plateau_courant.clear()
            plateau_courant.plateau_ligne_texte = iter_plateau_ligne_texte

            if reprendre_au_dernier_plateau:
                if plateau_courant.plateau_ligne_texte_universel == self._revalidation_dernier_plateau:
                    reprendre_au_dernier_plateau = False
                    self._logger.info("Phase 2 : Fin de reprise")
                nb_plateaux_a_valider -= 1
                continue

            if iter_plateau_ligne_texte in self.plateaux_valides:
                # Verifier de nouvelles formes de doublons (permutations) dans les plateaux valides
                # Construire les permutations de colonnes et jetons, rationnaliser et parcourir
                liste_permutations = self.__construire_les_permutations_de_colonnes(plateau_courant) \
                                    + self.__construire_les_permutations_de_jetons(plateau_courant)
                # Pour chaque permutation de colonne, realiser la permutation de jeton correspondante
                for plateau_permutation_de_colonne in self.__construire_les_permutations_de_colonnes(plateau_courant):
                    liste_permutations += self.__construire_les_permutations_de_jetons(plateau_permutation_de_colonne)
                # Eliminer les doublons et le plateau courant
                liste_permutations_texte = set([p.plateau_ligne_texte for p in liste_permutations])
                if iter_plateau_ligne_texte in liste_permutations_texte:
                    # Ne surtout pas effacer le plateau courant, on cherche les doublons.
                    liste_permutations_texte.remove(iter_plateau_ligne_texte)

                # Enregistrer continuement, car la tache est longue
                if liste_permutations_texte:
                    plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
                    for iter_plateau_a_effacer in liste_permutations_texte:
                        if iter_plateau_a_effacer in self.plateaux_valides:
                            self.plateaux_valides.remove(iter_plateau_a_effacer)
                            plateau.clear()
                            plateau.plateau_ligne_texte = iter_plateau_a_effacer
                            self._logger.debug(f"Phase 2 :  '{plateau.plateau_ligne_texte_universel}' : en doublon avec '{plateau_courant.plateau_ligne_texte_universel}'")
                nb_plateaux_a_valider -= 1

                if datetime.datetime.now().timestamp() - dernier_affichage > periode_affichage:
                    self._logger.info(f"Phase 2 : Il reste {nb_plateaux_a_valider} plateaux a valider")
                    dernier_affichage  = datetime.datetime.now().timestamp()
                    # Enregistrement du plateau courant pour une eventuelle reprise.
                    # + Reduire la liste des plateaux valides
                    self._revalidation_dernier_plateau = plateau_courant.plateau_ligne_texte_universel
                    self._export_json.forcer_export(self)

        self._revalidation_dernier_plateau = None
        self._revalidation_phase_2_terminee = True
        self._export_json.forcer_export(self)
        self._logger.info(f"Phase 2 : terminee")

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
                                       nom_plateau=nom, nom_export=nom)

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
            if "revalidation phase 1 terminee" in data_json:
                self._revalidation_phase_1_terminee = data_json["revalidation phase 1 terminee"]
            if "revalidation phase 2 terminee" in data_json:
                self._revalidation_phase_2_terminee = data_json["revalidation phase 2 terminee"]
            if "dernier plateau revalide" in data_json:
                self._revalidation_dernier_plateau = data_json["dernier plateau revalide"]
        else:
            self._revalidation_phase_1_terminee = False
            self._revalidation_phase_2_terminee = False
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
        self.__init_export_json()
        self.__importer_fichier_json()
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

class ResoudrePlateau:
    "Classe de resultion d'un plateau par parcours de toutes les possibilites de choix"
    def __init__(self, plateau_initial: Plateau):
        self._plateau_initial = copy.deepcopy(plateau_initial)
        self._liste_des_solutions = []
        # Statistiques des solutions:
        #   - la plus longue
        #   - la plus courte
        #   - la moyenne
        #   - le nombre de solution
        # Les longueurs sont toutes egales (courtes et longues).
        # La longueur de la solution est la grandeur qui quantifie la difficulte du plateau.
        self._statistiques = {}
        self._liste_plateaux_gagnants = None
        self._liste_des_choix_possibles = None
        self._liste_des_choix_courants = None
        self._difficulte = None
        nom_plateau = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}"
        nom = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}_Resolution_{plateau_initial.plateau_ligne_texte.replace(' ', '-')}"
        self._export_json_analyses = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom, repertoire = 'Analyses')
        self._export_json_solutions = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom, repertoire = 'Solutions')
        self.__importer_fichier_json()

    def __len__(self):
        "La longueur de la solution definit la difficulte"
        # Le nombre de soltuioon n'a pas d'incidence sur la difficulte
        if self.solution_la_plus_courte:
            return self.solution_la_plus_courte
        return 0

    def to_dict(self):
        dict_resoudre_plateau = {}
        dict_resoudre_plateau['plateau'] = self._plateau_initial.plateau_ligne_texte_universel
        dict_resoudre_plateau['nombre de solutions'] = self.nb_solutions
        dict_resoudre_plateau['solution la plus courte'] = self.solution_la_plus_courte
        dict_resoudre_plateau['solution la plus longue'] = self.solution_la_plus_longue
        dict_resoudre_plateau['solution moyenne'] = self.solution_moyenne
        dict_resoudre_plateau['difficulte'] = self.difficulte
        dict_resoudre_plateau['liste des solutions'] = self._liste_des_solutions
        return dict_resoudre_plateau

    def __ensemble_des_choix_possibles(self):
        "Liste tous les choix possible pour un plateau (valide et invalides)"
        if not self._liste_des_choix_possibles:
            # Liste de tous les possibles a construire selon la dimension du plateau
            self._liste_des_choix_possibles = []
            for depart in range(self._plateau_initial.nb_colonnes):
                for arrivee in range(self._plateau_initial.nb_colonnes):
                    if depart != arrivee:
                        self._liste_des_choix_possibles.append(tuple([depart, arrivee]))
        # Nombre de choix = (nb_colonnes * (nb_colonnes-1))
        return self._liste_des_choix_possibles

    def __ensemble_des_plateaux_gagnants(self):
        "Liste tous les plateaux gagnants"
        if self._liste_plateaux_gagnants is None:
            nb_c = self._plateau_initial.nb_colonnes
            nb_l = self._plateau_initial.nb_lignes
            nb_cv = self._plateau_initial.nb_colonnes_vides
            plateau_gagnant = Plateau(nb_c, nb_l, nb_cv)
            plateau_gagnant.creer_plateau_initial()

            self._liste_plateaux_gagnants = []
            # 'set()' est utilise pour eliminer les permutations identiques
            for permutation_courante in set(permutations(plateau_gagnant.plateau_rectangle_texte)):
                plateau_gagnant_courant = Plateau(nb_c, nb_l, nb_cv)
                plateau_gagnant_courant.plateau_rectangle_texte = permutation_courante
                self._liste_plateaux_gagnants.append(plateau_gagnant_courant.plateau_ligne_texte)
        return self._liste_plateaux_gagnants

    def __ajouter_choix(self, plateau: Plateau, choix):
        "Enregistre un choix et modifie le plateau selon ce choix"
        # Enregistrer le choix
        self._liste_des_choix_courants.append(choix[0:2])
        # Modifier le plateau
        plateau.deplacer_blocs(*choix)

    def __retirer_choix(self, plateau: Plateau, choix):
        "Annule le dernier choix et restaure le plateau precedent"
        # Desenregistrer le choix
        self._liste_des_choix_courants.pop()
        # Modifier le plateau
        plateau.annuler_le_deplacer_blocs(*choix)

    def __est_valide(self, plateau: Plateau, choix):
        "Verifie la validite du choix"
        c_depart, c_arrivee = choix
        # INVALIDE Si les colonnes de depart et d'arrivee sont identiques
        if c_depart == c_arrivee:
            return False
        # INVALIDE Si la colonne de depart est vide
        if plateau.la_colonne_est_vide(c_depart):
            return False
        # INVALIDE Si la colonne de depart est pleine et monocouleur
        if plateau.la_colonne_est_pleine_et_monocouleur(c_depart):
            return False
        # INVALIDE Si la colonne d'arrivee est pleine
        if plateau.la_colonne_est_pleine(c_arrivee):
            return False
        # INVALIDE Si la colonne d'arrivee n'est pas vide et n'a pas la meme couleur au sommet
        if not plateau.la_colonne_est_vide(c_arrivee) and \
            plateau.la_couleur_au_sommet_de_la_colonne(c_depart) != plateau.la_couleur_au_sommet_de_la_colonne(c_arrivee):
            return False
        # INVALIDE Si la colonne d'arrivee n'a pas assez de place
        if plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(c_depart) > plateau.nombre_de_case_vide_de_la_colonne(c_arrivee):
            return False
        return True

    def __solution_complete(self, plateau: Plateau):
        "Evalue si le plateau est termine (gagne ou bloque)"
        if plateau.plateau_ligne_texte in self.__ensemble_des_plateaux_gagnants():
            return True
        # TODO : Evaluer si le plateau est "bloque" => a observer, mais verification inutile jusque la.
        return False

    def __enregistrer_solution(self, plateau: Plateau):
        "Enregistre le parcours de la solution pour la restituer"
        # Enregistrer la liste des choix courant comme la solution
        self._liste_des_solutions.append(copy.deepcopy(self._liste_des_choix_courants))

        if 'solution la plus longue' not in self._statistiques \
            or len(self._liste_des_choix_courants) > self._statistiques['solution la plus longue']:
            self._statistiques['solution la plus longue'] = len(self._liste_des_choix_courants)
            
        if 'solution la plus courte' not in self._statistiques \
            or len(self._liste_des_choix_courants) < self._statistiques['solution la plus courte']:
            self._statistiques['solution la plus courte'] = len(self._liste_des_choix_courants)

        if 'nombre de solution' not in self._statistiques:
            self._statistiques['nombre de solution'] = 1
        else:
            self._statistiques['nombre de solution'] += 1

        self._export_json_solutions.exporter(self)

    def backtracking(self, plateau: Plateau = None):
        "Parcours de tous les choix afin de debusquer toutes les solutions"
        if plateau is None:
            if len(self._liste_des_solutions) != 0:
                # Le plateau est deja resolu et enregistre
                return
            plateau = self._plateau_initial
            self._liste_des_choix_courants = []
            self._profondeur_recursion = -1
        
        self._profondeur_recursion += 1
        # self._logger.info(self._profondeur_recursion)
        if self._profondeur_recursion > 50:
            raise RuntimeError("Appels recursifs infinis !")
        
        if self.__solution_complete(plateau):   # Condition d'arret
            self.__enregistrer_solution(plateau)
            self._profondeur_recursion -= 1
            return

        for choix in self.__ensemble_des_choix_possibles():
            if self.__est_valide(plateau, choix):  # Verifier si le choix est valide
                # Enrichir le choix du nombre de cases a deplacer (pour pouvoir retablir)
                nb_cases_deplacees = plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(choix[0])
                choix += tuple([nb_cases_deplacees])
                self.__ajouter_choix(plateau, choix)  # Prendre ce choix
                self.backtracking(plateau)  # Appeler recursivement la fonction
                self.__retirer_choix(plateau, choix)  # Annuler le choix (retour en arriere)
        
        if self._profondeur_recursion == 0:
            # fin de toutes les recherches
            self.exporter_fichier_json()
        self._profondeur_recursion -= 1

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les solutions et les statistiques du plateau"""
        self._export_json_solutions.forcer_export(self)

    def __importer_fichier_json(self):
        """Lit l'enregistrement JSON s'il existe"""
        data_json = self._export_json_analyses.importer()
        if 'nombre de solutions' in data_json:
            self._statistiques['nombre de solution'] = data_json['nombre de solutions']
        if 'solution la plus courte' in data_json:
            self._statistiques['solution la plus courte'] = data_json['solution la plus courte']
        if 'solution la plus longue' in data_json:
            self._statistiques['solution la plus longue'] = data_json['solution la plus longue']
        if 'solution moyenne' in data_json:
            self._statistiques['solution moyenne'] = data_json['solution moyenne']
        if 'difficulte' in data_json:
            self._difficulte = data_json['difficulte']
        if 'liste des solutions' in data_json:
            for solution in data_json['liste des solutions']:
                self._liste_des_solutions.append(solution)

    @property
    def nb_solutions(self):
        if 'nombre de solution' in self._statistiques:
            return self._statistiques['nombre de solution']
        return 0

    @property
    def solution_la_plus_courte(self):
        if 'solution la plus courte' in self._statistiques:
            return self._statistiques['solution la plus courte']
        return None

    @property
    def solution_la_plus_longue(self):
        if 'solution la plus longue' in self._statistiques:
            return self._statistiques['solution la plus longue']
        return None
    #TODO : Sur quelques plateaux, la solution la plus courte etait differente en longueru de la plus longue.
    #       C'etait sur un plateau 4x3 je crois. Voir s'il faut en tenir compte avec de grands ecarts.

    @property
    def solution_moyenne(self):
        # TODO : ResoudrePlateau().solution_moyenne => ABANDONNE, nettoyer le code de la 'moyenne' !
        if 'solution moyenne' in self._statistiques:
            return self._statistiques['solution moyenne']
        return None

    @property
    def difficulte(self):
        """Retourne la difficulte de la solution
La difficulte est le nombre de coups pour resoudre le plateau rapporte a la taille du plateau."""
        if self.solution_la_plus_courte is None:
            return None
        if not self._difficulte:
            surface_plateau_max = 12 * 12
            surface_plateau = self._plateau_initial.nb_colonnes * self._plateau_initial.nb_lignes
            inverse_ratio_surface = surface_plateau_max / surface_plateau
            self._difficulte = int( self.solution_la_plus_courte * inverse_ratio_surface )
        return self._difficulte

class ExportJSON:
    def __init__(self, delai, longueur, nom_plateau, nom_export, repertoire = REPERTOIRE_SORTIE_RACINE):
        self._delai_enregistrement = delai
        self._longueur_enregistrement = longueur
        self._chemin_enregistrement = Path(repertoire) / nom_plateau / (nom_export+'.json')

        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        self._longueur_dernier_enregistrement = 0

    def exporter(self, contenu):
        """Enregistre un fichier JSON selon des criteres de nombres et de temps.
Retourne True si l'export a ete realise"""
        if (len(contenu) - self._longueur_dernier_enregistrement >= self._longueur_enregistrement):
            return self.forcer_export(contenu)

        if (datetime.datetime.now().timestamp() - self._timestamp_dernier_enregistrement >= self._delai_enregistrement) \
            and (len(contenu) != self._longueur_dernier_enregistrement):
            return self.forcer_export(contenu)
        
        return False

    def forcer_export(self, contenu):
        """Enregistre un fichier JSON en ignorant les criteres.
Retourne True si l'export a ete realise"""
        # Enregistrement des donnees dans un fichier JSON
        if not self._chemin_enregistrement.parent.exists():
            self._chemin_enregistrement.parent.mkdir(parents=True, exist_ok=True)
        if type(contenu) == dict:
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                json.dump(contenu, fichier, ensure_ascii=False, indent=4)
        else:
            # Enregistrement d'une classe
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                json.dump(contenu.to_dict(), fichier, ensure_ascii=False, indent=4)
        self._longueur_dernier_enregistrement = len(contenu)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la derniere iteration realisee."""
        try:
            with open(self._chemin_enregistrement, "r", encoding='utf-8') as fichier:
                dico_json = json.load(fichier)
            return dico_json
        except FileNotFoundError:
            return {}

class ProfilerLeCode:
    def __init__(self, nom, actif = False):
        self.actif = actif
        self._nom = nom

    def start(self):
        if self.actif:
            # Profilage du code
            self._profil = cProfile.Profile()
            self._profil.enable()

    def stop(self):
        if self.actif:
            # Fin du profilage
            self._profil.disable()

            # Affichage des statistiques de profilage
            self._stats = pstats.Stats(self._profil).sort_stats('cumulative')
            self._stats.print_stats()

            # Exporter les statistiques dans un fichier texte
            with open(f'profiling_results_{self._nom}.txt', 'w') as fichier:
                self._stats = pstats.Stats(self._profil, stream=fichier)
                #stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)
                self._stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()

class CreerLesTaches:
    def __init__(self, nom, nb_colonnes, nb_lignes):
        self._nom = f'{nb_colonnes}.{nb_lignes}.{nom}'
        self._taches = [{'colonnes': c, 'lignes': l, 'complexite': c*l, 'terminee': False, 'en_cours': False} for c in range(2, nb_colonnes) for l in range(2, nb_lignes)]
        self._taches.sort(key=lambda x: x['complexite'])
        self._log = pathlib.Path('logs') / f'{nom}.log'
        self._old_log = pathlib.Path('logs') / f'{nom}_old.log'
        self._creer_le_journal()

    def _creer_le_journal(self, nouveau_fichier=False):
        # Creer l'arborescence du log
        if not self._log.parent.exists():
            pathlib.Path('logs').mkdir(parents=True, exist_ok=True)
        if nouveau_fichier:
            # Renommer le precedent log
            if self._log.exists():
                if self._old_log.exists():
                    self._old_log.unlink()
                self._log.rename(self._old_log)
        logging.basicConfig(filename=self._log, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def exporter(self):
        with open(f'{self._nom}.json', 'w', encoding='utf-8') as fichier:
            json.dump(self._taches, fichier, ensure_ascii=False, indent=4)

    def importer(self):
        if Path(f'{self._nom}.json').exists():
            with open(f'{self._nom}.json', 'r', encoding='utf-8') as fichier:
                self._taches = json.load(fichier)

    def __mettre_a_jour_tache(self, colonnes, lignes):
        logger = logging.getLogger(f"{colonnes}.{lignes}.CreerLesTaches")
        logger.info(f"Fin")
        tache_courante_traitee = False
        for tache in self._taches:
            if tache['colonnes'] == colonnes and tache['lignes'] == lignes:
                tache['terminee'] = True
                tache['en_cours'] = False
                tache_courante_traitee = True
                continue
            elif tache_courante_traitee and not tache['terminee'] and not tache['en_cours']:
                # Tache suivant celle qui vient de s'achever => indiquer son lancement
                tache_courante_traitee = False
                logger = logging.getLogger(f"{tache['colonnes']}.{tache['lignes']}.CreerLesTaches")
                logger.info(f"Lancement")
                tache['en_cours'] = True
                break
        self.exporter()

    def executer_taches(self, fonction, nb_processus=None):
        if nb_processus:
            cpt_processus = nb_processus
        else:
            cpt_processus = cpu_count()

        with Pool(processes=nb_processus) as pool:
            for tache in self._taches:
                if not tache['terminee'] and not tache['en_cours']:
                    pool.apply_async(fonction, (tache['colonnes'], tache['lignes']), callback=lambda _, c=tache['colonnes'], l=tache['lignes']: self.__mettre_a_jour_tache(c, l))
                    if cpt_processus and cpt_processus > 0:
                        logger = logging.getLogger(f"{tache['colonnes']}.{tache['lignes']}.CreerLesTaches")
                        logger.info(f"Lancement")
                        cpt_processus -= 1
                        tache['en_cours'] = True
                        self.exporter()
            pool.close()
            pool.join()

    @property
    def taches(self):
        return self._taches
