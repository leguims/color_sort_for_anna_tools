"Parcourt les plateaux exhaustifs et en trouve les solutions 'ColorWoordSort'"
import datetime
import time

import color_wood_sort as cws

COLONNES = range(2, 12) # [2] # range(2, 12)
LIGNES = range(2, 5) # [2] # range(2, 5)
PERIODE_SCRUTATION_SECONDES = 30*60
COLONNES_VIDES_MAX = 1
MEMOIRE_MAX = 500_000
PROFILER_LE_CODE = False


def chercher_des_solutions(colonnes, lignes):
    message = f"\n\r*** Generatrice {colonnes}x{lignes}:"
    plateau = cws.Plateau(colonnes, lignes, COLONNES_VIDES_MAX)
    plateau.creer_plateau_initial()
    # plateau.afficher()
    lot_de_plateaux = cws.LotDePlateaux(nb_plateaux_max = MEMOIRE_MAX)
    if lot_de_plateaux.est_deja_termine(colonnes, lignes, COLONNES_VIDES_MAX):
        message += " - Ce lot de plateaux est terminé"

        if lot_de_plateaux.nb_plateaux_valides != lot_de_plateaux.nb_plateaux_solutionnes:
            if lot_de_plateaux.nb_plateaux_valides < lot_de_plateaux.nb_plateaux_solutionnes:
                message += "\n\r - Il y a plus de plateaux de solutions que de plateaux valides ! Il y a un probleme !"
            message += f"\n\r - Il reste des solutions à trouver : {lot_de_plateaux.nb_plateaux_valides} != {lot_de_plateaux.nb_plateaux_solutionnes}"
            for plateau_ligne_texte_a_resoudre in lot_de_plateaux.plateaux_valides:
                plateau.clear()
                plateau.plateau_ligne_texte = plateau_ligne_texte_a_resoudre
                resolution = cws.ResoudrePlateau(plateau)
                resolution.backtracking()
                lot_de_plateaux.definir_difficulte_plateau(plateau, resolution.solution_la_plus_courte)

            lot_de_plateaux.arret_des_enregistrements_de_difficultes_plateaux()
            for difficulte, liste_plateaux in lot_de_plateaux.difficulte_plateaux.items():
                message += f"\n\r - Difficulté : {difficulte} - {len(liste_plateaux)} plateau{'x' if len(liste_plateaux) > 1 else ''}"
        else:
            message += " - Toutes les solutions sont trouvées."
    else:
        message += " - Ce lot de plateaux n'est pas encore terminé, pas de recherche de solution."
    return message

def chercher_en_boucle():
    messages = ""
    while(True):
        derniers_messages = messages
        messages = delta = ""
        for lignes in LIGNES:
            for colonnes in COLONNES:
                message = chercher_des_solutions(colonnes, lignes)
                messages += message
                if message not in derniers_messages:
                    delta += message
        if delta:
            print(delta)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"{current_time} - Attente entre 2 itérations de {PERIODE_SCRUTATION_SECONDES}s...")
        time.sleep(PERIODE_SCRUTATION_SECONDES)

def chercher():
    profil = cws.ProfilerLeCode('chercher_des_solutions', PROFILER_LE_CODE)
    profil.start()
    for lignes in LIGNES:
        for colonnes in COLONNES:
            chercher_des_solutions(colonnes, lignes)
    profil.stop()

if __name__ == "__main__":
    chercher_en_boucle()
    # chercher()
