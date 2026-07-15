# Copyright 2026 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Action plugin for zhmc_session module that treats the module return value as a
no_log value.
"""

from ..plugin_utils.common import NoLogActionBase


class ActionModule(NoLogActionBase):
    # pylint: disable=missing-class-docstring,(too-few-public-methods
    pass
