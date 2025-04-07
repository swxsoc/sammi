from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
import yaml

import sammi

__all__ = ["CdfAttributeManager"]

DEFAULT_GLOBAL_CDF_ATTRS_SCHEMA_FILE = "default_global_cdf_attrs_schema.yaml"
DEFAULT_VARIABLE_CDF_ATTRS_SCHEMA_FILE = "default_variable_cdf_attrs_schema.yaml"


class CdfAttributeManager:
    """
    Class for creating and managing CDF attributes based out of yaml files.
    The SAMMI default schema only includes attributes required for ISTP compliance.
    Additional mission-specific attributes or requirements should be added through additional global and variable schema layers.

    There are two main components to the SAMMI  CDF Attribut Manager, including both global and variable attribute information.

    Global schema information is loaded from YAML (dict-like) files in the following format:

    .. code-block:: yaml

        attribute_name:
            description: >
                Include a meaningful description of the attribute and context needed to understand
                its values.
            default: <string> # A default value for the attribute if needed/desired
            required: <bool> # Whether the attribute is required

    Variable schema information is loaded from YAML (dict-like) files in the following format:

    .. code-block:: yaml

        attribute_key:
            attribute_name:
                description: >
                    Include a meaningful description of the attribute and context needed to understand
                    its values.
                required: <bool> # Whether the attribute is required
                valid_values: <list> # A list of valid values that the attribute can take.
                alternate: <string> An additional attribute name that can be treated as an alternative of the given attribute.
        data:
            - attribute_name
            - ...
        support_data:
            - ...
        metadata:
            - ...

    Parameters
    ----------
    global_schema_layers :  `Optional[list[Path]]`
        Absolute file paths to global attribute schema files. These schema files are layered
        on top of one another in a latest-priority ordering. That is, the latest file that modifies
        a common schema attribute will take precedence over earlier values for a given attribute.
    variable_schema_layers :  `Optional[list[Path]]`
        Absolute file paths to variable attribute schema files. These schema files are layered
        on top of one another in a latest-priority ordering. That is, the latest file that modifies
        a common schema attribute will take precedence over earlier values for a given attribute.
    use_defaults: `Optional[bool]`
        Whether or not to load the default global and variable attribute schema files. These
        default schema files contain only the requirements for CDF ISTP validation.


    Examples
    --------
    To use, you can load one or many global and variable attribute files:


    >>> import sammi
    >>> cdf_attr_manager = sammi.cdf_attribute_manager.CdfAttributeManager(use_defaults=True)
    >>> data_path = Path(sammi.__file__).parent.parent / "sammi" / "data"
    >>> cdf_attr_manager.load_global_attributes(data_path / "default_global_cdf_attrs_schema.yaml")
    >>> cdf_attr_manager.load_global_attributes(data_path / "default_variable_cdf_attrs_schema.yaml")
    >>> cdf_attr_manager.load_variable_attributes(data_path / "variable_attrs.yaml") #doctest: +SKIP

    Later files will overwrite earlier files if the same attribute is defined.

    You can then get the global and variable attributes:

    If you provide an instrument_id, it will also add the attributes defined under
    instrument_id. If this is not included, then only the attributes defined in the top
    level of the file are used.


    >>> # Instrument ID is optional for refining the attributes used from the file
    >>> global_attrs = cdf_attr_manager.get_global_attributes("instrument_id")
    >>> variable_attrs = cdf_attr_manager.get_variable_attributes("Epoch") #doctest: +SKIP

    The variable and global attributes are validated against the schemas upon calling
    ``get_global_attributes`` and ``get_variable_attributes``.

    """

    def __init__(
        self,
        global_schema_layers: Optional[list[Path]] = None,
        variable_schema_layers: Optional[list[Path]] = None,
        use_defaults: Optional[bool] = True,
    ) -> None:
        # Input Validation
        if not use_defaults and (
            not global_schema_layers
            or not variable_schema_layers
            or len(global_schema_layers) == 0
            or len(variable_schema_layers) == 0
        ):
            raise ValueError(
                "Not enough information to create schema. You must either use the defaults or provide alternative layers for both global and variable attribbute schemas."
            )

        # Construct the Global Attribute Schema
        _global_attr_schema = {}
        if use_defaults:
            _def_global_attr_schema = self._load_default_global_attr_schema()
            _global_attr_schema = self._merge(
                base_layer=_global_attr_schema, new_layer=_def_global_attr_schema
            )
        if global_schema_layers is not None:
            for schema_layer_path in global_schema_layers:
                _global_attr_layer = CdfAttributeManager._load_yaml_data(
                    file_path=schema_layer_path
                )
                _global_attr_schema = self._merge(
                    base_layer=_global_attr_schema, new_layer=_global_attr_layer
                )
        # Set Final Member
        self._global_attr_schema = _global_attr_schema

        # Data Validation and Compliance for Variable Data
        _variable_attr_schema = {}
        if use_defaults:
            _def_variable_attr_schema = self._load_default_variable_attr_schema()
            _variable_attr_schema = self._merge(
                base_layer=_variable_attr_schema, new_layer=_def_variable_attr_schema
            )
        if variable_schema_layers is not None:
            for schema_layer_path in variable_schema_layers:
                _variable_attr_layer = CdfAttributeManager._load_yaml_data(
                    file_path=schema_layer_path
                )
                _variable_attr_schema = self._merge(
                    base_layer=_variable_attr_schema, new_layer=_variable_attr_layer
                )
        # Set the Final Member
        self._variable_attr_schema = _variable_attr_schema

        self._variable_attributes: dict = {}
        self._global_attributes: dict = self._load_default_global_attributes()

    @property
    def global_attribute_schema(self):
        """(`dict`) Schema for variable attributes of the file."""
        return self._global_attr_schema

    @property
    def variable_attribute_schema(self):
        """(`dict`) Schema for variable attributes of the file."""
        return self._variable_attr_schema

    # =========================================================================
    #                       INITIALIZATION FUNCTIONS
    # =========================================================================

    def _load_default_global_attr_schema(self) -> dict:
        """
        Load the default global schema from the source directory.

        Returns
        -------
        dict
            The dict representing the global schema.
        """
        # The Default Schema file is contained in the `sammi/data` directory
        default_schema_path = str(
            Path(sammi.__file__).parent.parent
            / "sammi"
            / "data"
            / DEFAULT_GLOBAL_CDF_ATTRS_SCHEMA_FILE
        )
        # Load the Schema
        return CdfAttributeManager._load_yaml_data(file_path=default_schema_path)

    def _load_default_variable_attr_schema(self) -> dict:
        """
        Load the default variable schema from the source directory.

        Returns
        -------
        dict
            The dict representing the variable schema.
        """
        # The Default Schema file is contained in the `sammi/data` directory
        default_schema_path = str(
            Path(sammi.__file__).parent.parent
            / "sammi"
            / "data"
            / DEFAULT_VARIABLE_CDF_ATTRS_SCHEMA_FILE
        )
        # Load the Schema
        return CdfAttributeManager._load_yaml_data(file_path=default_schema_path)

    def _load_default_global_attributes(self) -> dict:
        # Use the Existing Global Schema
        global_schema = self.global_attribute_schema
        return {
            attr_name: info["default"]
            for attr_name, info in global_schema.items()
            if info["default"] is not None
        }

    @staticmethod
    def _load_yaml_data(file_path: Path) -> dict:
        """
        Load a yaml file from the provided path.

        Parameters
        ----------
        file_path : `Path`
            Path to the yaml file to load.

        Returns
        -------
        dict
            Loaded yaml.
        """
        assert Path(file_path).exists()
        # Load the Yaml file to Dict
        yaml_data = {}
        with open(file_path, "rb") as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def _merge(self, base_layer: dict, new_layer: dict, path: list = None) -> None:
        """
        Function to do in-place merging and updating of two dictionaries.
        This is an improvemnent over the built-in dict.update() method, as it allows for nested dictionaries and lists.

        Parameters
        ----------
        base_layer : `dict`
            The base dictionary to merge into.
        new_layer : `dict`
            The new dictionary to merge into the base.
        path : `list`
            The path to the current dictionary being merged. Used for recursion.

        Returns
        -------
        None - operation is done in-place.
        """
        # If we are at the top of the recursion, and we don't have a path, create a new one
        if not path:
            path = []
        # for each key in the base layer
        for key in new_layer:
            # If its a shared key
            if key in base_layer:
                # If both are dictionaries
                if isinstance(base_layer[key], dict) and isinstance(
                    new_layer[key], dict
                ):
                    # Merge the two nested dictionaries together
                    self._merge(base_layer[key], new_layer[key], path + [str(key)])
                # If both are lists
                elif isinstance(base_layer[key], list) and isinstance(
                    new_layer[key], list
                ):
                    # Extend the list of the base layer by the new layer
                    base_layer[key].extend(new_layer[key])
                # If they are not lists or dicts (scalars)
                elif base_layer[key] != new_layer[key]:
                    # We've reached a conflict, may want to overwrite the base with the new layer.
                    base_layer[key] = new_layer[key]
            # If its not a shared key
            else:
                base_layer[key] = new_layer[key]
        return base_layer

    # =========================================================================
    #                       GLOBAL ATTRIBUTE FUNCTIONS
    # =========================================================================

    def load_global_attributes(self, file_path: Path) -> None:
        """
        Update the global attributes property with the attributes from the file.

        Calling this method multiple times on different files will add all the
        attributes from the files, overwriting existing attributes if they are
        duplicated.

        Parameters
        ----------
        file_path : `Path`
            File path to load the global attributes from.
        """
        new_global_layer = CdfAttributeManager._load_yaml_data(file_path)
        self._merge(self._global_attributes, new_global_layer)

    def add_global_attribute(self, attribute_name: str, attribute_value: str) -> None:
        """
        Add a single global attribute to the global attributes.

        This is intended only for dynamic global attributes which change per-file, such
        as Data_version. It is not intended to be used for static attributes, which
        should all be included in the YAML files.

        This will overwrite any existing value in attribute_name if it exists. The
        attribute must be in the global schema, or it will not be included as output.

        Parameters
        ----------
        attribute_name : str
            The name of the attribute to add.
        attribute_value : str
            The value of the attribute to add.
        """
        self._global_attributes[attribute_name] = attribute_value

    def get_global_attributes(self, instrument_id: str | None = None) -> dict:
        """
        Generate a dictionary global attributes based off the loaded schema and attrs.

        Validates against the global schema to ensure all required variables are
        present. It can also include instrument specific global attributes if
        instrumet_id is set.

        If an instrument_id is provided, the level and instrument specific
        attributes that were previously loaded using add_instrument_global_attrs will
        be included.

        Parameters
        ----------
        instrument_id : str
            The id of the CDF file, used to retrieve instrument and level
            specific global attributes. Suggested value is the logical_source_id.

        Returns
        -------
        output : dict
            The global attribute values created from the input global attribute files
            and schemas.
        """
        output = dict()
        for attr_name, attr_schema in self.global_attribute_schema.items():
            if attr_name in self._global_attributes:
                output[attr_name] = self._global_attributes[attr_name]
            # Retrieve instrument specific global attributes from the variable file
            elif (
                instrument_id is not None
                and attr_name in self._global_attributes[instrument_id]
            ):
                output[attr_name] = self._global_attributes[instrument_id][attr_name]
            elif attr_schema["required"] and attr_name not in self._global_attributes:
                # TODO throw an error
                output[attr_name] = None
        return output

    def global_attribute_template(self) -> dict:
        """
        Function to generate a template of required global attributes
        that must be set for a valid data file.

        Returns
        -------
        template : `dict`
            A template for required global attributes that must be provided.
        """
        template = {}
        for attr_name, attr_schema in self.global_attribute_schema.items():
            if attr_schema["required"] and attr_name not in self._global_attributes:
                template[attr_name] = None
        return template

    def global_attribute_info(self, attribute_name: Optional[str] = None) -> dict:
        """
        Function to generate a `dict` of information about each global
        metadata attribute. The `dict` contains all information in the
        global attribute schema including:

        - description: (`str`) A brief description of the attribute
        - default: (`str`) The default value used if none is provided
        - required: (`bool`) Whether the attribute is required


        Parameters
        ----------
        attribute_name : `str`, optional, default None
            The name of the attribute to get specific information for.

        Returns
        -------
        info: `dict`
            information about global metadata

        Raises
        ------
        KeyError: If attribute_name is not a recognized global attribute.
        """
        info = self.global_attribute_schema.copy()

        # Strip the Description of New Lines
        for attr_name in info.keys():
            info[attr_name]["description"] = info[attr_name]["description"].strip()

        # Limit the Info to the requested Attribute
        if attribute_name and attribute_name in info:
            info = info[attribute_name]
        elif attribute_name and attribute_name not in info:
            raise KeyError(
                f"Cannot find Global Metadata for attribute name: {attribute_name}"
            )

        return info

    # =========================================================================
    #                       VARIABLE ATTRIBUTE FUNCTIONS
    # =========================================================================

    def load_variable_attributes(self, file_path: Path) -> None:
        """
        Update the variable attributes property with the attributes from the file.

        Calling this method multiple times on different files will add all the
        attributes from the files, overwriting existing attributes if they are
        duplicated.

        Parameters
        ----------
        file_path : `Path`
            File path to load the variable attributes from.
        """
        new_variable_layer = CdfAttributeManager._load_yaml_data(file_path)
        self._merge(self._variable_attributes, new_variable_layer)

    def get_variable_attributes(
        self, variable_name: str, check_schema: bool = True
    ) -> dict:
        """
        Get the attributes for a given variable name.

        It retrieves the variable from previously loaded variable definition files and
        validates against the defined variable schemas.

        Parameters
        ----------
        variable_name : str
            The name of the variable to retrieve attributes for.

        check_schema : bool
            Flag to bypass schema validation.

        Returns
        -------
        dict
            Information containing specific variable attributes
            associated with "variable_name".
        """
        # Case to handle attributes not in schema
        if check_schema is False:
            if variable_name in self._variable_attributes:
                return_dict: dict = self._variable_attributes[variable_name]
                return return_dict
            # TODO: throw an error?
            return {}

        output = dict()
        for attr_name in self.variable_attribute_schema["attribute_key"]:
            # Standard case
            if attr_name in self._variable_attributes[variable_name]:
                output[attr_name] = self._variable_attributes[variable_name][attr_name]
            # Case to handle DEPEND_i schema issues
            elif attr_name == "DEPEND_i":
                # DEFAULT_0 is not required, UNLESS we are dealing with
                # variable_name = epoch
                # Find all the attributes of variable_name that contain "DEPEND"
                variable_depend_attrs = [
                    key
                    for key in self._variable_attributes[variable_name].keys()
                    if "DEPEND" in key
                ]
                # Confirm that each DEPEND_i attribute is unique
                if len(set(variable_depend_attrs)) != len(variable_depend_attrs):
                    logging.warning(
                        f"Found duplicate DEPEND_i attribute in variable "
                        f"{variable_name}: {variable_depend_attrs}"
                    )
                for variable_depend_attr in variable_depend_attrs:
                    output[variable_depend_attr] = self._variable_attributes[
                        variable_name
                    ][variable_depend_attr]
                # TODO: Add more DEPEND_0 variable checks!
            # Case to handle LABL_PTR_i schema issues
            elif attr_name == "LABL_PTR_i":
                # Find all the attributes of variable_name that contain "LABL_PTR"
                variable_labl_attrs = [
                    key
                    for key in self._variable_attributes[variable_name].keys()
                    if "LABL_PTR" in key
                ]
                for variable_labl_attr in variable_labl_attrs:
                    output[variable_labl_attr] = self._variable_attributes[
                        variable_name
                    ][variable_labl_attr]
            # Case to handle REPRESENTATION_i schema issues
            elif attr_name == "REPRESENTATION_i":
                # Find all the attributes of variable_name that contain
                # "REPRESENTATION_i"
                variable_rep_attrs = [
                    key
                    for key in self._variable_attributes[variable_name].keys()
                    if "REPRESENTATION" in key
                ]
                for variable_rep_attr in variable_rep_attrs:
                    output[variable_rep_attr] = self._variable_attributes[
                        variable_name
                    ][variable_rep_attr]
            # Validating required schema
            elif (
                self.variable_attribute_schema["attribute_key"][attr_name]["required"]
                and attr_name not in self._variable_attributes[variable_name]
            ):
                logging.warning(
                    "Required schema '"
                    + attr_name
                    + "' attribute not present for "
                    + variable_name
                )
                output[attr_name] = ""

        return output

    def variable_attribute_template(self) -> dict:
        """
        Function to generate a template of required variable attributes
        that must be set for a valid data file.

        Returns
        -------
        template: `dict`
            A template for required variable attributes that must be provided.
        """
        template = {}
        for attr_name, attr_schema in self.variable_attribute_schema[
            "attribute_key"
        ].items():
            if attr_schema["required"]:
                template[attr_name] = None
        return template

    def variable_attribute_info(self, attribute_name: Optional[str] = None) -> dict:
        """
        Function to generate a `dict` of information about each variable
        metadata attribute. The `dict` contains all information in the SWxSOC
        variable attribute schema including:

        - description: (`str`) A brief description of the attribute
        - required: (`bool`) Whether the attribute is required by SWxSOC standards
        - valid_values: (`str`) List of allowed values the attribute can take for SWxSOC products,
            if applicable
        - alternate: (`str`) An additional attribute name that can be treated as an alternative
            of the given attribute. Not all attributes have an alternative and only one of a given
            attribute or its alternate are required.
        - var_types: (`str`) A list of the variable types that require the given
            attribute to be present.

        Parameters
        ----------
        attribute_name : `str`, optional, default None
            The name of the attribute to get specific information for.

        Returns
        -------
        info: `dict`
            information about variable metadata

        Raises
        ------
        KeyError: If attribute_name is not a recognized variable attribute.
        """
        info = self.variable_attribute_schema["attribute_key"].copy()

        # Strip the Description of New Lines
        for attr_name in info.keys():
            info[attr_name]["description"] = info[attr_name]["description"].strip()

        # Create New Column to describe which VAR_TYPE's require the given attribute
        for attr_name in info.keys():
            # Create a new list to store the var types
            info[attr_name]["var_types"] = []
            for var_type in ["data", "support_data", "metadata"]:
                # If the attribute is required for the given var type
                if attr_name in self.variable_attribute_schema[var_type]:
                    info[attr_name]["var_types"].append(var_type)
            # Convert the list to a string that can be written to a CSV from the table
            info[attr_name]["var_types"] = ", ".join(info[attr_name]["var_types"])

        # Limit the Info to the requested Attribute
        if attribute_name and attribute_name in info:
            info = info[attribute_name]
        elif attribute_name and attribute_name not in info:
            raise KeyError(
                f"Cannot find Variable Metadata for attribute name: {attribute_name}"
            )

        return info
