"""
This module provides schema metadata templates an information.

"""

from pathlib import Path
from collections import OrderedDict
from typing import Optional
import yaml

import sammi

__all__ = ["SWxSchema"]

DEFAULT_GLOBAL_CDF_ATTRS_SCHEMA_FILE = "default_global_cdf_attrs_schema.yaml"
DEFAULT_VARIABLE_CDF_ATTRS_SCHEMA_FILE = "default_variable_cdf_attrs_schema.yaml"


class SWxSchema:
    """
    Class representing a schema for data requirements and formatting. The SWxSOC Default Schema
    only includes attributes required for ISTP compliance. Additional mission-specific attributes
    or requirements should be added through additional global and variable schema layers. For an
    example of how to layer schema files, please see the HERMES mission core package, and
    `HermesDataSchema` extension of the `SWXSchema` class.

    There are two main components to the Space Weather Data Schema, including both global and
    variable attribute information.

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

    """

    def __init__(
        self,
        global_schema_layers: Optional[list[Path]] = None,
        variable_schema_layers: Optional[list[Path]] = None,
        use_defaults: Optional[bool] = True,
    ):
        super().__init__()

        # Input Validation
        if not use_defaults and (
            global_schema_layers is None
            or variable_schema_layers is None
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
                _global_attr_layer = self._load_yaml_data(
                    yaml_file_path=schema_layer_path
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
                _variable_attr_layer = self._load_yaml_data(
                    yaml_file_path=schema_layer_path
                )
                _variable_attr_schema = self._merge(
                    base_layer=_variable_attr_schema, new_layer=_variable_attr_layer
                )
        # Set the Final Member
        self._variable_attr_schema = _variable_attr_schema

        # Load Default Global Attributes
        self._default_global_attributes = self._load_default_attributes()

    @property
    def global_attribute_schema(self):
        """(`dict`) Schema for variable attributes of the file."""
        return self._global_attr_schema

    @property
    def variable_attribute_schema(self):
        """(`dict`) Schema for variable attributes of the file."""
        return self._variable_attr_schema

    @property
    def default_global_attributes(self):
        """(`dict`) Default Global Attributes applied for all SWxSOC Data Files"""
        return self._default_global_attributes

    def _load_default_global_attr_schema(self) -> dict:
        # The Default Schema file is contained in theschema/data` directory
        default_schema_path = str(
            Path(sammi.__file__).parent.parent
            / "sammi"
            / "data"
            / DEFAULT_GLOBAL_CDF_ATTRS_SCHEMA_FILE
        )
        # Load the Schema
        return self._load_yaml_data(yaml_file_path=default_schema_path)

    def _load_default_variable_attr_schema(self) -> dict:
        # The Default Schema file is contained in the `swxschema/data` directory
        default_schema_path = str(
            Path(sammi.__file__).parent.parent
            / "sammi"
            / "data"
            / DEFAULT_VARIABLE_CDF_ATTRS_SCHEMA_FILE
        )
        # Load the Schema
        return self._load_yaml_data(yaml_file_path=default_schema_path)

    def _load_default_attributes(self) -> dict:
        # Use the Existing Global Schema
        global_schema = self.global_attribute_schema
        return {
            attr_name: info["default"]
            for attr_name, info in global_schema.items()
            if info["default"] is not None
        }

    def _load_yaml_data(self, yaml_file_path: Path) -> dict:
        """
        Function to load data from a Yaml file.

        Parameters
        ----------
        yaml_file_path: `Path`
            Path to schema file to be used for formatting.

        """
        assert Path(yaml_file_path).exists()
        # Load the Yaml file to Dict
        yaml_data = {}
        with open(yaml_file_path, "r") as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def global_attribute_template(self) -> OrderedDict:
        """
        Function to generate a template of required global attributes
        that must be set for a valid data file.

        Returns
        -------
        template : `OrderedDict`
            A template for required global attributes that must be provided.
        """
        template = OrderedDict()
        for attr_name, attr_schema in self.global_attribute_schema.items():
            if (
                attr_schema["required"]
                and attr_name not in self.default_global_attributes
            ):
                template[attr_name] = None
        return template

    def measurement_attribute_template(self) -> OrderedDict:
        """
        Function to generate a template of required measurement attributes
        that must be set for a valid data file.

        Returns
        -------
        template: `OrderedDict`
            A template for required variable attributes that must be provided.
        """
        template = OrderedDict()
        for attr_name, attr_schema in self.variable_attribute_schema[
            "attribute_key"
        ].items():
            if attr_schema["required"]:
                template[attr_name] = None
        return template

    def global_attribute_info(self, attribute_name: Optional[str] = None):
        """
        Function to generate a `pd.DataFrame` of information about each global
        metadata attribute. The `pd.DataFrame` contains all information in the SWxSOC
        global attribute schema including:

        - description: (`str`) A brief description of the attribute
        - default: (`str`) The default value used if none is provided
        - required: (`bool`) Whether the attribute is required by SWxSOC standards


        Parameters
        ----------
        attribute_name : `str`, optional, default None
            The name of the attribute to get specific information for.

        Returns
        -------
        info: `pd.DataFrame`
            A table of information about global metadata.

        Raises
        ------
        KeyError: If attribute_name is not a recognized global attribute.
        """
        import pandas as pd

        # Strip the Description of New Lines
        for attr_name in self.global_attribute_schema.keys():
            self.global_attribute_schema[attr_name]["description"] = (
                self.global_attribute_schema[attr_name]["description"].strip()
            )

        # Create the Info Table
        info = pd.DataFrame.from_dict(self.global_attribute_schema, orient="index")
        # Reset the Index, add Attribute as new column
        info.reset_index(names="Attribute", inplace=True)

        # Limit the Info to the requested Attribute
        if attribute_name and attribute_name in info["Attribute"].values:
            info = info[info["Attribute"] == attribute_name]
        elif attribute_name and attribute_name not in info["Attribute"].values:
            raise KeyError(
                f"Cannot find Global Metadata for attribute name: {attribute_name}"
            )

        return info

    def measurement_attribute_info(self, attribute_name: Optional[str] = None):
        """
        Function to generate a `pd.DataFrame` of information about each variable
        metadata attribute. The `pd.DataFrame` contains all information in the SWxSOC
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
        info: `pd.DataFrame`
            A table of information about variable metadata.

        Raises
        ------
        KeyError: If attribute_name is not a recognized variable attribute.
        """
        import pandas as pd

        measurement_attribute_key = self.variable_attribute_schema["attribute_key"]

        # Strip the Description of New Lines
        for attr_name in measurement_attribute_key.keys():
            measurement_attribute_key[attr_name]["description"] = (
                measurement_attribute_key[attr_name]["description"].strip()
            )

        # Create New Column to describe which VAR_TYPE's require the given attribute
        for attr_name in measurement_attribute_key.keys():
            # Create a new list to store the var types
            measurement_attribute_key[attr_name]["var_types"] = []
            for var_type in ["data", "support_data", "metadata"]:
                # If the attribute is required for the given var type
                if attr_name in self.variable_attribute_schema[var_type]:
                    measurement_attribute_key[attr_name]["var_types"].append(var_type)
            # Convert the list to a string that can be written to a CSV from the table
            measurement_attribute_key[attr_name]["var_types"] = ", ".join(
                measurement_attribute_key[attr_name]["var_types"]
            )

        # Create the Info Table
        info = pd.DataFrame.from_dict(measurement_attribute_key, orient="index")
        # Reset the Index, add Attribute as new column
        info.reset_index(names="Attribute", inplace=True)

        # Limit the Info to the requested Attribute
        if attribute_name and attribute_name in info["Attribute"].values:
            info = info[info["Attribute"] == attribute_name]
        elif attribute_name and attribute_name not in info["Attribute"].values:
            raise KeyError(
                f"Cannot find Variable Metadata for attribute name: {attribute_name}"
            )

        return info

    def _merge(self, base_layer: dict, new_layer: dict, path: list = None):
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
                if isinstance(base_layer[key], list) and isinstance(
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
