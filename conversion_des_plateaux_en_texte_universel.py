"Module pour convertir tous les JSON existants en 'texte_universel'"
import color_wood_sort as cws

COLONNES = range(2, 12) #[2] # range(2, 5) # range(2, 5) #11
LIGNES = range(2, 14) #[3] # [2,3] #4
COLONNES_VIDES_MAX = 1
PROFILER_LE_CODE = False

def conversion_des_plateaux_en_texte_universel(colonnes, lignes):
    print(f"{' '*colonnes}[{colonnes}x{lignes}] DEBUT - Revalider les plateaux")
    lot_de_plateaux = cws.LotDePlateaux((colonnes, lignes, COLONNES_VIDES_MAX))
    lot_de_plateaux.est_deja_termine()

    # Forcer la réécriture du JSON pour mettre à jour le format universel
    lot_de_plateaux._a_change = True
    lot_de_plateaux.exporter_fichier_json()

def chercher_en_sequence():
    for lignes in LIGNES:
        for colonnes in COLONNES:
            conversion_des_plateaux_en_texte_universel(colonnes, lignes)

def chercher_en_parallele():
    profil = cws.ProfilerLeCode('conversion_des_plateaux_en_texte_universel', PROFILER_LE_CODE)
    profil.start()

    taches = cws.CreerLesTaches(nom="conversion_des_plateaux_en_texte_universel", nb_colonnes=7, nb_lignes=3)
    # taches.exporter()
    taches.importer()
    taches.executer_taches(conversion_des_plateaux_en_texte_universel)

    profil.stop()

if __name__ == "__main__":
    #chercher_en_parallele()
    chercher_en_sequence()