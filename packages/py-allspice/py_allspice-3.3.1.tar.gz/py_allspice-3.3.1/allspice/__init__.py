"""
.. include:: ../README.md
   :start-line: 1
   :end-before: Installation
"""

from .allspice import (
    AllSpice,
)
from .apiobject import (
    Branch,
    Comment,
    Commit,
    Content,
    DesignReview,
    Issue,
    Milestone,
    Organization,
    Release,
    Repository,
    Team,
    User,
)
from .exceptions import AlreadyExistsException, NotFoundException

__version__ = "3.3.1"

__all__ = [
    "AllSpice",
    "User",
    "Organization",
    "Team",
    "Repository",
    "Branch",
    "NotFoundException",
    "AlreadyExistsException",
    "Issue",
    "Milestone",
    "Commit",
    "Comment",
    "Content",
    "DesignReview",
    "Release",
]
