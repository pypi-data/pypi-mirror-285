# Copyright (C) 2022 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

import pytest

from buildgrid._app.settings import parser

TEST_ENVIRON = {"TEST_VAR": "example.com"}

STRINGS_WITH_VARS = ["$TEST_VAR", "${TEST_VAR}", "http://$TEST_VAR", "http://${TEST_VAR}/~user"]
EXPANDED_STRINGS = ["example.com", "example.com", "http://example.com", "http://example.com/~user"]


@pytest.mark.parametrize("strings", zip(STRINGS_WITH_VARS, EXPANDED_STRINGS))
def test_expand_vars(strings):
    string, expanded_string = strings

    config = f"!expand-vars {string}"

    try:
        for name, value in TEST_ENVIRON.items():
            os.environ[name] = value

        parsed = parser.get_parser().safe_load(config)
        assert parsed == expanded_string
    finally:
        for name, value in TEST_ENVIRON.items():
            del os.environ[name]
