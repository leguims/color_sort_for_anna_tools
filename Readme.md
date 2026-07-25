Outils de productions et de résolution des plateaux du jeu [Range Les Couleurs Pour Anna d'Amour](https://github.com/leguims/godot-color-sort-for-anna)

# Structure

## Archives

Outils pour enregistrer les plateaux trouvés, analysés et classés.

## Core

Bibliothèque d'implementations des objets de base du projet : plateau, lot de plateau et résolution de plateau.

## io_utils

Ensemble d'outils mineurs transverses pour l'enregistrement de fichiers, la conversions de format durant la vie du projet, de mesure de temps, de profilage.

## pipeline

Scripts pour ordonanncer le flux des travaux en exploitant la bibliothèque "core".

# Flux de travaux (pipeline et workflow)

Les outils sont découpés est différents roles et en différentes phases de travail à réaliser. Le but étant d'identifier l'ensemble des plateaux de jeu possibles, des les filtrer pour limiter les doublons et d'en déterminer le niveau de difficulté. En dernières étape, des travaux d'ajustement de format et de filtrage son réalisés pour le jeu implémenté sur GODOT.

## Chercher des plateaux

Phase durant laquel l'ensemble exhaustif des plateaux sont recherchés pour une taille de plateau définit par son nombre de colonnes et des lignes.

## Filtrer les plateaux invalides ou ininteressants

Phase durant laquelle les plateaux en doublons ou inintéressants (une colonne déjà rangée) sont supprimés.

## Filtrer les doublons de permutations de jetons

Phase durant laquelle les plateaux identiques pour un humain sont supprimés. Pour la machine, un plateau avec un motif identique, mais des couleurs de jetons différents ne sont pas le même plateau. Pour le joueur, c'est un plateau identique.

## Filtrer les doublons de permutations de piles

Phase durant laquelle les plateaux identiques pour un humain sont supprimés. Pour la machine, des plateaux dont les colonnes sont interverties sont différents, mais pas pour l'humain.

## Filtrer les doublons de permutations de jetons de piles

Phase durant laquelle les plateaux identiques pour un humain sont supprimés. C'est le cas combinésde changement de couleurs et de piles.

## Chercher des solutions

Phase de recherche de toutes les solutions possibles d'un plateau. À partir de ces résultats, la difficulté du plateau est identifiée en fonction de son rapport entre son nombre de parties perdantes et gagnantes.

## Filtrer les solutions pour le jeu

Phase de filtrage selon l'interet des plateaux. Un plateau sans solution ou avec une profondeur de coup trop courte est supprimé.

## Export pour le jeu

Formatage du fichier des plateaux pour être exploitable par le jeu GODOT.

## Tronquer les solutions pour le jeu

Réduction arbitraire du fichier pour le jeu pour limiter le nombre de plateaux jouable dans le jeu. Si la banque de plateaux est de 1.000.000.000 plateaux, une vie de suffit pas à les résourdre. La liste de plateau dans le jeu sera de 200 plateaux pour que la campagne soit accessible et achevable.

# Versions

## V0.4.4 : Travaux pour la prochaine version

### Outillage

#### Recherche de plateaux
- Ajouter un "outil_divers" pour reset les parametres de recherche de plateaux
- Faire un itérateur qui s'appuie sur le plateau de plus petite taille:
  - Yx2 => Yx3 => Yx4 ... YxZ
  - Yx2 est produit classiquement, sans filtrage, sans optimisation
  - Yx3 parcourt tous les plateaux Yx2 valides et ajoutes toutes les combinaisons de la dernière rangée.
  - La liste des plateaux valides ainsi obtenus n'est pas exhaustives, mais le calcul est accéléré.

#### Revalidation
- Ajouter un "outil_divers" pour reset les parametres de revalidation des plateaux
- Similarité : Pour réduire les similarité : Rapidfuzz + seuil à ajuster (75% et plus). Voir s'il faut l'appliquer sur le fichier complet de solutions. Application sur "revalidation" = gain de temps + application sur "Solutions" pour gain de plaisir de jeu.

#### Etape 5 : Tronquer les solutions => Exporter solution vers GODOT
- Dans l'étape 5 (tronquer), ajouter un suffixe au plateau pour indiquer qu'il y a différentes longueurs de solutions.
- Dans le jeu, à l'affichage du plateau, faire apparaître "Défi 6 coups" car 6 est le nombre de coups minimum (dans cet exemple).
- Lors du calcul de score, ajouter un score spécifique sur la longueur.
  - Longueur max = 0 points.
  - Longueur min = max points
  - et un pourcentage entre les deux.
- Les infos de solutions sont séparées par un caractère spécial. Je propose le suffixe suivant:
  - "|MIN:6|MAX:7"
  - Solution la plus courte en 6 coups.
  - Solution la plus longue en 7 coups.
- Renommer l'étape 5. Ce n'est pas tronquer les solutions, c'est produire le fichier de solutions au format du jeu godot. Tronquer, ajouter infos plateau et autres. "Étape 5 = Exporter solution vers godot"

#### Divers
- pour les plateaux sans solution, lancer une recherche en ajoutant 1 colonne d'une seule ligne OU 1 case vide sur la derniere colonne.
- classer_les_solutions_tronquer.py : produire un UUID dans le fichier des solutions.
- classer_les_solutions_tronquer.py : Ajouter des filtres lors de la selection des plateaux:
	- nombre de colonnes min/max
	- nombre de lignes min/max
	- nombre de coups de la solution min/max
