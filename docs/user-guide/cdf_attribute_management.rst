.. cdf_attribute_management:

***********************************************************
Using SAMMI CDF Attribute Manager for Metadata Attributes
***********************************************************

Overview
========

The :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` class provides an interface to configure how metadata attributes are formatted in SWxSOC affiliated data products. 
The class represents a schema for metadata attribute requirements, validation, and formatting. 

It is important to understand the configuration options of :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` objects in order to attain the desired behavior of metadata attributes. 

The :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` class has two main attributes.
The class contains a :py:attr:`~sammi.cdf_attribute_manager.CdfAttributeManager.global_attribute_schema` member which configures global, or file level, metadata attributes. 
Second, the class contains a  :py:attr:`~sammi.cdf_attribute_manager.CdfAttributeManager.variable_attribute_schema` member which configures variable or measurement level metadata attributes. 
This guide contains two sections detailing the format of each of these class members, how they're used, and how you can extend or modify them to meet your specific needs. 

Each of the global and variable schemas are loaded from YAML (dict-like) files which can be combined to layer multiple schema elements into a single unified schema. 
This allows extensions and overrides to the default schema, and allows you to create new schema configurations for specific archive file types and specific metadata requirements.

Creating a CDF Attribute Manager
================================

Creating a :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` object directly includes passing one or more paths to schema files to layer on top of one another, and optionally whether to use the default base layer schema files. 
For more information on the default, base layer, schema files please see our :doc:`CDF Format Guide </user-guide/cdf_format_guide>`.

Here is an example of instantiation of a :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` object: 

.. code-block:: python

    global_layers = ["my_global_layer_1.yaml", "my_global_layer_2.yaml"]
    variable_layers = ["my_variable_layer_1.yaml", "my_variable_layer_2.yaml"]
    my_schema = CdfAttributeManager(
        global_schema_layers=global_layers,
        variable_schema_layers=variable_layers,
        use_defaults=False
    )

This will create a new schema object from scratch, without using the default CDF schema, and will overlay the `layer_2` files over the `layer_1` files. 
If there are no conflicts within the schema files, then their attributes will be merged, to create a superset of the two files.
If there are conflicts in the combination of schema layers, this is resolved in a latest-priority ordering. 
That is, if the are conflicts or duplicate keys in `layer_1` that also appear in `layer_2`, then the second layer will overwrite the values from the first layer in the resulting schema. 

Global Attribute Schemas
========================

Global metadata attribute schemas are used to define requirements at the global or file level. 
The global attribute schema is configured through YAML files, with the default configuration in :file:`sammi/data/default_global_cdf_attrs_schema.yaml`

The YAML file represents a dictionary of attribute information, keyed by the metadata attribute name. 
Information on the file format can be seen below:

.. code-block:: yaml

    attribute_name:
        description: <string>
        default: <string>
        required: <bool>
    attriubte_name: 
        description: <string> ...

Each of the keys for global metadata requirements are defined in the table below. 

.. list-table:: Global Attribute Schema
    :widths: 20 50 10 10
    :header-rows: 1

    * - Schema Key
      - Description
      - Data Type
      - Is Required?
    * - `attribute_name`
      - the name of the global metadata attribute as it should appear in your data products
      - `str`
      - `True`
    * - `description`
      - a description for the global metadata attribute and context needed to understand its values
      - `str`
      - `True`
    * - `default`
      - a default value for the attribute if needed/desired
      - `str` or `null`
      - `True`
    * - `required`
      - whether the global attribute is required in your data products 
      - `bool`
      - `True`

For more information on the default CDF schema, conforming to ISTP standards, please see the :doc:`CDF Format Guide </user-guide/cdf_format_guide>`. 

Variable Attribute Schemas
==========================

Variable metadata attribute schemas are used to define requirements at the variable or measurement level. 
The variable attribute schema is configured through YAML files, with the default configuration in file :file:`sammi/data/default_variable_cdf_attrs_schema.yaml`.

The variable attribute schema YAML file has two main parts.

    - The first part is the `attribute_key`, which is a dictionary of attribute information, keyed by the metadata attribute name. This part of the schema is formatted similarly to the global schema above. 
    - The second part is an index of what metadata attributes are required for different variable types. This defines what attributes are required for `data` variable types compared to `support_data` and `metadata` variable types.

An example of a valid file format can be seen below. 

.. code-block:: yaml

    attribute_key: 
        attribute_name_1:
            description: <string>
            required: <bool>
            valid_values: <bool>
            alternate: <string>
        attribute_name_2: 
            description: <string> ...
    data:
      - attribute_name_1
      - attribute_name_2
    support_data:
      - attribute_name_2
    metadata:
      - attribute_name_2


Each of the keys for variable metadata requirements are defined in the table below. 

.. list-table:: Variable Attribute Schema
    :widths: 15 50 7 18
    :header-rows: 1

    * - Schema Key
      - Description
      - Data Type
      - Is Required?
    * - `attribute_name`
      - the name of the variable metadata attribute as it should appear in your data products
      - `str`
      - `True`
    * - `description`
      - a description for the variable metadata attribute and context needed to understand its values
      - `str`
      - `True`
    * - `required`
      - whether the variable attribute is required in your data products 
      - `bool`
      - `True`
    * - `valid_values`
      - values that the attribute should be checked against
      - `list[str]` or `null`
      - `True`
    * - `alternate`
      - the potential name of a different attribute should be considered in replacement of the given attribute. For example, only one of `LABLAXIS` or `LABL_PTR_i` are required in ISTP guidelines and are treated as alternates here. 
      - `str` or `null`
      - `True`

For more information on the default CDF schema, conforming to ISTP standards, please see the :doc:`CDF Format Guide </user-guide/cdf_format_guide>`. 
