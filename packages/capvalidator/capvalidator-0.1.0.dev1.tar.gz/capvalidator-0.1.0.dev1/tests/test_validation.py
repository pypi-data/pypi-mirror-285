import pytest
from utils.helpers import get_fixtures
from capvalidator import validate_xml, ValidationResult

###############################################################################
# Obtain the fixture categories and assign the expected results
# of each test case

valid_fixtures, invalid_schema_fixtures, invalid_signature_fixtures, no_signature_fixture = get_fixtures()  # noqa

expected_results = []

for fixture in valid_fixtures:
    result = ValidationResult(True, "CAP XML file is valid.")
    expected_results.append((fixture, result))

for fixture in invalid_schema_fixtures:
    result = ValidationResult(False,
                              "CAP alert does not follow the CAP v1.2 schema.")
    expected_results.append((fixture, result))

for fixture in invalid_signature_fixtures:
    result = ValidationResult(False, "CAP alert signature is invalid or the data has been tampered with.")  # noqa
    expected_results.append((fixture, result))

for fixture in no_signature_fixture:
    result = ValidationResult(False, "CAP alert has not been signed.")
    expected_results.append((fixture, result))

###############################################################################
# Use the input data and expected result pair to create the test cases


@pytest.mark.parametrize("cap_name, expected_output", expected_results)
def test_validate_xml(request, cap_name, expected_output):
    """Tests the output of the validate_xml function over all
    CAP XML fixtures found in the data directory.

    Args:
        request (fixture): The pytest fixture request object.
        cap_name (str): The name of the CAP fixture.
        expected_output (object): The expected output of the validation.

    Returns:
        None
    """
    # Access the fixture contents
    cap = request.getfixturevalue(cap_name)

    # Perform the validation
    result = validate_xml(cap)

    # Check the result
    assert result.passed == expected_output.passed
    assert result.message == expected_output.message
