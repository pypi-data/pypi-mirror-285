import pytest
from capvalidator import get_dates
from capvalidator import DateResult

expected_results = [
    ('bf_valid',
     DateResult(sent='2024-07-02T20:10:00Z',
                effective='2024-07-02T20:15:00Z',
                onset='2024-07-02T20:15:00Z',
                expiry='2024-07-03T12:00:00Z')
     ),
    ('sc_valid',
     DateResult(sent='2024-05-19T13:18:00Z',
                effective='2024-05-19T13:30:00Z',
                onset='2024-05-19T13:30:00Z',
                expiry='2024-05-19T19:30:00Z')
     ),
    ('tg_valid',
     DateResult(sent='2024-06-06T15:15:00Z',
                effective='2024-06-06T17:00:00Z',
                onset='2024-06-06T17:15:00Z',
                expiry='2024-06-06T22:00:00Z')
     )
]


@pytest.mark.parametrize("cap_name, expected_output", expected_results)
def test_get_dates(request, cap_name, expected_output):
    """Tests the output of the get_dates function over all
    CAP XML fixtures found in the data directory.

    Args:
        request (fixture): The pytest fixture request object.
        cap_name (str): The name of the CAP fixture.
        expected_output (object): The expected dictionary of dates extracted.

    Returns:
        None
    """
    # Access the fixture contents
    cap = request.getfixturevalue(cap_name)

    # Perform the validation
    result = get_dates(cap)

    # Check the result
    assert result.sent == expected_output.sent
    assert result.effective == expected_output.effective
    assert result.onset == expected_output.onset
    assert result.expiry == expected_output.expiry
