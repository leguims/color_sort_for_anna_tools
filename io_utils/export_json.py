from contextlib import contextmanager
import datetime
import time
import json
import os
from pathlib import Path
import tempfile

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

        # 5 tentatives de lecture à : 5min, 11min, 18min, 26min, 35min et 45min
        ecriture = False
        for attente_en_min in range(5,10): # Range cumulé = 5+6+7+8+9+10 = 45 mins
            try:
                self.__atomic_write_json(self._chemin_enregistrement, contenu_dict)
                ecriture = True
                break
            except OSError as e:
                print(f"{self.now()} JSON.forcer_export() OSError '{self._chemin_court_str}'")
                print(f"OSError : '{e}'")
                # Attente avant la prochaine tentative d'écriture du fichier
                print(f"{self.now()} JSON.importer() OSError : Nouvelle tentative dans {attente_en_min} minutes")
                time.sleep(attente_en_min * 60)
        if not ecriture:
            print(f"{self.now()} JSON.forcer_export() Abandon de l'ecriture '{self._chemin_court_str}'")
            return False

        self._longueur_dernier_enregistrement = len(contenu_dict)
        self._timestamp_dernier_enregistrement = datetime.datetime.now().timestamp()
        return True

    @contextmanager
    def lockfile_blocking(self, lock_path: str):
        """
        Bloque indéfiniment tant que lock_path existe.
        Prend le verrou en créant lock_path de façon atomique.
        Relâche en supprimant lock_path à la sortie du with.
        """
        full_lock_path = lock_path + '.lock'
        while True:
            try:
                # Création atomique : si ça existe -> FileExistsError
                fd = os.open(full_lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)

                # Verrou acquis
                try:
                    yield
                finally:
                    try:
                        # Liberer le lock
                        os.unlink(full_lock_path)
                    except FileNotFoundError:
                        pass
                return

            except FileExistsError:
                # Quelqu'un a déjà le verrou => attente infinie
                time.sleep(5.0)

    def __atomic_write_json(self, path: str, data) -> None:
        # On écrit dans le même dossier pour que os.replace soit atomique
        dir_name = os.path.dirname(path) or "."
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=dir_name)

        try:
            with self.lockfile_blocking(path):
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    if 'Resolution' not in str(self._chemin_enregistrement):
                        print(f"{self.now()} JSON.__atomic_write_json() fichier ouvert '{self._chemin_court_str}'")
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    f.flush()
                    os.fsync(f.fileno())  # force la persistance avant le swap (utile sur certains FS)

                # Remplacement atomique : les lecteurs verront soit l’ancienne version,
                # soit la nouvelle, jamais un fichier à moitié écrit.
                os.replace(tmp_path, path)

        finally:
            # Si jamais ça échoue avant os.replace, on nettoie
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except OSError:
                pass
        if 'Resolution' not in str(self._chemin_enregistrement):
            print(f"{self.now()} JSON.__atomic_write_json() fichier ferme '{self._chemin_court_str}'")

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la derniere iteration realisee."""
        # 5 tentatives de lecture à : 5min, 11min, 18min, 26min, 35min et 45min
        for attente_en_min in range(1,6): # Range cumulé = 5+6+7+8+9+10 = 45 mins
            try:
                with self.lockfile_blocking(self._chemin_enregistrement):
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
        print(f"{self.now()} JSON.importer() Abandon de lecture '{self._chemin_court_str}'")
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
