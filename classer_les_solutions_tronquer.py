"""Découpe l'ensemble des solutions inter-plateaux en des ensembles plus petits de solutions
Adapté pour avoir un fichier de solutions restreint pour le jeu"""
import datetime
import time

import color_wood_sort as cws

# Filtrer les plateaux à 2 lignes ou 2 colonnes qui sont trop triviaux et repetitifs.
PERIODE_SCRUTATION_SECONDES = 30*60
PROFILER_LE_CODE = False

TAILLE = 10

def tronquer_les_solutions(taille = TAILLE, decallage = 0):
    message = f"\n\r*** Tronquer le classement des Solutions :"

    solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export='Solutions_classees', repertoire='Solutions')
    solutions_classees = solutions_classees_json.importer()
    solutions_classees_tronquees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=f'Solutions_classees_T{taille}_D{decallage}', repertoire='Solutions')

    if "liste difficulte des plateaux" in solutions_classees:
        dict_difficulte = solutions_classees["liste difficulte des plateaux"]
        # Filtrer les plateaux sans solutions ou trop triviaux
        for difficulte, liste_plateaux in dict_difficulte.items():
            dict_difficulte[difficulte] = liste_plateaux[decallage:decallage+taille]
        solutions_classees_tronquees_json.forcer_export(solutions_classees)
    return message

def afficher_synthese(taille = TAILLE, decallage = 0):
    message = f"\n\r*** Synthèse des Solutions:"
    solutions_classees_json = cws.ExportJSON(delai=60, longueur=100, nom_plateau='', nom_export=f'Solutions_classees_T{taille}_D{decallage}', repertoire='Solutions')
    solutions_classees = solutions_classees_json.importer()

    somme_plateaux = 0
    for difficulte, liste_plateaux in solutions_classees.get('liste difficulte des plateaux').items():
        print(f" - Difficulté : {difficulte} - {len(liste_plateaux)} plateau{pluriel(liste_plateaux, 'x')}")
        if difficulte != 'None':
            somme_plateaux += len(liste_plateaux)
    print(f" - Total : {somme_plateaux} plateau{pluriel(liste_plateaux, 'x')} valide{pluriel(liste_plateaux, 's')}")

def pluriel(LIGNES, lettre='s'):
    return lettre if len(LIGNES) > 1 else ""

def chercher_en_boucle():
    messages = ""
    while(True):
        derniers_messages = messages
        messages = delta = ""
        message = tronquer_les_solutions()
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

    for i in range(10):
        # Effacer l'existant
        #solutions_classees_json = cws.ExportJSON(0, 0, '', nom_export=f'Solutions_classees_T{TAILLE}_D{i * TAILLE}', repertoire='Solutions')
        solutions_classees_json = cws.ExportJSON(0, 0, '', nom_export=f'Solutions_classees_T{(i+1)*TAILLE}_D{0}', repertoire='Solutions')
        solutions_classees_json.effacer()
        
        messages = ""
        #message = tronquer_les_solutions(TAILLE, i * TAILLE)
        message = tronquer_les_solutions((i+1) * TAILLE, 0)
        messages += message
        profil.stop()
        print(messages)

        afficher_synthese()

if __name__ == "__main__":
    # chercher_en_boucle()
    chercher()
