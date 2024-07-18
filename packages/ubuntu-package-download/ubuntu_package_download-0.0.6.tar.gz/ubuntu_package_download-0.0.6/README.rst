=======================
Ubuntu Package Download
=======================


.. image:: https://img.shields.io/pypi/v/ubuntu_package_download.svg
        :target: https://pypi.python.org/pypi/ubuntu_package_download

.. image:: https://img.shields.io/travis/philroche/ubuntu_package_download.svg
        :target: https://travis-ci.com/philroche/ubuntu_package_download

.. image:: https://readthedocs.org/projects/ubuntu-package-download/badge/?version=latest
        :target: https://ubuntu-package-download.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

Helpful utility to download Ubuntu debian packages

Process/Order of finding the package and fallback logic:

    1. Attempt to find the package in the specified series and architecture
    2. If the package is not found in the specified series and architecture attempt to find the package in the `all` architecture (amd64)
    3. If the package is not found in the `all` architecture attempt to find the package in a previous series if the `fallback_series` flag is set to True
    4. If the package is not found in a previous series attempt to find the previous version of the package in the same series if the `fallback_version` flag is set to True

    If not found in any of the above steps log an error message to the console.


* Free software: GNU General Public License v3
* Documentation: https://ubuntu-package-download.readthedocs.io.


Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
