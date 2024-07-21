"""
## Library for typical workflows
Made by Annhilati
"""

from .Stochastics import binomialDF
from .Numbers import isPrime, factorial
from .Console import FancyConsole, Color, Time, log

FC = FancyConsole
C = Color
T = Time

__all__ = ["binomialDF", "isPrime", "factorial",
           "GitHub", "Webhook",
           "FancyConsole", "FC", "Color", "C", "Time", "T", "log"]



class GitHub():
    "Utility class for interactions with GitHub"
    from .GitHub import Repository
    Repository = Repository

class Discord():
    "Utility class for interactions with Discord"
    from .Discord import Webhook
    Webhook = Webhook