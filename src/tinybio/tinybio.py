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
    the decentralized registration and authentication functions). The :obj:`node`
    objects would be instantiated locally by each of these three parties.

    >>> nodes = [node(), node(), node()]

    The preprocessing phase that the nodes must execute can be simulated using
    the :obj:`preprocess` function. It is assumed that biometric descriptors
    used for registration and authentication are represented as lists of
    :obj:`float` values. All such descriptors must be of the same length,
    and this length must be supplied as the second argument to the
    :obj:`preprocess` function.

    >>> preprocess(nodes, length=4)

    It is then possible for a client to register itself by obtaining
    a registration :obj:`token`. Suppose the client has a biometric
    descriptor represented as a vector of floating point values. The
    client can create a :obj:`request` for masks using the
    :obj:`request.registration` method.

    >>> reg_descriptor = [0.5, 0.3, 0.7, 0.1]
    >>> reg_request = request.registration(reg_descriptor)

    The client can deliver the request to each node, at which point that node
    can locally use its :obj:`~tinynmc.tinynmc.node.masks` method (inherited
    from the :obj:`tinynmc.tinynmc.node` class) to generate masks that can
    be returned to the requesting client.

    >>> reg_masks = [node.masks(reg_request) for node in nodes]

    The client can then generate locally a registration :obj:`token` (*i.e.*, a
    masked descriptor) via the :obj:`token.registration` method.

    >>> reg_token = token.registration(reg_masks, reg_descriptor)

    At any later point, it is possible to perform an authentication workflow.
    Masks for the authentication descriptor can be requested via a process
    that parallels the one for registration (in this case using the
    :obj:`request.authentication` method).

    >>> auth_descriptor = [0.1, 0.4, 0.8, 0.2]
    >>> auth_request = request.authentication(auth_descriptor)
    >>> auth_masks = [node.masks(auth_request) for node in nodes]

    Given the masks for the authentication descriptor, the authentication
    :obj:`token` (*i.e.*, a masked descriptor) can be generated locally by
    the client via the :obj:`token.authentication` method.

    >>> auth_token = token.authentication(auth_masks, auth_descriptor)

    Finally, the client can broadcast its original registration token together
    with its authentication token. Each node can then compute locally its share of
    the authentication result. These shares can be reconstructed by the validating
    party using the :obj:`reveal` function to obtain the Euclidean distance
    between the registration and authentication descriptors.

    >>> shares = [node.authenticate(reg_token, auth_token) for node in nodes]
    >>> abs(reveal(shares) - 0.43) <= 0.05 # Use comparison for floating point value.
    True
    """
    def authenticate(
            self: node,
            registration_token: token,
            authentication_token: token
        ) -> modulo:
        """
        Perform computation associated with an authentication workflow.

        :param registration_token: Registration token to be used in the
            local computation by this node.
        :param authentication_token: Authentication token to be used in the
            local computation by this node.
        """
        return self.compute(
            getattr(self, '_signature'),
            [registration_token, authentication_token]
        )

class request(list[tuple[int, int]]):
    """
    Data structure for representing registration and authentication requests.
    """
    @staticmethod
    def registration(descriptor: Sequence[float]) -> request:
        """
        Encode descriptor into a registration request.

        :param descriptor: Biometric descriptor to be used for registration.

        This request can be submitted to each node to obtain masks for the
        descriptor.

        >>> reg_descriptor = [0.5, 0.3, 0.7, 0.1]
        >>> isinstance(request.registration(reg_descriptor), request)
        True
        """
        return request(_encode(descriptor, False).keys())

    @staticmethod
    def authentication(descriptor: Sequence[float]) -> request:
        """
        Encode descriptor into an authentication request.

        :param descriptor: Biometric descriptor to be used for authentication.

        This request can be submitted to each node to obtain masks for the
        descriptor.

        >>> auth_descriptor = [0.1, 0.4, 0.8, 0.2]
        >>> isinstance(request.authentication(auth_descriptor), request)
        True
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

        :param masks: Collection of masks to be applied to the descriptor.
        :param descriptor: Biometric descriptor to be converted into a token.

        Suppose masks have already been obtained from the nodes via the steps
        below.

        >>> nodes = [node(), node(), node()]
        >>> preprocess(nodes, 4)
        >>> descriptor = [0.5, 0.3, 0.7, 0.1]
        >>> masks = [node.masks(request.registration(descriptor)) for node in nodes]

        This method can be used to mask the original descriptor (in preparation
        for broadcasting it to the nodes).
        
        >>> isinstance(token.registration(masks, descriptor), token)
        True
        """
        return token(tinynmc.masked_factors(_encode(descriptor, False), masks))

    @staticmethod
    def authentication(
            masks: Iterable[dict[tuple[int, int], modulo]],
            descriptor: Sequence[float]
        ) -> token:
        """
        Mask descriptor and create an authentication token.

        :param masks: Collection of masks to be applied to the descriptor.
        :param descriptor: Biometric descriptor to be converted into a token.

        Suppose masks have already been obtained from the nodes via the steps
        below.

        >>> nodes = [node(), node(), node()]
        >>> preprocess(nodes, 4)
        >>> descriptor = [0.5, 0.3, 0.7, 0.1]
        >>> masks = [node.masks(request.authentication(descriptor)) for node in nodes]

        This method can be used to mask the original descriptor (in preparation
        for broadcasting it to the nodes).
        
        >>> isinstance(token.authentication(masks, descriptor), token)
        True
        """
        return token(tinynmc.masked_factors(_encode(descriptor, True), masks))

def preprocess(nodes: Sequence[node], length: int):
    """
    Simulate a preprocessing phase among the collection of nodes for a workflow
    that supports registration and authentication descriptor vectors of the
    specified length.

    :param nodes: Collection of nodes involved in the workflow.
    :param length: Number of components in each descriptor list to be used
        in the workflow.

    >>> nodes = [node(), node(), node()]
    >>> preprocess(nodes, length=4)
    """
    signature = [1, 1] + ([2] * length)
    tinynmc.preprocess(signature, nodes)
    for node_ in nodes:
        setattr(node_, '_signature', signature)

def reveal(shares: Iterable[modulo]) -> float:
    """
    Reconstruct the result of the overall workflow from its shares and convert
    it into a meaningful output (*i.e.*, the Euclidean distance between the
    registration descriptor and the authentication descriptor).

    :param shares: Shares that can be reconstructed into a result.

    Suppose the shares below are returned from the three nodes in a workflow.

    >>> p = 4215209819
    >>> shares = [modulo(2042458237, p), modulo(1046840547, p), modulo(1125923365, p)]

    This method converts a collection of secret shares from the nodes into
    a floating point value representing the Euclidean distance between the
    registration and authentication descriptors.

    >>> abs(reveal(shares) - 0.43) <= 0.05 # Use comparison for floating point value.
    True
    """
    return math.sqrt(int(sum(shares)) / (2 ** (2 * _PRECISION)))

if __name__ == '__main__':
    doctest.testmod() # pragma: no cover
