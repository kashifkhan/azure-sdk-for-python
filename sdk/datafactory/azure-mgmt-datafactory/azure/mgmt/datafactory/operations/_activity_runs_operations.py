# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------
from io import IOBase
import sys
from typing import Any, Callable, Dict, IO, Optional, TypeVar, Union, overload

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.mgmt.core.exceptions import ARMErrorFormat

from .. import models as _models
from .._serialization import Serializer

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def build_query_by_pipeline_run_request(
    resource_group_name: str, factory_name: str, run_id: str, subscription_id: str, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version: str = kwargs.pop("api_version", _params.pop("api-version", "2018-06-01"))
    content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = kwargs.pop(
        "template_url",
        "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.DataFactory/factories/{factoryName}/pipelineruns/{runId}/queryActivityruns",
    )  # pylint: disable=line-too-long
    path_format_arguments = {
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, "str"),
        "resourceGroupName": _SERIALIZER.url(
            "resource_group_name", resource_group_name, "str", max_length=90, min_length=1, pattern=r"^[-\w\._\(\)]+$"
        ),
        "factoryName": _SERIALIZER.url(
            "factory_name",
            factory_name,
            "str",
            max_length=63,
            min_length=3,
            pattern=r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$",
        ),
        "runId": _SERIALIZER.url("run_id", run_id, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

    # Construct headers
    if content_type is not None:
        _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, **kwargs)


class ActivityRunsOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.mgmt.datafactory.DataFactoryManagementClient`'s
        :attr:`activity_runs` attribute.
    """

    models = _models

    def __init__(self, *args, **kwargs):
        input_args = list(args)
        self._client = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @overload
    def query_by_pipeline_run(
        self,
        resource_group_name: str,
        factory_name: str,
        run_id: str,
        filter_parameters: _models.RunFilterParameters,
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.ActivityRunsQueryResponse:
        """Query activity runs based on input filter conditions.

        :param resource_group_name: The resource group name. Required.
        :type resource_group_name: str
        :param factory_name: The factory name. Required.
        :type factory_name: str
        :param run_id: The pipeline run identifier. Required.
        :type run_id: str
        :param filter_parameters: Parameters to filter the activity runs. Required.
        :type filter_parameters: ~azure.mgmt.datafactory.models.RunFilterParameters
        :keyword content_type: Body Parameter content-type. Content type parameter for JSON body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ActivityRunsQueryResponse or the result of cls(response)
        :rtype: ~azure.mgmt.datafactory.models.ActivityRunsQueryResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def query_by_pipeline_run(
        self,
        resource_group_name: str,
        factory_name: str,
        run_id: str,
        filter_parameters: IO[bytes],
        *,
        content_type: str = "application/json",
        **kwargs: Any
    ) -> _models.ActivityRunsQueryResponse:
        """Query activity runs based on input filter conditions.

        :param resource_group_name: The resource group name. Required.
        :type resource_group_name: str
        :param factory_name: The factory name. Required.
        :type factory_name: str
        :param run_id: The pipeline run identifier. Required.
        :type run_id: str
        :param filter_parameters: Parameters to filter the activity runs. Required.
        :type filter_parameters: IO[bytes]
        :keyword content_type: Body Parameter content-type. Content type parameter for binary body.
         Default value is "application/json".
        :paramtype content_type: str
        :return: ActivityRunsQueryResponse or the result of cls(response)
        :rtype: ~azure.mgmt.datafactory.models.ActivityRunsQueryResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def query_by_pipeline_run(
        self,
        resource_group_name: str,
        factory_name: str,
        run_id: str,
        filter_parameters: Union[_models.RunFilterParameters, IO[bytes]],
        **kwargs: Any
    ) -> _models.ActivityRunsQueryResponse:
        """Query activity runs based on input filter conditions.

        :param resource_group_name: The resource group name. Required.
        :type resource_group_name: str
        :param factory_name: The factory name. Required.
        :type factory_name: str
        :param run_id: The pipeline run identifier. Required.
        :type run_id: str
        :param filter_parameters: Parameters to filter the activity runs. Is either a
         RunFilterParameters type or a IO[bytes] type. Required.
        :type filter_parameters: ~azure.mgmt.datafactory.models.RunFilterParameters or IO[bytes]
        :return: ActivityRunsQueryResponse or the result of cls(response)
        :rtype: ~azure.mgmt.datafactory.models.ActivityRunsQueryResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        error_map: MutableMapping = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version: str = kwargs.pop("api_version", _params.pop("api-version", self._config.api_version))
        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.ActivityRunsQueryResponse] = kwargs.pop("cls", None)

        content_type = content_type or "application/json"
        _json = None
        _content = None
        if isinstance(filter_parameters, (IOBase, bytes)):
            _content = filter_parameters
        else:
            _json = self._serialize.body(filter_parameters, "RunFilterParameters")

        _request = build_query_by_pipeline_run_request(
            resource_group_name=resource_group_name,
            factory_name=factory_name,
            run_id=run_id,
            subscription_id=self._config.subscription_id,
            api_version=api_version,
            content_type=content_type,
            json=_json,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(_request.url)

        _stream = False
        pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response, error_format=ARMErrorFormat)

        deserialized = self._deserialize("ActivityRunsQueryResponse", pipeline_response.http_response)

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore
