# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

try:
    from ._models_py3 import ErrorResponse, ErrorResponseException
    from ._models_py3 import Identity
    from ._models_py3 import PolicyAssignment
    from ._models_py3 import PolicyDefinition
    from ._models_py3 import PolicyDefinitionReference
    from ._models_py3 import PolicySetDefinition
    from ._models_py3 import PolicySku
except (SyntaxError, ImportError):
    from ._models import ErrorResponse, ErrorResponseException
    from ._models import Identity
    from ._models import PolicyAssignment
    from ._models import PolicyDefinition
    from ._models import PolicyDefinitionReference
    from ._models import PolicySetDefinition
    from ._models import PolicySku
from ._paged_models import PolicyAssignmentPaged
from ._paged_models import PolicyDefinitionPaged
from ._paged_models import PolicySetDefinitionPaged
from ._policy_client_enums import (
    ResourceIdentityType,
    PolicyType,
    PolicyMode,
)

__all__ = [
    'ErrorResponse', 'ErrorResponseException',
    'Identity',
    'PolicyAssignment',
    'PolicyDefinition',
    'PolicyDefinitionReference',
    'PolicySetDefinition',
    'PolicySku',
    'PolicyAssignmentPaged',
    'PolicyDefinitionPaged',
    'PolicySetDefinitionPaged',
    'ResourceIdentityType',
    'PolicyType',
    'PolicyMode',
]
