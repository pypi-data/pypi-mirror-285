from typing import Mapping, Optional, overload, Union

import httpx
import openai
from openai.lib.azure import AsyncAzureADTokenProvider, AzureADTokenProvider

from maitai._config import config
from maitai._maitai import Chat
from maitai._maitai_async import AsyncChat

DEFAULT_MAX_RETRIES = 2


class MaitaiAsyncAzureOpenAIClient:
    @overload
    def __init__(
        self,
        *,
        azure_endpoint: str,
        maitai_api_key: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AsyncAzureADTokenProvider] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        maitai_api_key: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AsyncAzureADTokenProvider] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        base_url: str,
        maitai_api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AsyncAzureADTokenProvider] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        maitai_api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AsyncAzureADTokenProvider] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        _strict_response_validation: bool = False,
    ):
        if maitai_api_key:
            config.initialize(maitai_api_key)
        self.client = openai.AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_version=api_version,
            api_key=api_key,
            azure_ad_token=azure_ad_token,
            azure_ad_token_provider=azure_ad_token_provider,
            organization=organization,
            project=project,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )

        self.chat = AsyncChat(self.client)


class MaitaiAzureOpenAIClient:
    @overload
    def __init__(
        self,
        *,
        maitai_api_key: Optional[str] = None,
        azure_endpoint: str,
        azure_deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AzureADTokenProvider] = None,
        organization: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        maitai_api_key: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AzureADTokenProvider] = None,
        organization: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    @overload
    def __init__(
        self,
        *,
        base_url: str,
        maitai_api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AzureADTokenProvider] = None,
        organization: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        ...

    def __init__(
        self,
        *,
        maitai_api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        azure_deployment: Optional[str] = None,
        api_key: Optional[str] = None,
        azure_ad_token: Optional[str] = None,
        azure_ad_token_provider: Optional[AzureADTokenProvider] = None,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Union[float, httpx.Timeout, None, openai.NotGiven] = openai.NotGiven,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: bool = False,
    ) -> None:
        if maitai_api_key:
            config.initialize(maitai_api_key)
        self.client = openai.AzureOpenAI(
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
            api_version=api_version,
            api_key=api_key,
            azure_ad_token=azure_ad_token,
            azure_ad_token_provider=azure_ad_token_provider,
            organization=organization,
            project=project,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )
        self.chat = Chat(self.client)
