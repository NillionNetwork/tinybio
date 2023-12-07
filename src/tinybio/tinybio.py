"""
Minimal pure-Python library that implements a basic version of a
secure decentralized biometric authentication functionality via
a secure multi-party computation protocol.
"""
from __future__ import annotations
from typing import Sequence, Iterable
import doctest
import math
from modulo import modulo
import tinynmc

_PRECISION = 8
"""
Precision (*i.e.*, number of digits after the decimal point in a binary
representation of a value) for fixed-point rationals.
"""

def _encode(
        descriptor: Sequence[float],
        for_auth: bool = False
    ) -> dict[tuple[int, int], int]:
    """
    Encode data for requests to nodes.
    """
    reg_0_or_auth_1 = int(for_auth)
    encoding = [round(value * (2 ** _PRECISION)) for value in descriptor]

    coords_to_values = {
        (reg_0_or_auth_1, 0): \
            sum(value ** 2 for value in encoding)
    }
    for (index, value) in enumerate(encoding, 2):
        coords_to_values[(index, reg_0_or_auth_1)] = (-2 if for_auth else 1) * value

    return coords_to_values

class node(tinynmc.node):
    """
    Data structure for maintaining the information associated with a node
    and performing node operations.

    Suppose that a workflows is supported by three nodes (parties performing
    the decentralized registration and authentication functions). The node
    objects would be instantiated locally by each of these three parties.

    >>> nodes = [node(), node(), node()]

    The preprocessing phase that the nodes must execute can be simulated using
    the :obj:`preprocess` function. It is assumed that biometric descriptors
    used for registration and authentication are represented as lists of
    floating point numbers. All such descriptors must be of the same length,
    and this length must be supplied as the second argument to the
    :obj:`preprocess` function.

    >>> preprocess(nodes, 3)

    It is then possible to register some data (*i.e.*, a biometric descriptor
    represented as a vector of floating point values) by requesting the masks
    from each node and submitting a registration *token* (*i.e.*, a masked
    descriptor that is computed locally by the registering party) to the nodes.

    >>> reg_descriptor = [0.5, 0.3, 0.7]
    >>> reg_masks = [node.masks(request.registration(reg_descriptor)) for node in nodes]
    >>> reg_token = token.registration(reg_masks, reg_descriptor)

    At a later point, it is possible to perform an authentication workflow.
    After requesting masks for the authentication descriptor, the authentication
    token (*i.e.*, a masked descriptor) can be generated locally by the party
    interested in authenticating itself.

    >>> auth_descriptor = [0.1, 0.4, 0.8]
    >>> auth_masks = [node.masks(request.authentication(auth_descriptor)) for node in nodes]
    >>> auth_token = token.authentication(auth_masks, auth_descriptor)

    Finally, the party interested in authenticating itself can broadcast its
    original registration token together with its authentication token. Each
    node then computes locally its share of the authentication result. These
    shares can be reconstructed by a designated authority to obtain a result.

    >>> shares = [node.authenticate([reg_token, auth_token]) for node in nodes]
    >>> abs(reveal(shares) - 0.42) <= 0.1 # Use comparison for floating point value.
    True
    """
    def authenticate(
            self: node,
            tokens: Sequence[dict[tuple[int, int], modulo]]
        ) -> modulo:
        """
        Perform computation associated with an authentication workflow.
        """
        return self.compute(getattr(self, '_signature'), tokens)

class request(list[tuple[int, int]]):
    """
    Data structure for representing registration and authentication requests.
    """
    @staticmethod
    def registration(descriptor: Sequence[float]) -> request:
        """
        Encode descriptor into a registration request.
        """
        return request(_encode(descriptor, False).keys())

    @staticmethod
    def authentication(descriptor: Sequence[float]) -> request:
        """
        Encode descriptor into an authentication request.
        """
        return request(_encode(descriptor, True).keys())

class token(dict[tuple[int, int], modulo]):
    """
    Data structure for representing registration and authentication tokens.
    """
    @staticmethod
    def registration(
            masks: Iterable[dict[tuple[int, int], modulo]],
            descriptor: Sequence[float]
        ) -> token:
        """
        Mask descriptor and create a registration token.
        """
        return token(tinynmc.masked_factors(_encode(descriptor, False), masks))

    @staticmethod
    def authentication(
            masks: Iterable[dict[tuple[int, int], modulo]],
            descriptor: Sequence[float]
        ) -> token:
        """
        Mask descriptor and create an authentication token.
        """
        return token(tinynmc.masked_factors(_encode(descriptor, True), masks))

def preprocess(nodes: Sequence[node], length: int):
    """
    Simulate a preprocessing phase among the collection of nodes for a workflow
    that supports registration and authentication descriptor vectors of the
    specified length.
    """
    signature = [1, 1] + ([2] * length)
    tinynmc.preprocess(signature, nodes)
    for node_ in nodes:
        setattr(node_, '_signature', signature)

def reveal(shares: Iterable[modulo]) -> float:
    """
    Reconstruct the result of the overall workflow from its shares and convert
    it into a meaningful output (as a percentage).
    """
    return math.sqrt(int(sum(shares)) / (2 ** (2 * _PRECISION)))

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
