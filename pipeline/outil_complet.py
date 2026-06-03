"Module pour créer, résoudre et qualifier les solutions des plateaux de 'ColorWoodSort'"
import logging
from pathlib import Path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # pour importer depuis le dossier parent

from pipeline.outil_etape_1_chercher_des_plateaux import ChercherDesPlateaux
from pipeline.outil_etape_2_filtrer_plateaux_invalides_ou_ininteressants import FiltrerLesPlateaux as FiltrerLesPlateauxInvalidesOuIniteressants
from pipeline.outil_etape_3_filtrer_doublons_permutation_jetons import FiltrerLesPlateaux as FiltrerLesPlateauxPermutationJetons
from pipeline.outil_etape_4_filtrer_doublons_permutation_piles import FiltrerLesPlateaux as FiltrerLesPlateauxPermutationPiles
from pipeline.outil_etape_5_filtrer_doublons_permutation_jetons_piles import FiltrerLesPlateaux as FiltrerLesPlateauxPermutationJetonsPiles
from pipeline.outil_etape_6_chercher_des_solutions import ChercherDesSolutions
from pipeline.outil_etape_7_filtrer_les_solutions_pour_godot import FiltrerLesSolutions
from pipeline.outil_etape_8_exporter_pour_godot import ExporterLesSolutionsPourGodot
from pipeline.outil_etape_9_tronquer_les_solutions_godot import TronquerLesSolutionsGodot

class OutilComplet:
    "Module pour traiter la chaine complete Etape 1 à 9 avec un ensemble de plateaux différents'"
    def __init__(self,
                 liste_nb_colonnes: list[int],
                 liste_nb_lignes: list[int],
                 nb_colonnes_vides: int,
                 repertoire_pipeline: Path,
                 nom_tache: str,
                 fichier_journal: Path):
        self._liste_nb_colonnes = liste_nb_colonnes
        self._liste_nb_lignes = liste_nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_pipeline = repertoire_pipeline
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        if not self._fichier_journal.parent.exists():
            self._fichier_journal.parent.mkdir(parents=True, exist_ok=True)
        self._elapsed_time = 0.

    def __str__(self) -> str:
        return f"Duree du traitement complet : {self._elapsed_time:.4f} secondes".replace('.', ',')

    @property
    def elapsed(self):
        return self._elapsed_time

    def chercher_des_plateaux(self):
        chercher = ChercherDesPlateaux(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_1_chercher_des_plateaux'),
            repertoire_filtre=str(self._repertoire_pipeline/'pipeline_5_filtre_doublons_permutation_jetons_piles'),
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        chercher.chercher_en_sequence()
        self._elapsed_time += chercher.elapsed

    def filtrer_les_plateaux_invalides_ou_initeressants(self):
        filtrer = FiltrerLesPlateauxInvalidesOuIniteressants(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_1_chercher_des_plateaux'),
            repertoire_filtre=str(self._repertoire_pipeline/'pipeline_2_filtrer_plateaux_invalides_ou_ininteressants'),
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.chercher_en_sequence()
        self._elapsed_time += filtrer.elapsed

    def filtrer_les_plateaux_permutation_jetons(self):
        filtrer = FiltrerLesPlateauxPermutationJetons(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_2_filtrer_plateaux_invalides_ou_ininteressants'),
            repertoire_filtre=str(self._repertoire_pipeline/'pipeline_3_filtre_doublons_permutation_jetons'),
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.chercher_en_sequence()
        self._elapsed_time += filtrer.elapsed

    def filtrer_les_plateaux_permutation_piles(self):
        filtrer = FiltrerLesPlateauxPermutationPiles(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_3_filtre_doublons_permutation_jetons'),
            repertoire_filtre=str(self._repertoire_pipeline/'pipeline_4_filtre_doublons_permutation_piles'),
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.chercher_en_sequence()
        self._elapsed_time += filtrer.elapsed

    def filtrer_les_plateaux_permutation_jetons_piles(self):
        filtrer = FiltrerLesPlateauxPermutationJetonsPiles(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_4_filtre_doublons_permutation_piles'),
            repertoire_filtre=str(self._repertoire_pipeline/'pipeline_5_filtre_doublons_permutation_jetons_piles'),
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        filtrer.chercher_en_sequence()
        self._elapsed_time += filtrer.elapsed

    def chercher_des_solutions(self):
        chercheur = ChercherDesSolutions(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_5_filtre_doublons_permutation_jetons_piles'),
            repertoire_difficulte=str(self._repertoire_pipeline/'pipeline_6_plateaux_avec_difficulte'),
            repertoire_solution=str(self._repertoire_pipeline/'pipeline_6_solutions'),
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        chercheur.chercher_en_sequence()
        self._elapsed_time += chercheur.elapsed

    def classer_les_solutions(self, nb_coups_min=3):
        classeur = FiltrerLesSolutions(
            nb_colonnes=self._liste_nb_colonnes,
            nb_lignes=self._liste_nb_lignes,
            nb_colonnes_vides=self._nb_colonnes_vides,
            repertoire_analyse=str(self._repertoire_pipeline/'pipeline_6_plateaux_avec_difficulte'),
            repertoire_solution=str(self._repertoire_pipeline/'pipeline_6_solutions'),
            fichier_solution='7_filtrer_les_solutions_pour_godot',
            nb_coups_min=nb_coups_min,
            nom_tache=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        classeur.chercher_en_sequence()
        self._elapsed_time += classeur.elapsed

    def exporter_pour_godot(self):
        export = ExporterLesSolutionsPourGodot(
            repertoire_solution=str(self._repertoire_pipeline/'pipeline_6_solutions'),
            fichier_solution='7_filtrer_les_solutions_pour_godot',
            fichier_godot='8_exporter_pour_godot_Solutions_classees',
            nom_etape=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        export.exporter_vers_godot()
        self._elapsed_time += export.elapsed

    def tronquer_les_solutions(self, taille_tronquee, decallage=0):
        tronqueur = TronquerLesSolutionsGodot(
            repertoire_solution=str(self._repertoire_pipeline/'pipeline_6_solutions'),
            fichier_godot='8_exporter_pour_godot_Solutions_classees',
            fichier_godot_tronque='9_tronquer_les_solutions_godot',
            nombre_de_plateaux=200,
            nom_etape=self._nom_tache,
            fichier_journal=self._fichier_journal
        )
        tronqueur.tronquer()
        self._elapsed_time += tronqueur.elapsed

    def chercher_en_sequence(self):
        self.chercher_des_plateaux()
        self.filtrer_les_plateaux_invalides_ou_initeressants()
        self.filtrer_les_plateaux_permutation_jetons()
        self.filtrer_les_plateaux_permutation_piles()
        self.filtrer_les_plateaux_permutation_jetons_piles()
        self.chercher_des_solutions()

    def export_godot(self):
        # La synthese des solutions s'applique à tous les plateaux disponibles.
        self._liste_nb_colonnes = range(2, 12)
        self._liste_nb_lignes = range(2, 14)
        self.classer_les_solutions()
        self.exporter_pour_godot()
        self.tronquer_les_solutions(taille_tronquee=200, decallage=0)
        logging.basicConfig(filename=self._fichier_journal, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(self._nom_tache)
        logger.info(self)

if __name__ == "__main__":
    NOM_TACHE = 'outil_complet'
    FICHIER_JOURNAL = Path('..') / '..' / 'logs' / f'{NOM_TACHE}.log'
    REPERTOIRE_PIPELINE = Path('..') / '..' / 'Pipelines'

    PROFILER_LE_CODE = False

    # Pour avoir une sequence complete sur un type de plateau
    for colonne in range(2,4):
        for ligne in range(3,6):
            outil_complet = OutilComplet(
                liste_nb_colonnes=[colonne],
                liste_nb_lignes=[ligne],
                nb_colonnes_vides=1,
                repertoire_pipeline=REPERTOIRE_PIPELINE,
                nom_tache=NOM_TACHE,
                fichier_journal=FICHIER_JOURNAL
            )
            outil_complet.chercher_en_sequence()

    # La synthese des solutions s'applique à tous les plateaux disponibles.
    outil_complet = OutilComplet(
        liste_nb_colonnes=[2],
        liste_nb_lignes=[2],
        nb_colonnes_vides=1,
        repertoire_pipeline=REPERTOIRE_PIPELINE,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    outil_complet.export_godot()
