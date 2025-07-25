# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) Python Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from copy import deepcopy
from typing import Any, Optional, TYPE_CHECKING, cast
from typing_extensions import Self

from azure.core.pipeline import policies
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.settings import settings
from azure.mgmt.core import ARMPipelineClient
from azure.mgmt.core.policies import ARMAutoResourceProviderRegistrationPolicy
from azure.mgmt.core.tools import get_arm_endpoints

from ._configuration import OracleDatabaseMgmtClientConfiguration
from ._utils.serialization import Deserializer, Serializer
from .operations import (
    AutonomousDatabaseBackupsOperations,
    AutonomousDatabaseCharacterSetsOperations,
    AutonomousDatabaseNationalCharacterSetsOperations,
    AutonomousDatabaseVersionsOperations,
    AutonomousDatabasesOperations,
    CloudExadataInfrastructuresOperations,
    CloudVmClustersOperations,
    DbNodesOperations,
    DbServersOperations,
    DbSystemShapesOperations,
    DnsPrivateViewsOperations,
    DnsPrivateZonesOperations,
    ExadbVmClustersOperations,
    ExascaleDbNodesOperations,
    ExascaleDbStorageVaultsOperations,
    FlexComponentsOperations,
    GiMinorVersionsOperations,
    GiVersionsOperations,
    ListActionsOperations,
    Operations,
    OracleSubscriptionsOperations,
    SystemVersionsOperations,
    VirtualNetworkAddressesOperations,
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class OracleDatabaseMgmtClient:  # pylint: disable=too-many-instance-attributes
    """OracleDatabaseMgmtClient.

    :ivar operations: Operations operations
    :vartype operations: azure.mgmt.oracledatabase.operations.Operations
    :ivar cloud_exadata_infrastructures: CloudExadataInfrastructuresOperations operations
    :vartype cloud_exadata_infrastructures:
     azure.mgmt.oracledatabase.operations.CloudExadataInfrastructuresOperations
    :ivar list_actions: ListActionsOperations operations
    :vartype list_actions: azure.mgmt.oracledatabase.operations.ListActionsOperations
    :ivar db_servers: DbServersOperations operations
    :vartype db_servers: azure.mgmt.oracledatabase.operations.DbServersOperations
    :ivar cloud_vm_clusters: CloudVmClustersOperations operations
    :vartype cloud_vm_clusters: azure.mgmt.oracledatabase.operations.CloudVmClustersOperations
    :ivar virtual_network_addresses: VirtualNetworkAddressesOperations operations
    :vartype virtual_network_addresses:
     azure.mgmt.oracledatabase.operations.VirtualNetworkAddressesOperations
    :ivar system_versions: SystemVersionsOperations operations
    :vartype system_versions: azure.mgmt.oracledatabase.operations.SystemVersionsOperations
    :ivar oracle_subscriptions: OracleSubscriptionsOperations operations
    :vartype oracle_subscriptions:
     azure.mgmt.oracledatabase.operations.OracleSubscriptionsOperations
    :ivar db_nodes: DbNodesOperations operations
    :vartype db_nodes: azure.mgmt.oracledatabase.operations.DbNodesOperations
    :ivar gi_versions: GiVersionsOperations operations
    :vartype gi_versions: azure.mgmt.oracledatabase.operations.GiVersionsOperations
    :ivar gi_minor_versions: GiMinorVersionsOperations operations
    :vartype gi_minor_versions: azure.mgmt.oracledatabase.operations.GiMinorVersionsOperations
    :ivar db_system_shapes: DbSystemShapesOperations operations
    :vartype db_system_shapes: azure.mgmt.oracledatabase.operations.DbSystemShapesOperations
    :ivar dns_private_views: DnsPrivateViewsOperations operations
    :vartype dns_private_views: azure.mgmt.oracledatabase.operations.DnsPrivateViewsOperations
    :ivar dns_private_zones: DnsPrivateZonesOperations operations
    :vartype dns_private_zones: azure.mgmt.oracledatabase.operations.DnsPrivateZonesOperations
    :ivar flex_components: FlexComponentsOperations operations
    :vartype flex_components: azure.mgmt.oracledatabase.operations.FlexComponentsOperations
    :ivar autonomous_databases: AutonomousDatabasesOperations operations
    :vartype autonomous_databases:
     azure.mgmt.oracledatabase.operations.AutonomousDatabasesOperations
    :ivar autonomous_database_backups: AutonomousDatabaseBackupsOperations operations
    :vartype autonomous_database_backups:
     azure.mgmt.oracledatabase.operations.AutonomousDatabaseBackupsOperations
    :ivar autonomous_database_character_sets: AutonomousDatabaseCharacterSetsOperations operations
    :vartype autonomous_database_character_sets:
     azure.mgmt.oracledatabase.operations.AutonomousDatabaseCharacterSetsOperations
    :ivar autonomous_database_national_character_sets:
     AutonomousDatabaseNationalCharacterSetsOperations operations
    :vartype autonomous_database_national_character_sets:
     azure.mgmt.oracledatabase.operations.AutonomousDatabaseNationalCharacterSetsOperations
    :ivar autonomous_database_versions: AutonomousDatabaseVersionsOperations operations
    :vartype autonomous_database_versions:
     azure.mgmt.oracledatabase.operations.AutonomousDatabaseVersionsOperations
    :ivar exadb_vm_clusters: ExadbVmClustersOperations operations
    :vartype exadb_vm_clusters: azure.mgmt.oracledatabase.operations.ExadbVmClustersOperations
    :ivar exascale_db_nodes: ExascaleDbNodesOperations operations
    :vartype exascale_db_nodes: azure.mgmt.oracledatabase.operations.ExascaleDbNodesOperations
    :ivar exascale_db_storage_vaults: ExascaleDbStorageVaultsOperations operations
    :vartype exascale_db_storage_vaults:
     azure.mgmt.oracledatabase.operations.ExascaleDbStorageVaultsOperations
    :param credential: Credential used to authenticate requests to the service. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :param subscription_id: The ID of the target subscription. The value must be an UUID. Required.
    :type subscription_id: str
    :param base_url: Service host. Default value is None.
    :type base_url: str
    :keyword api_version: The API version to use for this operation. Default value is "2025-03-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self, credential: "TokenCredential", subscription_id: str, base_url: Optional[str] = None, **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        _cloud = kwargs.pop("cloud_setting", None) or settings.current.azure_cloud  # type: ignore
        _endpoints = get_arm_endpoints(_cloud)
        if not base_url:
            base_url = _endpoints["resource_manager"]
        credential_scopes = kwargs.pop("credential_scopes", _endpoints["credential_scopes"])
        self._config = OracleDatabaseMgmtClientConfiguration(
            credential=credential,
            subscription_id=subscription_id,
            base_url=cast(str, base_url),
            credential_scopes=credential_scopes,
            **kwargs
        )

        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                ARMAutoResourceProviderRegistrationPolicy(),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]
        self._client: ARMPipelineClient = ARMPipelineClient(base_url=cast(str, _endpoint), policies=_policies, **kwargs)

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False
        self.operations = Operations(self._client, self._config, self._serialize, self._deserialize)
        self.cloud_exadata_infrastructures = CloudExadataInfrastructuresOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.list_actions = ListActionsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.db_servers = DbServersOperations(self._client, self._config, self._serialize, self._deserialize)
        self.cloud_vm_clusters = CloudVmClustersOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.virtual_network_addresses = VirtualNetworkAddressesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.system_versions = SystemVersionsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.oracle_subscriptions = OracleSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.db_nodes = DbNodesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.gi_versions = GiVersionsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.gi_minor_versions = GiMinorVersionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.db_system_shapes = DbSystemShapesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.dns_private_views = DnsPrivateViewsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.dns_private_zones = DnsPrivateZonesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.flex_components = FlexComponentsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.autonomous_databases = AutonomousDatabasesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.autonomous_database_backups = AutonomousDatabaseBackupsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.autonomous_database_character_sets = AutonomousDatabaseCharacterSetsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.autonomous_database_national_character_sets = AutonomousDatabaseNationalCharacterSetsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.autonomous_database_versions = AutonomousDatabaseVersionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.exadb_vm_clusters = ExadbVmClustersOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.exascale_db_nodes = ExascaleDbNodesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.exascale_db_storage_vaults = ExascaleDbStorageVaultsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )

    def send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """

        request_copy = deepcopy(request)
        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.base_url", self._config.base_url, "str", skip_quote=True),
        }

        request_copy.url = self._client.format_url(request_copy.url, **path_format_arguments)
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)
