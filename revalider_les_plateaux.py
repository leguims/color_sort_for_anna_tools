"Module pour créer des plateaux de 'ColorWoodSort'"
from itertools import permutations

import color_wood_sort as cws

COLONNES = range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
LIGNES = range(2, 14) #[3] # [2,3] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 5_000_000
PROFILER_LE_CODE = False

def revalider_les_plateaux(colonnes, lignes):
    print(f"{' '*colonnes}[{colonnes}x{lignes}] DEBUT - Revalider les plateaux")
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX), nb_plateaux_max = MEMOIRE_MAX)
    lot_de_plateaux.est_deja_termine()
    # Parcourir les plateaux et supprimer les plateaux "invalides"
    lot_de_plateaux.mettre_a_jour_les_plateaux_valides()

def chercher_en_sequence():
    for lignes in LIGNES:
        for colonnes in COLONNES:
            revalider_les_plateaux(colonnes, lignes)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode('revalider_les_plateaux', PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom="revalider_les_plateaux", nb_colonnes=7, nb_lignes=3)
    # taches.exporter()
    taches.importer()
    taches.executer_taches(revalider_les_plateaux)

    profil.stop()

if __name__ == "__main__":
    #chercher_en_parallele()
    chercher_en_sequence()