from pathlib import Path
import tempfile

import pytest
import yaml

from sammi.cdf_attribute_manager import CdfAttributeManager


@pytest.fixture()
def cdf_manager():
    """Initialize CdfAttributeManager with default properties."""
    cdf_manager = CdfAttributeManager(use_defaults=True)
    return cdf_manager


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
            _ = CdfAttributeManager()._load_yaml_data(tmpdirname + "test.yaml")


def test_default_attr_schema(cdf_manager):
    """
    Test function that covers:
        _load_default_global_attr_schema
        _load_default_variable_attr_schema
    """

    # Default global tests
    assert cdf_manager.global_attribute_schema["DOI"]["required"] is False
    assert cdf_manager.global_attribute_schema["Data_type"]["required"] is True

    # Default variable tests
    assert (
        cdf_manager.variable_attribute_schema["attribute_key"]["ABSOLUTE_ERROR"][
            "required"
        ]
        is False
    )
    assert (
        cdf_manager.variable_attribute_schema["attribute_key"]["CATDESC"]["required"]
        is True
    )


def test_cdf_manager_invalid_params():
    """Test Creating a Schema with Invalid Parameters"""
    with pytest.raises(ValueError):
        _ = CdfAttributeManager(
            global_schema_layers=None, variable_schema_layers=None, use_defaults=None
        )


def test_cdf_manager_custom_layers():
    """Test Creating a Schema with Custom Layers"""
    with tempfile.TemporaryDirectory() as tmpdirname:

        # Create Extra Global Layer for Testing
        global_layer_content = """
        test_attribute:
            description: This is a test attribute
            default: null
            required: true
        Data_type:
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

        cdf_manager = CdfAttributeManager(
            global_schema_layers=[global_test_path],
            variable_schema_layers=[variable_test_path],
            use_defaults=True,
        )

        assert cdf_manager.global_attribute_schema is not None
        # Assert Test Attribute is Added to the Global Schema
        assert "test_attribute" in cdf_manager.global_attribute_schema
        assert cdf_manager.global_attribute_schema["test_attribute"]["required"]
        # Assert Data_type is Overwritten in Global Schema
        assert "Data_type" in cdf_manager.global_attribute_schema
        assert cdf_manager.global_attribute_schema["Data_type"]["required"]
        # Assert other Data_type attributes are not overwritten
        assert (
            cdf_manager.global_attribute_schema["Data_type"]["description"] is not None
        )

        assert cdf_manager.variable_attribute_schema is not None
        # Assert Test Attribute is Added to the Variable Schema
        assert (
            "test_attribute" in cdf_manager.variable_attribute_schema["attribute_key"]
        )
        assert cdf_manager.variable_attribute_schema["attribute_key"]["test_attribute"][
            "required"
        ]
        # Assert SI_CONVERSION is Overwritten in Variable Schema
        assert "SI_CONVERSION" in cdf_manager.variable_attribute_schema["attribute_key"]
        assert cdf_manager.variable_attribute_schema["attribute_key"]["SI_CONVERSION"][
            "required"
        ]

        # Assert Var Type Lists are Updated
        assert len(cdf_manager.variable_attribute_schema["data"]) > 2
        assert len(cdf_manager.variable_attribute_schema["support_data"]) > 2
        assert len(cdf_manager.variable_attribute_schema["metadata"]) > 1
        assert "test_attribute" in cdf_manager.variable_attribute_schema["data"]
        assert "test_attribute" in cdf_manager.variable_attribute_schema["support_data"]
        assert "test_attribute" in cdf_manager.variable_attribute_schema["metadata"]
        assert "SI_CONVERSION" in cdf_manager.variable_attribute_schema["data"]
        assert "SI_CONVERSION" in cdf_manager.variable_attribute_schema["support_data"]
        assert "SI_CONVERSION" not in cdf_manager.variable_attribute_schema["metadata"]


def test_load_global_attribute(cdf_manager):
    """
    Test function that covers:
        load_global_attributes
    """

    test_data_dir = Path(__file__).parent / "test_data"
    # Initialize CdfAttributeManager object which loads in default info
    cdf_manager.load_global_attributes(
        test_data_dir / "imap_default_global_cdf_attrs.yaml"
    )

    # Testing information has been loaded in
    assert cdf_manager._global_attributes["Project"] == "STP>Solar-Terrestrial Physics"
    assert (
        cdf_manager._global_attributes["Source_name"]
        == "IMAP>Interstellar Mapping and Acceleration Probe"
    )
    assert (
        cdf_manager._global_attributes["Discipline"]
        == "Solar Physics>Heliospheric Physics"
    )
    assert (
        cdf_manager._global_attributes["Mission_group"]
        == "IMAP>Interstellar Mapping and Acceleration Probe"
    )
    assert cdf_manager._global_attributes["PI_name"] == "Dr. David J. McComas"
    assert (
        cdf_manager._global_attributes["PI_affiliation"]
        == "Princeton Plasma Physics Laboratory, 100 Stellarator Road, "
        "Princeton, NJ 08540"
    )
    assert (
        cdf_manager._global_attributes["File_naming_convention"]
        == "source_descriptor_datatype_yyyyMMdd_vNNN"
    )
    # The following test should fail because "DOI" is not an attribute in
    #   imap_default_global_cdf_attrs.yaml
    with pytest.raises(KeyError):
        assert cdf_manager._global_attributes["DOI"] == "test"

    # Load in different data
    cdf_manager.load_global_attributes(
        test_data_dir / "default_global_test_cdf_attrs.yaml"
    )

    # Testing attributes carried over
    assert (
        cdf_manager._global_attributes["File_naming_convention"]
        == "source_descriptor_datatype_yyyyMMdd_vNNN"
    )
    assert (
        cdf_manager._global_attributes["Discipline"]
        == "Solar Physics>Heliospheric Physics"
    )

    # Testing attributes newly loaded
    assert cdf_manager._global_attributes["Project"] == "STP>Solar-Terrestrial Physics"
    assert (
        cdf_manager._global_attributes["Source_name"]
        == "IMAP>Interstellar Mapping and Acceleration Probe"
    )
    assert cdf_manager._global_attributes["Mission_group"] == "Dysfunctional Cats"
    assert cdf_manager._global_attributes["PI_name"] == "Ana Manica"
    assert cdf_manager._global_attributes["PI_affiliation"] == "LASP, CU"
    assert cdf_manager._global_attributes["Data_version"] == 2
    assert cdf_manager._global_attributes["DOI"] == "test"

    # Testing that everything loaded into the global attrs is present in
    #   the global attrs schema
    for attr in cdf_manager._global_attributes.keys():
        assert attr in cdf_manager.global_attribute_schema.keys()


def test_get_global_attributes(cdf_manager):
    """
    Test function that covers:
        get_global_attributes
    """
    # Change filepath to load test global attributes
    test_data_dir = Path(__file__).parent / "test_data"
    cdf_manager.load_global_attributes(
        test_data_dir / "default_global_test_cdf_attrs.yaml"
    )
    cdf_manager.load_global_attributes(test_data_dir / "imap_test_global.yaml")

    # Loading in instrument specific attributes
    test_get_global_attrs = cdf_manager.get_global_attributes("imap_test_T1_test")

    # Testing information previously loaded into global attributes (first if statement)
    assert test_get_global_attrs["Project"] == "STP>Solar-Terrestrial Physics"
    assert (
        test_get_global_attrs["Source_name"]
        == "IMAP>Interstellar Mapping and Acceleration Probe"
    )
    assert test_get_global_attrs["Mission_group"] == "Dysfunctional Cats"
    # Testing instrument specific global attributes (first elif statement)
    assert test_get_global_attrs["Descriptor"] == "TEST>Testinstrument"
    assert test_get_global_attrs["Data_type"] == "T1_test-one>Test-1 test one"
    assert test_get_global_attrs["Logical_source"] == "imap_test_T1_test"
    assert (
        test_get_global_attrs["Logical_source_description"]
        == "IMAP Mission TEST one document Level-T1."
    )
    # Not given, and not required information
    with pytest.raises(KeyError):
        assert test_get_global_attrs["bad_name"] == "false info"

    # Testing second elif statement
    test_error_elif = cdf_manager.get_global_attributes("imap_test_T3_test")
    with pytest.raises(KeyError):
        assert test_error_elif["Generation_date"] == "Does Not Exist"

    # Load in more data using get_global_attributes
    test_get_global_attrs_2 = cdf_manager.get_global_attributes("imap_test_T2_test")
    # Testing information previously loaded into global attributes (first if statement)
    assert test_get_global_attrs_2["Project"] == "STP>Solar-Terrestrial Physics"
    # Testing first elif statement
    assert test_get_global_attrs_2["Descriptor"] == "TEST>Testinstrument"
    # "Data_type" not required according to default schema
    assert test_get_global_attrs_2["Data_type"] == "T2_test-two>Test-2 test two"

    # Testing that required schema keys are in get_global_attributes
    for attr_name in cdf_manager.global_attribute_schema.keys():
        required_schema = cdf_manager.global_attribute_schema[attr_name]["required"]
        if required_schema is True:
            assert attr_name in test_get_global_attrs.keys()


def test_instrument_id_format(cdf_manager):
    """
    Test function that covers:
        get_global_attributes
    """
    # Change filepath to load test global attributes
    test_data_dir = Path(__file__).parent / "test_data"
    cdf_manager.load_global_attributes(
        test_data_dir / "imap_default_global_cdf_attrs.yaml"
    )
    cdf_manager.load_global_attributes(test_data_dir / "imap_test_global.yaml")

    # Loading in instrument specific attributes
    test_get_global_attrs = cdf_manager.get_global_attributes("imap_test_T1_test")

    # Testing how instrument_id operates
    assert test_get_global_attrs["Project"] == cdf_manager._global_attributes["Project"]
    assert (
        test_get_global_attrs["Source_name"]
        == cdf_manager._global_attributes["Source_name"]
    )
    assert (
        test_get_global_attrs["Data_type"]
        == cdf_manager._global_attributes["imap_test_T1_test"]["Data_type"]
    )
    assert (
        cdf_manager._global_attributes["imap_test_T1_test"]["Logical_source"]
        == "imap_test_T1_test"
    )
    with pytest.raises(KeyError):
        assert cdf_manager._global_attributes["imap_test_T1_test"]["Project"]


def test_add_global_attribute(cdf_manager):
    """
    Test function that covers:
        add_global_attribute
    """
    # Change filepath to load test global attributes
    test_data_dir = Path(__file__).parent / "test_data"
    cdf_manager.load_global_attributes(
        test_data_dir / "imap_default_global_cdf_attrs.yaml"
    )
    cdf_manager.load_global_attributes(test_data_dir / "imap_test_global.yaml")

    # Changing a dynamic global variable
    cdf_manager.add_global_attribute("Project", "Test Project")
    test_get_global_attrs = cdf_manager.get_global_attributes("imap_test_T1_test")
    assert cdf_manager._global_attributes["Project"] == "Test Project"
    assert test_get_global_attrs["Project"] == "Test Project"

    # Testing adding required global attribute
    cdf_manager._global_attributes.__delitem__("Source_name")
    # Reloading get_global_attributes to pick up deleted Source_name
    test_get_global_attrs = cdf_manager.get_global_attributes("imap_test_T1_test")
    with pytest.raises(KeyError):
        assert cdf_manager._global_attributes["Source_name"]
    assert test_get_global_attrs["Source_name"] is None

    # Adding deleted global attribute
    cdf_manager.add_global_attribute("Source_name", "anas_source")
    assert cdf_manager._global_attributes["Source_name"] == "anas_source"
    # Reloading get_global_attributes to pick up added Source_name
    test_get_global_attrs = cdf_manager.get_global_attributes("imap_test_T1_test")
    assert test_get_global_attrs["Source_name"] == "anas_source"

    # Testing instrument specific attribute
    cdf_manager._global_attributes["imap_test_T1_test"].__delitem__("Logical_source")
    # Reloading get_global_attributes to pick up deleted Source_name
    test_get_global_attrs = cdf_manager.get_global_attributes("imap_test_T1_test")
    with pytest.raises(KeyError):
        assert cdf_manager._global_attributes["imap_test_T1_test"]["Logical_source"]
    assert test_get_global_attrs["Logical_source"] is None


def test_variable_attribute(cdf_manager):
    """
    Test function that covers:
        load_variable_attributes
        get_variable_attributes
    """

    test_data_dir = Path(__file__).parent / "test_data"
    cdf_manager.load_global_attributes(
        test_data_dir / "imap_default_global_cdf_attrs.yaml"
    )
    # Loading in test data
    cdf_manager.load_variable_attributes(test_data_dir / "imap_test_variable.yaml")

    # All variables required to have:
    expected_attributes = [
        "CATDESC",
        "DEPEND_0",
        "DISPLAY_TYPE",
        "FIELDNAM",
        "FILLVAL",
        "FORMAT",
        "LABLAXIS",
        "UNITS",
        "VALIDMIN",
        "VALIDMAX",
        "VAR_TYPE",
    ]

    # Assuring all required attributes are loaded in
    for attr_name in cdf_manager.variable_attribute_schema["attribute_key"]:
        attribute = cdf_manager.variable_attribute_schema["attribute_key"][attr_name]
        if attribute["required"] is True:
            for exp_attr in expected_attributes:
                assert (
                    exp_attr in cdf_manager.variable_attribute_schema["attribute_key"]
                )

    # Testing specific attributes
    assert (
        cdf_manager._variable_attributes["default_attrs"]["DEPEND_0"]
        == cdf_manager._variable_attributes["default_attrs"]["DEPEND_0"]
    )
    assert cdf_manager._variable_attributes["default_attrs"]["FILLVAL"] == -10
    assert cdf_manager._variable_attributes["test_field_1"]["DEPEND_0"] == "test_depend"
    assert (
        cdf_manager._variable_attributes["default_attrs"]["VAR_TYPE"] == "test_var_type"
    )
    with pytest.raises(KeyError):
        assert cdf_manager._variable_attributes["default_attrs"]["CATDESC"] == "test"


def test_get_variable_attributes(cdf_manager):
    """
    Test function that covers:
        load_variable_attributes
        get_variable_attributes
    """
    # Change filepath to load test global attributes
    test_data_dir = Path(__file__).parent / "test_data"
    cdf_manager.load_global_attributes(
        test_data_dir / "imap_default_global_cdf_attrs.yaml"
    )
    # Loading in test data
    cdf_manager.load_variable_attributes(test_data_dir / "imap_test_variable.yaml")

    # Loading in instrument specific attributes
    imap_test_variable = cdf_manager.get_variable_attributes("test_field_1")

    # Make sure all expected attributes are present
    for variable_attrs in cdf_manager.variable_attribute_schema["attribute_key"]:
        required_var_attributes = cdf_manager.variable_attribute_schema[
            "attribute_key"
        ][variable_attrs]["required"]
        if required_var_attributes is True:
            assert variable_attrs in imap_test_variable.keys()

    # Calling default attributes
    assert imap_test_variable["DEPEND_0"] == "test_depend"
    assert imap_test_variable["DISPLAY_TYPE"] == "test_display_type"
    assert imap_test_variable["FILLVAL"] == -10

    # Calling required attributes
    assert imap_test_variable["CATDESC"] == "test time"
    assert imap_test_variable["TIME_BASE"] == 10
    assert imap_test_variable["DEPEND_1"] == "test_depend_1"
    assert imap_test_variable["DEPEND_2"] == "test_depend_2"

    # Calling to non required attributes
    assert imap_test_variable["LEAP_SECONDS_INCLUDED"] == "test_not_required"

    # Calling attribute name that does not exist
    with pytest.raises(KeyError):
        assert imap_test_variable["DOES_NOT_EXIST"]

    # Testing for attribute not in schema
    with pytest.raises(KeyError):
        assert imap_test_variable["NOT_IN_SCHEMA"]

    # Load in different data, test again
    imap_test_variable_2 = cdf_manager.get_variable_attributes("test_field_2")
    # Calling default attributes
    assert imap_test_variable_2["DEPEND_0"] == "test_depend"
    assert imap_test_variable_2["DISPLAY_TYPE"] == "test_display_type"
    assert imap_test_variable_2["FILLVAL"] == -10

    # Calling required attributes
    assert imap_test_variable_2["CATDESC"] == "test time 2"
    assert imap_test_variable_2["TIME_BASE"] == 11

    # Loading in different data to test logger errors, empty strings,
    # and DEPEND_i with i >= 1 condition
    imap_test_variable_3 = cdf_manager.get_variable_attributes("test_field_3")

    assert imap_test_variable_3["DEPEND_1"] == "depend_1_test_3"
    assert imap_test_variable_3["DEPEND_0"] == ""
    assert imap_test_variable_3["CATDESC"] == ""
    assert imap_test_variable_3["REPRESENTATION_2"] == "representation_2"
    assert imap_test_variable_3["LABL_PTR_1"] == "labl_ptr_1"

    # check_schema = False
    imap_test_variable_1_false = cdf_manager.get_variable_attributes(
        "test_field_1", False
    )
    assert imap_test_variable_1_false["NOT_IN_SCHEMA"] == "not_in_schema"
    assert imap_test_variable_1_false["VALIDMIN"] == 0

    var_with_non_ascii_text = cdf_manager.get_variable_attributes("test_field_4")
    assert var_with_non_ascii_text["CATDESC"] == "α-particles"


def test_sw_templates(cdf_manager):
    """Test Global and Variable Attribute Templates"""

    # Global Attribute Template
    assert cdf_manager.global_attribute_template() is not None
    assert isinstance(cdf_manager.global_attribute_template(), dict)

    # Variable Attribute Template
    assert cdf_manager.variable_attribute_template() is not None
    assert isinstance(cdf_manager.variable_attribute_template(), dict)


def test_sw_info(cdf_manager):
    """Test Global and Variable Attribute Info Functions"""

    # Global Attribute Info
    assert cdf_manager.global_attribute_info() is not None
    assert isinstance(cdf_manager.global_attribute_info(), dict)
    assert isinstance(
        cdf_manager.global_attribute_info(attribute_name="Descriptor"), dict
    )
    with pytest.raises(KeyError):
        _ = cdf_manager.global_attribute_info(attribute_name="NotAnAttribute")

    # Variable Attribute Info
    assert cdf_manager.variable_attribute_info() is not None
    assert isinstance(cdf_manager.variable_attribute_info(), dict)
    assert isinstance(
        cdf_manager.variable_attribute_info(attribute_name="CATDESC"), dict
    )
    with pytest.raises(KeyError):
        _ = cdf_manager.variable_attribute_info(attribute_name="NotAnAttribute")
