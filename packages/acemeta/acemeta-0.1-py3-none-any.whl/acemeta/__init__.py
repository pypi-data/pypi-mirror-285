"""
## Library for typical workflows
"""

from .Stochastics import binomialDF
from .Numbers import isPrime, factorial

__all__ = ["binomialDF", "isPrime", "factorial",
           "GitHub", "Webhook"]



class GitHub():
    "Utility class for interactions with GitHub"
    from .GitHub import Repository

    Repository = Repository

class Discord():
    "Utility class for interactions with Discord"
    from .Discord import Webhook

    Webhook = Webhook