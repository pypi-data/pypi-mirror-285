###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

from .validate import Validator

__version__ = '0.1.0-dev2'


class ValidationResult:
    def __init__(self, passed, message):
        self.passed = passed
        self.message = message


class DateResult:
    def __init__(self, sent, effective, onset, expiry):
        self.sent = sent
        self.effective = effective
        self.onset = onset
        self.expiry = expiry


def check_schema(cap) -> tuple:
    """Interface to the schema validation method of the Validator class, which
    is used in the CLI.
    """
    return Validator(cap).schema()


def check_signature(cap) -> tuple:
    """Interface to the signature verification method of the Validator class,
    which is used in the CLI.
    """
    return Validator(cap).signature()


def get_dates(cap) -> DateResult:
    """Interface to the date extraction method of the Validator class, which
    can be used in the API.

    Args:
        cap (bytes): The CAP alert XML file byte contents to be parsed.

    Returns:
        DateResult: The extracted date-time values.
    """
    dates = Validator(cap).get_dates()
    return DateResult(dates['sent'],
                      dates['effective'],
                      dates['onset'],
                      dates['expiry'])


def validate_xml(cap) -> ValidationResult:
    """Performs the two steps of CAP validation: schema validation
    and signature verification.

    Args:
        cap (bytes): The CAP alert XML file byte contents to be validated.

    Returns:
        ValidationResult: The validation status and the associated message
        justifying the status.
    """
    # Draft code to demonstrate the process of CAP validation

    follows_schema, msg = check_schema(cap)
    if not follows_schema:
        return ValidationResult(False, msg)

    signature_valid, msg = check_signature(cap)
    if not signature_valid:
        return ValidationResult(False, msg)  # noqa

    return ValidationResult(True, "CAP XML file is valid.")
