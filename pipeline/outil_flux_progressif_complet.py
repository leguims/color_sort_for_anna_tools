"""Module pour traiter la chaine complete Etape 2 à 5 avec un ensemble de plateaux différents

Créer une copie des plateaux
Appliquer un filtrage de similarité severe (1% par exemple)
Appliquer les étapes 2 à 5

Recommencer tout en augmentant legerement la similarité.

L'objectif est de traiter de bout en bout des plateaux qui ne se ressemblent pas.
Biensur, la démarche Etape 1 à 5 est à conserver, mais elle est très longue."""
import logging
import pathlib
from rapidfuzz import fuzz

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from core.plateau import Plateau
from core.lot_de_plateaux import LotDePlateaux
from io_utils.profiler_le_code import ProfilerLeCode
from io_utils.creer_les_taches import CreerLesTaches

from pipeline.outil_etape_2_filtrer_plateaux_invalides_ou_initeressants import FiltrerLesPlateaux as FiltrerLesPlateauxInvalidesOuIniteressants
from pipeline.outil_etape_3_filtrer_doublons_permutation_jetons import FiltrerLesPlateaux as FiltrerLesPlateauxPermutationJetons
from pipeline.outil_etape_4_filtrer_doublons_permutation_piles import FiltrerLesPlateaux as FiltrerLesPlateauxPermutationPiles
from pipeline.outil_etape_5_filtrer_doublons_permutation_jetons_piles import FiltrerLesPlateaux as FiltrerLesPlateauxPermutationJetonsPiles
from pipeline.outil_etape_6_chercher_des_solutions import ChercherDesSolutions
from pipeline.outil_etape_7_filtrer_les_solutions_pour_godot import FiltrerLesSolutions
from pipeline.outil_etape_8_classer_les_solutions_tronquer import TronquerLesSolutions
from pipeline.outil_etape_9_exporter_pour_godot import ExporterLesSolutionsPourGodot

# TODO : Appliquer le filtre par similarité basse sur l'ensemble des plateaux avec solutions (Après étape 3)
# TODO : Prévoir une étape pour le faire en essayant d'atteindre un nombre de plateau X par difficulté (Après étape 3)

class FluxProgressif:
    "Module pour traiter la chaine complete Etape 2 à 5 avec un ensemble de plateaux différents'"
    def __init__(self,
                 nb_colonnes,
                 nb_lignes,
                 nb_colonnes_vides,
                 repertoire_analyse_base,
                 repertoire_analyse,
                 repertoire_solution,
                 fichier_solution,
                 nom_tache,
                 fichier_journal):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse_base = repertoire_analyse_base
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_solution = repertoire_solution
        self._fichier_solution = fichier_solution
        self._spec_plateau = (self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal

    def copie_plateaux_base(self, seuil_similarite_max):
        """Créer une copie des plateaux de base vers le repertoire d'analyse courant"""
        logger = logging.getLogger(f"{self._nb_colonnes}.{self._nb_lignes}.{self._nom_tache}")
        logger.info("DEBUT copie_plateaux_base")
        logger.info("Lecture des plateaux de references")
        spec_plateau = (self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        lot_de_plateaux_base = LotDePlateaux(spec_plateau,
                                            repertoire_export_json=self._repertoire_analyse_base)
        iter_plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        # Parcourir les plateaux de base
        logger.info("Copie des plateaux selon similarite")
        for plateau_ligne_texte in lot_de_plateaux_base.plateaux_valides:
            iter_plateau.clear()
            iter_plateau.plateau_ligne_texte = plateau_ligne_texte
            # Vérifier que le plateaux de base à ajouter n'est pas similaire à un plateau déjà existant.
            if self.verifier_similarite(iter_plateau, seuil_similarite_max):
                self._lot_de_plateaux.plateau_est_ignore(plateau_ligne_texte)
        # Indiquer la fin de recherche de plateaux (necessaire pour chercher des solutions)
        self._lot_de_plateaux.arret_des_enregistrements()
        self._lot_de_plateaux.exporter_fichier_json()
        logger.info("Copie des plateaux terminee")

    def verifier_similarite(self, plateau_ref : Plateau, seuil_similarite_max):
        """Retourner l'intervale de similarite avec les plateaux existants"""
        plateau_ref_ligne_texte_universel = plateau_ref.plateau_ligne_texte_universel.replace(' ', '_').replace('.', ' ')
        iter_plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        for iter_plateau_valide_ligne_texte in self._lot_de_plateaux.plateaux_valides:
            iter_plateau.clear()
            iter_plateau.plateau_ligne_texte = iter_plateau_valide_ligne_texte
            similarite = fuzz.token_sort_ratio(iter_plateau.plateau_ligne_texte_universel.replace(' ', '_').replace('.', ' '),
                                                plateau_ref_ligne_texte_universel)
            if similarite >= seuil_similarite_max:
                return False
        return True

    def filtrer_les_plateaux_invalides_ou_initeressants(self):
        filtrer = FiltrerLesPlateauxInvalidesOuIniteressants(
            nb_colonnes=[self._nb_colonnes],
            nb_lignes=[self._nb_lignes],
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.filtrer_les_plateaux(self._nb_colonnes, self._nb_lignes)
        # Mettre à jour le lot de plateaux
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)

    def filtrer_les_plateaux_permutation_jetons(self):
        filtrer = FiltrerLesPlateauxPermutationJetons(
            nb_colonnes=[self._nb_colonnes],
            nb_lignes=[self._nb_lignes],
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.filtrer_les_plateaux(self._nb_colonnes, self._nb_lignes)
        # Mettre à jour le lot de plateaux
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)

    def filtrer_les_plateaux_permutation_piles(self):
        filtrer = FiltrerLesPlateauxPermutationPiles(
            nb_colonnes=[self._nb_colonnes],
            nb_lignes=[self._nb_lignes],
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.filtrer_les_plateaux(self._nb_colonnes, self._nb_lignes)
        # Mettre à jour le lot de plateaux
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)

    def filtrer_les_plateaux_permutation_jetons_piles(self):
        filtrer = FiltrerLesPlateauxPermutationJetonsPiles(
            nb_colonnes=[self._nb_colonnes],
            nb_lignes=[self._nb_lignes],
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.filtrer_les_plateaux(self._nb_colonnes, self._nb_lignes)
        # Mettre à jour le lot de plateaux
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)

    def chercher_des_solutions(self):
        chercheur = ChercherDesSolutions(
            nb_colonnes=[self._nb_colonnes],
            nb_lignes=[self._nb_lignes],
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            repertoire_solution=self._repertoire_solution,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        chercheur.chercher_des_solutions(self._nb_colonnes, self._nb_lignes)

    def classer_les_solutions(self, nb_coups_min=3):
        classeur = FiltrerLesSolutions(
            nb_colonnes=self._nb_colonnes,
            nb_lignes=self._nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            repertoire_solution=self._repertoire_solution,
            fichier_solution=self._fichier_solution,
            nb_coups_min=nb_coups_min,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        classeur.classer_les_solutions(self._nb_colonnes, self._nb_lignes)

    def tronquer_les_solutions(self, taille_tronquee, decallage=0):
        tronqueur = TronquerLesSolutions(
            repertoire_solution=self._repertoire_solution,
            fichier_solution=self._fichier_solution,
            taille_tronquee=taille_tronquee,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        tronqueur.tronquer_les_solutions(taille_tronquee, decallage)
        tronqueur.afficher_synthese(decallage)

    def exporter_pour_godot(self):
        # TODO
        pass

    def __len__(self):
        return len(self._lot_de_plateaux)

if __name__ == "__main__":
    NOM_TACHE = 'flux_progressif_complet'
    FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

    PROFILER_LE_CODE = False

    # Iteration avec un seuil de similarité de 1%
    #   Copier les plateaux (avec le filtrage de similarité)
    #   Pour chaque taille de plateau (colonnes x lignes):
    #     Appliquer les étape 2
    #     Appliquer les étape 3
    #     Appliquer les étape 4
    #     Appliquer les étape 5
    #     Sauvegarder les solutions
    #     Sauvegarder le fichier de difficultés avec le nombre de plateaux totaux
    #   Changer de seuil de similarité (2%, 5%, 10% ...)
    for similarite in [90]: # range(50, 90, 5):
        for colonne in [3]: # range(3, 12):
            for ligne in [4]: # range(3, 12):
                flux_progressif = FluxProgressif(
                    nb_colonnes=colonne,
                    nb_lignes=ligne,
                    nb_colonnes_vides=1,
                    repertoire_analyse_base='Analyses',
                    repertoire_analyse='Analyse_flux_progressif_'+str(similarite),
                    repertoire_solution='Solutions_flux_progressif_NEW_RESOLUTION',
                    fichier_solution='Solutions_classees_'+str(similarite),
                    nom_tache='flux_progressif_complet',
                    fichier_journal=pathlib.Path('logs') / f'{NOM_TACHE}.log'
                )
                # Seuil faible = moins de plateaux ; seuil élevé = plus de plateaux (similaires entre eux)
                flux_progressif.copie_plateaux_base(seuil_similarite_max=similarite)
                entete = f"{colonne}x{ligne} SIM-{similarite} : "
                print(f"{entete}Nb plateaux dans le flux progressif : {len(flux_progressif)}")
                if len(flux_progressif):
                    if len(flux_progressif) > 1:
                        flux_progressif.filtrer_les_plateaux_invalides_ou_initeressants()
                        print(f"{' ' * len(entete)}Nb plateaux restants (invalides ou initeressants) : {len(flux_progressif)}")
                        flux_progressif.filtrer_les_plateaux_permutation_jetons()
                        print(f"{' ' * len(entete)}Nb plateaux restants (permutations jetons) : {len(flux_progressif)}")
                        flux_progressif.filtrer_les_plateaux_permutation_piles()
                        print(f"{' ' * len(entete)}Nb plateaux restants (permutations piles) : {len(flux_progressif)}")
                        flux_progressif.filtrer_les_plateaux_permutation_jetons_piles()
                        print(f"{' ' * len(entete)}Nb plateaux restants (permutations jetons et piles) : {len(flux_progressif)}")
                    flux_progressif.chercher_des_solutions()
                    flux_progressif.classer_les_solutions(nb_coups_min=3)
    flux_progressif.tronquer_les_solutions(taille_tronquee=10, decallage=0)
    flux_progressif.exporter_pour_godot() # TODO
