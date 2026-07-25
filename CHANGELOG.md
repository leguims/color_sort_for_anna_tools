# Liste des fonctionnalités


## V0.4.0

### Outillage
- Decomposer les outils pour réaliser un forkflow (pipeline)

#### Refactoring
- Structurer tout le dépot pour réorganiser les sources, les outils et les tests
    - arbrescence : core, io_utils, tests et pipeline
- Améliorer le code pour simplifier la maintenance:
    - creer des modules
    - faire une API
    - realiser des methodes deporter dans des ficheirs à theme
    - Réalisé pour : plateau.py, lot_de_plateaux.py et resoudre.py

#### Difficulté de plateau
- Dans la recherche de solution, réorganiser pour conserver:
  - La quantité de blocage pour chaque longueur
- Baser la difficulté le rapport : Nb Blocage / (Nb Blocage + Nb Solutionsd)
- Difficulté entre 0 et 100 (le plus difficile)

## V0.3.6 :Travaux réalisés

### Outillage
- Rendre parametrable depuis les scripts "outil_*" les chemins vers "Analyses" et "Solutions"

#### Revalidation
- Similarité : Difflib : inclus dans python Réalisé avec Rapidfuzz

#### Difficulté de plateau
- Dans la recherche de solution, réorganiser pour conserver:
  - La solution la plus courte (1 seule)
  - La quantité de solution pour chaque longueur
- Baser la difficulté sur le nombre d'alternatives (les occasions de faire une erreur) de la solution
  - noter avec la solution le nombre de coups possibles à chaque étapes.
  - une étape sans alternative est inintéressante.
  - Définir la difficulté:
    - Parcourir la solution la plus courte
    - À chaque coup, identifier s'il y a plusieurs coups jouables.
    - Difficulté = multiplier les coups legaux à chaque étape. Comme ça "1 coup" est neutre sur le score final.
- Ajouter un "outil_divers" pour mettre au nouveau format les solutions déjà trouvées

#### Deploiement de versions
- changement de version : les nouveaux tableaux et les anciens tableaux sont en collision.
- définir le modèle de mise à jour : tout à zéro, on poursuit en cumulé, on poursuit en perdant l'ancien => à définir pour chaque version
- Sauvegarder le numéro de version dans la sauvegarde et l'utiliser lors du lancement d'une nouvelle version pour réaliser tous les travaux de mise à jour de changement de version nécessaire.
- enregistrer la liste des nom de plateaux achevés => dans les statistiques du joueur

## V0.3.1 : Travaux réalisés

### Outillage

#### Revalidation
- Revalidation Phase 2 : il faut décomposer en plusieurs phases, car en 8x3, après 90 minutes, il est toujours bloqué dans la première sous boucle.
	- Vérifier à chaque étape de revalidation que le fichier est enregistré
	- Comparer le resultat avec l'ancien algo
- À chaque itération, repartir sur la nouvelle base et ne pas vérifier les plateaux effacés précedemment

#### Accélération de recherche
- Ajouter un champs "Dernier plateau recherche" pour reprendre la recherche de plateau plus efficacement.

## V0.3.0 : Travaux réalisés

### Outillage
- outils : utiliser le module "logging" pour tracer l'avancement des threads dans leur tâches.
	- traces Plateau : utiliser le module "logging" pour tracer l'avancement dans la classe.
	- traces LotDePlateaux : utiliser le module "logging" pour tracer l'avancement dans la classe.
	- traces ResoudrePlateau : utiliser le module "logging" pour tracer l'avancement dans la classe.
	- traces ExportJSON : utiliser le module "logging" pour tracer l'avancement dans la classe.
- Enregistrer le format "plateau_ligne_texte_universel" dans tous les JSON.
- Vérifier sur un petit plateau (ex: 3x6) :
	- le parcours des combinaisons
	- l'arrêt du parcours
	- la reprise

#### Revalidation
- Réaliser un script d'élagage des plateaux valides.
	- 'ABC.CBA' ==(A devient B)== 'BAC.CAB'
	- Etat des lieux :
		- "ABA.CBA.CBC.   " : filtré
		- "ACA.ACB.BCB.   " : conservé
		- "BAB.CAB.CAC.   " : filtré
		- "BAB.BAC.CAC.   " : filtré
		- "ABA.ABC.CBC.   " : filtré
		- "ACA.BCA.BCB.   " : filtré
		- Pour filtrer ce doublon, il faut appliquer les permutations de jetons à chaque permutations de piles.
- 'classer_les_solutions.py' Réaliser un script d'élagage des solutions quand un plateau de départ a déjà une colonne de résolue.
- 'chercheur_de_plateaux.py' Ne pas considérer les plateaux avec une pile déjà résolue.

#### Accélération de recherche
- Rénovation et Accélération des recherches:
	- Dans les analyses JSON 'Analyses\Plateaux_*\Plateaux_*.json:
		- Supprimer les champs 'debut' + 'fin' + 'durée'
		- Ajouter un champs 'revalidation phase 1 terminee'
		- Ajouter un champs 'revalidation phase 2 terminee'
		- Ajouter un mecanisme de classement systématique des listes de plateaux avant de produire le JSON.
		- Ajouter un champs 'dernier plateau revalide' pour reprise de validation.
		- Modifier l'algorithme de reprise de recherche de plateau : boucler et itérer tant que toutes les solutions connues ne sont pas identifiées.
	- Dans 'chercheur_de_plateaux.py', filtrer uniquement les plateaux valides et les plateaux avec un pile résolue.
	- Dans 'revalider_les_plateaux.py', appliquer l'ensemble des filtre, dont ceux qui sont long (permutations de piles ou de jetons).
	- Avec la simplification de la recherche, les compteurs de changements deviennent inutiles. (compter_plateau_a_ignorer)
	- (recherche) Pour la recherche de plateaux, voir si la reprise directement sur le dernier plateau trouvé permet de gagner du temps dans les itérations. Mais dans ce cas, il faut etre capable de s'arreter quand le tour du compteur est réalisé. C'est à dire que la permutation 'plateau.pour_permutations' apparait.
- Itération LotDePlateaux : Idée d'optimisation : Lors de la recherche, avant de tester la validité, passer toutes les itérations avec la première colonne pleine de 'A'.
- LotDePlateaux : Idée d'optimisation : Réaliser cette optimisation sur la dernière colonne avec la case vide ' '
- Itération LotDePlateaux : Idée d'optimisation : Après étude, lorsque la premiere colonne est vidée de ses 'A', ils ne reviendront plus, c'est la fin de l'itération.
- Itération LotDePlateaux : Idée d'optimisation : Trouver la premiere permutation valide proposée par l'outil de permutation et en extraire une regle 'Colonnes x Lignes'
- Itération LotDePlateaux : Idée d'optimisation : Implémenter ce départ et évaluer le gain. "2x6" passe de 10mins à 5mins.
- Itération LotDePlateaux : Idée d'optimisation : Trouver la 1ere permutation valide devrait dispenser de faire les combinaisons avec la colonne 'A' pleine.
- Itération LotDePlateaux : Idée d'optimisation : Lors de la recherche, avant de tester la validité, passer toutes les itérations sans 'A' dans la première colonne.
- Ajouter un champs "Dernier plateau a valider" pour reprendre la recherche de plateau plus efficacement.

#### Difficulté de plateau
- Définir le niveau de difficulté d'un plateau selon les critères suivants :
	- longueur solution et nombre de jetons sur le plateau (exhaustif)
		- SurfacePlateau = NombreDePiles x NombreDeJetonParPile du plateau effectif
		- SurfacePlateauMax = NombreDePilesMax x NombreDeJetonParPileMax (11x3 = max actuel; 12x12 = max théroique à court terme)
		- ProfondeurSolution = Nombre de mouvements pour la solution
		- Difficulté = Entier de ( ProfondeurSolution x SurfacePlateauMax / SurfacePlateau)

## V0.2 : Travaux réalisés
- outillage : produire un JSON des plateaux par niveau.
- outillage : réécrire les plateaux avec les "." pour identifier les "colonnes x lignes" et mélanger les plateaux de forme différentes
- outillage : construire un JSON selon une configuration qui indique le nombre de tableau de chaque niveau.

### Bug V0.2 :
- l'algorithme de difficulté est mauvais pour un plateau 3x5 qui est surclassé ! ("AABAA.A    .BBBB " 3x5 en X coups = difficulté 28) bien plus facile que ("BCA.CDB.CDA.BDA.   " 5x3 en X coups = 10) Abandon (c'est la cohabitation de l'ancienne échelle de difficulté de 1 à 10 qui cause cette discontinuité.)
