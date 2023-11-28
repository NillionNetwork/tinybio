"""
Minimal pure-Python library that implements a basic version of a
secure decentralized biometric authentication functionality via
a secure multi-party computation protocol.
"""
from __future__ import annotations
import doctest
import tinynmc

class node(tinynmc.node):
    """
    Data structure for maintaining the information associated with a node
    and performing node operations.
    """
    def register(self, data):
        """
        Register submitted data.
        """
        setattr(self, '_data', data)

    def login(self, data):
        """
        Perform computation associated with a login operation.
        """
        pass

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
