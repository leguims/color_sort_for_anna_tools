import datetime
import time
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
        try:
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.forcer_export() fichier ouvert '{self._chemin_court_str}'")
                json.dump(contenu_dict, fichier, ensure_ascii=False, indent=4)
        except OSError as e:
            print(f"{self.now()} JSON.forcer_export() OSError '{self._chemin_court_str}'")
            print(f"OSError : '{e}'")
            return False
        if 'Resolution' not in str(self._chemin_enregistrement):
            print(f"{self.now()} JSON.forcer_export() fichier ferme '{self._chemin_court_str}'")

        self._longueur_dernier_enregistrement = len(contenu_dict)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la derniere iteration realisee."""
        # 5 tentatives de lecture à : 0min, 1min, 3min, 6min, 10min et 15min
        for attente_en_min in range(1,6): # Range cumulé = 15
            try:
                with open(self._chemin_enregistrement, "r", encoding='utf-8') as fichier:
                    if 'Resolution' not in str(self._chemin_enregistrement):
                        print(f"{self.now()} JSON.importer() fichier ouvert '{self._chemin_court_str}'")
                    dico_json = self.json_load(fichier)
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.importer() fichier ferme '{self._chemin_court_str}'")
                return dico_json

            except FileNotFoundError as e:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.importer() FileNotFoundError '{self._chemin_court_str}'")
                    # print(f"FileNotFoundError : '{e}'")
                return {}
            except OSError as e:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.importer() OSError sur open '{self._chemin_court_str}'")
                    print(f"OSError : '{e}'")
                # Attente avant la prochaine tentative de lecture du fichier
                print(f"{self.now()} JSON.importer() OSError : Nouvelle tentative dans {attente_en_min} minutes")
                time.sleep(attente_en_min * 60)
            except MemoryError as e:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.importer() MemoryError sur open '{self._chemin_court_str}'")
                    # print(f"MemoryError : '{e}'")
                return {}
        return {}

    def json_load(self, fichier):
        """Decode le JSON du fichier."""
        try:
            dico_json = json.load(fichier)
        except json.decoder.JSONDecodeError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() JSONDecodeError '{self._chemin_court_str}'")
                print(f"JSONDecodeError : '{e}'")
            return {}
        except OSError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() OSError sur json.load '{self._chemin_court_str}'")
                print(f"OSError sur json.load: '{e}'")
            raise OSError(e) # Remonter l'exception pour relire le fichier plus tard
        except MemoryError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() MemoryError sur json.load '{self._chemin_court_str}'")
                # print(f"MemoryError : '{e}'")
            return {}
        return dico_json
