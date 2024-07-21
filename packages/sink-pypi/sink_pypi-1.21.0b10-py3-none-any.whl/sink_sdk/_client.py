# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import json
from typing import Any, Dict, Union, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import resources as _resources, _constants, _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Body,
    Omit,
    Query,
    Headers,
    Timeout,
    NoneType,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import (
    is_given,
    get_async_library,
    maybe_coerce_float,
    maybe_coerce_boolean,
    maybe_coerce_integer,
)
from ._version import __version__
from ._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import SinkError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
    make_request_options,
)
from .types.api_status import APIStatus

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "_resources",
    "Sink",
    "AsyncSink",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "https://demo.stainlessapi.com/",
    "sandbox": "https://demo-sanbox.stainlessapi.com/",
}


class Sink(SyncAPIClient):
    testing: _resources.TestingResource
    complex_queries: _resources.ComplexQueriesResource
    casing: _resources.CasingResource
    default_req_options: _resources.DefaultReqOptionsResource
    tools: _resources.ToolsResource
    undocumented_resource: _resources.UndocumentedResourceResource
    method_config: _resources.MethodConfigResource
    streaming: _resources.StreamingResource
    pagination_tests: _resources.PaginationTestsResource
    docstrings: _resources.DocstringsResource
    invalid_schemas: _resources.InvalidSchemasResource
    resource_refs: _resources.ResourceRefsResource
    cards: _resources.CardsResource
    files: _resources.FilesResource
    binaries: _resources.BinariesResource
    resources: _resources.ResourcesResource
    config_tools: _resources.ConfigToolsResource
    company: _resources.CompanyResource
    openapi_formats: _resources.OpenAPIFormatsResource
    parent: _resources.ParentResource
    envelopes: _resources.EnvelopesResource
    types: _resources.TypesResource
    clients: _resources.ClientsResource
    names: _resources.NamesResource
    widgets: _resources.WidgetsResource
    webhooks: _resources.WebhooksResource
    client_params: _resources.ClientParamsResource
    responses: _resources.ResponsesResource
    path_params: _resources.PathParamsResource
    positional_params: _resources.PositionalParamsResource
    empty_body: _resources.EmptyBodyResource
    query_params: _resources.QueryParamsResource
    body_params: _resources.BodyParamsResource
    header_params: _resources.HeaderParamsResource
    mixed_params: _resources.MixedParamsResource
    make_ambiguous_schemas_looser: _resources.MakeAmbiguousSchemasLooserResource
    make_ambiguous_schemas_explicit: _resources.MakeAmbiguousSchemasExplicitResource
    decorator_tests: _resources.DecoratorTestsResource
    tests: _resources.TestsResource
    deeply_nested: _resources.DeeplyNestedResource
    version_1_30_names: _resources.Version1_30NamesResource
    recursion: _resources.RecursionResource
    shared_query_params: _resources.SharedQueryParamsResource
    model_referenced_in_parent_and_child: _resources.ModelReferencedInParentAndChildResource
    only_custom_methods: _resources.OnlyCustomMethodsResource
    with_raw_response: SinkWithRawResponse
    with_streaming_response: SinkWithStreamedResponse

    # client options
    user_token: str | None
    api_key_header: str | None
    api_key_query: str | None
    username: str
    client_id: str | None
    client_secret: str | None
    some_boolean_arg: bool | None
    some_integer_arg: int | None
    some_number_arg: float | None
    some_number_arg_required: float
    some_number_arg_required_no_default: float
    some_number_arg_required_no_default_no_env: float
    required_arg_no_env: str
    required_arg_no_env_with_default: str
    client_path_param: str | None
    camel_case_path: str | None
    client_query_param: str | None
    client_path_or_query_param: str | None

    # constants
    CONSTANT_WITH_NEWLINES = _constants.CONSTANT_WITH_NEWLINES

    _environment: Literal["production", "sandbox"] | NotGiven

    def __init__(
        self,
        *,
        user_token: str | None = None,
        api_key_header: str | None = None,
        api_key_query: str | None = None,
        username: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        some_boolean_arg: bool | None = None,
        some_integer_arg: int | None = None,
        some_number_arg: float | None = None,
        some_number_arg_required: float | None = None,
        some_number_arg_required_no_default: float | None = None,
        some_number_arg_required_no_default_no_env: float,
        required_arg_no_env: str,
        required_arg_no_env_with_default: str | None = "hi!",
        client_path_param: str | None = None,
        camel_case_path: str | None = None,
        client_query_param: str | None = None,
        client_path_or_query_param: str | None = None,
        environment: Literal["production", "sandbox"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous sink client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `user_token` from `SINK_CUSTOM_API_KEY_ENV`
        - `api_key_header` from `SINK_CUSTOM_API_KEY_HEADER_ENV`
        - `api_key_query` from `SINK_CUSTOM_API_KEY_QUERY_ENV`
        - `username` from `SINK_USER`
        - `client_id` from `SINK_CLIENT_ID`
        - `client_secret` from `SINK_CLIENT_SECRET`
        - `some_boolean_arg` from `SINK_SOME_BOOLEAN_ARG`
        - `some_integer_arg` from `SINK_SOME_INTEGER_ARG`
        - `some_number_arg` from `SINK_SOME_NUMBER_ARG`
        - `some_number_arg_required` from `SINK_SOME_NUMBER_ARG`
        - `some_number_arg_required_no_default` from `SINK_SOME_NUMBER_ARG`
        """
        if user_token is None:
            user_token = os.environ.get("SINK_CUSTOM_API_KEY_ENV")
        self.user_token = user_token

        if api_key_header is None:
            api_key_header = os.environ.get("SINK_CUSTOM_API_KEY_HEADER_ENV")
        self.api_key_header = api_key_header

        if api_key_query is None:
            api_key_query = os.environ.get("SINK_CUSTOM_API_KEY_QUERY_ENV")
        self.api_key_query = api_key_query

        if username is None:
            username = os.environ.get("SINK_USER")
        if username is None:
            raise SinkError(
                "The username client option must be set either by passing username to the client or by setting the SINK_USER environment variable"
            )
        self.username = username

        if client_id is None:
            client_id = os.environ.get("SINK_CLIENT_ID")
        self.client_id = client_id

        if client_secret is None:
            client_secret = os.environ.get("SINK_CLIENT_SECRET") or "hellosecret"
        self.client_secret = client_secret

        if some_boolean_arg is None:
            some_boolean_arg = maybe_coerce_boolean(os.environ.get("SINK_SOME_BOOLEAN_ARG")) or True
        self.some_boolean_arg = some_boolean_arg

        if some_integer_arg is None:
            some_integer_arg = maybe_coerce_integer(os.environ.get("SINK_SOME_INTEGER_ARG")) or 123
        self.some_integer_arg = some_integer_arg

        if some_number_arg is None:
            some_number_arg = maybe_coerce_float(os.environ.get("SINK_SOME_NUMBER_ARG")) or 1.2
        self.some_number_arg = some_number_arg

        if some_number_arg_required is None:
            some_number_arg_required = maybe_coerce_float(os.environ.get("SINK_SOME_NUMBER_ARG")) or 1.2
        self.some_number_arg_required = some_number_arg_required

        if some_number_arg_required_no_default is None:
            some_number_arg_required_no_default = maybe_coerce_float(os.environ.get("SINK_SOME_NUMBER_ARG"))
        if some_number_arg_required_no_default is None:
            raise SinkError(
                "The some_number_arg_required_no_default client option must be set either by passing some_number_arg_required_no_default to the client or by setting the SINK_SOME_NUMBER_ARG environment variable"
            )
        self.some_number_arg_required_no_default = some_number_arg_required_no_default

        self.some_number_arg_required_no_default_no_env = some_number_arg_required_no_default_no_env

        self.required_arg_no_env = required_arg_no_env

        if required_arg_no_env_with_default is None:
            required_arg_no_env_with_default = "hi!"
        self.required_arg_no_env_with_default = required_arg_no_env_with_default

        self.client_path_param = client_path_param

        self.camel_case_path = camel_case_path

        self.client_query_param = client_query_param

        self.client_path_or_query_param = client_path_or_query_param

        self._environment = environment

        base_url_env = os.environ.get("SINK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `SINK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._idempotency_header = "Idempotency-Key"

        self._default_stream_cls = Stream

        self.testing = _resources.TestingResource(self)
        self.complex_queries = _resources.ComplexQueriesResource(self)
        self.casing = _resources.CasingResource(self)
        self.default_req_options = _resources.DefaultReqOptionsResource(self)
        self.tools = _resources.ToolsResource(self)
        self.undocumented_resource = _resources.UndocumentedResourceResource(self)
        self.method_config = _resources.MethodConfigResource(self)
        self.streaming = _resources.StreamingResource(self)
        self.pagination_tests = _resources.PaginationTestsResource(self)
        self.docstrings = _resources.DocstringsResource(self)
        self.invalid_schemas = _resources.InvalidSchemasResource(self)
        self.resource_refs = _resources.ResourceRefsResource(self)
        self.cards = _resources.CardsResource(self)
        self.files = _resources.FilesResource(self)
        self.binaries = _resources.BinariesResource(self)
        self.resources = _resources.ResourcesResource(self)
        self.config_tools = _resources.ConfigToolsResource(self)
        self.company = _resources.CompanyResource(self)
        self.openapi_formats = _resources.OpenAPIFormatsResource(self)
        self.parent = _resources.ParentResource(self)
        self.envelopes = _resources.EnvelopesResource(self)
        self.types = _resources.TypesResource(self)
        self.clients = _resources.ClientsResource(self)
        self.names = _resources.NamesResource(self)
        self.widgets = _resources.WidgetsResource(self)
        self.webhooks = _resources.WebhooksResource(self)
        self.client_params = _resources.ClientParamsResource(self)
        self.responses = _resources.ResponsesResource(self)
        self.path_params = _resources.PathParamsResource(self)
        self.positional_params = _resources.PositionalParamsResource(self)
        self.empty_body = _resources.EmptyBodyResource(self)
        self.query_params = _resources.QueryParamsResource(self)
        self.body_params = _resources.BodyParamsResource(self)
        self.header_params = _resources.HeaderParamsResource(self)
        self.mixed_params = _resources.MixedParamsResource(self)
        self.make_ambiguous_schemas_looser = _resources.MakeAmbiguousSchemasLooserResource(self)
        self.make_ambiguous_schemas_explicit = _resources.MakeAmbiguousSchemasExplicitResource(self)
        self.decorator_tests = _resources.DecoratorTestsResource(self)
        self.tests = _resources.TestsResource(self)
        self.deeply_nested = _resources.DeeplyNestedResource(self)
        self.version_1_30_names = _resources.Version1_30NamesResource(self)
        self.recursion = _resources.RecursionResource(self)
        self.shared_query_params = _resources.SharedQueryParamsResource(self)
        self.model_referenced_in_parent_and_child = _resources.ModelReferencedInParentAndChildResource(self)
        self.only_custom_methods = _resources.OnlyCustomMethodsResource(self)
        self.with_raw_response = SinkWithRawResponse(self)
        self.with_streaming_response = SinkWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        if self._bearer_auth:
            return self._bearer_auth
        if self._api_key_auth:
            return self._api_key_auth
        return {}

    @property
    def _bearer_auth(self) -> dict[str, str]:
        user_token = self.user_token
        if user_token is None:
            return {}
        return {"Authorization": f"Bearer {user_token}"}

    @property
    def _api_key_auth(self) -> dict[str, str]:
        api_key_header = self.api_key_header
        if api_key_header is None:
            return {}
        return {"X-STL-APIKEY": api_key_header}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            "My-Api-Version": "11",
            "X-Enable-Metrics": "1",
            "X-Client-UserName": self.username,
            "X-Client-Secret": self.client_secret if self.client_secret is not None else Omit(),
            "X-Integer": str(self.some_integer_arg) if self.some_integer_arg is not None else Omit(),
            **self._custom_headers,
        }

    @property
    @override
    def default_query(self) -> dict[str, object]:
        return {
            **super().default_query,
            "stl-api-key": self.api_key_query if self.api_key_query is not None else Omit(),
            **self._custom_query,
        }

    def copy(
        self,
        *,
        user_token: str | None = None,
        api_key_header: str | None = None,
        api_key_query: str | None = None,
        username: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        some_boolean_arg: bool | None = None,
        some_integer_arg: int | None = None,
        some_number_arg: float | None = None,
        some_number_arg_required: float | None = None,
        some_number_arg_required_no_default: float | None = None,
        some_number_arg_required_no_default_no_env: float | None = None,
        required_arg_no_env: str | None = None,
        required_arg_no_env_with_default: str | None = None,
        client_path_param: str | None = None,
        camel_case_path: str | None = None,
        client_query_param: str | None = None,
        client_path_or_query_param: str | None = None,
        environment: Literal["production", "sandbox"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            user_token=user_token or self.user_token,
            api_key_header=api_key_header or self.api_key_header,
            api_key_query=api_key_query or self.api_key_query,
            username=username or self.username,
            client_id=client_id or self.client_id,
            client_secret=client_secret or self.client_secret,
            some_boolean_arg=some_boolean_arg or self.some_boolean_arg,
            some_integer_arg=some_integer_arg or self.some_integer_arg,
            some_number_arg=some_number_arg or self.some_number_arg,
            some_number_arg_required=some_number_arg_required or self.some_number_arg_required,
            some_number_arg_required_no_default=some_number_arg_required_no_default
            or self.some_number_arg_required_no_default,
            some_number_arg_required_no_default_no_env=some_number_arg_required_no_default_no_env
            or self.some_number_arg_required_no_default_no_env,
            required_arg_no_env=required_arg_no_env or self.required_arg_no_env,
            required_arg_no_env_with_default=required_arg_no_env_with_default or self.required_arg_no_env_with_default,
            client_path_param=client_path_param or self.client_path_param,
            camel_case_path=camel_case_path or self.camel_case_path,
            client_query_param=client_query_param or self.client_query_param,
            client_path_or_query_param=client_path_or_query_param or self.client_path_or_query_param,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    def api_status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIStatus:
        """API status check"""
        return self.get(
            "/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIStatus,
        )

    api_status_alias = api_status

    def create_no_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """Endpoint returning no response"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self.post(
            "/no_response",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def get_auth_url(
        self,
        *,
        print_data: bool,
        redirect_uri: str,
        client_id: str,
    ) -> str:
        """A top level custom method on the sink customer."""
        if print_data:
            # used to test imports
            print(json.dumps("foo"))  # noqa: T201

        return str(
            httpx.URL(
                "http://localhost:8000/auth",
                params={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                },
            )
        )

    def _get_client_path_param_path_param(self) -> str:
        from_client = self.client_path_param
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing client_path_param argument; Please provide it at the client level, e.g. Sink(client_path_param='abcd') or per method."
        )

    def _get_camel_case_path_path_param(self) -> str:
        from_client = self.camel_case_path
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing camel_case_path argument; Please provide it at the client level, e.g. Sink(camel_case_path='abcd') or per method."
        )

    def _get_client_path_or_query_param_path_param(self) -> str:
        from_client = self.client_path_or_query_param
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing client_path_or_query_param argument; Please provide it at the client level, e.g. Sink(client_path_or_query_param='abcd') or per method."
        )

    def _get_client_query_param_query_param(self) -> str | None:
        return self.client_query_param

    def _get_client_path_or_query_param_query_param(self) -> str | None:
        return self.client_path_or_query_param

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncSink(AsyncAPIClient):
    testing: _resources.AsyncTestingResource
    complex_queries: _resources.AsyncComplexQueriesResource
    casing: _resources.AsyncCasingResource
    default_req_options: _resources.AsyncDefaultReqOptionsResource
    tools: _resources.AsyncToolsResource
    undocumented_resource: _resources.AsyncUndocumentedResourceResource
    method_config: _resources.AsyncMethodConfigResource
    streaming: _resources.AsyncStreamingResource
    pagination_tests: _resources.AsyncPaginationTestsResource
    docstrings: _resources.AsyncDocstringsResource
    invalid_schemas: _resources.AsyncInvalidSchemasResource
    resource_refs: _resources.AsyncResourceRefsResource
    cards: _resources.AsyncCardsResource
    files: _resources.AsyncFilesResource
    binaries: _resources.AsyncBinariesResource
    resources: _resources.AsyncResourcesResource
    config_tools: _resources.AsyncConfigToolsResource
    company: _resources.AsyncCompanyResource
    openapi_formats: _resources.AsyncOpenAPIFormatsResource
    parent: _resources.AsyncParentResource
    envelopes: _resources.AsyncEnvelopesResource
    types: _resources.AsyncTypesResource
    clients: _resources.AsyncClientsResource
    names: _resources.AsyncNamesResource
    widgets: _resources.AsyncWidgetsResource
    webhooks: _resources.AsyncWebhooksResource
    client_params: _resources.AsyncClientParamsResource
    responses: _resources.AsyncResponsesResource
    path_params: _resources.AsyncPathParamsResource
    positional_params: _resources.AsyncPositionalParamsResource
    empty_body: _resources.AsyncEmptyBodyResource
    query_params: _resources.AsyncQueryParamsResource
    body_params: _resources.AsyncBodyParamsResource
    header_params: _resources.AsyncHeaderParamsResource
    mixed_params: _resources.AsyncMixedParamsResource
    make_ambiguous_schemas_looser: _resources.AsyncMakeAmbiguousSchemasLooserResource
    make_ambiguous_schemas_explicit: _resources.AsyncMakeAmbiguousSchemasExplicitResource
    decorator_tests: _resources.AsyncDecoratorTestsResource
    tests: _resources.AsyncTestsResource
    deeply_nested: _resources.AsyncDeeplyNestedResource
    version_1_30_names: _resources.AsyncVersion1_30NamesResource
    recursion: _resources.AsyncRecursionResource
    shared_query_params: _resources.AsyncSharedQueryParamsResource
    model_referenced_in_parent_and_child: _resources.AsyncModelReferencedInParentAndChildResource
    only_custom_methods: _resources.AsyncOnlyCustomMethodsResource
    with_raw_response: AsyncSinkWithRawResponse
    with_streaming_response: AsyncSinkWithStreamedResponse

    # client options
    user_token: str | None
    api_key_header: str | None
    api_key_query: str | None
    username: str
    client_id: str | None
    client_secret: str | None
    some_boolean_arg: bool | None
    some_integer_arg: int | None
    some_number_arg: float | None
    some_number_arg_required: float
    some_number_arg_required_no_default: float
    some_number_arg_required_no_default_no_env: float
    required_arg_no_env: str
    required_arg_no_env_with_default: str
    client_path_param: str | None
    camel_case_path: str | None
    client_query_param: str | None
    client_path_or_query_param: str | None

    # constants
    CONSTANT_WITH_NEWLINES = _constants.CONSTANT_WITH_NEWLINES

    _environment: Literal["production", "sandbox"] | NotGiven

    def __init__(
        self,
        *,
        user_token: str | None = None,
        api_key_header: str | None = None,
        api_key_query: str | None = None,
        username: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        some_boolean_arg: bool | None = None,
        some_integer_arg: int | None = None,
        some_number_arg: float | None = None,
        some_number_arg_required: float | None = None,
        some_number_arg_required_no_default: float | None = None,
        some_number_arg_required_no_default_no_env: float,
        required_arg_no_env: str,
        required_arg_no_env_with_default: str | None = "hi!",
        client_path_param: str | None = None,
        camel_case_path: str | None = None,
        client_query_param: str | None = None,
        client_path_or_query_param: str | None = None,
        environment: Literal["production", "sandbox"] | NotGiven = NOT_GIVEN,
        base_url: str | httpx.URL | None | NotGiven = NOT_GIVEN,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async sink client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `user_token` from `SINK_CUSTOM_API_KEY_ENV`
        - `api_key_header` from `SINK_CUSTOM_API_KEY_HEADER_ENV`
        - `api_key_query` from `SINK_CUSTOM_API_KEY_QUERY_ENV`
        - `username` from `SINK_USER`
        - `client_id` from `SINK_CLIENT_ID`
        - `client_secret` from `SINK_CLIENT_SECRET`
        - `some_boolean_arg` from `SINK_SOME_BOOLEAN_ARG`
        - `some_integer_arg` from `SINK_SOME_INTEGER_ARG`
        - `some_number_arg` from `SINK_SOME_NUMBER_ARG`
        - `some_number_arg_required` from `SINK_SOME_NUMBER_ARG`
        - `some_number_arg_required_no_default` from `SINK_SOME_NUMBER_ARG`
        """
        if user_token is None:
            user_token = os.environ.get("SINK_CUSTOM_API_KEY_ENV")
        self.user_token = user_token

        if api_key_header is None:
            api_key_header = os.environ.get("SINK_CUSTOM_API_KEY_HEADER_ENV")
        self.api_key_header = api_key_header

        if api_key_query is None:
            api_key_query = os.environ.get("SINK_CUSTOM_API_KEY_QUERY_ENV")
        self.api_key_query = api_key_query

        if username is None:
            username = os.environ.get("SINK_USER")
        if username is None:
            raise SinkError(
                "The username client option must be set either by passing username to the client or by setting the SINK_USER environment variable"
            )
        self.username = username

        if client_id is None:
            client_id = os.environ.get("SINK_CLIENT_ID")
        self.client_id = client_id

        if client_secret is None:
            client_secret = os.environ.get("SINK_CLIENT_SECRET") or "hellosecret"
        self.client_secret = client_secret

        if some_boolean_arg is None:
            some_boolean_arg = maybe_coerce_boolean(os.environ.get("SINK_SOME_BOOLEAN_ARG")) or True
        self.some_boolean_arg = some_boolean_arg

        if some_integer_arg is None:
            some_integer_arg = maybe_coerce_integer(os.environ.get("SINK_SOME_INTEGER_ARG")) or 123
        self.some_integer_arg = some_integer_arg

        if some_number_arg is None:
            some_number_arg = maybe_coerce_float(os.environ.get("SINK_SOME_NUMBER_ARG")) or 1.2
        self.some_number_arg = some_number_arg

        if some_number_arg_required is None:
            some_number_arg_required = maybe_coerce_float(os.environ.get("SINK_SOME_NUMBER_ARG")) or 1.2
        self.some_number_arg_required = some_number_arg_required

        if some_number_arg_required_no_default is None:
            some_number_arg_required_no_default = maybe_coerce_float(os.environ.get("SINK_SOME_NUMBER_ARG"))
        if some_number_arg_required_no_default is None:
            raise SinkError(
                "The some_number_arg_required_no_default client option must be set either by passing some_number_arg_required_no_default to the client or by setting the SINK_SOME_NUMBER_ARG environment variable"
            )
        self.some_number_arg_required_no_default = some_number_arg_required_no_default

        self.some_number_arg_required_no_default_no_env = some_number_arg_required_no_default_no_env

        self.required_arg_no_env = required_arg_no_env

        if required_arg_no_env_with_default is None:
            required_arg_no_env_with_default = "hi!"
        self.required_arg_no_env_with_default = required_arg_no_env_with_default

        self.client_path_param = client_path_param

        self.camel_case_path = camel_case_path

        self.client_query_param = client_query_param

        self.client_path_or_query_param = client_path_or_query_param

        self._environment = environment

        base_url_env = os.environ.get("SINK_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `SINK_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self._idempotency_header = "Idempotency-Key"

        self._default_stream_cls = AsyncStream

        self.testing = _resources.AsyncTestingResource(self)
        self.complex_queries = _resources.AsyncComplexQueriesResource(self)
        self.casing = _resources.AsyncCasingResource(self)
        self.default_req_options = _resources.AsyncDefaultReqOptionsResource(self)
        self.tools = _resources.AsyncToolsResource(self)
        self.undocumented_resource = _resources.AsyncUndocumentedResourceResource(self)
        self.method_config = _resources.AsyncMethodConfigResource(self)
        self.streaming = _resources.AsyncStreamingResource(self)
        self.pagination_tests = _resources.AsyncPaginationTestsResource(self)
        self.docstrings = _resources.AsyncDocstringsResource(self)
        self.invalid_schemas = _resources.AsyncInvalidSchemasResource(self)
        self.resource_refs = _resources.AsyncResourceRefsResource(self)
        self.cards = _resources.AsyncCardsResource(self)
        self.files = _resources.AsyncFilesResource(self)
        self.binaries = _resources.AsyncBinariesResource(self)
        self.resources = _resources.AsyncResourcesResource(self)
        self.config_tools = _resources.AsyncConfigToolsResource(self)
        self.company = _resources.AsyncCompanyResource(self)
        self.openapi_formats = _resources.AsyncOpenAPIFormatsResource(self)
        self.parent = _resources.AsyncParentResource(self)
        self.envelopes = _resources.AsyncEnvelopesResource(self)
        self.types = _resources.AsyncTypesResource(self)
        self.clients = _resources.AsyncClientsResource(self)
        self.names = _resources.AsyncNamesResource(self)
        self.widgets = _resources.AsyncWidgetsResource(self)
        self.webhooks = _resources.AsyncWebhooksResource(self)
        self.client_params = _resources.AsyncClientParamsResource(self)
        self.responses = _resources.AsyncResponsesResource(self)
        self.path_params = _resources.AsyncPathParamsResource(self)
        self.positional_params = _resources.AsyncPositionalParamsResource(self)
        self.empty_body = _resources.AsyncEmptyBodyResource(self)
        self.query_params = _resources.AsyncQueryParamsResource(self)
        self.body_params = _resources.AsyncBodyParamsResource(self)
        self.header_params = _resources.AsyncHeaderParamsResource(self)
        self.mixed_params = _resources.AsyncMixedParamsResource(self)
        self.make_ambiguous_schemas_looser = _resources.AsyncMakeAmbiguousSchemasLooserResource(self)
        self.make_ambiguous_schemas_explicit = _resources.AsyncMakeAmbiguousSchemasExplicitResource(self)
        self.decorator_tests = _resources.AsyncDecoratorTestsResource(self)
        self.tests = _resources.AsyncTestsResource(self)
        self.deeply_nested = _resources.AsyncDeeplyNestedResource(self)
        self.version_1_30_names = _resources.AsyncVersion1_30NamesResource(self)
        self.recursion = _resources.AsyncRecursionResource(self)
        self.shared_query_params = _resources.AsyncSharedQueryParamsResource(self)
        self.model_referenced_in_parent_and_child = _resources.AsyncModelReferencedInParentAndChildResource(self)
        self.only_custom_methods = _resources.AsyncOnlyCustomMethodsResource(self)
        self.with_raw_response = AsyncSinkWithRawResponse(self)
        self.with_streaming_response = AsyncSinkWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        if self._bearer_auth:
            return self._bearer_auth
        if self._api_key_auth:
            return self._api_key_auth
        return {}

    @property
    def _bearer_auth(self) -> dict[str, str]:
        user_token = self.user_token
        if user_token is None:
            return {}
        return {"Authorization": f"Bearer {user_token}"}

    @property
    def _api_key_auth(self) -> dict[str, str]:
        api_key_header = self.api_key_header
        if api_key_header is None:
            return {}
        return {"X-STL-APIKEY": api_key_header}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            "My-Api-Version": "11",
            "X-Enable-Metrics": "1",
            "X-Client-UserName": self.username,
            "X-Client-Secret": self.client_secret if self.client_secret is not None else Omit(),
            "X-Integer": str(self.some_integer_arg) if self.some_integer_arg is not None else Omit(),
            **self._custom_headers,
        }

    @property
    @override
    def default_query(self) -> dict[str, object]:
        return {
            **super().default_query,
            "stl-api-key": self.api_key_query if self.api_key_query is not None else Omit(),
            **self._custom_query,
        }

    def copy(
        self,
        *,
        user_token: str | None = None,
        api_key_header: str | None = None,
        api_key_query: str | None = None,
        username: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        some_boolean_arg: bool | None = None,
        some_integer_arg: int | None = None,
        some_number_arg: float | None = None,
        some_number_arg_required: float | None = None,
        some_number_arg_required_no_default: float | None = None,
        some_number_arg_required_no_default_no_env: float | None = None,
        required_arg_no_env: str | None = None,
        required_arg_no_env_with_default: str | None = None,
        client_path_param: str | None = None,
        camel_case_path: str | None = None,
        client_query_param: str | None = None,
        client_path_or_query_param: str | None = None,
        environment: Literal["production", "sandbox"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            user_token=user_token or self.user_token,
            api_key_header=api_key_header or self.api_key_header,
            api_key_query=api_key_query or self.api_key_query,
            username=username or self.username,
            client_id=client_id or self.client_id,
            client_secret=client_secret or self.client_secret,
            some_boolean_arg=some_boolean_arg or self.some_boolean_arg,
            some_integer_arg=some_integer_arg or self.some_integer_arg,
            some_number_arg=some_number_arg or self.some_number_arg,
            some_number_arg_required=some_number_arg_required or self.some_number_arg_required,
            some_number_arg_required_no_default=some_number_arg_required_no_default
            or self.some_number_arg_required_no_default,
            some_number_arg_required_no_default_no_env=some_number_arg_required_no_default_no_env
            or self.some_number_arg_required_no_default_no_env,
            required_arg_no_env=required_arg_no_env or self.required_arg_no_env,
            required_arg_no_env_with_default=required_arg_no_env_with_default or self.required_arg_no_env_with_default,
            client_path_param=client_path_param or self.client_path_param,
            camel_case_path=camel_case_path or self.camel_case_path,
            client_query_param=client_query_param or self.client_query_param,
            client_path_or_query_param=client_path_or_query_param or self.client_path_or_query_param,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    async def api_status(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> APIStatus:
        """API status check"""
        return await self.get(
            "/status",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=APIStatus,
        )

    api_status_alias = api_status

    async def create_no_response(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """Endpoint returning no response"""
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self.post(
            "/no_response",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def get_auth_url(
        self,
        *,
        print_data: bool,
        redirect_uri: str,
        client_id: str,
    ) -> str:
        """A top level custom method on the sink customer."""
        if print_data:
            # used to test imports
            print(json.dumps("foo"))  # noqa: T201

        return str(
            httpx.URL(
                "http://localhost:8000/auth",
                params={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                },
            )
        )

    def _get_client_path_param_path_param(self) -> str:
        from_client = self.client_path_param
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing client_path_param argument; Please provide it at the client level, e.g. AsyncSink(client_path_param='abcd') or per method."
        )

    def _get_camel_case_path_path_param(self) -> str:
        from_client = self.camel_case_path
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing camel_case_path argument; Please provide it at the client level, e.g. AsyncSink(camel_case_path='abcd') or per method."
        )

    def _get_client_path_or_query_param_path_param(self) -> str:
        from_client = self.client_path_or_query_param
        if from_client is not None:
            return from_client

        raise ValueError(
            "Missing client_path_or_query_param argument; Please provide it at the client level, e.g. AsyncSink(client_path_or_query_param='abcd') or per method."
        )

    def _get_client_query_param_query_param(self) -> str | None:
        return self.client_query_param

    def _get_client_path_or_query_param_query_param(self) -> str | None:
        return self.client_path_or_query_param

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class SinkWithRawResponse:
    def __init__(self, client: Sink) -> None:
        self.testing = _resources.TestingResourceWithRawResponse(client.testing)
        self.complex_queries = _resources.ComplexQueriesResourceWithRawResponse(client.complex_queries)
        self.casing = _resources.CasingResourceWithRawResponse(client.casing)
        self.default_req_options = _resources.DefaultReqOptionsResourceWithRawResponse(client.default_req_options)
        self.tools = _resources.ToolsResourceWithRawResponse(client.tools)
        self.undocumented_resource = _resources.UndocumentedResourceResourceWithRawResponse(
            client.undocumented_resource
        )
        self.method_config = _resources.MethodConfigResourceWithRawResponse(client.method_config)
        self.streaming = _resources.StreamingResourceWithRawResponse(client.streaming)
        self.pagination_tests = _resources.PaginationTestsResourceWithRawResponse(client.pagination_tests)
        self.docstrings = _resources.DocstringsResourceWithRawResponse(client.docstrings)
        self.invalid_schemas = _resources.InvalidSchemasResourceWithRawResponse(client.invalid_schemas)
        self.resource_refs = _resources.ResourceRefsResourceWithRawResponse(client.resource_refs)
        self.cards = _resources.CardsResourceWithRawResponse(client.cards)
        self.files = _resources.FilesResourceWithRawResponse(client.files)
        self.binaries = _resources.BinariesResourceWithRawResponse(client.binaries)
        self.resources = _resources.ResourcesResourceWithRawResponse(client.resources)
        self.config_tools = _resources.ConfigToolsResourceWithRawResponse(client.config_tools)
        self.company = _resources.CompanyResourceWithRawResponse(client.company)
        self.openapi_formats = _resources.OpenAPIFormatsResourceWithRawResponse(client.openapi_formats)
        self.parent = _resources.ParentResourceWithRawResponse(client.parent)
        self.envelopes = _resources.EnvelopesResourceWithRawResponse(client.envelopes)
        self.types = _resources.TypesResourceWithRawResponse(client.types)
        self.clients = _resources.ClientsResourceWithRawResponse(client.clients)
        self.names = _resources.NamesResourceWithRawResponse(client.names)
        self.widgets = _resources.WidgetsResourceWithRawResponse(client.widgets)
        self.client_params = _resources.ClientParamsResourceWithRawResponse(client.client_params)
        self.responses = _resources.ResponsesResourceWithRawResponse(client.responses)
        self.path_params = _resources.PathParamsResourceWithRawResponse(client.path_params)
        self.positional_params = _resources.PositionalParamsResourceWithRawResponse(client.positional_params)
        self.empty_body = _resources.EmptyBodyResourceWithRawResponse(client.empty_body)
        self.query_params = _resources.QueryParamsResourceWithRawResponse(client.query_params)
        self.body_params = _resources.BodyParamsResourceWithRawResponse(client.body_params)
        self.header_params = _resources.HeaderParamsResourceWithRawResponse(client.header_params)
        self.mixed_params = _resources.MixedParamsResourceWithRawResponse(client.mixed_params)
        self.make_ambiguous_schemas_looser = _resources.MakeAmbiguousSchemasLooserResourceWithRawResponse(
            client.make_ambiguous_schemas_looser
        )
        self.make_ambiguous_schemas_explicit = _resources.MakeAmbiguousSchemasExplicitResourceWithRawResponse(
            client.make_ambiguous_schemas_explicit
        )
        self.decorator_tests = _resources.DecoratorTestsResourceWithRawResponse(client.decorator_tests)
        self.tests = _resources.TestsResourceWithRawResponse(client.tests)
        self.deeply_nested = _resources.DeeplyNestedResourceWithRawResponse(client.deeply_nested)
        self.version_1_30_names = _resources.Version1_30NamesResourceWithRawResponse(client.version_1_30_names)
        self.recursion = _resources.RecursionResourceWithRawResponse(client.recursion)
        self.shared_query_params = _resources.SharedQueryParamsResourceWithRawResponse(client.shared_query_params)
        self.model_referenced_in_parent_and_child = _resources.ModelReferencedInParentAndChildResourceWithRawResponse(
            client.model_referenced_in_parent_and_child
        )

        self.api_status = to_raw_response_wrapper(
            client.api_status,
        )
        self.api_status_alias = to_raw_response_wrapper(
            client.api_status_alias,
        )
        self.create_no_response = to_raw_response_wrapper(
            client.create_no_response,
        )


class AsyncSinkWithRawResponse:
    def __init__(self, client: AsyncSink) -> None:
        self.testing = _resources.AsyncTestingResourceWithRawResponse(client.testing)
        self.complex_queries = _resources.AsyncComplexQueriesResourceWithRawResponse(client.complex_queries)
        self.casing = _resources.AsyncCasingResourceWithRawResponse(client.casing)
        self.default_req_options = _resources.AsyncDefaultReqOptionsResourceWithRawResponse(client.default_req_options)
        self.tools = _resources.AsyncToolsResourceWithRawResponse(client.tools)
        self.undocumented_resource = _resources.AsyncUndocumentedResourceResourceWithRawResponse(
            client.undocumented_resource
        )
        self.method_config = _resources.AsyncMethodConfigResourceWithRawResponse(client.method_config)
        self.streaming = _resources.AsyncStreamingResourceWithRawResponse(client.streaming)
        self.pagination_tests = _resources.AsyncPaginationTestsResourceWithRawResponse(client.pagination_tests)
        self.docstrings = _resources.AsyncDocstringsResourceWithRawResponse(client.docstrings)
        self.invalid_schemas = _resources.AsyncInvalidSchemasResourceWithRawResponse(client.invalid_schemas)
        self.resource_refs = _resources.AsyncResourceRefsResourceWithRawResponse(client.resource_refs)
        self.cards = _resources.AsyncCardsResourceWithRawResponse(client.cards)
        self.files = _resources.AsyncFilesResourceWithRawResponse(client.files)
        self.binaries = _resources.AsyncBinariesResourceWithRawResponse(client.binaries)
        self.resources = _resources.AsyncResourcesResourceWithRawResponse(client.resources)
        self.config_tools = _resources.AsyncConfigToolsResourceWithRawResponse(client.config_tools)
        self.company = _resources.AsyncCompanyResourceWithRawResponse(client.company)
        self.openapi_formats = _resources.AsyncOpenAPIFormatsResourceWithRawResponse(client.openapi_formats)
        self.parent = _resources.AsyncParentResourceWithRawResponse(client.parent)
        self.envelopes = _resources.AsyncEnvelopesResourceWithRawResponse(client.envelopes)
        self.types = _resources.AsyncTypesResourceWithRawResponse(client.types)
        self.clients = _resources.AsyncClientsResourceWithRawResponse(client.clients)
        self.names = _resources.AsyncNamesResourceWithRawResponse(client.names)
        self.widgets = _resources.AsyncWidgetsResourceWithRawResponse(client.widgets)
        self.client_params = _resources.AsyncClientParamsResourceWithRawResponse(client.client_params)
        self.responses = _resources.AsyncResponsesResourceWithRawResponse(client.responses)
        self.path_params = _resources.AsyncPathParamsResourceWithRawResponse(client.path_params)
        self.positional_params = _resources.AsyncPositionalParamsResourceWithRawResponse(client.positional_params)
        self.empty_body = _resources.AsyncEmptyBodyResourceWithRawResponse(client.empty_body)
        self.query_params = _resources.AsyncQueryParamsResourceWithRawResponse(client.query_params)
        self.body_params = _resources.AsyncBodyParamsResourceWithRawResponse(client.body_params)
        self.header_params = _resources.AsyncHeaderParamsResourceWithRawResponse(client.header_params)
        self.mixed_params = _resources.AsyncMixedParamsResourceWithRawResponse(client.mixed_params)
        self.make_ambiguous_schemas_looser = _resources.AsyncMakeAmbiguousSchemasLooserResourceWithRawResponse(
            client.make_ambiguous_schemas_looser
        )
        self.make_ambiguous_schemas_explicit = _resources.AsyncMakeAmbiguousSchemasExplicitResourceWithRawResponse(
            client.make_ambiguous_schemas_explicit
        )
        self.decorator_tests = _resources.AsyncDecoratorTestsResourceWithRawResponse(client.decorator_tests)
        self.tests = _resources.AsyncTestsResourceWithRawResponse(client.tests)
        self.deeply_nested = _resources.AsyncDeeplyNestedResourceWithRawResponse(client.deeply_nested)
        self.version_1_30_names = _resources.AsyncVersion1_30NamesResourceWithRawResponse(client.version_1_30_names)
        self.recursion = _resources.AsyncRecursionResourceWithRawResponse(client.recursion)
        self.shared_query_params = _resources.AsyncSharedQueryParamsResourceWithRawResponse(client.shared_query_params)
        self.model_referenced_in_parent_and_child = (
            _resources.AsyncModelReferencedInParentAndChildResourceWithRawResponse(
                client.model_referenced_in_parent_and_child
            )
        )

        self.api_status = async_to_raw_response_wrapper(
            client.api_status,
        )
        self.api_status_alias = async_to_raw_response_wrapper(
            client.api_status_alias,
        )
        self.create_no_response = async_to_raw_response_wrapper(
            client.create_no_response,
        )


class SinkWithStreamedResponse:
    def __init__(self, client: Sink) -> None:
        self.testing = _resources.TestingResourceWithStreamingResponse(client.testing)
        self.complex_queries = _resources.ComplexQueriesResourceWithStreamingResponse(client.complex_queries)
        self.casing = _resources.CasingResourceWithStreamingResponse(client.casing)
        self.default_req_options = _resources.DefaultReqOptionsResourceWithStreamingResponse(client.default_req_options)
        self.tools = _resources.ToolsResourceWithStreamingResponse(client.tools)
        self.undocumented_resource = _resources.UndocumentedResourceResourceWithStreamingResponse(
            client.undocumented_resource
        )
        self.method_config = _resources.MethodConfigResourceWithStreamingResponse(client.method_config)
        self.streaming = _resources.StreamingResourceWithStreamingResponse(client.streaming)
        self.pagination_tests = _resources.PaginationTestsResourceWithStreamingResponse(client.pagination_tests)
        self.docstrings = _resources.DocstringsResourceWithStreamingResponse(client.docstrings)
        self.invalid_schemas = _resources.InvalidSchemasResourceWithStreamingResponse(client.invalid_schemas)
        self.resource_refs = _resources.ResourceRefsResourceWithStreamingResponse(client.resource_refs)
        self.cards = _resources.CardsResourceWithStreamingResponse(client.cards)
        self.files = _resources.FilesResourceWithStreamingResponse(client.files)
        self.binaries = _resources.BinariesResourceWithStreamingResponse(client.binaries)
        self.resources = _resources.ResourcesResourceWithStreamingResponse(client.resources)
        self.config_tools = _resources.ConfigToolsResourceWithStreamingResponse(client.config_tools)
        self.company = _resources.CompanyResourceWithStreamingResponse(client.company)
        self.openapi_formats = _resources.OpenAPIFormatsResourceWithStreamingResponse(client.openapi_formats)
        self.parent = _resources.ParentResourceWithStreamingResponse(client.parent)
        self.envelopes = _resources.EnvelopesResourceWithStreamingResponse(client.envelopes)
        self.types = _resources.TypesResourceWithStreamingResponse(client.types)
        self.clients = _resources.ClientsResourceWithStreamingResponse(client.clients)
        self.names = _resources.NamesResourceWithStreamingResponse(client.names)
        self.widgets = _resources.WidgetsResourceWithStreamingResponse(client.widgets)
        self.client_params = _resources.ClientParamsResourceWithStreamingResponse(client.client_params)
        self.responses = _resources.ResponsesResourceWithStreamingResponse(client.responses)
        self.path_params = _resources.PathParamsResourceWithStreamingResponse(client.path_params)
        self.positional_params = _resources.PositionalParamsResourceWithStreamingResponse(client.positional_params)
        self.empty_body = _resources.EmptyBodyResourceWithStreamingResponse(client.empty_body)
        self.query_params = _resources.QueryParamsResourceWithStreamingResponse(client.query_params)
        self.body_params = _resources.BodyParamsResourceWithStreamingResponse(client.body_params)
        self.header_params = _resources.HeaderParamsResourceWithStreamingResponse(client.header_params)
        self.mixed_params = _resources.MixedParamsResourceWithStreamingResponse(client.mixed_params)
        self.make_ambiguous_schemas_looser = _resources.MakeAmbiguousSchemasLooserResourceWithStreamingResponse(
            client.make_ambiguous_schemas_looser
        )
        self.make_ambiguous_schemas_explicit = _resources.MakeAmbiguousSchemasExplicitResourceWithStreamingResponse(
            client.make_ambiguous_schemas_explicit
        )
        self.decorator_tests = _resources.DecoratorTestsResourceWithStreamingResponse(client.decorator_tests)
        self.tests = _resources.TestsResourceWithStreamingResponse(client.tests)
        self.deeply_nested = _resources.DeeplyNestedResourceWithStreamingResponse(client.deeply_nested)
        self.version_1_30_names = _resources.Version1_30NamesResourceWithStreamingResponse(client.version_1_30_names)
        self.recursion = _resources.RecursionResourceWithStreamingResponse(client.recursion)
        self.shared_query_params = _resources.SharedQueryParamsResourceWithStreamingResponse(client.shared_query_params)
        self.model_referenced_in_parent_and_child = (
            _resources.ModelReferencedInParentAndChildResourceWithStreamingResponse(
                client.model_referenced_in_parent_and_child
            )
        )

        self.api_status = to_streamed_response_wrapper(
            client.api_status,
        )
        self.api_status_alias = to_streamed_response_wrapper(
            client.api_status_alias,
        )
        self.create_no_response = to_streamed_response_wrapper(
            client.create_no_response,
        )


class AsyncSinkWithStreamedResponse:
    def __init__(self, client: AsyncSink) -> None:
        self.testing = _resources.AsyncTestingResourceWithStreamingResponse(client.testing)
        self.complex_queries = _resources.AsyncComplexQueriesResourceWithStreamingResponse(client.complex_queries)
        self.casing = _resources.AsyncCasingResourceWithStreamingResponse(client.casing)
        self.default_req_options = _resources.AsyncDefaultReqOptionsResourceWithStreamingResponse(
            client.default_req_options
        )
        self.tools = _resources.AsyncToolsResourceWithStreamingResponse(client.tools)
        self.undocumented_resource = _resources.AsyncUndocumentedResourceResourceWithStreamingResponse(
            client.undocumented_resource
        )
        self.method_config = _resources.AsyncMethodConfigResourceWithStreamingResponse(client.method_config)
        self.streaming = _resources.AsyncStreamingResourceWithStreamingResponse(client.streaming)
        self.pagination_tests = _resources.AsyncPaginationTestsResourceWithStreamingResponse(client.pagination_tests)
        self.docstrings = _resources.AsyncDocstringsResourceWithStreamingResponse(client.docstrings)
        self.invalid_schemas = _resources.AsyncInvalidSchemasResourceWithStreamingResponse(client.invalid_schemas)
        self.resource_refs = _resources.AsyncResourceRefsResourceWithStreamingResponse(client.resource_refs)
        self.cards = _resources.AsyncCardsResourceWithStreamingResponse(client.cards)
        self.files = _resources.AsyncFilesResourceWithStreamingResponse(client.files)
        self.binaries = _resources.AsyncBinariesResourceWithStreamingResponse(client.binaries)
        self.resources = _resources.AsyncResourcesResourceWithStreamingResponse(client.resources)
        self.config_tools = _resources.AsyncConfigToolsResourceWithStreamingResponse(client.config_tools)
        self.company = _resources.AsyncCompanyResourceWithStreamingResponse(client.company)
        self.openapi_formats = _resources.AsyncOpenAPIFormatsResourceWithStreamingResponse(client.openapi_formats)
        self.parent = _resources.AsyncParentResourceWithStreamingResponse(client.parent)
        self.envelopes = _resources.AsyncEnvelopesResourceWithStreamingResponse(client.envelopes)
        self.types = _resources.AsyncTypesResourceWithStreamingResponse(client.types)
        self.clients = _resources.AsyncClientsResourceWithStreamingResponse(client.clients)
        self.names = _resources.AsyncNamesResourceWithStreamingResponse(client.names)
        self.widgets = _resources.AsyncWidgetsResourceWithStreamingResponse(client.widgets)
        self.client_params = _resources.AsyncClientParamsResourceWithStreamingResponse(client.client_params)
        self.responses = _resources.AsyncResponsesResourceWithStreamingResponse(client.responses)
        self.path_params = _resources.AsyncPathParamsResourceWithStreamingResponse(client.path_params)
        self.positional_params = _resources.AsyncPositionalParamsResourceWithStreamingResponse(client.positional_params)
        self.empty_body = _resources.AsyncEmptyBodyResourceWithStreamingResponse(client.empty_body)
        self.query_params = _resources.AsyncQueryParamsResourceWithStreamingResponse(client.query_params)
        self.body_params = _resources.AsyncBodyParamsResourceWithStreamingResponse(client.body_params)
        self.header_params = _resources.AsyncHeaderParamsResourceWithStreamingResponse(client.header_params)
        self.mixed_params = _resources.AsyncMixedParamsResourceWithStreamingResponse(client.mixed_params)
        self.make_ambiguous_schemas_looser = _resources.AsyncMakeAmbiguousSchemasLooserResourceWithStreamingResponse(
            client.make_ambiguous_schemas_looser
        )
        self.make_ambiguous_schemas_explicit = (
            _resources.AsyncMakeAmbiguousSchemasExplicitResourceWithStreamingResponse(
                client.make_ambiguous_schemas_explicit
            )
        )
        self.decorator_tests = _resources.AsyncDecoratorTestsResourceWithStreamingResponse(client.decorator_tests)
        self.tests = _resources.AsyncTestsResourceWithStreamingResponse(client.tests)
        self.deeply_nested = _resources.AsyncDeeplyNestedResourceWithStreamingResponse(client.deeply_nested)
        self.version_1_30_names = _resources.AsyncVersion1_30NamesResourceWithStreamingResponse(
            client.version_1_30_names
        )
        self.recursion = _resources.AsyncRecursionResourceWithStreamingResponse(client.recursion)
        self.shared_query_params = _resources.AsyncSharedQueryParamsResourceWithStreamingResponse(
            client.shared_query_params
        )
        self.model_referenced_in_parent_and_child = (
            _resources.AsyncModelReferencedInParentAndChildResourceWithStreamingResponse(
                client.model_referenced_in_parent_and_child
            )
        )

        self.api_status = async_to_streamed_response_wrapper(
            client.api_status,
        )
        self.api_status_alias = async_to_streamed_response_wrapper(
            client.api_status_alias,
        )
        self.create_no_response = async_to_streamed_response_wrapper(
            client.create_no_response,
        )


Client = Sink

AsyncClient = AsyncSink
