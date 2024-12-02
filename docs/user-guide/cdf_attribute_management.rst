.. cdf_attribute_management:

***********************************************************
Using SAMMI CDF Attribute Manager for Metadata Attributes
***********************************************************

Overview
========

The :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` class provides an interface to configure how metadata attributes are formatted in data products.
The class represents a schema for metadata attribute requirements, validation, and formatting.

It is important to understand the configuration options of :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` objects in order to attain the desired behavior of metadata attributes.

The :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` class has two main attributes.

* The class contains a :py:attr:`~sammi.cdf_attribute_manager.CdfAttributeManager.global_attribute_schema` member which configures global, or file level, metadata attributes.
* Second, the class contains a  :py:attr:`~sammi.cdf_attribute_manager.CdfAttributeManager.variable_attribute_schema` member which configures variable or measurement level metadata attributes.

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


Creating and Using Attribute Files
==================================

Attribute files for CDF are also stored in YAML format. Like the schemas, these files can be layered and combined together to create some shared default
values and overwrite them with other files.

It is also possible to use YAML syntax to create complex data structures. For example, YAML anchors and aliases can be used to create a base set of attributes and then extend them for specific instruments or data levels.

.. code-block:: yaml

    int_fillval: &int_fillval -9223372036854775808

    base_attributes: &base
        DISPLAY_TYPE: no_plot
        TIME_BASE: J2000
        TIME_SCALE: Terrestrial Time
        FILLVAL: *int_fillval

    variable_defaults: &variable_defaults
        VAR_TYPE: data
        FORMAT: I10

    variable_attribute:
        <<: *base
        <<: *variable_defaults
        CATDESC: Variable attribute description

`More information on YAML syntax. <https://www.yaml.info/learn/index.html>`_

Global attributes are defined using the key-value pairs for required and optional attributes. (example taken from `IMAP <https://github.com/IMAP-Science-Operations-Center/imap_processing/blob/dev/imap_processing/cdf/config/imap_default_global_cdf_attrs.yaml>`_):

.. code-block:: yaml

    Project: STP>Solar Terrestrial Probes
    Source_name: IMAP>Interstellar Mapping and Acceleration Probe
    Discipline: Solar Physics>Heliospheric Physics
    Mission_group: IMAP

It is also possible to create instrument and level specific global attributes. For example, the ``Data_level`` global attribute is specific to the level of the data product. These can be defined as "instrument_ids" in one file and retrieved one at a time.

Example taken from `the GLOWS instrument <https://github.com/IMAP-Science-Operations-Center/imap_processing/blob/dev/imap_processing/cdf/config/imap_glows_global_cdf_attrs.yaml>`_ on IMAP.

.. code-block:: yaml

    instrument_base: &instrument_base
      Descriptor: GLOWS>GLObal Solar Wind Structure
      TEXT: >
        The GLObal Solar Wind Structure (GLOWS) is a non-imaging single-pixel Lyman-alpha
        photometer to investigate the global heliolatitudinal structure of the solar wind
        and its evolution during the solar cycle. Additionally, GLOWS investigates the
        distribution of interstellar neutral hydrogen (ISN H) and the solar radiation
        pressure acting on ISN H. The objectives of GLOWS are accomplished by observation
        of the modulation of heliospheric backscatter glow of ISN H (the helioglow)
        along a scanning circle in the sky.
        GLOWS design and assembly is led by the Space Research Center, Warsaw, Poland
        (CBK PAN). See https://imap.princeton.edu/instruments/glows for more details.
      Instrument_type: Imagers (space)

    imap_glows_l1a_hist:
      <<: *instrument_base
      Data_level: L1A
      Data_type: L1A_hist>Level-1A histogram
      Logical_source: imap_glows_l1a_hist
      Logical_source_description: IMAP Mission GLOWS Histogram Level-1A Data.

    imap_glows_l1a_de:
      <<: *instrument_base
      Data_level: L1A
      Data_type: L1A_de>Level-1A direct event
      Logical_source: imap_glows_l1a_de
      Logical_source_description: IMAP Mission GLOWS Direct Event Level-1A Data.


These global attributes can be added to an instance of cdf_attribute_manager and then retrieved and validated:

.. code-block:: python

    shared_global_attributes = Path("shared_global_attributes.yaml")
    instrument_global_attributes = Path("instrument_global_attributes.yaml")

    cdf_manager = CdfAttributeManager(use_defaults=True)

    # Load in the global attributes
    cdf_manager.load_global_attributes(shared_global_attributes)
    cdf_manager.load_global_attributes(instrument_global_attributes)

    # retrieve the global attributes, including the specific GLOWS L1A Histogram attributes
    global_attrs = cdf_manager.get_global_attributes(instrument_id="imap_glows_l1a_hist")


Variable attribute files work similarly to the instrument ID. Each variable has a name assigned to it, which then has a set of attributes associated with it. YAML anchors and aliases are used to create
defaults and shared information. Then, the variable attributes are retrieved with the name.


.. code-block:: yaml

    int_fillval: &int_fillval -9223372036854775808

    default_attrs: &default_attrs
      DISPLAY_TYPE: no_plot
      TIME_BASE: J2000
      TIME_SCALE: Terrestrial Time
      REFERENCE_POSITION: Rotating Earth Geoid
      FILLVAL: *int_fillval

    support_data_defaults: &support_data_defaults
      <<: *default_attrs
      DEPEND_0: epoch
      VALIDMIN: 0
      VALIDMAX: 1
      DISPLAY_TYPE: time_series
      VAR_TYPE: support_data
      FORMAT: I10
      RESOLUTION: ISO8601

    bins_attrs:
      <<:  *default_attrs
      VALIDMAX: 3599
      CATDESC: Histogram bin number
      FIELDNAM: Bin number
      FORMAT: I5
      LABLAXIS: Counts
      FILLVAL: -32768
      MONOTON: INCREASE
      SCALETYP: linear


These variable attributes can be added to an instance of cdf_attribute_manager and then retrieved and validated:

.. code-block:: python

    variable_attributes = Path("variable_attributes.yaml")

    # Load attributes
    cdf_manager.load_variable_attributes(variable_attributes)

    # Retrieve attributes
    variable_attrs = cdf_manager.get_variable_attributes("bins_attrs")

All the attributes are validated to ISTP standards once retrieved using ``get_variable_attributes()``. Validation can be skipped with the ``check_schema`` flag on ``get_variable_attributes()``.