import cProfile
import pstats

class ProfilerLeCode:
    def __init__(self, nom, actif = False):
        self.actif = actif
        self._nom = nom

    def start(self):
        if self.actif:
            # Profilage du code
            self._profil = cProfile.Profile()
            self._profil.enable()

    def stop(self):
        if self.actif:
            # Fin du profilage
            self._profil.disable()

            # Affichage des statistiques de profilage
            self._stats = pstats.Stats(self._profil).sort_stats('cumulative')
            self._stats.print_stats()

            # Exporter les statistiques dans un fichier texte
            with open(f'profiling_results_{self._nom}.txt', 'w') as fichier:
                self._stats = pstats.Stats(self._profil, stream=fichier)
                #stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)
                self._stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
