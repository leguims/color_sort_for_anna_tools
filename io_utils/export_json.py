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
        self._chemin_enregistrement = (Path(repertoire) / nom_plateau / (nom_export+'.json')).resolve()
        self._chemin_enregistrement_str = str(self._chemin_enregistrement)
        print(f"{self.now()} ExportJSON : '{ self._chemin_enregistrement_str}'")
        self._log_fichier_absent = True
        self._log_ouverture_fichier = True
        # Pour les logs
        if nom_plateau:
            # Recherche de plateaux, filtres et solutions
            pipeline = self._chemin_enregistrement.parts[-3]
            if 'solutions_unitaires' in pipeline:
                pipeline = 'solutions_unitaires'
                type_plateaux = nom_plateau.removeprefix('Plateaux_').removesuffix('.json')
                plateau = nom_export.removeprefix('Plateaux_'+type_plateaux+'_').removesuffix('.json')
                self._chemin_court_str = f"{pipeline} {type_plateaux} : {plateau}"
                self._log_fichier_absent = False
                self._log_ouverture_fichier = False
            else:
                type_plateaux = nom_plateau.removeprefix('Plateaux_').removesuffix('.json')
                self._chemin_court_str = f"{pipeline} : {type_plateaux}"
        else:
            # Regroupement des plateaux heterogenes
            pipeline = Path(repertoire).name
            type_plateaux = nom_export
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
                self.__atomic_write_json(contenu_dict)
                ecriture = True
                break
            except OSError as e:
                print(f"{self.now()} JSON.forcer_export() OSError '{self._chemin_court_str}'")
                print(f"OSError : '{e}'")
                print("OSError:", repr(e))
                print("errno:", getattr(e, "errno", None))
                print("strerror:", getattr(e, "strerror", None))
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
    def lockfile_blocking(self):
        """
        Bloque indéfiniment tant que lock_path existe.
        Prend le verrou en créant lock_path de façon atomique.
        Relâche en supprimant lock_path à la sortie du with.
        """
        if not self._chemin_enregistrement.exists():
            # print(f"{self.now()} JSON.lockfile_blocking() Pas de lock pour le fichier inexistant '{Path(self._chemin_enregistrement).name}'")
            yield
        elif self._chemin_enregistrement.is_dir():
            print(f"{self.now()} JSON.lockfile_blocking() Pas de lock pour le repertoire '{self._chemin_enregistrement.name}'")
            yield
        elif not self._chemin_enregistrement.is_file():
            print(f"{self.now()} JSON.lockfile_blocking() Lock uniquement pour les fichiers '{self._chemin_enregistrement.name}'")
            yield
        else:
            attente_max = 5
            full_lock_path = self._chemin_enregistrement_str + '.lock'
            lock_trace = self._chemin_enregistrement.name.removeprefix('Plateaux_').removesuffix('.json')
            while True:
                # Création atomique : si ça existe -> FileExistsError
                try:
                    with open(full_lock_path, "xb") as f:
                        pass    # lock file binaire et vide
                except FileExistsError:
                    # Quelqu'un a déjà le verrou => attente infinie
                    print(f"{self.now()} JSON.lockfile_blocking() bloqué :       '{lock_trace}'")
                    if attente_max:
                        attente_max -= 1
                        print("attente 60s")
                        time.sleep(60.0)
                    else:
                        raise FileExistsError
                except OSError as e:
                    print(f"{self.now()} JSON.lockfile_blocking() OSError sur creation/fermeture du lockfile '{lock_trace}'")

                    print("full_lock_path:", full_lock_path)
                    print("CWD:", os.getcwd())
                    print("to delete:", full_lock_path)
                    print("exists:", os.path.exists(full_lock_path))
                    print("isfile:", os.path.isfile(full_lock_path))
                    print("isdir:", os.path.isdir(full_lock_path))
                    print("parent:", os.path.dirname(full_lock_path))
                    print("parent writable:", os.access(os.path.dirname(full_lock_path), os.W_OK))

                    print(e)
                    print("OSError:", repr(e))
                    print("errno:", getattr(e, "errno", None))
                    print("strerror:", getattr(e, "strerror", None))
                    raise OSError

                # Verrou acquis
                # print(f"{self.now()} JSON.lockfile_blocking() Reservation :  '{lock_trace}'")
                try:
                    yield
                finally:
                    last_error = None
                    for i in range(5):
                        try:
                            # Liberer le lock
                            Path(full_lock_path).unlink(missing_ok=True)
                            # print(f"{self.now()} JSON.lockfile_blocking() Liberation :   '{lock_trace}'")
                            return
                        except PermissionError as e:
                            print(f"{self.now()} JSON.lockfile_blocking() PermissionError sur effacement du lockfile '{lock_trace}'")
                            last_error = e
                        except OSError as e:
                            print(f"{self.now()} JSON.lockfile_blocking() OSError sur effacement du lockfile '{lock_trace}'")
                            last_error = e
                        # Pour le debug de PermissionError/OSError
                        print("full_lock_path:", full_lock_path)
                        print("CWD:", os.getcwd())
                        print("to delete:", full_lock_path)
                        print("exists:", os.path.exists(full_lock_path))
                        print("isfile:", os.path.isfile(full_lock_path))
                        print("isdir:", os.path.isdir(full_lock_path))
                        print("parent:", os.path.dirname(full_lock_path))
                        print("parent writable:", os.access(os.path.dirname(full_lock_path), os.W_OK))

                        print(last_error)
                        print("PermissionError:", repr(last_error))
                        print("errno:", getattr(last_error, "errno", None))
                        print("strerror:", getattr(last_error, "strerror", None))

                        time.sleep(0.1)
                    if last_error:
                        raise last_error

    def __atomic_write_json(self, data) -> None:
        if not self._chemin_enregistrement.exists():
            # print(f"{self.now()} JSON.__atomic_write_json() Ecriture atomique d'un nouveau fichier '{Path(path).name}'")
            pass
        elif self._chemin_enregistrement.is_dir():
            print(f"{self.now()} JSON.__atomic_write_json() Pas d'écriture atomique sur un repertoire '{self._chemin_enregistrement.name}'")
            return
        elif not self._chemin_enregistrement.is_file():
            print(f"{self.now()} JSON.__atomic_write_json() Ecriture atomique uniquement pour les fichiers '{self._chemin_enregistrement.name}'")
            return

        # On écrit dans le même dossier pour que os.replace soit atomique
        dir_name = os.path.dirname(self._chemin_enregistrement_str) or "."
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=dir_name)

        try:
            with self.lockfile_blocking():
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    if self._log_ouverture_fichier:
                        print(f"{self.now()} JSON.__atomic_write_json() fichier ouvert '{self._chemin_court_str}'")
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    f.flush()
                    os.fsync(f.fileno())  # force la persistance avant le swap (utile sur certains FS)

                # Remplacement atomique : les lecteurs verront soit l’ancienne version,
                # soit la nouvelle, jamais un fichier à moitié écrit.
                try:
                    os.replace(tmp_path, self._chemin_enregistrement_str)
                except OSError as e:
                    print(f"{self.now()} JSON.__atomic_write_json() OSError sur os.replace '{self._chemin_court_str}'")
                    print("OSError:", repr(e))
                    print("errno:", getattr(e, "errno", None))
                    print("strerror:", getattr(e, "strerror", None))
        except FileExistsError:
            # Fichier bloqué
            print(f"{self.now()} JSON.__atomic_write_json() FileExistsError le fichier est bloqué, pas d'écriture sur '{self._chemin_court_str}'")
            raise FileExistsError

        finally:
            # Si jamais ça échoue avant os.replace, on nettoie
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except OSError:
                pass
        if self._log_ouverture_fichier:
            print(f"{self.now()} JSON.__atomic_write_json() fichier ferme '{self._chemin_court_str}'")

    def effacer(self):
        """Effacer le contenu du fichier existant"""
        return self.forcer_export(dict())

    def importer(self):
        """Lit dans un fichier JSON les informations totales ou de la derniere iteration realisee."""
        dico_json = {}
        # 5 tentatives de lecture à : 5min, 11min, 18min, 26min, 35min et 45min
        for attente_en_min in range(1,6): # Range cumulé = 5+6+7+8+9+10 = 45 mins
            try:
                with self.lockfile_blocking():
                    try:
                        with open(self._chemin_enregistrement_str, "r", encoding='utf-8') as fichier:
                            if self._log_ouverture_fichier:
                                print(f"{self.now()} JSON.importer() fichier ouvert '{self._chemin_court_str}'")
                            dico_json = self.json_load(fichier)
                    except FileNotFoundError as e:
                        if self._log_fichier_absent:
                            print(f"{self.now()} JSON.importer() FileNotFoundError '{self._chemin_court_str}'")
                            # print(f"FileNotFoundError : '{e}'")
                    except OSError as e:
                        print(f"{self.now()} JSON.importer() OSError sur open '{self._chemin_court_str}'")
                        print("OSError:", repr(e))
                        print("errno:", getattr(e, "errno", None))
                        print("strerror:", getattr(e, "strerror", None))
                    except MemoryError as e:
                        print(f"{self.now()} JSON.importer() MemoryError sur open '{self._chemin_court_str}'")
                        # print(f"MemoryError : '{e}'")
                if self._log_ouverture_fichier:
                    print(f"{self.now()} JSON.importer() fichier ferme '{self._chemin_court_str}'")
                return dico_json

            except FileExistsError:
                # Attente avant la prochaine tentative de lecture du fichier
                print(f"{self.now()} JSON.importer() FileExistsError sur open '{self._chemin_court_str}'")
                print(f"{self.now()} JSON.importer() lock bloqué : Nouvelle tentative dans {attente_en_min} minutes")
                time.sleep(attente_en_min * 60)
        print(f"{self.now()} JSON.importer() Abandon de lecture '{self._chemin_court_str}'")
        return dico_json

    def json_load(self, fichier):
        """Decode le JSON du fichier."""
        try:
            dico_json = json.load(fichier)
        except json.decoder.JSONDecodeError as e:
            print(f"{self.now()} JSON.importer() JSONDecodeError '{self._chemin_court_str}'")
            print(f"JSONDecodeError : '{e}'")
            # TODO : effacer le fichier.
            print(f"{self.now()} JSON.importer() Effacer le fichier JSON corrompu '{self._chemin_court_str}'")
            return {}
        except OSError as e:
            print(f"{self.now()} JSON.importer() OSError sur json.load '{self._chemin_court_str}'")
            print(f"OSError sur json.load: '{e}'")
            print("OSError:", repr(e))
            print("errno:", getattr(e, "errno", None))
            print("strerror:", getattr(e, "strerror", None))
            raise OSError(e) # Remonter l'exception pour relire le fichier plus tard
        except MemoryError as e:
            print(f"{self.now()} JSON.importer() MemoryError sur json.load '{self._chemin_court_str}'")
            # print(f"MemoryError : '{e}'")
            return {}
        return dico_json
