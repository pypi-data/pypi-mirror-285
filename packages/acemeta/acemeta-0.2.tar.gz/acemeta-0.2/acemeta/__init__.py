"""
## Library for typical workflows
Made by Annhilati
"""

from .Stochastics import binomialDF
from .Numbers import isPrime, factorial
from .Console import FancyConsole, Color

FC = FancyConsole
C = Color

__all__ = ["binomialDF", "isPrime", "factorial",
           "GitHub", "Webhook",
           "FancyConsole", "FC", "Color", "C"]



class GitHub():
    "Utility class for interactions with GitHub"
    from .GitHub import Repository
    Repository = Repository

class Discord():
    "Utility class for interactions with Discord"
    from .Discord import Webhook
    Webhook = Webhook