"""
Package resolution : expose uniquement ResoudrePlateau à l'extérieur,
tout en évitant les imports circulaires.
"""

# On importe d'abord les sous-modules pour casser les cycles
from . import model
# from . import choix
from . import heuristics
from . import io
from . import resolution
from . import validation


# Maintenant que tout est chargé, on peut exposer ResoudrePlateau
ResoudrePlateau = model.ResoudrePlateau

__all__ = ["ResoudrePlateau"]
