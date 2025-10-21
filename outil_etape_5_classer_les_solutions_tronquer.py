"""Decoupe l'ensemble des solutions inter-plateaux en des ensembles plus petits de solutions
Adapte pour avoir un fichier de solutions restreint pour le jeu"""
import datetime
import time
import logging
import pathlib

from export_json import ExportJSON
from profiler_le_code import ProfilerLeCode

# TODO : Classer par difficulté dans le fichier de solutions

class TronquerLesSolutions:
    """Decoupe l'ensemble des solutions inter-plateaux en des ensembles plus petits de solutions
    Adapte pour avoir un fichier de solutions restreint pour le jeu"""
    def __init__(self,
                repertoire_solution,
                taille_tronquee,
                nom_tache,
                fichier_journal,
                profiler_le_code = False,
                periode_scrutation_secondes = 30*60): # en secondes
        self._repertoire_solution = repertoire_solution
        self._taille_tronquee = taille_tronquee
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes

    def tronquer_les_solutions(self, taille, decallage = 0):
        # Configurer le logger
        logger = logging.getLogger(f"tronquer.{self._nom_tache}")
        logger.info(f"\n\r*** Tronquer le classement des Solutions :")

        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()
        solutions_classees_tronquees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=f'Solutions_classees_T{taille}_D{decallage}', repertoire=self._repertoire_solution)

        if "liste difficulte des plateaux" in solutions_classees:
            dict_difficulte = solutions_classees["liste difficulte des plateaux"]
            dict_difficulte_tronque = {}
            # Gommer la notion de 'nb_coups' pour le jeu
            for difficulte, dico_nb_coups in dict_difficulte.items():
                for nb_coups, liste_plateaux in dico_nb_coups.items():
                    if difficulte not in dict_difficulte_tronque:
                        dict_difficulte_tronque[difficulte] = []
                    dict_difficulte_tronque[difficulte] += liste_plateaux[decallage: decallage + taille]
            # Tronquer les solutions
            for difficulte, liste_plateaux in dict_difficulte_tronque.items():
                liste_plateaux = liste_plateaux[0:taille]
            solutions_classees["liste difficulte des plateaux"] = dict_difficulte_tronque
            solutions_classees_tronquees_json.forcer_export(solutions_classees)

    def afficher_synthese(self, decallage = 0):
        # Configurer le logger
        logger = logging.getLogger("tronquer.afficher_synthese")
        logger.info(f"*** Synthese des Solutions:")
        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=f'Solutions_classees_T{self._taille_tronquee}_D{decallage}', repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()

        somme_plateaux = 0
        for difficulte, liste_plateaux in solutions_classees.get('liste difficulte des plateaux').items():
            logger.info(f" - Difficulte : {difficulte} - {len(liste_plateaux)} plateau{self.pluriel(liste_plateaux, 'x')}")
            if difficulte != 'None':
                somme_plateaux += len(liste_plateaux)
        logger.info(f" - Total : {somme_plateaux} plateau{self.pluriel(range(somme_plateaux), 'x')} valide{self.pluriel(range(somme_plateaux), 's')}")

    def pluriel(self, LIGNES, lettre='s'):
        return lettre if len(LIGNES) > 1 else ""

    def chercher_en_boucle(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")
        while(True):
            self.tronquer_les_solutions(self._taille_tronquee)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)

    def chercher_en_sequence(self):
        profil = ProfilerLeCode('chercher_des_solutions', self._profiler_le_code)
        profil.start()

        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for i in range(10):
            # Effacer l'existant
            #solutions_classees_json = ExportJSON(0, 0, '', nom_export=f'Solutions_classees_T{TAILLE}_D{i * TAILLE}', repertoire=self._repertoire_solution)
            solutions_classees_json = ExportJSON(0, 0, '', nom_export=f'Solutions_classees_T{(i+1)*self._taille_tronquee}_D{0}', repertoire=self._repertoire_solution)
            solutions_classees_json.effacer()
            
            # tronquer_les_solutions(TAILLE, i * TAILLE)
            self.tronquer_les_solutions((i+1) * self._taille_tronquee, 0)
            profil.stop()

            self.afficher_synthese()

if __name__ == "__main__":
    NOM_TACHE = 'tronquer_les_solutions'
    FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    tronquer_solutions = TronquerLesSolutions(
        repertoire_solution='Solutions_nouvelle_architecture',
        taille_tronquee=10,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL,
        periode_scrutation_secondes=30*60
    )
    # tronquer_solutions.chercher_en_parallele()
    tronquer_solutions.chercher_en_sequence()
