"Module pour creer, resoudre et qualifier les solutions des plateaux de 'ColorWoordSort'"
from itertools import permutations
import copy

from plateau import Plateau
from export_json import ExportJSON

class ResoudrePlateau:
    "Classe de resolution d'un plateau par parcours de toutes les possibilites de choix"
    def __init__(self, plateau_initial: Plateau, repertoire_analyse, repertoire_solution):
        self._plateau_initial = copy.deepcopy(plateau_initial)
        # Statistiques des solutions:
        #    {
        #        "plateau": "AAAB.BB  .AB  ",
        #        # key = longueur de la solution
        #        # value = nombre de solutions de cette longueur
        #        "dico des longueurs": {3: 12, 4: 24},
        #        # Produit des choix à chaque étape de la solution la plus courte / rapporté à la taille du plateau
        #        # coup 1 = 3 choix, coup 2 = 2 choix et coup 3 = 1 choix
        #        # difficulté = 3x2x1 * (12x12) / (3 x 4)
        #        "difficulte": 72,
        #        "solution": []
        #    }
        # Les longueurs sont toutes egales (courtes et longues).
        # La difficulté dépend de :
        #   - Le nombre de choix
        #   - La taille du plateau.
        self._dico_des_longueurs = {}
        self._difficulte = None
        self._solution = None

        self._liste_des_choix_possibles = None
        self._liste_plateaux_gagnants = None

        nom_plateau = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}"
        nom_solution = f"Plateaux_{self._plateau_initial.nb_colonnes}x{self._plateau_initial._nb_lignes}_Resolution_{plateau_initial.plateau_ligne_texte.replace(' ', '-')}"
        self._export_json_analyses = ExportJSON(delai=60, longueur=100,
                                                nom_plateau=nom_plateau,
                                                nom_export=nom_solution,
                                                repertoire = repertoire_analyse)
        self._export_json_solutions = ExportJSON(delai=60, longueur=100,
                                                 nom_plateau=nom_plateau,
                                                 nom_export=nom_solution,
                                                 repertoire = repertoire_solution)
        self.__importer_fichier_json()

    def __len__(self):
        "La longueur de la solution definit la difficulte"
        # Le nombre de solution n'a pas d'incidence sur la difficulte
        return len(self._solution) if self._solution else 0

    def to_dict(self):
        dict_resoudre_plateau = {
            'plateau': self._plateau_initial.plateau_ligne_texte_universel,
            'dico des longueurs': self._dico_des_longueurs,
            'difficulte': self._difficulte if self._difficulte else 0,
            'solution': self._solution
        }
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

    def __ajouter_choix(self, plateau: Plateau, liste_des_choix_courants, choix):
        "Enregistre un choix et modifie le plateau selon ce choix"
        # Enregistrer le choix
        liste_des_choix_courants.append(choix[0:2])
        # Modifier le plateau
        plateau.deplacer_blocs(*choix)

    def __retirer_choix(self, plateau: Plateau, liste_des_choix_courants, choix):
        "Annule le dernier choix et restaure le plateau precedent"
        # Desenregistrer le choix
        liste_des_choix_courants.pop()
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

    def __enregistrer_solution(self, liste_des_choix_courants):
        "Enregistre le parcours de la solution pour la restituer"
        len_solution_courante = len(liste_des_choix_courants)
        # Si elle est plus courte, enregistrer la liste des choix courant comme la solution
        if self._solution is None or len_solution_courante < len(self._solution):
            self._solution = copy.deepcopy(liste_des_choix_courants)
            self._difficulte = None  # Reinitialiser la difficulte pour forcer son recalcul
            self.difficulte  # Calculer la difficulté de la solution

        # Mettre a jour les statistiques
        if len_solution_courante in self._dico_des_longueurs:
            self._dico_des_longueurs[len_solution_courante] += 1
        else:
            self._dico_des_longueurs[len_solution_courante] = 1

        self._export_json_solutions.exporter(self)

    def backtracking(self, plateau: Plateau = None, liste_des_choix_courants = None, profondeur_recursion = None):
        "Parcours de tous les choix afin de debusquer toutes les solutions"
        if plateau is None:
            if self._solution is not None:
                # Le plateau est deja resolu et enregistre
                return
            plateau = copy.deepcopy(self._plateau_initial)
            liste_des_choix_courants = []
            profondeur_recursion = -1
        
        profondeur_recursion += 1
        # self._logger.info(profondeur_recursionn)
        if profondeur_recursion > 50:
            raise RuntimeError("Appels recursifs infinis !")
        
        if self.__solution_complete(plateau):   # Condition d'arret
            self.__enregistrer_solution(liste_des_choix_courants)
            profondeur_recursion -= 1
            return

        for choix in self.__ensemble_des_choix_possibles():
            if self.__est_valide(plateau, choix):  # Verifier si le choix est valide
                # Enrichir le choix du nombre de cases a deplacer (pour pouvoir retablir)
                nb_cases_deplacees = plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(choix[0])
                choix += tuple([nb_cases_deplacees])
                self.__ajouter_choix(plateau, liste_des_choix_courants, choix)  # Prendre ce choix
                self.backtracking(plateau, liste_des_choix_courants, profondeur_recursion)  # Appeler recursivement la fonction
                self.__retirer_choix(plateau, liste_des_choix_courants, choix)  # Annuler le choix (retour en arriere)
        
        if profondeur_recursion == 0:
            # fin de toutes les recherches
            self.exporter_fichier_json()
        profondeur_recursion -= 1

    def exporter_fichier_json(self):
        """Enregistre un fichier JSON avec les solutions et les statistiques du plateau"""
        self._export_json_solutions.forcer_export(self)

    def __importer_fichier_json(self):
        """Lit l'enregistrement JSON s'il existe"""
        data_json = self._export_json_analyses.importer()
        if 'dico des longueurs' in data_json:
            self._dico_des_longueurs = data_json.get('dico des longueurs')
        if 'difficulte' in data_json:
            self._difficulte = data_json.get('difficulte')
        if 'solution' in data_json:
            self._solution = data_json['solution']

    @property
    def difficulte(self):
        """Retourne la difficulte de la solution
        La difficulté dépend de :
        - Le nombre de choix
        - La taille du plateau"""
        if self._solution is None:
            return None
        if not self._difficulte:
            surface_plateau_max = 12 * 12
            surface_plateau = self._plateau_initial.nb_colonnes * self._plateau_initial.nb_lignes
            inverse_ratio_surface = surface_plateau_max / surface_plateau

            # Parcourir la solution et quantifier le nombre de choix
            nb_choix_total = 1
            plateau = copy.deepcopy(self._plateau_initial)
            liste_des_choix_courants = []
            for coup in self._solution:
                nb_choix_courant = 0
                for choix_possible in self.__ensemble_des_choix_possibles():
                    if self.__est_valide(plateau, choix_possible):
                        nb_choix_courant += 1
                # Multiplier les niveaux de choix
                nb_choix_total *= nb_choix_courant
                # Appliquer le coup pour avancer dans la solution
                nb_cases_deplacees = plateau.nombre_de_cases_monocouleur_au_sommet_de_la_colonne(coup[0])
                coup += tuple([nb_cases_deplacees])
                self.__ajouter_choix(plateau, liste_des_choix_courants, coup)  # Jouer ce coup

            self._difficulte = int( nb_choix_total * inverse_ratio_surface )
            # print(f"Calcul de la difficulté : {nb_choix_total} x {inverse_ratio_surface} = {self._difficulte} pour le plateau '{self._plateau_initial.plateau_ligne_texte_universel.replace(' ','-')}' avec une solution de longueur {len(self._solution)} (surface {surface_plateau})")
        return self._difficulte
