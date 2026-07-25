import datetime
import json
from pathlib import Path

class ExportJSON:
    def __init__(self, delai, longueur, nom_plateau, nom_export, repertoire):
        self._delai_enregistrement = delai
        self._longueur_enregistrement = longueur
        self._chemin_enregistrement = Path(repertoire) / nom_plateau / (nom_export+'.json')

        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        self._longueur_dernier_enregistrement = 0

    @property
    def chemin_enregistrement(self) -> Path:
        return self._chemin_enregistrement

    def chemin_court_str(self, chemin : Path) -> str:
        pipeline = chemin.parent.parent
        type_plateaux = chemin.name.removeprefix('Plateaux_').removesuffix('.json')
        return f"{pipeline} : {type_plateaux}"

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
        chemin = self._chemin_enregistrement
        fin_chemin = Path() / chemin.parts[-3] / chemin.parts[-2] / chemin.parts[-1]
        fin_chemin = self.chemin_court_str(fin_chemin)
        if not self._chemin_enregistrement.parent.exists():
            self._chemin_enregistrement.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self._chemin_enregistrement, "w", encoding='utf-8') as fichier:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.forcer_export() fichier ouvert '{fin_chemin}'")
                if type(contenu) == dict:
                    json.dump(contenu, fichier, ensure_ascii=False, indent=4)
                else:
                    # Enregistrement d'une classe
                    json.dump(contenu.to_dict(), fichier, ensure_ascii=False, indent=4)
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.forcer_export() fichier ferme '{fin_chemin}'")
        except OSError as e:
            print(f"{self.now()} JSON.forcer_export() OSError '{fin_chemin}'")
            print(f"OSError : '{e}'")
            return False

        self._longueur_dernier_enregistrement = len(contenu)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la derniere iteration realisee."""
        chemin = self._chemin_enregistrement
        fin_chemin = Path() / chemin.parts[-3] / chemin.parts[-2] / chemin.parts[-1]
        fin_chemin = self.chemin_court_str(fin_chemin)
        try:
            with open(self._chemin_enregistrement, "r", encoding='utf-8') as fichier:
                if 'Resolution' not in str(self._chemin_enregistrement):
                    print(f"{self.now()} JSON.importer() fichier ouvert '{fin_chemin}'")
                    # print(f"{self.now()} - JSON.importer()")
                    # print(f"{fin_chemin}")
                    # print(f"fichier ouvert")
                dico_json = json.load(fichier)
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() fichier ferme '{fin_chemin}'")
                # print(f"{self.now()} - JSON.importer()")
                # print(f"{fin_chemin}")
                # print(f"fichier ferme")
            return dico_json
        except FileNotFoundError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() FileNotFoundError '{fin_chemin}'")
                # print(f"{self.now()} - JSON.importer()")
                # print(f"{fin_chemin}")
                # print(f"FileNotFoundError : '{e}'")
            return {}
        except json.decoder.JSONDecodeError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() JSONDecodeError '{fin_chemin}'")
                # print(f"{self.now()} - JSON.importer()")
                # print(f"{fin_chemin}")
                print(f"JSONDecodeError : '{e}'")
            return {}
        except OSError as e:
            if 'Resolution' not in str(self._chemin_enregistrement):
                print(f"{self.now()} JSON.importer() OSError '{fin_chemin}'")
                # print(f"{self.now()} - JSON.importer()")
                # print(f"{fin_chemin}")
                print(f"OSError : '{e}'")
            return {}
