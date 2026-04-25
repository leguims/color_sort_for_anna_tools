"""
Package lot_de_plateaux : expose uniquement LotDePlateaux
tout en évitant les imports circulaires.
"""

# Phase 1 : charger les sous-modules
from . import model
from . import io
from . import filter
from . import generator
from . import level

# Phase 2 : exposer uniquement la classe publique
LotDePlateaux = model.LotDePlateaux

__all__ = ["LotDePlateaux"]
