import datetime
import json
from pathlib import Path

class ExportJSON:
    def __init__(self, delai, longueur, nom_plateau, nom_export, repertoire):
        self._delai_enregistrement = delai
        self._longueur_enregistrement = longueur
        self._chemin_enregistrement = Path(repertoire) / nom_plateau / (nom_export+'.json')
        # Pour les logs
        pipeline = self._chemin_enregistrement.parts[-3]
        type_plateaux = nom_plateau.removeprefix('Plateaux_').removesuffix('.json')
        self._chemin_court_str = f"{pipeline} : {type_plateaux}"

        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        self._longueur_dernier_enregistrement = 0

    @property
    def chemin_enregistrement(self) -> Path:
        return self._chemin_enregistrement

    def now(self) -> str:
        return str(datetime.datetime.now().replace(microsecond=0))

    def exporter(self, contenu):
        """Enregistre un fichier JSON selon des criteres de nombres et de temps.
Retourne True si l'export a ete realise"""
        if (len(contenu) - self._longueur_dernier_enregistrement >= self._longueur_enregistrement):
            return self.forcer_export(contenu)

        if (datetime.datetime.now().timestamp() - self._timestamp_dernier_enregistrement >= self._delai_enregistrement) \
            and (len(contenu) == 0 or len(contenu) != self._longueur_dernier_enregistrement):
            return self.forcer_export(contenu)
        
        return False

    def forcer_export(self, contenu):
        """Enregistre un fichier JSON en ignorant les criteres.
Retourne True si l'export a ete realise"""
        # Enregistrement des donnees dans un fichier JSON
        if not self._chemin_enregistrement.parent.exists():
            self._chemin_enregistrement.parent.mkdir(parents=True, exist_ok=True)
        try:
            if type(contenu) == dict:
                contenu_dict = contenu
            else:
                try:
                    # Enregistrement d'une classe
                    contenu_dict = contenu.to_dict()
                except MemoryError as e:
                    print(f"{self.now()} JSON.forcer_export() MemoryError '{self._chemin_court_str}'")
                    # print(f"MemoryError : '{e}'")
                    return False
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.forcer_export() fichier ouvert '{self._chemin_court_str}'")
                json.dump(contenu_dict, fichier, ensure_ascii=False, indent=4)
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.forcer_export() fichier ferme '{self._chemin_court_str}'")
        except OSError as e:
            print(f"{self.now()} JSON.forcer_export() OSError '{self._chemin_court_str}'")
            print(f"OSError : '{e}'")
            return False

        self._longueur_dernier_enregistrement = len(contenu_dict)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la derniere iteration realisee."""
        try:
            with open(self._chemin_enregistrement, "r", encoding='utf-8') as fichier:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.importer() fichier ouvert '{self._chemin_court_str}'")
                dico_json = json.load(fichier)
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() fichier ferme '{self._chemin_court_str}'")
            return dico_json
        except FileNotFoundError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() FileNotFoundError '{self._chemin_court_str}'")
                # print(f"FileNotFoundError : '{e}'")
            return {}
        except json.decoder.JSONDecodeError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() JSONDecodeError '{self._chemin_court_str}'")
                print(f"JSONDecodeError : '{e}'")
            return {}
        except OSError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() OSError '{self._chemin_court_str}'")
                print(f"OSError : '{e}'")
            return {}
        except MemoryError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() MemoryError '{self._chemin_court_str}'")
                # print(f"MemoryError : '{e}'")
            return {}
        return {}
