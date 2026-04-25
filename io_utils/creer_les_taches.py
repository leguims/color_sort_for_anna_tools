import pathlib
import json
from multiprocessing import Pool, cpu_count
import logging

class CreerLesTaches:
    def __init__(self, nom, liste_colonnes, liste_lignes):
        self._nom = f'{max(liste_colonnes)}.{max(liste_lignes)}.{nom}'
        self._taches = [{'colonnes': c, 'lignes': l, 'complexite': c*l, 'terminee': False, 'en_cours': False} for c in liste_colonnes for l in liste_lignes]
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
        if pathlib.Path(f'{self._nom}.json').exists():
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
