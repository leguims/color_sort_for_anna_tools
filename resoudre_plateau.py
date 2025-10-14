"Module pour creer, resoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations
import copy

from plateau import Plateau
from export_json import ExportJSON

class ResoudrePlateau:
    "Classe de resultion d'un plateau par parcours de toutes les possibilites de choix"
    def __init__(self, plateau_initial: Plateau, repertoire_analyse, repertoire_solution):
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
        self._export_json_analyses = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom, repertoire = repertoire_analyse)
        self._export_json_solutions = ExportJSON(delai=60, longueur=100, nom_plateau=nom_plateau, nom_export=nom, repertoire = repertoire_solution)
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
