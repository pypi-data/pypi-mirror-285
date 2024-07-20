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


import hashlib
import json

from buildgrid.server.persistence.sql.impl import get_partial_capabilities_hashes


def test_get_partial_capabilities_hashes() -> None:
    capabilities = {}
    assert sorted(get_partial_capabilities_hashes(capabilities)) == [
        hashlib.sha1(json.dumps(capabilities, sort_keys=True).encode()).hexdigest()
    ]

    expected_partial_capabilities = [
        {},
        {"OSFamily": ["Linux"]},
        {"ISA": ["x86-32"]},
        {"ISA": ["x86-64"]},
        {"OSFamily": ["Linux"], "ISA": ["x86-32"]},
        {"OSFamily": ["Linux"], "ISA": ["x86-64"]},
        {"ISA": ["x86-32", "x86-64"]},
        {"OSFamily": ["Linux"], "ISA": ["x86-32", "x86-64"]},
    ]
    expected_partial_capabilities_hashes = sorted(
        list(
            map(
                lambda cap: hashlib.sha1(json.dumps(cap, sort_keys=True).encode()).hexdigest(),
                expected_partial_capabilities,
            )
        )
    )

    capabilities = {"OSFamily": "Linux", "ISA": {"x86-32", "x86-64"}}
    assert sorted(get_partial_capabilities_hashes(capabilities)) == expected_partial_capabilities_hashes

    # Should be the same if the string is passed in as a singleton set
    capabilities = {"OSFamily": {"Linux"}, "ISA": {"x86-32", "x86-64"}}
    assert sorted(get_partial_capabilities_hashes(capabilities)) == expected_partial_capabilities_hashes

    # Changing the order of the ISA values should produce the same hashes
    capabilities = {"OSFamily": "Linux", "ISA": {"x86-64", "x86-32"}}
    assert sorted(get_partial_capabilities_hashes(capabilities)) == expected_partial_capabilities_hashes
