.. _cdf_format_guide:

*******************************
CDF Format Guide
*******************************

===============
1. Introduction
===============

The :py:class:`~sammi.cdf_attribute_manager.CdfAttributeManager` class provides an interface to examine the CDF Format Guide.

---------------------
1.1 Purpose and Scope
---------------------

This document is provided as a reference for construction of standard CDF files.
It is intended to complement information available from the Space Physics Data Facility (listed in Sec. 1.2).
It lays down REQUIREMENTS and RECOMMENDATIONS for Level 2 (and above) CDF files that are intended for public access, and should be taken as RECOMMENDATIONs for all other mission CDFs.
This document is based on discussions with personnel at NASA's Space Physics Data Facility (SPDF).
It is intended to provide sufficient reference material to understand CDF files and the requirements for creating mission-specific CDF files.

--------------
1.2 References
--------------

Relevant documents that provide background material and support details provided in this guide are listed below:

- `SPDF CDF User's Guide <http://cdf.gsfc.nasa.gov/>`_
- `SKTEditor <http://spdf.gsfc.nasa.gov/sp_use_of_cdf.html>`_
- `ISTP Guidelines <http://spdf.gsfc.nasa.gov/istp_guide/istp_guide.html>`_
- `ISTP/IACG Global Attributes <http://spdf.gsfc.nasa.gov/istp_guide/gattributes.html>`_

==============
2. Conventions
==============

Scientific data products that will be shared between SWxSOC entities (e.g. missions, ITFs, IDS groups) or made available to the general research community, stored as CDF data files, are expected to be compatible with CDF version 3.5.
Data that will not be shared beyond an individual team may be stored in any format that is convenient for that team.

--------------------------------------
2.1 Science Product Naming Conventions
--------------------------------------

Data products will be produced with the following filename format where the individual identifying components are described in Table 2-1.
Additionally, to ensure software compatibility between disparate systems, filenames will consist of all lowercase characters.
Filenames are used as a system identifier for a logical grouping of data and are also stored in the `Logical_file_id` global attribute field (see Section 3.1).
It is expected that filenames will be created dynamically from the attributes identified in Section 3 of this document.

**Filename Format**
    `scId_instrumentId_mode_dataLevel_optionalDataProductDescriptor_startTime_vX.Y.Z.ext`

.. list-table:: Table 2-1: Filename Component Description
   :widths: 25 50 25
   :header-rows: 1

   * - Short Name
     - Description
     - Valid Options
   * - scID
     - Spacecraft ID
     - `hermes`, `gdc`, `padre`, ...
   * - instrumentId
     - Instrument or investigation identifier shortened to three letter acronym.
     - `eea`, `mrt`, `nms`, `spn`, `meddea`, ...
   * - mode
     - *TBS*
     - `default`, `brst`, ...
   * - dataLevel
     - The level to which the data product has been processed
     - `l0`, `l1`, `ql`, `l2`, `l3`, `l4`
   * - optionalDataProductDescriptor
     - This is an optional field that may not be needed for all products. Where it is used, identifier should be short (e.q. 3-8 characters) descriptors that are helpful to end-users. If a descriptor contains multiple components, underscores are used to separate those components.
     - An optional time span may be specified as "2s" to represent a data file that spans two seconds. In this case, "10s" and "5m" are other expected values that correspond with ten seconds and 5 minutes respectively.
   * - startTime
     - The start time of the contained data given in `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_ format.
     - `20230519T000003`
   * - vX.Y.Z
     - The 3-part version number of the data product. Full description of this identifier is provided in Section 3.1.1 of this document.
     - `v0.0.0`, `v<#.#.#>`
   * - .ext
     - The required file extension, where CDF is required.
     - `.cdf`

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2.1.1 Version Numbering Guidelines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The three-part version number contains the interface number, quality number, and bug fix/revision number.
The initial release of CDF data that is suitable for scientific publication should begin with “v1.Y.Z”.
Each component of the version number is incremented in integer steps, as needed, and Table 3-2 describes the instances in which the value should be incremented.
Release “v0.Y.Z” may be used for early development purposes.

.. list-table:: Table 2-2: Version Numbering Guidelines
   :widths: 25 25 50
   :header-rows: 1

   * - Part
     - Name
     - Description
   * - X
     - Interface Number
     - Increments in this number represent a significant change to the processing software and/or to the content/structure of the file. These changes may be incompatible with existing code. Increments in this number may require code changes to software.
   * - Y
     - Quality Number
     - This number represents a change in the quality of the data in the file, such as change in calibration or increase in fidelity. Changes should not impact software but may require consideration when processing data.
   * - Z
     - Bug Fix / Revision Number
     - This number changes to indicate minor changes to the contents of the file due to reprocessing of missing data. Any dependent data products should generally be reprocessed if this value changes.

====================
3. Global Attributes
====================

Global attributes are used to provide information about the data set as an entity.
Together with variables and variable attributes, the global attributes make the data correctly and independently usable by someone not connected with the instrument team, and hence, a good archive product.

The required, recommended, and optional global attributes that have been identified for use with ISTP-compliant data products are listed below.
Additional global attributes can be defined but they must start with a letter and can otherwise contain letters, numbers, and the underscore character (no other special characters allowed).
Note that CDF attributes are case-sensitive and must exactly follow what is shown here.

Detailed descriptions of the attributes listed below are available at the `ISTP/IACG Global Attributes Webpage <http://spdf.gsfc.nasa.gov/istp_guide/gattributes.html>`_.

--------------------------------------
3.1 Required Global Attributes
--------------------------------------

The following global attributes shown in Table 3-1 are required with ISTP-compliant data products.
For each attribute the following information is provided:

* description: (`str`) A brief description of the attribute
* default: (`str`) The default value used if none is provided
* required: (`bool`) Whether the attribute is required by ISTP standards

Note that this table is derived from :file:`sammi/data/default_global_cdf_attrs_schema.yaml`

.. csv-table:: Table 3-1: Required Global Attributes
   :file: ../generated/global_attributes.csv
   :widths: 30, 70, 30, 30
   :header-rows: 1

--------------------------------------
3.2 Recommended Attributes
--------------------------------------

The following global attributes are recommended but not required with ISTP-compliant data products.

.. list-table:: Table 3-2: Recommended Attributes
   :widths: 25 50
   :header-rows: 1

   * - Attribute
     - Description
   * - Acknowledgement
     - This field indicates how the data should be cited.
   * - Generated_by
     - This attribute indicates where users can get more information about this data and/or check for new versions.

--------------------------------------
3.3 Optional Attributes
--------------------------------------

.. list-table:: Table 3-3: Optional Attributes
   :widths: 25 50
   :header-rows: 1

   * - Attribute
     - Description
   * - Parents
     - This attribute lists the parent data files for files of derived and merged data sets. The syntax for a CDF parent is: "CDF>logical_file_id". Multiple entry values are used for multiple parents.
   * - Skeleton_version
     - This is a text attribute containing the skeleton file version number.
   * - Rules_of_use
     - Text containing information on citability and/or PI access restrictions. This may point to a World Wide Web page specifying the rules of use. Rules of Use are determined on both a mission and instrument basis, at the discretion of the PI.
   * - Time_resolution
     - Specifies time resolution of the file, e.g., "3 seconds".


============
4. Variables
============

There are three types of variables that should be included in CDF files:

* data,
* support data,
* metadata.

Additionally, required attributes are listed with each variable type listed below.

To facilitate data exchange and software development, variable names should be consistent across instruments and spacecraft.
Additionally, it is preferable that data types are consistent throughout all data products (e.g. all real variables are CDF_REAL4, all integer variables are CDF_INT2, and flag/status variables are UINT2).
This is not to imply that only these data types are allowable within CDF files.
All CDF supported data types are available for use by SWxSOC affiliated projects.

For detailed information and examples, please see the `ISTP/IACG Webpage <http://spdf.gsfc.nasa.gov/istp_guide/variables.html>`

--------------------------------------
4.1 Data
--------------------------------------

These are variables of primary importance (e.g., density, magnetic field, particle flux).
Data is always time (record) varying but can be of any dimensionality or CDF supported data type.
Real or Integer data are always defined as having one element.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.1.1 Naming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SWxSOC affiliated data variables must adhere to the following naming convention
* `scId_instrumentId_paramName`

An underscore is used to separate different fields in the variable name.
It is strongly recommended that variable names employ further fields, qualifiers and information designed to identify unambiguously the nature of the variable, instrument mode and data processing level, with sufficient detail to lead the user to the unique source file which contains the variable.
It is recommended that these follow the order shown below.

* `scId_instrumentId_paramName[_coordSys][_paramQualifier][_subModeLevel][_mode][_dataLevel]`

where the required fields are described in Table 4-1 and the optional fields are described in Table 4-2.
An example data variable would be `hermes_eea_n_gse_l2`.

.. list-table:: Table 4-1: Required Data Variable Fields
   :widths: 25 50
   :header-rows: 1

   * - Required Field Name
     - Description
   * - scId
     - Spacecraft identifier, see Table 2-1 for acceptable values
   * - instrumentId
     - Instrument or investigation identifier, see Table 2-1 for acceptable values and note the caveats listed in Section 4.1.1.1.
   * - paramName
     - Data parameter identifier, a short (a few letters) representation of the physical parameter held in the variable.

.. list-table:: Table 4-2: Optional Data Variable Fields
   :widths: 25 50
   :header-rows: 1

   * - Optional Field Name
     - Description
   * - coordSys
     - An acronym for the coordinate system in which the parameter is cast.
   * - paramQualifier
     - Parameter descriptor, which may include multiple components separated by a "_" as needed (e.g. "pa_0" indicates a pitch angle of 0).
   * - subModeLevel
     - Qualifier(s) to include mode and data level information supplementary to the following two fields.
   * - mode
     - See Table 2-1 for acceptable values.
   * - dataLevel
     - See Table 2-1 for acceptable values.

"""""""""""""""
4.1.1.1 Caveats
"""""""""""""""

Note the following caveats in the variable naming conventions:

* CDF variable names must begin with a letter and can contain numbers and underscores, but no other special characters.
* In general, the instrumentId field follows the convention used for file names as defined in Section 2.1.
  However, since variable names cannot contain a hyphen, an underscore should be used instead of a hyphen when needing to separate instrument components.
  For instance, "eea-ion" is a valid instrumentId in a filename but when used in a variable name, "eea_ion" should be used instead.
* To ensure software compatibility between disparate systems, parameter names will consist of all lowercase characters.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.1.2 Required Epoch Variable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All ISTP-compliant CDF data files must contain at least one variable of data type CDF_TIME_TT2000, typically named "Epoch".
This variable should normally be the first variable in each CDF data set.
All time varying variables in the CDF data set will depend on either this "epoch" variable or on another variable of type CDF_TIME_TT2000 (e.g. hermes_eea_epoch).
More than one CDF_TIME_TT2000 type variable is allowed in a data set to allow for more than one time resolution, using the required DEPEND_0 attribute (see Section 5.5) to associate a time variable to a given data variable.
It is recommended that all such time variables use “epoch” within their variable name.

For ISTP, but not necessarily for all mission's data, the time value of a record refers to the center of the accumulation period for the record if the measurement is not an instantaneous one.
Time variables used as DEPEND_0 are strongly recommended to have DELTA_PLUS_VAR and DELTA_MINUS_VAR attributes which delineate the time interval over which the data was sampled, integrated, or otherwise representative of.
This also locates the timetag within that interval.

The epoch datatype, CDF_TIME_TT2000, is defined as an 8-byte signed integer with the characteristics shown in Table 5-3.

.. list-table:: Table 4-3: Characteristics of CDF_TIME_TT2000
   :widths: 25 50
   :header-rows: 1

   * - Name
     - Example
   * - time_base
     - J2000 (Julian date 2451545.0 TT or 2000 January 1, 12h TT)
   * - resolution
     - nanoseconds
   * - time_scale
     - Terrestrial Time (TT)
   * - units
     - nanoseconds
   * - reference_position
     - rotating Earth Geoid

Given a current list of leap seconds, conversion between TT and UTC is straightforward (TT = TAI + 32.184s; TT = UTC + deltaAT + 32.184s, where deltaAT is the sum of the leap seconds since 1960; for example, for 2009, deltaAT = 34s).
Pad values of -9223372036854775808 (0x8000000000000000) which corresponds to 1707-09-22T12:13:15.145224192; recommended FILLVAL is same.

It is proposed that the required data variables VALIDMIN and VALIDMAX are given values corresponding to the dates 1990-01-01T00:00:00 and 2100-01-01T00:00:00 as these are well outside any expected valid times.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.1.3 Required Attributes: Data Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data variables require the following attributes:

* CATDESC
* DEPEND_0
* DEPEND_i [for dimensional data variables]
* DISPLAY_TYPE
* FIELDNAM
* FILLVAL
* FORMAT or FORM_PTR
* LABLAXIS or LABL_PTR_i
* SI_CONVERSION
* UNITS or UNIT_PTR
* VALIDMIN and VALIDMAX
* VAR_TYPE

In addition, the following attributes are strongly recommended for vectors, tensors and quaternions which are held in or relate to a particular coordinate system:

* COORDINATE_SYSTEM
* TENSOR_ORDER
* REPRESENTATION_i
* OPERATOR_TYPE [for quaternions]

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.1.4 Attributes for DEPEND_i Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Variables appearing in a data variable's DEPEND_i attribute require a minimal set of their own attributes to fulfill their role in supporting the data variable.
The standard SUPPORT_DATA variable attributes are listed in Section 4.2.2.
Other standard variable attributes are optional.

--------------------------------------
4.2 Support Data
--------------------------------------

These are variables of secondary importance employed as DEPEND_i variables as described in section 4.1.3 (e.g., time, energy_bands associated with particle flux), but they may also be used for housekeeping or other information not normally used for scientific analysis.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.2.1 Naming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Support data variable names must begin with a letter and can contain numbers and underscores, but no other special characters.
Support data variable names need not follow the same naming convention as Data Variables (4.1.1) but may be shortened for convenience.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.2.2 Required Attributes: Support Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* CATDESC
* DEPEND_0 (if time varying)
* FIELDNAM
* FILLVAL (if time varying)
* FORMAT/FORM_PTR
* LABLAXIS or LABL_PTR_i
* SI_CONVERSION
* UNITS/UNIT_PTR
* VALIDMIN (if time varying)
* VALIDMAX (if time varying)
* VAR_TYPE = “support_data”

Other attributes may also be present.

--------------------------------------
4.3 Metadata
--------------------------------------

These are variables of secondary importance (e.g. a variable holding "Bx”, “By”, “Bz" to label magnetic field).
Metadata are usually text strings as opposed to the numerical values held in DEPEND_i support data.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.3.1 Naming
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Metadata variable names must begin with a letter and can contain numbers and underscores, but no other special characters.
Metadata variable names need not follow the same naming convention as Data Variables (4.1.1) but may be shortened for convenience.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
4.3.2 Required Attributes: Metadata Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* CATDESC
* DEPEND_0 (if time varying, this value must be “Epoch”)
* FIELDNAM
* FILLVAL (if time varying)
* FORMAT/FORM_PTR
* VAR_TYPE = metadata

--------------------------------------
4.4 Variable Attribute Schema
--------------------------------------

The following variable attributes shown in Table 5-4 are required with ISTP-compliant data products.
For each attribute the following information is provided:

* description: (`str`) A brief description of the attribute
* required: (`bool`) Whether the attribute is required by ISTP standards
* valid_values: (`list`) List of allowed values the attribute can take for ISTP-compliant products,
  if applicable
* alternate: (`str`) An additional attribute name that can be treated as an alternative
  of the given attribute. Not all attributes have an alternative and only one of a given
  attribute or its alternate are required.
* var_types: (`str`) A list of the variable types that require the given
  attribute to be present.

Note that this table is derived from :file:`sammi/data/default_variable_cdf_attrs_schema.yaml`

.. csv-table:: Table 4-4 SWxSOC Variable Attribute Schema
   :file: ../generated/variable_attributes.csv