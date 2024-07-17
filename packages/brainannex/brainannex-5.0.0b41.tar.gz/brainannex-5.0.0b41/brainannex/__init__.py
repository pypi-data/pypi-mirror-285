"""
    BrainAnnex
    ~~~~~~~~~~

    Full-Stack Data/Knowledge Management with Neo4j

	https://BrainAnnex.org

    :copyright: (c) 2015-2024 by Julian West and the BrainAnnex project.
    :license: MIT, see LICENSE for more details.
"""

__version__ = "5.0.0-beta.41"


from brainannex.neo_schema.neo_schema import NeoSchema
from brainannex.data_manager import DataManager
from brainannex.user_manager import UserManager
from brainannex.categories import Categories
from brainannex.collections import Collections


__all__ = [
    'NeoSchema',
    'DataManager',
    'UserManager',
    'Categories',
    'Collections',
    'version'
]


def version():
    return __version__
