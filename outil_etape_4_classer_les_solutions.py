"Parcourt les plateaux resolus et les rassemble dans le fichier 'Solutions_classees.json' par difficulte avec une ecriture universelle"
import datetime
import time
import logging
import pathlib

from plateau import Plateau
from lot_de_plateaux import LotDePlateaux
from profiler_le_code import ProfilerLeCode
from export_json import ExportJSON

class ClasserLesSolutions:
    """Parcourt les plateaux resolus et les rassemble dans le fichier
    'Solutions_classees.json' par difficulte avec une ecriture universelle"""
    def __init__(self, nb_colonnes, nb_lignes, nb_colonnes_vides,
                repertoire_analyse,
                repertoire_solution,
                fichier_solution,
                nb_coups_min,
                nom_tache,
                fichier_journal,
                profiler_le_code = False,
                periode_scrutation_secondes = 30*60): # en secondes
        self._nb_colonnes = nb_colonnes
        self._nb_lignes = nb_lignes
        self._nb_colonnes_vides = nb_colonnes_vides
        self._repertoire_analyse = repertoire_analyse
        self._repertoire_solution = repertoire_solution
        self._fichier_solution = fichier_solution
        self._nb_coups_min = nb_coups_min
        self._nom_tache = nom_tache
        self._fichier_journal = fichier_journal
        self._profiler_le_code = profiler_le_code
        self._periode_scrutation_secondes = periode_scrutation_secondes

    def classer_les_solutions(self, colonnes, lignes, taciturne=False):
        # Configurer le logger
        logger = logging.getLogger(f"{colonnes}.{lignes}.{self._nom_tache}")
        if not taciturne:
            logger.info(f"DEBUT")
        # logger.info(plateau.plateau_ligne_texte_universel)
        lot_de_plateaux = LotDePlateaux((colonnes, lignes, self._nb_colonnes_vides),
                                        repertoire_export_json=self._repertoire_analyse)
        if lot_de_plateaux.est_deja_termine(): # or True: # True = Classe toutes les solutions a l'heure actuel.
            if not taciturne:
                logger.info("Ce lot de plateaux est termine")

            solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=self._fichier_solution, repertoire=self._repertoire_solution)
            solutions_classees = solutions_classees_json.importer()
            plateau = Plateau(colonnes, lignes, self._nb_colonnes_vides)

            liste_plateaux_avec_solutions = lot_de_plateaux.to_dict().get('liste difficulte des plateaux')
            if "liste difficulte des plateaux" not in solutions_classees:
                solutions_classees["liste difficulte des plateaux"] = {}
            dict_difficulte = solutions_classees["liste difficulte des plateaux"]
            # Filtrer les plateaux sans solutions ou trop triviaux
            for difficulte, dico_nb_coups in liste_plateaux_avec_solutions.items():
                for nb_coups, liste_plateaux in dico_nb_coups.items():
                    logger.info(f"\n\r - Difficulte : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{self.pluriel(liste_plateaux, 'x')}")
                    if difficulte is not None and nb_coups is not None and int(nb_coups) >= self._nb_coups_min :
                        if str(difficulte) not in dict_difficulte:
                            dict_difficulte[str(difficulte)] = {}
                        if str(nb_coups) not in dict_difficulte[str(difficulte)]:
                            dict_difficulte[str(difficulte)][str(nb_coups)] = []
                        difficulte_courante = dict_difficulte[str(difficulte)][str(nb_coups)]
                        for plateau_ligne_texte_universel in liste_plateaux:
                            plateau.clear()
                            plateau.plateau_ligne_texte_universel = plateau_ligne_texte_universel
                            # Eviter les doublons
                            if plateau.plateau_ligne_texte_universel not in difficulte_courante:
                                difficulte_courante.append(plateau.plateau_ligne_texte_universel)
            self.ordonner_difficulte_nombre_coups(solutions_classees["liste difficulte des plateaux"])
            solutions_classees_json.forcer_export(solutions_classees)
        else:
            if not taciturne:
                logger.info(" - Ce lot de plateaux n'est pas encore termine, pas de classement de solutions.")

    # Copie de 'LotDePlateaux.arret_des_enregistrements_de_difficultes_plateaux()'
    def ordonner_difficulte_nombre_coups(self, ensemble_des_difficultes_de_plateaux):
        "Methode qui classe les difficultes et nombres de coups des solutions"
        # Classement des difficultes
        cles_difficulte = list(ensemble_des_difficultes_de_plateaux.keys())
        if None in cles_difficulte:
            cles_difficulte.remove(None) # None est inclassable avec 'list().sort()'
        cles_difficulte.sort()
        dico_difficulte_classe = {k: ensemble_des_difficultes_de_plateaux[k] for k in cles_difficulte}
        if None in ensemble_des_difficultes_de_plateaux:
            dico_difficulte_classe[None] = ensemble_des_difficultes_de_plateaux[None]
        ensemble_des_difficultes_de_plateaux.clear()
        ensemble_des_difficultes_de_plateaux.update(dico_difficulte_classe)
        
        # Classement du nombre de coups
        for difficulte, dico_nb_coups in ensemble_des_difficultes_de_plateaux.items():
            cles_nb_coups = list(dico_nb_coups.keys())
            if None in cles_nb_coups:
                cles_nb_coups.remove(None) # None est inclassable avec 'list().sort()'
            cles_nb_coups.sort()
            dico_nb_coups_classe = {k: dico_nb_coups[k] for k in cles_nb_coups}
            if None in dico_nb_coups:
                dico_nb_coups_classe[None] = dico_nb_coups[None]
            dico_nb_coups.clear()
            dico_nb_coups.update(dico_nb_coups_classe)

    def afficher_synthese(self):
        logger = logging.getLogger(f"chercher.afficher_synthese")
        logger.info(f"*** Synthese des Solutions:")
        solutions_classees_json = ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire=self._repertoire_solution)
        solutions_classees = solutions_classees_json.importer()

        somme_plateaux = 0
        for difficulte, dico_nb_coups in solutions_classees.get('liste difficulte des plateaux').items():
            for nb_coups, liste_plateaux in dico_nb_coups.items():
                logger.info(f" - Difficulte : {difficulte} en {nb_coups} coups : {len(liste_plateaux)} plateau{self.pluriel(liste_plateaux, 'x')}")
                if difficulte != 'None':
                    somme_plateaux += len(liste_plateaux)
        logger.info(f" - Total : {somme_plateaux} plateau{self.pluriel(range(somme_plateaux), 'x')} valide{self.pluriel(range(somme_plateaux), 's')}")

    def pluriel(self, LIGNES, lettre='s'):
        return lettre if len(LIGNES) > 1 else ""

    def chercher_en_boucle(self):
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_boucle.NOUVELLE-RECHERCHE")

        taciturne = False # 1ere iteration n'est pas taciturne
        while(True):
            logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
            for iter_lignes in self._nb_lignes:
                for iter_colonnes in self._nb_colonnes:
                    self.classer_les_solutions(iter_colonnes, iter_lignes, taciturne=taciturne)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            logger.info(f"{current_time} - Attente entre 2 iterations de {self._periode_scrutation_secondes}s...")
            time.sleep(self._periode_scrutation_secondes)
            taciturne = True

    def chercher_en_sequence(self):
        profil = ProfilerLeCode('chercher_des_solutions', self._profiler_le_code)
        profil.start()

        # Effacer l'existant
        solutions_classees_json = ExportJSON(0, 0, '', nom_export='Solutions_classees', repertoire=self._repertoire_solution)
        solutions_classees_json.effacer()
        
        # Configurer le logger
        logger = logging.getLogger(f"chercher_en_sequence.NOUVELLE-RECHERCHE")
        logger.info('-'*10 + " NOUVELLE RECHERCHE " + '-'*10)
        for iter_lignes in self._nb_lignes:
            for iter_colonnes in self._nb_colonnes:
                self.classer_les_solutions(iter_colonnes, iter_lignes)
        profil.stop()

        self.afficher_synthese()

if __name__ == "__main__":
    NOM_TACHE = 'classer_les_solutions'
    FICHIER_JOURNAL = pathlib.Path('logs') / f'{NOM_TACHE}.log'

    # Configurer le logger
    logging.basicConfig(filename=FICHIER_JOURNAL, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    classer_solutions = ClasserLesSolutions(
        nb_colonnes=[3], # range(3, 14) # [2]
        nb_lignes=[4], # range(3, 14) # [2]
        nb_colonnes_vides=1,
        repertoire_analyse='Analyse_nouvelle_architecture',
        repertoire_solution='Solutions_nouvelle_architecture',
        fichier_solution='Solutions_classees',
        nb_coups_min=3,
        nom_tache=NOM_TACHE,
        fichier_journal=FICHIER_JOURNAL
    )
    # classer_solutions.chercher_en_parallele()
    classer_solutions.chercher_en_sequence()
