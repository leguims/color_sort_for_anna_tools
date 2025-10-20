"""Module pour traiter la chaine complete Etape 2 à 5 avec un ensemble de plateaux différents

Créer une copie des plateaux
Appliquer un filtrage de similarité severe (1% par exemple)
Appliquer les étapt 2 à 5

Recommencer tout en augmentant legerement la similarité.

L'objectif est de traiter de bout en bout des plateaux qui ne se ressemblent pas.
Biensur, la démarche Etape 1 à 5 est à conserver, mais elle est très longue."""
import logging
import pathlib
import datetime
from rapidfuzz import fuzz

from plateau import Plateau
from lot_de_plateaux import LotDePlateaux
from profiler_le_code import ProfilerLeCode
from creer_les_taches import CreerLesTaches

from outil_etape_2_revalider_les_plateaux import RevaliderLesPlateaux
from outil_etape_3_chercheur_de_solutions import ChercherDesSolutions
from outil_etape_4_classer_les_solutions import ClasserLesSolutions
from outil_etape_5_classer_les_solutions_tronquer import TronquerLesSolutions

class FluxProgressif:
    "Module pour traiter la chaine complete Etape 2 à 5 avec un ensemble de plateaux différents'"
    def __init__(self,
                 nb_colonnes,
                 nb_lignes,
                 nb_colonnes_vides,
                 repertoire_analyse_base,
                 repertoire_analyse,
                 repertoire_solution,
                 nom_tache,
                 fichier_journal):
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse_base = repertoire_analyse_base
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_solution = repertoire_solution
        self._spec_plateau = (self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal

    def copie_plateaux_base(self, seuil_similarite_max):
        """Créer une copie des plateaux de base vers le repertoire d'analyse courant"""
        spec_plateau = (self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        lot_de_plateaux_base = LotDePlateaux(spec_plateau,
                                            repertoire_export_json=self._repertoire_analyse_base)
        iter_plateau = Plateau(self._nb_colonnes, self._nb_lignes, self._nb_colonnes_vides)
        # Parcourir les plteaux de base
        for plateau_ligne_texte in lot_de_plateaux_base.plateaux_valides:
            iter_plateau.clear()
            iter_plateau.plateau_ligne_texte = plateau_ligne_texte
            # Vérifier que le plateaux de base à ajouter n'est pas similaire à un plateau déjà existant.
            if self.verifier_similarite(iter_plateau, seuil_similarite_max):
                self._lot_de_plateaux.est_ignore(plateau_ligne_texte)
        self._lot_de_plateaux.exporter_fichier_json()

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

    def revalider_les_plateaux(self):
        revalider = RevaliderLesPlateaux(
            nb_colonnes=[self._nb_colonnes],
            nb_lignes=[self._nb_lignes],
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=self._repertoire_analyse,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        revalider.revalider_les_plateaux(self._nb_colonnes, self._nb_lignes)
        # Mettre à jour le lot de plateaux
        self._lot_de_plateaux = LotDePlateaux(self._spec_plateau,
                                                repertoire_export_json=self._repertoire_analyse)

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

    flux_progressif = FluxProgressif(
        nb_colonnes=3,
        nb_lignes=4,
        nb_colonnes_vides=1,
        repertoire_analyse_base='Analyse_nouvelle_architecture',
        repertoire_analyse='Analyse_flux_progressif',
        repertoire_solution='Solutions_flux_progressif',
        nom_tache='flux_progressif_complet',
        fichier_journal=pathlib.Path('logs') / f'{NOM_TACHE}.log'
    )
    # Seuil faible = moins de plateaux ; seuil élevé = plus de plateaux (similaires entre eux)
    flux_progressif.copie_plateaux_base(seuil_similarite_max=10)
    print(f"Nb plateaux dans le flux progressif : {len(flux_progressif)}")
    flux_progressif.revalider_les_plateaux()
    print(f"Nb plateaux dans le flux progressif : {len(flux_progressif)}")
