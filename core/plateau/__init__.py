"""
Package plateau : expose uniquement Plateau à l'extérieur,
tout en évitant les imports circulaires.
"""

# On importe d'abord les sous-modules pour casser les cycles
from . import model
from . import format
from . import ops
from . import generator
from . import validator
from . import normalize
from . import exceptions

# Maintenant que tout est chargé, on peut exposer Plateau
Plateau = model.Plateau

# Et éventuellement l'exception publique
PlateauInvalidable = exceptions.PlateauInvalidable

__all__ = ["Plateau", "PlateauInvalidable"]
