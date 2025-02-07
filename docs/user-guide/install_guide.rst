.. install_guide


*****************
Installing SAMMI
*****************

Overview
========

SAMMI can be found on PyPI at `https://pypi.org/project/sammi-cdf/ <https://pypi.org/project/sammi-cdf/>`_ and can be installed using pip:

.. code-block:: bash

    pip install sammi-cdf

Validate Installation
=====================

To validate that SAMMI has been installed correctly, you can try importing the package in a Python environment:

.. code-block:: python

    from sammi.validation import CDFValidator
    from pathlib import Path
    CDFValidator().validate(Path("path/to/your/file.cdf"))
