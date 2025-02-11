.. cdf_validation:

***********************************************************
Using SAMMI CDF Validator for ISTP Attribute Validation
***********************************************************

Overview
========

The :py:class:`~sammi.validation.CDFValidator` class provides an interface to validate CDF files against the ISTP guidelines using the SPDF validation API.
This ensures that your CDF files conform to the required standards and helps identify any issues with the metadata attributes.

Creating a Validator
====================

Creating a :py:class:`~sammi.validation.CDFValidator` object is straightforward. You can instantiate it with the default API URL or provide a custom one if needed.

.. code-block:: python

    from sammi.validation import CDFValidator

    # Create a validator with the default API URL
    validator = CDFValidator()

    # Create a validator with a custom API URL
    custom_validator = CDFValidator(api_url="https://custom.api.url/validate")

Examples
========

Here are some examples of how to use the :py:class:`~sammi.validation.CDFValidator` class to validate your CDF files.

Validating a CDF File
---------------------

To validate a CDF file, use the :py:meth:`~sammi.validation.CDFValidator.validate` method. This method returns a list of error messages, if any.

.. code-block:: python

    from pathlib import Path
    from sammi.validation import CDFValidator

    # Initialize the validator
    validator = CDFValidator()

    # Path to the CDF file to validate
    cdf_path = Path("/path/to/your/file.cdf")

    # Validate the CDF file
    errors = validator.validate(cdf_path)

    # Print the validation errors
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(error)
    else:
        print("No validation errors found.")

Validating a CDF File and Getting Raw Response
----------------------------------------------

If you need the raw response from the SPDF validation API, use the :py:meth:`~sammi.validation.CDFValidator.validate_raw` method.

.. code-block:: python

    from pathlib import Path
    from sammi.validation import CDFValidator

    # Initialize the validator
    validator = CDFValidator()

    # Path to the CDF file to validate
    cdf_path = Path("/path/to/your/file.cdf")

    # Get the raw validation response
    raw_response = validator.validate_raw(cdf_path)

    # Print the raw response
    print(raw_response)
