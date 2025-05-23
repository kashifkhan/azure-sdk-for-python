# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from copy import deepcopy
from typing import Any, TYPE_CHECKING
from typing_extensions import Self

from azure.core.pipeline import policies
from azure.core.rest import HttpRequest, HttpResponse
from azure.mgmt.core import ARMPipelineClient
from azure.mgmt.core.policies import ARMAutoResourceProviderRegistrationPolicy

from . import models as _models
from ._configuration import ContainerAppsAPIClientConfiguration
from ._serialization import Deserializer, Serializer
from .operations import (
    AvailableWorkloadProfilesOperations,
    BillingMetersOperations,
    CertificatesOperations,
    ConnectedEnvironmentsCertificatesOperations,
    ConnectedEnvironmentsDaprComponentsOperations,
    ConnectedEnvironmentsOperations,
    ConnectedEnvironmentsStoragesOperations,
    ContainerAppsAPIClientOperationsMixin,
    ContainerAppsAuthConfigsOperations,
    ContainerAppsDiagnosticsOperations,
    ContainerAppsOperations,
    ContainerAppsRevisionReplicasOperations,
    ContainerAppsRevisionsOperations,
    ContainerAppsSessionPoolsOperations,
    ContainerAppsSourceControlsOperations,
    DaprComponentsOperations,
    JavaComponentsOperations,
    JobsExecutionsOperations,
    JobsOperations,
    ManagedCertificatesOperations,
    ManagedEnvironmentDiagnosticsOperations,
    ManagedEnvironmentUsagesOperations,
    ManagedEnvironmentsDiagnosticsOperations,
    ManagedEnvironmentsOperations,
    ManagedEnvironmentsStoragesOperations,
    NamespacesOperations,
    Operations,
    UsagesOperations,
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class ContainerAppsAPIClient(ContainerAppsAPIClientOperationsMixin):  # pylint: disable=too-many-instance-attributes
    """ContainerAppsAPIClient.

    :ivar container_apps_auth_configs: ContainerAppsAuthConfigsOperations operations
    :vartype container_apps_auth_configs:
     azure.mgmt.appcontainers.operations.ContainerAppsAuthConfigsOperations
    :ivar available_workload_profiles: AvailableWorkloadProfilesOperations operations
    :vartype available_workload_profiles:
     azure.mgmt.appcontainers.operations.AvailableWorkloadProfilesOperations
    :ivar billing_meters: BillingMetersOperations operations
    :vartype billing_meters: azure.mgmt.appcontainers.operations.BillingMetersOperations
    :ivar connected_environments: ConnectedEnvironmentsOperations operations
    :vartype connected_environments:
     azure.mgmt.appcontainers.operations.ConnectedEnvironmentsOperations
    :ivar connected_environments_certificates: ConnectedEnvironmentsCertificatesOperations
     operations
    :vartype connected_environments_certificates:
     azure.mgmt.appcontainers.operations.ConnectedEnvironmentsCertificatesOperations
    :ivar connected_environments_dapr_components: ConnectedEnvironmentsDaprComponentsOperations
     operations
    :vartype connected_environments_dapr_components:
     azure.mgmt.appcontainers.operations.ConnectedEnvironmentsDaprComponentsOperations
    :ivar connected_environments_storages: ConnectedEnvironmentsStoragesOperations operations
    :vartype connected_environments_storages:
     azure.mgmt.appcontainers.operations.ConnectedEnvironmentsStoragesOperations
    :ivar container_apps: ContainerAppsOperations operations
    :vartype container_apps: azure.mgmt.appcontainers.operations.ContainerAppsOperations
    :ivar container_apps_revisions: ContainerAppsRevisionsOperations operations
    :vartype container_apps_revisions:
     azure.mgmt.appcontainers.operations.ContainerAppsRevisionsOperations
    :ivar container_apps_revision_replicas: ContainerAppsRevisionReplicasOperations operations
    :vartype container_apps_revision_replicas:
     azure.mgmt.appcontainers.operations.ContainerAppsRevisionReplicasOperations
    :ivar container_apps_diagnostics: ContainerAppsDiagnosticsOperations operations
    :vartype container_apps_diagnostics:
     azure.mgmt.appcontainers.operations.ContainerAppsDiagnosticsOperations
    :ivar managed_environment_diagnostics: ManagedEnvironmentDiagnosticsOperations operations
    :vartype managed_environment_diagnostics:
     azure.mgmt.appcontainers.operations.ManagedEnvironmentDiagnosticsOperations
    :ivar managed_environments_diagnostics: ManagedEnvironmentsDiagnosticsOperations operations
    :vartype managed_environments_diagnostics:
     azure.mgmt.appcontainers.operations.ManagedEnvironmentsDiagnosticsOperations
    :ivar jobs: JobsOperations operations
    :vartype jobs: azure.mgmt.appcontainers.operations.JobsOperations
    :ivar operations: Operations operations
    :vartype operations: azure.mgmt.appcontainers.operations.Operations
    :ivar java_components: JavaComponentsOperations operations
    :vartype java_components: azure.mgmt.appcontainers.operations.JavaComponentsOperations
    :ivar jobs_executions: JobsExecutionsOperations operations
    :vartype jobs_executions: azure.mgmt.appcontainers.operations.JobsExecutionsOperations
    :ivar managed_environments: ManagedEnvironmentsOperations operations
    :vartype managed_environments:
     azure.mgmt.appcontainers.operations.ManagedEnvironmentsOperations
    :ivar certificates: CertificatesOperations operations
    :vartype certificates: azure.mgmt.appcontainers.operations.CertificatesOperations
    :ivar managed_certificates: ManagedCertificatesOperations operations
    :vartype managed_certificates:
     azure.mgmt.appcontainers.operations.ManagedCertificatesOperations
    :ivar namespaces: NamespacesOperations operations
    :vartype namespaces: azure.mgmt.appcontainers.operations.NamespacesOperations
    :ivar dapr_components: DaprComponentsOperations operations
    :vartype dapr_components: azure.mgmt.appcontainers.operations.DaprComponentsOperations
    :ivar managed_environments_storages: ManagedEnvironmentsStoragesOperations operations
    :vartype managed_environments_storages:
     azure.mgmt.appcontainers.operations.ManagedEnvironmentsStoragesOperations
    :ivar container_apps_session_pools: ContainerAppsSessionPoolsOperations operations
    :vartype container_apps_session_pools:
     azure.mgmt.appcontainers.operations.ContainerAppsSessionPoolsOperations
    :ivar container_apps_source_controls: ContainerAppsSourceControlsOperations operations
    :vartype container_apps_source_controls:
     azure.mgmt.appcontainers.operations.ContainerAppsSourceControlsOperations
    :ivar usages: UsagesOperations operations
    :vartype usages: azure.mgmt.appcontainers.operations.UsagesOperations
    :ivar managed_environment_usages: ManagedEnvironmentUsagesOperations operations
    :vartype managed_environment_usages:
     azure.mgmt.appcontainers.operations.ManagedEnvironmentUsagesOperations
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential
    :param subscription_id: The ID of the target subscription. Required.
    :type subscription_id: str
    :param base_url: Service URL. Default value is "https://management.azure.com".
    :type base_url: str
    :keyword api_version: Api Version. Default value is "2025-01-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        credential: "TokenCredential",
        subscription_id: str,
        base_url: str = "https://management.azure.com",
        **kwargs: Any
    ) -> None:
        self._config = ContainerAppsAPIClientConfiguration(
            credential=credential, subscription_id=subscription_id, **kwargs
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
        self._client: ARMPipelineClient = ARMPipelineClient(base_url=base_url, policies=_policies, **kwargs)

        client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._serialize.client_side_validation = False
        self.container_apps_auth_configs = ContainerAppsAuthConfigsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.available_workload_profiles = AvailableWorkloadProfilesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.billing_meters = BillingMetersOperations(self._client, self._config, self._serialize, self._deserialize)
        self.connected_environments = ConnectedEnvironmentsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.connected_environments_certificates = ConnectedEnvironmentsCertificatesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.connected_environments_dapr_components = ConnectedEnvironmentsDaprComponentsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.connected_environments_storages = ConnectedEnvironmentsStoragesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.container_apps = ContainerAppsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.container_apps_revisions = ContainerAppsRevisionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.container_apps_revision_replicas = ContainerAppsRevisionReplicasOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.container_apps_diagnostics = ContainerAppsDiagnosticsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.managed_environment_diagnostics = ManagedEnvironmentDiagnosticsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.managed_environments_diagnostics = ManagedEnvironmentsDiagnosticsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.jobs = JobsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.operations = Operations(self._client, self._config, self._serialize, self._deserialize)
        self.java_components = JavaComponentsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.jobs_executions = JobsExecutionsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.managed_environments = ManagedEnvironmentsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.certificates = CertificatesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.managed_certificates = ManagedCertificatesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.namespaces = NamespacesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.dapr_components = DaprComponentsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.managed_environments_storages = ManagedEnvironmentsStoragesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.container_apps_session_pools = ContainerAppsSessionPoolsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.container_apps_source_controls = ContainerAppsSourceControlsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.usages = UsagesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.managed_environment_usages = ManagedEnvironmentUsagesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )

    def _send_request(self, request: HttpRequest, *, stream: bool = False, **kwargs: Any) -> HttpResponse:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = client._send_request(request)
        <HttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """

        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self._client.__exit__(*exc_details)
