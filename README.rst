=======
tinybio
=======

Minimal pure-Python library that implements a basic version of a `secure decentralized biometric authentication <https://nillion.pub/decentralized-multifactor-authentication.pdf>`__ functionality via a `secure multi-party computation protocol <https://eprint.iacr.org/2023/1740>`__.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/tinybio.svg
   :target: https://badge.fury.io/py/tinybio
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/tinybio/badge/?version=latest
   :target: https://tinybio.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/nillion-oss/tinybio/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/nillion-oss/tinybio/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/nillion-oss/tinybio/badge.svg?branch=main
   :target: https://coveralls.io/github/nillion-oss/tinybio?branch=main
   :alt: Coveralls test coverage summary.

Installation and Usage
----------------------

This library is available as a `package on PyPI <https://pypi.org/project/tinybio>`__:

.. code-block:: bash

    python -m pip install tinybio

The library can be imported in the usual way:

.. code-block:: python

    import tinybio
    from tinybio import *

Basic Example
^^^^^^^^^^^^^

Suppose that a workflows is supported by three nodes (parties performing the decentralized registration and authentication functions). The node objects would be instantiated locally by each of these three parties:

.. code-block:: python

    >>> nodes = [node(), node(), node()]

The preprocessing phase that the nodes must execute can be simulated. The second parameter specifies the length of a biometric descriptor (*i.e.*, list of floating point values):

.. code-block:: python
    
    >>> preprocess(nodes, length=4)

.. |token| replace:: ``token``
.. _token: https://tinybio.readthedocs.io/en/0.1.0/_source/tinybio.html#tinybio.tinybio.token

.. |float| replace:: ``float``
.. _float: https://docs.python.org/3/library/functions.html#float

Suppose the client has a biometric descriptor represented as a vector of |float|_ values. The client can create a request for masks and then obtain masks from each node. The client can then locally generate a registration |token|_ (*i.e.*, a masked descriptor that is computed locally by the registering party):

.. code-block:: python

    >>> reg_descriptor = [0.5, 0.3, 0.7, 0.1]
    >>> reg_masks = [node.masks(request.registration(reg_descriptor)) for node in nodes]
    >>> reg_token = token.registration(reg_masks, reg_descriptor)

At a later point, the client can perform an authentication workflow. After requesting masks for the authentication descriptor in a manner similar to the above, the client can generate an authentication |token|_ (*i.e.*, a masked descriptor) locally:

.. code-block:: python

    >>> auth_descriptor = [0.1, 0.4, 0.8, 0.2]
    >>> auth_masks = [node.masks(request.authentication(auth_descriptor)) for node in nodes]
    >>> auth_token = token.authentication(auth_masks, auth_descriptor)

Finally, the party interested in authenticating itself can broadcast its original registration token together with its authentication token. Each node can then compute locally its share of the authentication result. These shares can be reconstructed by the validating party to obtain the result (*i.e.*, the Euclidean distance between the registration and authentication descriptors):

.. code-block:: python

    >>> shares = [node.authenticate(reg_token, auth_token) for node in nodes]
    >>> reveal(shares) # Floating point results may differ slightly.
    0.43375208257785347

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__:

.. code-block:: bash

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__:

.. code-block:: bash

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details):

.. code-block:: bash

    python -m pip install .[test]
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__:

.. code-block:: bash

    python src/tinybio/tinybio.py -v

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install .[lint]
    python -m pylint src/tinybio

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/nillion-oss/tinybio>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/tinybio>`__ by a package maintainer. First, install the dependencies required for packaging and publishing:

.. code-block:: bash

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number):

.. code-block:: bash

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive:

.. code-block:: bash

    rm -rf build dist src/*.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__:

.. code-block:: bash

    python -m twine upload dist/*
