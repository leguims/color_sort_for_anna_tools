"Module pour créer, résoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations

import color_wood_sort as cws

COLONNES = [3] # range(2, 5) # range(2, 5) #11
LIGNES = [3] # [2,3] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 5_000_000
PROFILER_LE_CODE = False

def chercher_des_plateaux(colonnes, lignes):
    print(f"[{colonnes}x{lignes}] DEBUT")
    plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    plateau.creer_plateau_initial()
    # plateau.afficher()
    lot_de_plateaux = cws.LotDePlateaux(nb_plateaux_max = MEMOIRE_MAX)
    if not lot_de_plateaux.est_deja_termine(colonnes, lignes, COLONNES_VIDES_MAX):
        # lot_de_plateaux.fixer_taille_memoire_max(5)
        plateau_courant = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
        for permutation_courante in permutations(plateau.pour_permutations):
            # Verifier que ce plateau est nouveau
            plateau_courant.plateau_ligne = permutation_courante
            if not lot_de_plateaux.est_ignore(plateau_courant):
                if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                    print(f"[{colonnes}x{lignes}] nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
            plateau_courant.clear()

        lot_de_plateaux.arret_des_enregistrements()
        # lot_de_plateaux.exporter_fichier_json()

        if lot_de_plateaux.duree < 0.001:
            print(f"[{colonnes}x{lignes}] duree={int(lot_de_plateaux.duree*1_000_000)} microsecondes")
        elif lot_de_plateaux.duree < 1:
            print(f"[{colonnes}x{lignes}] duree={int(lot_de_plateaux.duree*1_000)} millisecondes")
        elif lot_de_plateaux.duree < 60:
            print(f"[{colonnes}x{lignes}] duree={int(lot_de_plateaux.duree)} secondes")
        elif lot_de_plateaux.duree < 60*60:
            print(f"[{colonnes}x{lignes}] duree={int(lot_de_plateaux.duree / 60)} minutes {int(lot_de_plateaux.duree % 60)} secondes")
        elif lot_de_plateaux.duree < 60*60*24:
            print(f"[{colonnes}x{lignes}] duree={int(lot_de_plateaux.duree / (60*60))} heures {int(lot_de_plateaux.duree % (60*60))} minutes")
        else:
            print(f"[{colonnes}x{lignes}] duree={int(lot_de_plateaux.duree / (60*60*24))} jours {int(lot_de_plateaux.duree % (60*60*24))} heures")

        print(f"[{colonnes}x{lignes}] nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        print(f"[{colonnes}x{lignes}] nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
    else:
        print(f"[{colonnes}x{lignes}] Ce lot de plateaux est déjà terminé")


def chercher_en_sequence():
    for lignes in LIGNES:
        for colonnes in COLONNES:
            chercher_des_plateaux(colonnes, lignes)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode('chercher_des_plateaux', PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom="chercher_des_plateaux", nb_colonnes=12, nb_lignes=5)
    taches.exporter()
    taches.executer_taches(chercher_des_plateaux)

    profil.stop()

if __name__ == "__main__":
    chercher_en_parallele()