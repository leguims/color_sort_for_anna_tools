"Module pour créer des plateaux de 'ColorWoodSort'"
from itertools import permutations

import color_wood_sort as cws

COLONNES = [3] # range(2, 5) # range(2, 5) #11
LIGNES = [3] # [2,3] #4
COLONNES_VIDES_MAX = 1
PROFILER_LE_CODE = False

def chercher_des_plateaux(colonnes, lignes):
    print(f"{' '*colonnes}[{colonnes}x{lignes}] DEBUT")
    plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    plateau.creer_plateau_initial()
    # plateau.afficher()
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX))
    if not lot_de_plateaux.est_deja_termine():
        # lot_de_plateaux.fixer_taille_memoire_max(5)
        for permutation_courante in permutations(plateau.pour_permutations):
            # Verifier que ce plateau est nouveau
            permutation_courante = ''.join(permutation_courante)
            if not lot_de_plateaux.est_ignore(permutation_courante):
                if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                    print(f"{' '*colonnes}[{colonnes}x{lignes}] nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")

        lot_de_plateaux.arret_des_enregistrements()
        # lot_de_plateaux.exporter_fichier_json()

        print(f"{' '*colonnes}[{colonnes}x{lignes}] duree={lot_de_plateaux.formater_duree(lot_de_plateaux.duree)}")

        print(f"{' '*colonnes}[{colonnes}x{lignes}] nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        print(f"{' '*colonnes}[{colonnes}x{lignes}] nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
    else:
        print(f"{' '*colonnes}[{colonnes}x{lignes}] Ce lot de plateaux est déjà terminé")


def chercher_en_sequence():
    for lignes in LIGNES:
        for colonnes in COLONNES:
            chercher_des_plateaux(colonnes, lignes)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode('chercher_des_plateaux', PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom="chercher_des_plateaux", nb_colonnes=12, nb_lignes=5)
    # taches.exporter()
    taches.importer()
    taches.executer_taches(chercher_des_plateaux)

    profil.stop()

if __name__ == "__main__":
    chercher_en_parallele()