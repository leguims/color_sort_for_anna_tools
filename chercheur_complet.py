"Module pour créer, résoudre et qualifier les soltuions des plateaux de 'ColorWoordSort'"
from itertools import permutations #, product, combinations#, combinations_with_replacement

import color_wood_sort as cws

COLONNES = range(2, 5) # range(2, 5) #11
LIGNES = [2] # [2,3] #4
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000_000
PROFILER_LE_CODE = False

def chercher_les_plateaux_et_les_solutions(colonnes, lignes):
    print(f"*** Generatrice {colonnes}x{lignes}: DEBUT")
    plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    plateau.creer_plateau_initial()
    plateau.afficher()
    lot_de_plateaux = cws.LotDePlateaux(nb_plateaux_max = MEMOIRE_MAX)
    if not lot_de_plateaux.est_deja_termine(colonnes, lignes, COLONNES_VIDES_MAX):
        # lot_de_plateaux.fixer_taille_memoire_max(5)
        plateau_courant = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
        for permutation_courante in permutations(plateau.pour_permutations):
            # Verifier que ce plateau est nouveau
            plateau_courant.plateau_ligne = permutation_courante
            if not lot_de_plateaux.est_ignore(plateau_courant):
                if lot_de_plateaux.nb_plateaux_valides % 400 == 0:
                    print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
            plateau_courant.clear()

        lot_de_plateaux.arret_des_enregistrements()
        # lot_de_plateaux.exporter_fichier_json()
        if (lot_de_plateaux.duree) < 10:
            print(f"*** Generatrice {colonnes}x{lignes}: FIN en {
                int((lot_de_plateaux.duree)*1000)} millisecondes")
        else:
            print(f"*** Generatrice {colonnes}x{lignes}: FIN en {
                int(lot_de_plateaux.duree)} secondes")
        print(f"nb_plateaux_valides={lot_de_plateaux.nb_plateaux_valides}")
        print(f"nb_plateaux_ignores={lot_de_plateaux.nb_plateaux_ignores}")
    else:
        print("Ce lot de plateaux est déjà terminé")

    print('*'*60 + ' RESOLUTION')
    for plateau_ligne_texte_a_resoudre in lot_de_plateaux.plateaux_valides:
        plateau.clear()
        plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
        resolution = cws.ResoudrePlateau(plateau)
        resolution.backtracking()
        lot_de_plateaux.definir_difficulte_plateau(plateau, resolution.solution_la_plus_courte)
        # print(f"'{plateau_ligne_texte_a_resoudre}' : nombre de solutions = {resolution.nb_solutions}, solution moyenne = {resolution.solution_moyenne}, la plus courte = {resolution.solution_la_plus_courte}, la plus longue = {resolution.solution_la_plus_longue}")
        # print(f"'{plateau_ligne_texte_a_resoudre}' : nombre de solutions = {resolution.nb_solutions}, la plus courte = {resolution.solution_la_plus_courte}")

    lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
    for difficulte, liste_plateaux in lot_de_plateaux.difficulte_plateaux.items():
        # print(f"*** Difficulté : {difficulte}")
        # print(f"{' '*5}'{liste_plateaux}'")
        print(f"*** Difficulté : {difficulte} - {len(liste_plateaux)} plateau{'x' if len(liste_plateaux) > 1 else ''}")
    print('*'*80)


def main():
    profil = cws.ProfilerLeCode('chercher_les_plateaux_et_les_solutions', PROFILER_LE_CODE)
    profil.start()
    for lignes in LIGNES:
        for colonnes in COLONNES:
            chercher_les_plateaux_et_les_solutions(colonnes, lignes)
    profil.stop()

if __name__ == "__main__":
    main()
