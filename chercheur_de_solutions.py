"Parcourt les plateaux exhaustifs et en trouve les solutions 'ColorWoordSort'"
from itertools import permutations #, product, combinations#, combinations_with_replacement
import cProfile
import pstats
import time

import color_wood_sort as cws

COLONNES = range(2, 12) # [2] # range(2, 12)
LIGNES = range(2, 5) # [2] # range(2, 5)
PERIODE_SCRUTATION_SECONDES = 10 # 10*60
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000_000
PROFILER_LE_CODE = False

if PROFILER_LE_CODE:
    # Profilage du code
    profil = cProfile.Profile()
    profil.enable()

while(True):
    for lignes in LIGNES:
        for colonnes in COLONNES:
            print(f"\n\r*** Generatrice {colonnes}x{lignes}: DEBUT")
            plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
            plateau.creer_plateau_initial()
            # plateau.afficher()
            lot_de_plateaux = cws.LotDePlateaux(nb_plateaux_max = MEMOIRE_MAX)
            if lot_de_plateaux.est_deja_termine(colonnes, lignes, COLONNES_VIDES_MAX):
                print("Ce lot de plateaux est déjà terminé, recherche de nouvelles solutions")

                if lot_de_plateaux.nb_plateaux_valides != lot_de_plateaux.nb_plateaux_solutionnes:
                    if lot_de_plateaux.nb_plateaux_valides < lot_de_plateaux.nb_plateaux_solutionnes:
                        print("Il y a plus de plateaus de solutions que de plateaux valides ! Il y a un probleme !")
                    print(f"Il reste des solutions à trouver : {lot_de_plateaux.nb_plateaux_valides} != {lot_de_plateaux.nb_plateaux_solutionnes}")
                    for plateau_ligne_texte_a_resoudre in lot_de_plateaux.plateaux_valides:
                        plateau.clear()
                        plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
                        resolution = cws.ResoudrePlateau(plateau)
                        resolution.backtracking()
                        lot_de_plateaux.definir_difficulte_plateau(plateau, resolution.solution_la_plus_courte)

                    lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
                    for difficulte, liste_plateaux in lot_de_plateaux.difficulte_plateaux.items():
                        print(f"*** Difficulté : {difficulte} - {len(liste_plateaux)} plateau{'x' if len(liste_plateaux) > 1 else ''}")
                else:
                    print("Toutes les solutions sont trouvées")
            else:
                print("Ce lot de plateaux n'est pas encore terminé, pas de recherche de solution")
    time.sleep(PERIODE_SCRUTATION_SECONDES)


if PROFILER_LE_CODE:
    # Fin du profilage
    profil.disable()

    # Affichage des statistiques de profilage
    stats = pstats.Stats(profil).sort_stats('cumulative')
    stats.print_stats()

    # Exporter les statistiques dans un fichier texte
    with open('profiling_results.txt', 'w') as fichier:
        stats = pstats.Stats(profil, stream=fichier)
        #stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(10)
        stats.sort_stats(pstats.SortKey.CUMULATIVE).print_stats()
