# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from copy import deepcopy
from typing import Any, Awaitable, Optional, TYPE_CHECKING, cast
from typing_extensions import Self

from azure.core.pipeline import policies
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.settings import settings
from azure.mgmt.core import AsyncARMPipelineClient
from azure.mgmt.core.policies import AsyncARMAutoResourceProviderRegistrationPolicy
from azure.mgmt.core.tools import get_arm_endpoints

from .. import models as _models
from .._utils.serialization import Deserializer, Serializer
from ._configuration import EventGridManagementClientConfiguration
from .operations import (
    CaCertificatesOperations,
    ChannelsOperations,
    ClientGroupsOperations,
    ClientsOperations,
    DomainEventSubscriptionsOperations,
    DomainTopicEventSubscriptionsOperations,
    DomainTopicsOperations,
    DomainsOperations,
    EventSubscriptionsOperations,
    ExtensionTopicsOperations,
    NamespaceTopicEventSubscriptionsOperations,
    NamespaceTopicsOperations,
    NamespacesOperations,
    NetworkSecurityPerimeterConfigurationsOperations,
    Operations,
    PartnerConfigurationsOperations,
    PartnerDestinationsOperations,
    PartnerNamespacesOperations,
    PartnerRegistrationsOperations,
    PartnerTopicEventSubscriptionsOperations,
    PartnerTopicsOperations,
    PermissionBindingsOperations,
    PrivateEndpointConnectionsOperations,
    PrivateLinkResourcesOperations,
    SystemTopicEventSubscriptionsOperations,
    SystemTopicsOperations,
    TopicEventSubscriptionsOperations,
    TopicSpacesOperations,
    TopicTypesOperations,
    TopicsOperations,
    VerifiedPartnersOperations,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class EventGridManagementClient:  # pylint: disable=too-many-instance-attributes
    """Azure EventGrid Management Client.

    :ivar ca_certificates: CaCertificatesOperations operations
    :vartype ca_certificates: azure.mgmt.eventgrid.aio.operations.CaCertificatesOperations
    :ivar channels: ChannelsOperations operations
    :vartype channels: azure.mgmt.eventgrid.aio.operations.ChannelsOperations
    :ivar client_groups: ClientGroupsOperations operations
    :vartype client_groups: azure.mgmt.eventgrid.aio.operations.ClientGroupsOperations
    :ivar clients: ClientsOperations operations
    :vartype clients: azure.mgmt.eventgrid.aio.operations.ClientsOperations
    :ivar domains: DomainsOperations operations
    :vartype domains: azure.mgmt.eventgrid.aio.operations.DomainsOperations
    :ivar domain_topics: DomainTopicsOperations operations
    :vartype domain_topics: azure.mgmt.eventgrid.aio.operations.DomainTopicsOperations
    :ivar domain_topic_event_subscriptions: DomainTopicEventSubscriptionsOperations operations
    :vartype domain_topic_event_subscriptions:
     azure.mgmt.eventgrid.aio.operations.DomainTopicEventSubscriptionsOperations
    :ivar topic_event_subscriptions: TopicEventSubscriptionsOperations operations
    :vartype topic_event_subscriptions:
     azure.mgmt.eventgrid.aio.operations.TopicEventSubscriptionsOperations
    :ivar domain_event_subscriptions: DomainEventSubscriptionsOperations operations
    :vartype domain_event_subscriptions:
     azure.mgmt.eventgrid.aio.operations.DomainEventSubscriptionsOperations
    :ivar event_subscriptions: EventSubscriptionsOperations operations
    :vartype event_subscriptions: azure.mgmt.eventgrid.aio.operations.EventSubscriptionsOperations
    :ivar system_topic_event_subscriptions: SystemTopicEventSubscriptionsOperations operations
    :vartype system_topic_event_subscriptions:
     azure.mgmt.eventgrid.aio.operations.SystemTopicEventSubscriptionsOperations
    :ivar namespace_topic_event_subscriptions: NamespaceTopicEventSubscriptionsOperations
     operations
    :vartype namespace_topic_event_subscriptions:
     azure.mgmt.eventgrid.aio.operations.NamespaceTopicEventSubscriptionsOperations
    :ivar partner_topic_event_subscriptions: PartnerTopicEventSubscriptionsOperations operations
    :vartype partner_topic_event_subscriptions:
     azure.mgmt.eventgrid.aio.operations.PartnerTopicEventSubscriptionsOperations
    :ivar namespaces: NamespacesOperations operations
    :vartype namespaces: azure.mgmt.eventgrid.aio.operations.NamespacesOperations
    :ivar namespace_topics: NamespaceTopicsOperations operations
    :vartype namespace_topics: azure.mgmt.eventgrid.aio.operations.NamespaceTopicsOperations
    :ivar operations: Operations operations
    :vartype operations: azure.mgmt.eventgrid.aio.operations.Operations
    :ivar partner_configurations: PartnerConfigurationsOperations operations
    :vartype partner_configurations:
     azure.mgmt.eventgrid.aio.operations.PartnerConfigurationsOperations
    :ivar partner_destinations: PartnerDestinationsOperations operations
    :vartype partner_destinations:
     azure.mgmt.eventgrid.aio.operations.PartnerDestinationsOperations
    :ivar partner_namespaces: PartnerNamespacesOperations operations
    :vartype partner_namespaces: azure.mgmt.eventgrid.aio.operations.PartnerNamespacesOperations
    :ivar partner_registrations: PartnerRegistrationsOperations operations
    :vartype partner_registrations:
     azure.mgmt.eventgrid.aio.operations.PartnerRegistrationsOperations
    :ivar partner_topics: PartnerTopicsOperations operations
    :vartype partner_topics: azure.mgmt.eventgrid.aio.operations.PartnerTopicsOperations
    :ivar network_security_perimeter_configurations:
     NetworkSecurityPerimeterConfigurationsOperations operations
    :vartype network_security_perimeter_configurations:
     azure.mgmt.eventgrid.aio.operations.NetworkSecurityPerimeterConfigurationsOperations
    :ivar permission_bindings: PermissionBindingsOperations operations
    :vartype permission_bindings: azure.mgmt.eventgrid.aio.operations.PermissionBindingsOperations
    :ivar private_endpoint_connections: PrivateEndpointConnectionsOperations operations
    :vartype private_endpoint_connections:
     azure.mgmt.eventgrid.aio.operations.PrivateEndpointConnectionsOperations
    :ivar private_link_resources: PrivateLinkResourcesOperations operations
    :vartype private_link_resources:
     azure.mgmt.eventgrid.aio.operations.PrivateLinkResourcesOperations
    :ivar system_topics: SystemTopicsOperations operations
    :vartype system_topics: azure.mgmt.eventgrid.aio.operations.SystemTopicsOperations
    :ivar topics: TopicsOperations operations
    :vartype topics: azure.mgmt.eventgrid.aio.operations.TopicsOperations
    :ivar extension_topics: ExtensionTopicsOperations operations
    :vartype extension_topics: azure.mgmt.eventgrid.aio.operations.ExtensionTopicsOperations
    :ivar topic_spaces: TopicSpacesOperations operations
    :vartype topic_spaces: azure.mgmt.eventgrid.aio.operations.TopicSpacesOperations
    :ivar topic_types: TopicTypesOperations operations
    :vartype topic_types: azure.mgmt.eventgrid.aio.operations.TopicTypesOperations
    :ivar verified_partners: VerifiedPartnersOperations operations
    :vartype verified_partners: azure.mgmt.eventgrid.aio.operations.VerifiedPartnersOperations
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :param subscription_id: Subscription credentials that uniquely identify a Microsoft Azure
     subscription. The subscription ID forms part of the URI for every service call. Required.
    :type subscription_id: str
    :param base_url: Service URL. Default value is None.
    :type base_url: str
    :keyword api_version: Api Version. Default value is "2025-04-01-preview". Note that overriding
     this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self, credential: "AsyncTokenCredential", subscription_id: str, base_url: Optional[str] = None, **kwargs: Any
    ) -> None:
        _cloud = kwargs.pop("cloud_setting", None) or settings.current.azure_cloud  # type: ignore
        _endpoints = get_arm_endpoints(_cloud)
        if not base_url:
            base_url = _endpoints["resource_manager"]
        credential_scopes = kwargs.pop("credential_scopes", _endpoints["credential_scopes"])
        self._config = EventGridManagementClientConfiguration(
            credential=credential, subscription_id=subscription_id, credential_scopes=credential_scopes, **kwargs
        )

        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                AsyncARMAutoResourceProviderRegistrationPolicy(),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]
        self._client: AsyncARMPipelineClient = AsyncARMPipelineClient(
            base_url=cast(str, base_url), policies=_policies, **kwargs
        )

        client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._serialize.client_side_validation = False
        self.ca_certificates = CaCertificatesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.channels = ChannelsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.client_groups = ClientGroupsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.clients = ClientsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.domains = DomainsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.domain_topics = DomainTopicsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.domain_topic_event_subscriptions = DomainTopicEventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.topic_event_subscriptions = TopicEventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.domain_event_subscriptions = DomainEventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.event_subscriptions = EventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.system_topic_event_subscriptions = SystemTopicEventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.namespace_topic_event_subscriptions = NamespaceTopicEventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.partner_topic_event_subscriptions = PartnerTopicEventSubscriptionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.namespaces = NamespacesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.namespace_topics = NamespaceTopicsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.operations = Operations(self._client, self._config, self._serialize, self._deserialize)
        self.partner_configurations = PartnerConfigurationsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.partner_destinations = PartnerDestinationsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.partner_namespaces = PartnerNamespacesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.partner_registrations = PartnerRegistrationsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.partner_topics = PartnerTopicsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.network_security_perimeter_configurations = NetworkSecurityPerimeterConfigurationsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.permission_bindings = PermissionBindingsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.private_endpoint_connections = PrivateEndpointConnectionsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.private_link_resources = PrivateLinkResourcesOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.system_topics = SystemTopicsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.topics = TopicsOperations(self._client, self._config, self._serialize, self._deserialize)
        self.extension_topics = ExtensionTopicsOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.topic_spaces = TopicSpacesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.topic_types = TopicTypesOperations(self._client, self._config, self._serialize, self._deserialize)
        self.verified_partners = VerifiedPartnersOperations(
            self._client, self._config, self._serialize, self._deserialize
        )

    def _send_request(
        self, request: HttpRequest, *, stream: bool = False, **kwargs: Any
    ) -> Awaitable[AsyncHttpResponse]:
        """Runs the network request through the client's chained policies.

        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "https://www.example.org/")
        <HttpRequest [GET], url: 'https://www.example.org/'>
        >>> response = await client._send_request(request)
        <AsyncHttpResponse: 200 OK>

        For more information on this code flow, see https://aka.ms/azsdk/dpcodegen/python/send_request

        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """

        request_copy = deepcopy(request)
        request_copy.url = self._client.format_url(request_copy.url)
        return self._client.send_request(request_copy, stream=stream, **kwargs)  # type: ignore

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self._client.__aexit__(*exc_details)
