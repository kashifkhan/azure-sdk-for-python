# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) Python Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential

from azure.mgmt.deviceregistry import DeviceRegistryMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-deviceregistry
# USAGE
    python update_schema_registry.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = DeviceRegistryMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="SUBSCRIPTION_ID",
    )

    response = client.schema_registries.begin_update(
        resource_group_name="myResourceGroup",
        schema_registry_name="my-schema-registry",
        properties={
            "properties": {
                "description": "This is a sample Schema Registry",
                "displayName": "Schema Registry namespace 001",
            },
            "tags": {},
        },
    ).result()
    print(response)


# x-ms-original-file: 2024-09-01-preview/Update_SchemaRegistry.json
if __name__ == "__main__":
    main()
