"""
Minimal pure-Python library that implements a basic version of a
secure decentralized biometric authentication functionality via
a secure multi-party computation protocol.
"""
from __future__ import annotations
from typing import Sequence, Iterable
import doctest
from modulo import modulo
import tinynmc

_PRECISION = 16
"""
Precision (*i.e.*, number of digits after the decimal point) for fixed-point
rationals.
"""

def _encode(data, is_login=0):
    """
    Encode data for requests to nodes.
    """
    encoding = [round(value * (2 ** _PRECISION)) for value in data]

    coords_to_values = {(is_login, 0): sum(value * value for value in encoding)}
    for (index, value) in enumerate(encoding, 2):
        coords_to_values[(index, is_login)] = ((is_login * 3) - 2) * value

    return coords_to_values

class node(tinynmc.node):
    """
    Data structure for maintaining the information associated with a node
    and performing node operations.
    """
    def authenticate(self, tokens):
        """
        Perform computation associated with a login operation.
        """
        return self.compute(getattr(self, '_signature'), tokens)

def preprocess(length: int, nodes: Sequence[node]):
    """
    Simulate a preprocessing phase among the collection of nodes for a workflow
    that supports registration and authentication data vectors of the specified
    length.
    """
    signature = [1, 1] + ([2] * length)
    tinynmc.preprocess(signature, nodes)
    for node_ in nodes:
        setattr(node_, '_signature', signature)

def registration_request(data):
    """
    Encode data into a registration request.
    """
    return _encode(data, 0).keys()

def authentication_request(data):
    """
    Encode data into an authentication request.
    """
    return _encode(data, 1).keys()

def registration_token(masks, data):
    """
    Mask data to create a registration token.
    """
    return tinynmc.masked_factors(_encode(data, 0), masks)

def authentication_token(masks, data):
    """
    Mask data to create an authentication token.
    """
    return tinynmc.masked_factors(_encode(data, 1), masks)

def reveal(shares: Iterable[modulo]) -> int:
    """
    Reconstruct the result of the overall workflow from its shares and convert
    it into a meaningful output (as a percentage).
    """
    return (100 * int(sum(shares))) // (2 ** (2 * _PRECISION))

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
