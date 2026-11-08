import os
import json
import glob
from PIL import Image, ImageDraw, ImageFont
import matplotlib.colors as mcolors
import re

# ==========================================
# PALETTE DE COULEURS GODOT
# ==========================================
GODOT_COLORS_RAW = {
    'A': 'RED',
    'B': 'BLUEVIOLET',
    'C': 'FORESTGREEN',
    'D': 'AQUA',
    'E': 'SADDLEBROWN',
    'F': 'DEEPSKYBLUE',
    'G': 'MAGENTA',
    'H': 'TOMATO',
    'I': 'BLUE',
    'J': 'CORNFLOWERBLUE',
    'K': 'VIOLET',
    'L': 'TEAL',
    'M': 'SLATEGRAY',
    'N': 'SANDYBROWN',
    'O': 'DARKGRAY',
    'P': 'BLACK',
    'Q': 'CHARTREUSE',
    'R': 'CRIMSON',
    'S': 'DARKGREEN',
    'T': 'DARKORANGE',
    'U': 'DEEPPINK',
    'V': 'HOTPINK',
    'W': 'MAROON',
    'X': 'MEDIUMSLATEBLUE',
    'Y': 'TURQUOISE',
    'Z': 'SPRINGGREEN',
}

def godot_to_rgb(color_name):
    """Convertit un nom de couleur Godot en tuple (R, G, B)."""
    try:
        hex_val = mcolors.to_hex(color_name.lower())
        return mcolors.to_rgb(hex_val)
    except Exception:
        return (128, 128, 128)

COLOR_MAP = {}
for jeton, cname in GODOT_COLORS_RAW.items():
    r, g, b = godot_to_rgb(cname)
    COLOR_MAP[jeton] = (int(r * 255), int(g * 255), int(b * 255))

COLOR_ESPACE_BG = (220, 210, 230)

# ==========================================
# FONCTION DE DESSIN D'UN PLATEAU
# ==========================================
def dessiner_plateau_img(nom_plateau, cell_size=18):
    """
    Parse la chaîne du plateau (séparée par des '.') et génère une image PIL du plateau.
    La hauteur du quadrillage s'adapte STRICTEMENT à la pile la plus haute du plateau.
    """
    piles_raw = nom_plateau.split('.')
    piles = [p.rstrip(' ') for p in piles_raw]
    
    nb_piles = len(piles)
    hauteur_max = max(len(p) for p in piles) if piles else 1

    img_w = nb_piles * cell_size + (nb_piles + 1) * 3
    img_h = hauteur_max * cell_size + (hauteur_max + 1) * 3

    img = Image.new("RGBA", (img_w, img_h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    font = charger_font_emoji(int(cell_size * 0.65))

    for col_idx, pile in enumerate(piles):
        x = 3 + col_idx * (cell_size + 3)
        
        # 1. Fond de la colonne (hauteur stricte du plateau)
        for row_idx in range(hauteur_max):
            y = img_h - 3 - (row_idx + 1) * (cell_size + 3)
            draw.rectangle([x, y, x + cell_size, y + cell_size], fill=COLOR_ESPACE_BG, outline=(170, 150, 190), width=1)

        # 2. Dessin des jetons (de bas en haut)
        for row_idx, char in enumerate(pile):
            y = img_h - 3 - (row_idx + 1) * (cell_size + 3)
            
            if char in COLOR_MAP:
                bg_color = COLOR_MAP[char]
                draw.rectangle([x, y, x + cell_size, y + cell_size], fill=bg_color, outline=(255, 255, 255), width=1)
                
                luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]) / 255
                text_color = (0, 0, 0) if luminance > 0.6 else (255, 255, 255)
                
                bbox = font.getbbox(char)
                w_txt = bbox[2] - bbox[0]
                tx = x + (cell_size - w_txt) / 2
                ty = y + (cell_size - (bbox[3] - bbox[1])) / 2 - bbox[1]
                draw.text((tx, ty), char, fill=text_color, font=font)

    return img

def extraire_numero_niveau(nom_niveau):
    """Extrait intelligemment le numéro d'un niveau pour un tri naturel."""
    match = re.search(r'\d+', nom_niveau)
    return int(match.group()) if match else 0

# ==========================================
# GENERATION DE L'INFOGRAPHIE GLOBALE
# ==========================================
def charger_font_emoji(size : int):
    # Tentative de chargement d'une police supportant les emojis
    try:
        # Sous Windows (Segoe UI Emoji)
        font_emoji = ImageFont.truetype("seguiemj.ttf", size)
    except Exception:
        try:
            # Sous Linux/macOS (Apple Color Emoji ou Noto Color Emoji)
            font_emoji = ImageFont.truetype("NotoColorEmoji.ttf", size)
        except Exception:
            font_emoji = ImageFont.load_default(size) # Repli sur la police standard si aucune police emoji n'est trouvée
    return font_emoji


def generer_infographie():
    fichiers = glob.glob("Synthese_*.json")
    if not fichiers:
        if os.path.exists("Synthese.json"):
            fichier_json = "Synthese.json"
        else:
            print("❌ Aucun fichier Synthese_*.json ou Synthese.json trouvé.")
            return
    else:
        fichier_json = fichiers[0]

    print(f"📖 Lecture du fichier : {fichier_json}")
    with open(fichier_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    campagne_info = data.get("campagne", {})
    nom_campagne = campagne_info.get("campagne", "Campagne Inconnue")
    niveaux = campagne_info.get("niveaux", [])

    # Tri des niveaux de manière croissante (niveau_1, niveau_2, ..., niveau_10)
    niveaux_tries = sorted(niveaux, key=lambda n: extraire_numero_niveau(n.get("niveau", "")))

    liste_plateaux = []
    for niv in niveaux_tries:
        nom_niv = niv.get("niveau", "Niveau Inconnu")
        for plat in niv.get("plateaux", []):
            liste_plateaux.append((nom_niv, plat))

    if not liste_plateaux:
        print("❌ Aucun plateau trouvé dans le fichier JSON.")
        return

    # Configuration de la grille
    cards_per_row = 3
    card_w = 420
    card_h = 335
    padding = 20
    header_h = 70

    nb_plateaux = len(liste_plateaux)
    nb_rows = (nb_plateaux + cards_per_row - 1) // cards_per_row

    total_w = padding + cards_per_row * (card_w + padding)
    total_h = header_h + padding + nb_rows * (card_h + padding)

    canvas = Image.new("RGB", (total_w, total_h), (245, 247, 250))
    draw = ImageDraw.Draw(canvas)

    font_title = charger_font_emoji(26)
    font_sub = charger_font_emoji(15)
    font_bold = charger_font_emoji(13)
    font_norm = charger_font_emoji(12)
    font_small = charger_font_emoji(10)
    font_tiny = charger_font_emoji(10)

    # En-tête principal
    draw.rectangle([0, 0, total_w, header_h], fill=(30, 41, 59))
    draw.text((padding, 15), f"INFOGRAPHIE DE SYNTHÈSE", fill=(255, 255, 255), font=font_title)
    draw.text((padding, 45), f"Campagne : {nom_campagne}", fill=(203, 213, 225), font=font_sub)

    # Rendu des cartes de chaque plateau
    for idx, (nom_niv, plat) in enumerate(liste_plateaux):
        row = idx // cards_per_row
        col = idx % cards_per_row

        x_card = padding + col * (card_w + padding)
        y_card = header_h + padding + row * (card_h + padding)

        # Carte individuelle
        draw.rectangle([x_card, y_card, x_card + card_w, y_card + card_h], fill=(255, 255, 255), outline=(226, 232, 240), width=2)
        draw.rectangle([x_card, y_card, x_card + card_w, y_card + 32], fill=(241, 245, 249))
        draw.text((x_card + 10, y_card + 7), f"{nom_niv.upper()}", fill=(71, 85, 105), font=font_bold)
        
        gameplay = plat.get("gameplay", "")
        diff = plat.get("difficulte", "")
        
        # Affichage décalé pour "Diff" et le "Gameplay"
        txt_diff = f"Diff: {diff}"
        draw.text((x_card + 140, y_card + 7), txt_diff, fill=(100, 116, 139), font=font_norm)
        
        txt_gameplay = f"{gameplay}"
        draw.text((x_card + 235, y_card + 7), txt_gameplay, fill=(100, 116, 139), font=font_norm)

        # Affichage du nom plateau exact
        nom_plat = plat.get("nom", "")
        draw.text((x_card + 10, y_card + 36), f"Nom plateau : {nom_plat}", fill=(120, 53, 15), font=font_small)

        # Rendu visuel strict du plateau
        img_plat = dessiner_plateau_img(nom_plat, cell_size=18)
        
        px = x_card + 10
        py = y_card + 52
        canvas.paste(img_plat, (px, py), img_plat)

        # Statistiques de durées (Min, Médiane, Moyenne, Max)
        sx = x_card + img_plat.width + 18
        sy = y_card + 52
        
        duree_info = plat.get("duree", {})
        d_min = duree_info.get("min", "-")
        d_med = duree_info.get("mediane", "-")
        d_moy = duree_info.get("moyenne", "-")
        d_max = duree_info.get("max", "-")

        draw.text((sx, sy), "Temps :", fill=(30, 41, 59), font=font_bold)
        draw.text((sx, sy + 16), f"Min: {d_min}s | Méd: {d_med}s", fill=(71, 85, 105), font=font_norm)
        draw.text((sx, sy + 32), f"Moy: {d_moy}s | Max: {d_max}s", fill=(71, 85, 105), font=font_norm)

        # 1. Top 3 (trié par temps croissant)
        sy_top = sy + 54
        draw.text((sx, sy_top), "Top 3 :", fill=(30, 41, 59), font=font_bold)

        cles_exclues = {"difficulte", "gameplay", "nom", "duree", "statut"}
        joueurs_durees = []
        for k, v in plat.items():
            if k not in cles_exclues and isinstance(v, (int, float)):
                joueurs_durees.append((k, v))

        joueurs_par_temps = sorted(joueurs_durees, key=lambda x: x[1])
        top_3 = joueurs_par_temps[:3]

        if not top_3:
            draw.text((sx, sy_top + 18), "Aucun résultat enregistré", fill=(148, 163, 184), font=font_norm)
        else:
            rungs = ["1er", "2e", "3e"]
            for rank_idx, (j_nom, j_temps) in enumerate(top_3):
                txt_rank = f"{rungs[rank_idx]} : {j_nom} ({j_temps:.1f}s)"
                draw.text((sx, sy_top + 18 + rank_idx * 15), txt_rank, fill=(51, 65, 85), font=font_norm)

        # 2. Liste complète des participants (triée par ordre alphabétique)
        sy_all = sy_top + 18 + 3 * 15 + 6
        draw.text((sx, sy_all), "Participants :", fill=(30, 41, 59), font=font_bold)

        joueurs_alpha = sorted(joueurs_durees, key=lambda x: x[0].lower())
        
        if not joueurs_alpha:
            draw.text((sx, sy_all + 16), "Aucun participant", fill=(148, 163, 184), font=font_tiny)
        else:
            liste_str = ", ".join([f"{j[0]} ({j[1]:.1f}s)" for j in joueurs_alpha])
            
            max_chars_ligne = 38
            mots = liste_str.split(", ")
            ligne_courante = ""
            ligne_y = sy_all + 16
            
            for mot in mots:
                test_ligne = f"{ligne_courante}, {mot}" if ligne_courante else mot
                if len(test_ligne) <= max_chars_ligne:
                    ligne_courante = test_ligne
                else:
                    draw.text((sx, ligne_y), ligne_courante, fill=(100, 116, 139), font=font_tiny)
                    ligne_y += 13
                    ligne_courante = mot
            if ligne_courante:
                draw.text((sx, ligne_y), ligne_courante, fill=(100, 116, 139), font=font_tiny)

    # Nom du fichier de sortie avec le préfixe "rtc_" demandé
    nom_sortie = f"rtc_Infographie_{nom_campagne}.png"
    
    try:
        canvas.save(nom_sortie)
        print(f"\n✨ Infographie générée avec succès : {nom_sortie}")
    except PermissionError:
        print(f"\n❌ Erreur : Impossible d'enregistrer le fichier '{nom_sortie}'.")
        print("💡 Le fichier est probablement ouvert dans une visionneuse d'images. Veuillez le fermer et relancer le script.")
    except Exception as e:
        print(f"\n❌ Erreur lors de l'enregistrement : {e}")

if __name__ == "__main__":
    generer_infographie()