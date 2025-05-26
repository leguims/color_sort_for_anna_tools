"Module pour creer, resoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
import logging

# TODO : reprendre l'enregistrement a partir du fichier. => Pas d'amelioration, essayer de comprendre.

class Plateau:
    "Classe qui implemente un plateau. Son contenu et ses differentes representations."
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides=1):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._est_valide = None
        self._est_interessant = None
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
        self._logger = logging.getLogger(f"{self._nb_colonnes}.{self._nb_lignes}.{Plateau.__name__}")

    def clear(self):
        "Efface le plateau pour en ecrire un nouveau"
        self._est_valide = None
        self._est_interessant = None
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

    def creer_plateau_permutation_initial(self):
        """"Cree un plateau en ligne initial pour la permutation.
        Ce plateau est le premier plateau valide produit à partir
        du plateau retourné par le methode 'creer_plateau_initial'.
        exemple 4x4 = ['A', 'A', 'A', 'B', 'A', 'B', 'B', 'B', 'C', 'C', 'C', ' ', 'C', ' ', ' ', ' ']
        ... ='AAAB.ABBB.CCC .C   '"""
        # 2x7 : ['A'x(L-1)] .A[' 'x(L-1)]]
        # 3x7 : ['A'x(L-1)]B.A['B'x(L-1)].[' 'x(L)]]
        # 4x7 : ['A'x(L-1)]B.A['B'x(L-1)].['C'x(L-1)] .C[' 'x(L-1)]]
        # 5x7 : ['A'x(L-1)]B.A['B'x(L-1)].['C'x(L-1)]D.C['D'x(L-1)].[' 'x(L)]]
        # 6x7 : ['A'x(L-1)]B.A['B'x(L-1)].['C'x(L-1)]D.C['D'x(L-1)].['E'x(L-1)] .E[' 'x(L-1)]
        if not self._plateau_ligne:
            plateau = []
            famille_et_vide = self._liste_familles + [' ']
            for colonne in range(1, self._nb_colonnes+1):
                if colonne >= 2:
                    famille_precedente = famille_et_vide[colonne-2]
                famille = famille_et_vide[colonne-1]
                if colonne < self._nb_colonnes:
                    famille_suivante = famille_et_vide[colonne]

                if (colonne == self._nb_colonnes):
                    # Derniere colonne (famille = ' ')
                    if self._nb_colonnes%2 == 0: # paire
                        plateau += [famille_precedente] + [famille]*(self._nb_lignes-1)
                    else: # impaire
                        plateau += [famille]*self._nb_lignes
                else :
                    if colonne%2 == 1: # impaire
                        plateau += [famille]*(self._nb_lignes-1) + [famille_suivante]
                    else: # paire
                        plateau += [famille_precedente] + [famille]*(self._nb_lignes-1)
            self.plateau_ligne = tuple(plateau)
            self._logger.info(f"Plateau de permutation initial = '{self.plateau_ligne_texte_universel}'")


    @property
    def est_valide(self):
        """"Verifie si le plateau en parametre est valide"""
        if self._plateau_ligne and self._est_valide is None:
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

    @property
    def est_interessant(self):
        """"Verifie si le plateau en parametre est interessant"""
        if self._plateau_ligne and self._est_interessant is None:
            self._est_interessant = True
            # Est-ce que le plateau est interessant ?
            # Une colonne achevee est sans interet.
            if self.une_colonne_est_pleine_et_monocouleur():
                self._est_interessant = False
        return self._est_interessant

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
