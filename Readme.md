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

Le versionnage est donné par rapport aux versions sorties du jeu. C'est une simplification de gestion au dépend de l'enrichissement fonctionnel de l'outil qui en est indépendant.

## Branches

### recherche_par_parent

La variation avec la branche _main_ se situe au niveau de la recherche de plateaux. Pour accelérer la découverte de plateaux, la recherche est exhaustive pour les plateaux 'Yx2' (Y colonnes et 2 lignes). Par contre, la recherche de niveau suivante s'appuie sur la liste des plateaux du parent. Cela permet de gagner du temps même si une masse importante de plateaux valide sont ignorés.
- 2x2 => 2x3 => 2x4 => ... => 2x11
- ...
- 11x2 => 11x3 => 11x4 => ... => 11x11

Ci-dessus :
- 2x2 est exhaustif et 2x3 à 2x11 enrichit la liste des plateaux de son parent.
- 11x2 est exhaustif et 11x3 à 11x11 enrichit la liste des plateaux de son parent.

### ancien_algo, future_1, future_2, future_3, future_4, future_5

Branche de diagnostic de performance de la recherche de plateaux selon les filtres appliqués. A la découverte d'un plateau, faut-il ignorer tous ses doublons ou les ajouter dans une liste pour ne pas les étudier plus tard ? Le temps de productions des doublons est conséquent et l'argent en vaut-il la chandelle.

|  | Passé (ancien_algo) | Présent (main) | future_1 | future_2 | future_3 | future_4 | future_5 |
|-|-|-|-|-|-|-|-|
| Algo | permutation | product | product Sans ‘ignoré’ | product perm_pile (1) perm_jeton (2) Perm_jeton_pile (3) | product perm_pile (1) perm_jeton (2) | product perm_pile (1) | product Perm_jeton (2) |
| __Plateau__ | __3x5__ |
| Durée | 1800 s | __312 s__ | __364 s__ | _378 s_ | 373 s | __367 s__ | 368 s |
| Gain | 100 % | __477 %__ | __394 %__ | 375 % | 382 % | __390 %__ | 389 % |
| __Plateau__ | __4x3__ |
| Durée | 1800 s | __287 s__ | __363 s__ | _374 s_ | 374 s | __353 s__ | 365 s |
| Gain | 100 % | __525 %__ | __396 %__ | 380 % | 380 % | __409 %__ | 393 % |
|   |   | __TOP 1__ | __TOP 3__ |  |  | __TOP 2__ |  |
| Espace disque total Ko | __208__ | 3900 | 3900 | __1500__ | 1800 | __1700__ | 2300 |
|   | __TOP 1__ |  |  | __TOP 2__ |  | __TOP 3__ |  |
| Synthèse |   |   |  |   |   | __TOP 1__ |  |



C'est le compromis de la branche __future_4__ qui a été retenue pour la suite.

## V0.4.5 : Travaux pour la prochaine version

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
- Dans l'export des plateaux vers GODOT, associer le mode de jeu avec le plateau.
- Appliquer un décalage dans l'alphabet d'un plateau pour chaque jeton lors de l'exportation godot.

#### Divers
- pour les plateaux sans solution, lancer une recherche en ajoutant 1 colonne d'une seule ligne OU 1 case vide sur la derniere colonne.
- classer_les_solutions_tronquer.py : produire un UUID dans le fichier des solutions.
- classer_les_solutions_tronquer.py : Ajouter des filtres lors de la selection des plateaux:
	- nombre de colonnes min/max
	- nombre de lignes min/max
	- nombre de coups de la solution min/max

## V1.0 : Travaux long terme

### Minage des grands plateaux

J'ai depuis le début eu à coeur de choisir mes plateaux parmi une population exhaustive. Mais la recherche de plateaux devient longue avec la taille des plateaux. Le nombre de plateaux trouvés, puis filtrés, puis résolus devient immense. Un première optimisation a été réalisée avec la recherche par parent (voir le chapitre sur la branche 'recherche_par_parent') pour limiter la recherche brute.

Après avoir vu des vidéos de 'Code BH' qui mettent en oeuvre des scenarii d'evolutions et de deep learning. Je me demande si cette stratégie ne serait pas l'étape suivante de minage pour trouver les plateaux interessant à long terme et de large taille.

Pour ce faire, il faudrait définir:
- Les parents initiaux : les plateaux initiaux de toutes les tailles : 5x5 à 10x10
- la physique de recherche et d'évolution : quel changement à chaque génération
  - Deplacement de jetons du le plateau parent.
  - Plateau valide
- les critères de score d'un plateau : indicateurs de résolution
  - Nombres de solutions
  - Nombre d'echecs
  - differentes longueurs de solutions/echecs

### Export GODOT de la campagne

Lors de l'export des solutions classées vers GODOT, associer des elements de jeu à chaque plateau:
- Plateau : Texte universel du plateau
- Difficulté : Taux d'echec du plateau
- Type de jeu : Classique, Memoire, Défi, Qui Perd Gagne, Double Face
- [Memoire] [Défi] Nombre de coups cible
- [Double Face] Difficulté Face 1 et 2

Le fichier d'export des plateaux devient directement la partition de la campagne.