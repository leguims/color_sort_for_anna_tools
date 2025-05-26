import datetime
import json
from pathlib import Path


# TODO : Modifier de l'exterieur ce chemin de base.
REPERTOIRE_SORTIE_RACINE = 'Analyses'

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
