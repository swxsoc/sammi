import pytest
import tempfile
from pathlib import Path
from collections import OrderedDict
import yaml
import pandas as pd

from sammi.schema import SWxSchema


def test_sw_schema_default():
    """Test Creating a Schema with Default Parameters"""
    schema = SWxSchema()

    # Global Attribute Schema
    assert schema.global_attribute_schema is not None
    assert isinstance(schema.global_attribute_schema, dict)

    # Variable Attribute Schema
    assert schema.variable_attribute_schema is not None
    assert isinstance(schema.variable_attribute_schema, dict)

    # Default Global Attributes
    assert schema.default_global_attributes is not None
    assert isinstance(schema.default_global_attributes, dict)


def test_sw_schema_invalid_params():
    """Test Creating a Schema with Invalid Parameters"""
    with pytest.raises(ValueError):
        _ = SWxSchema(
            global_schema_layers=None, variable_schema_layers=None, use_defaults=None
        )


def test_sw_schema_custom_layers():
    """Test Creating a Schema with Custom Layers"""
    with tempfile.TemporaryDirectory() as tmpdirname:

        # Create Extra Global Layer for Testing
        global_layer_content = """
        test_attribute:
            description: This is a test attribute
            default: null
            required: true
        Data_type:
            description: >
                This attribute is used by CDF file writing software to create a filename.
            default: null
            required: true   # NOT originally required in Default Schema
        """

        global_test_path = Path(tmpdirname) / "global_test.yaml"
        with open(global_test_path, "w") as file:
            file.write(global_layer_content)
        assert global_test_path.is_file()

        # Create Extra Variable Layer for Testing
        variable_layer_content = """
        attribute_key:
            test_attribute:
                description: This is a test attribute
                required: true
                valid_values: null
                alternate: null
            SI_CONVERSION:
                description: The conversion factor to SI units.
                required: true  # NOT originally required in Default Schema
                valid_values: null
                alternate: null
        data:
            - test_attribute
            - SI_CONVERSION
        support_data:
            - test_attribute
            - SI_CONVERSION
        metadata:
            - test_attribute
        """

        variable_test_path = Path(tmpdirname) / "variable_test.yaml"
        with open(variable_test_path, "w") as file:
            file.write(variable_layer_content)
        assert variable_test_path.is_file()

        schema = SWxSchema(
            global_schema_layers=[global_test_path],
            variable_schema_layers=[variable_test_path],
            use_defaults=True,
        )

        assert schema.global_attribute_schema is not None
        # Assert Test Attribute is Added to the Global Schema
        assert "test_attribute" in schema.global_attribute_schema
        assert schema.global_attribute_schema["test_attribute"]["required"]
        # Assert Data_type is Overwritten in Global Schema
        assert "Data_type" in schema.global_attribute_schema
        assert schema.global_attribute_schema["Data_type"]["required"]

        assert schema.variable_attribute_schema is not None
        # Assert Test Attribute is Added to the Variable Schema
        assert "test_attribute" in schema.variable_attribute_schema["attribute_key"]
        assert schema.variable_attribute_schema["attribute_key"]["test_attribute"][
            "required"
        ]
        # Assert SI_CONVERSION is Overwritten in Variable Schema
        assert "SI_CONVERSION" in schema.variable_attribute_schema["attribute_key"]
        assert schema.variable_attribute_schema["attribute_key"]["SI_CONVERSION"][
            "required"
        ]

        # Assert Var Type Lists are Updated
        assert len(schema.variable_attribute_schema["data"]) > 2
        assert len(schema.variable_attribute_schema["support_data"]) > 2
        assert len(schema.variable_attribute_schema["metadata"]) > 1
        assert "test_attribute" in schema.variable_attribute_schema["data"]
        assert "test_attribute" in schema.variable_attribute_schema["support_data"]
        assert "test_attribute" in schema.variable_attribute_schema["metadata"]
        assert "SI_CONVERSION" in schema.variable_attribute_schema["data"]
        assert "SI_CONVERSION" in schema.variable_attribute_schema["support_data"]
        assert "SI_CONVERSION" not in schema.variable_attribute_schema["metadata"]


def test_sw_templates():
    """Test Global and Measurement Attribute Templates"""
    schema = SWxSchema()

    # Global Attribute Template
    assert schema.global_attribute_template() is not None
    assert isinstance(schema.global_attribute_template(), OrderedDict)

    # Measurement Attribute Template
    assert schema.measurement_attribute_template() is not None
    assert isinstance(schema.measurement_attribute_template(), OrderedDict)


def test_sw_info():
    """Test Global and Measurement Attribute Info Functions"""
    schema = SWxSchema()

    # Global Attribute Info
    assert schema.global_attribute_info() is not None
    assert isinstance(schema.global_attribute_info(), pd.DataFrame)
    assert isinstance(
        schema.global_attribute_info(attribute_name="Descriptor"), pd.DataFrame
    )
    with pytest.raises(KeyError):
        _ = schema.global_attribute_info(attribute_name="NotAnAttribute")

    # Measurement Attribute Info
    assert schema.measurement_attribute_info() is not None
    assert isinstance(schema.measurement_attribute_info(), pd.DataFrame)
    assert isinstance(
        schema.measurement_attribute_info(attribute_name="CATDESC"), pd.DataFrame
    )
    with pytest.raises(KeyError):
        _ = schema.measurement_attribute_info(attribute_name="NotAnAttribute")


def test_load_yaml_data():
    """Test Loading Yaml Data for Schema Files"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # This function writes invalid YAML content into a file
        invalid_yaml = """
        name: John Doe
        age 30
        """

        with open(tmpdirname + "test.yaml", "w") as file:
            file.write(invalid_yaml)

        # Load from an non-existant file
        with pytest.raises(yaml.YAMLError):
            _ = SWxSchema()._load_yaml_data(tmpdirname + "test.yaml")
