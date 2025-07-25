# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
import pytest
from azure.mgmt.msi.v2024_11_30.aio import ManagedServiceIdentityClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestManagedServiceIdentityFederatedIdentityCredentialsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(ManagedServiceIdentityClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_federated_identity_credentials_list(self, resource_group):
        response = self.client.federated_identity_credentials.list(
            resource_group_name=resource_group.name,
            resource_name="str",
            api_version="2024-11-30",
        )
        result = [r async for r in response]
        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_federated_identity_credentials_create_or_update(self, resource_group):
        response = await self.client.federated_identity_credentials.create_or_update(
            resource_group_name=resource_group.name,
            resource_name="str",
            federated_identity_credential_resource_name="str",
            parameters={
                "audiences": ["str"],
                "id": "str",
                "issuer": "str",
                "name": "str",
                "subject": "str",
                "systemData": {
                    "createdAt": "2020-02-20 00:00:00",
                    "createdBy": "str",
                    "createdByType": "str",
                    "lastModifiedAt": "2020-02-20 00:00:00",
                    "lastModifiedBy": "str",
                    "lastModifiedByType": "str",
                },
                "type": "str",
            },
            api_version="2024-11-30",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_federated_identity_credentials_get(self, resource_group):
        response = await self.client.federated_identity_credentials.get(
            resource_group_name=resource_group.name,
            resource_name="str",
            federated_identity_credential_resource_name="str",
            api_version="2024-11-30",
        )

        # please add some check logic here by yourself
        # ...

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_federated_identity_credentials_delete(self, resource_group):
        response = await self.client.federated_identity_credentials.delete(
            resource_group_name=resource_group.name,
            resource_name="str",
            federated_identity_credential_resource_name="str",
            api_version="2024-11-30",
        )

        # please add some check logic here by yourself
        # ...
