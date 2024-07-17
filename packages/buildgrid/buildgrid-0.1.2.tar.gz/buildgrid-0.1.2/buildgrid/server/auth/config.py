# Copyright (C) 2023 Bloomberg LP
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
import re
from typing import Dict, List, Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field


class Acl(BaseModel):
    actor: Optional[str] = Field(default=None)
    requests: Optional[List[str]] = Field(default=None)
    subject: Optional[str] = Field(default=None)
    workflow: Optional[str] = Field(default=None)

    def is_authorized(
        self,
        request_name: str,
        actor: Optional[str] = None,
        subject: Optional[str] = None,
        workflow: Optional[str] = None,
    ) -> bool:
        if self.actor is not None and not re.match(self.actor, actor or ""):
            return False

        if self.subject is not None and not re.match(self.subject, subject or ""):
            return False

        if self.workflow is not None and not re.match(self.workflow, workflow or ""):
            return False

        if self.requests is not None and request_name not in self.requests:
            return False

        return True


class InstanceAuthorizationConfig(BaseModel):
    allow: Union[Literal["all"], List[Acl]]

    def is_authorized(
        self,
        request_name: str,
        actor: Optional[str] = None,
        subject: Optional[str] = None,
        workflow: Optional[str] = None,
    ) -> bool:
        if self.allow == "all":
            return True

        return any(acl.is_authorized(request_name, actor, subject, workflow) for acl in self.allow)


def parse_auth_config(path: Union[str, bytes, "os.PathLike[str]"]) -> Dict[str, InstanceAuthorizationConfig]:
    with open(path) as config_file:
        config = yaml.safe_load(config_file)
    return {
        instance_name: InstanceAuthorizationConfig(**instance_config)
        for instance_name, instance_config in config.items()
    }
