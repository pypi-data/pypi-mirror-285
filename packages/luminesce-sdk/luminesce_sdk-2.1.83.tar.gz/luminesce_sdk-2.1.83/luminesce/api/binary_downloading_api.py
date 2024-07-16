# coding: utf-8

"""
    FINBOURNE Luminesce Web API

    FINBOURNE Technology  # noqa: E501

    Contact: info@finbourne.com
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


import re  # noqa: F401
import io
import warnings

from pydantic.v1 import validate_arguments, ValidationError
from typing import overload, Optional, Union, Awaitable

from typing_extensions import Annotated
from pydantic.v1 import Field, StrictStr

from typing import List, Optional, Union

from luminesce.models.luminesce_binary_type import LuminesceBinaryType

from luminesce.api_client import ApiClient
from luminesce.api_response import ApiResponse
from luminesce.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class BinaryDownloadingApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @overload
    async def download_binary(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to download (each requires separate licenses and entitlements)")] = None, version : Annotated[Optional[StrictStr], Field(description="An explicit version of the binary.  Leave blank to get the latest version (recommended)")] = None, **kwargs) -> bytearray:  # noqa: E501
        ...

    @overload
    def download_binary(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to download (each requires separate licenses and entitlements)")] = None, version : Annotated[Optional[StrictStr], Field(description="An explicit version of the binary.  Leave blank to get the latest version (recommended)")] = None, async_req: Optional[bool]=True, **kwargs) -> bytearray:  # noqa: E501
        ...

    @validate_arguments
    def download_binary(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to download (each requires separate licenses and entitlements)")] = None, version : Annotated[Optional[StrictStr], Field(description="An explicit version of the binary.  Leave blank to get the latest version (recommended)")] = None, async_req: Optional[bool]=None, **kwargs) -> Union[bytearray, Awaitable[bytearray]]:  # noqa: E501
        """[EXPERIMENTAL] DownloadBinary: Downloads the latest version (or specific if needs be) of the specified Luminesce Binary, given the required entitlements.  # noqa: E501

         Downloads the latest version (or specific if needs be) of the specified Luminesce Binary, given the required entitlements.  *NOTE:* This endpoint is an alternative to time-consuming manual distribution via Drive or Email. > it relies on as underlying datastore that is not quite as \"Highly Available\" to the degree  > that FINBOURNE services generally are.   > Thus it is not subject to the same SLAs as other API endpoints are. > *If you perceive an outage, please try again later.*  Once a file has been downloaded the following steps can be used to install it (for the dotnet tools at least):  1. Open a terminal and cd to the directory you downloaded it to 2. Install / extract files from that package via: ``` dotnet tool install NameOfFileWithoutVersionNumberOrExtension -g --add-source \".\" ``` e.g. ``` dotnet tool install Finbourne.Luminesce.DbProviders.Oracle_Snowflake -g --add-source \".\" ``` 3. Execute them (see documentation for specific binary)...  The installed binaries can then be found in - Windows - `%USERPROFILE%\\.dotnet\\tools\\.store\\` - Linux/macOS - `$HOME/.dotnet/tools/.store/`  The following error codes are to be anticipated with standard Problem Detail reports: - 400 BadRequest - binary file is not available for some reason (e.g. permissions or invalid version) - 401 Unauthorized - 403 Forbidden   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.download_binary(type, version, async_req=True)
        >>> result = thread.get()

        :param type: Type of binary to download (each requires separate licenses and entitlements)
        :type type: LuminesceBinaryType
        :param version: An explicit version of the binary.  Leave blank to get the latest version (recommended)
        :type version: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: bytearray
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the download_binary_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        if async_req is not None:
            kwargs['async_req'] = async_req
        return self.download_binary_with_http_info(type, version, **kwargs)  # noqa: E501

    @validate_arguments
    def download_binary_with_http_info(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to download (each requires separate licenses and entitlements)")] = None, version : Annotated[Optional[StrictStr], Field(description="An explicit version of the binary.  Leave blank to get the latest version (recommended)")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """[EXPERIMENTAL] DownloadBinary: Downloads the latest version (or specific if needs be) of the specified Luminesce Binary, given the required entitlements.  # noqa: E501

         Downloads the latest version (or specific if needs be) of the specified Luminesce Binary, given the required entitlements.  *NOTE:* This endpoint is an alternative to time-consuming manual distribution via Drive or Email. > it relies on as underlying datastore that is not quite as \"Highly Available\" to the degree  > that FINBOURNE services generally are.   > Thus it is not subject to the same SLAs as other API endpoints are. > *If you perceive an outage, please try again later.*  Once a file has been downloaded the following steps can be used to install it (for the dotnet tools at least):  1. Open a terminal and cd to the directory you downloaded it to 2. Install / extract files from that package via: ``` dotnet tool install NameOfFileWithoutVersionNumberOrExtension -g --add-source \".\" ``` e.g. ``` dotnet tool install Finbourne.Luminesce.DbProviders.Oracle_Snowflake -g --add-source \".\" ``` 3. Execute them (see documentation for specific binary)...  The installed binaries can then be found in - Windows - `%USERPROFILE%\\.dotnet\\tools\\.store\\` - Linux/macOS - `$HOME/.dotnet/tools/.store/`  The following error codes are to be anticipated with standard Problem Detail reports: - 400 BadRequest - binary file is not available for some reason (e.g. permissions or invalid version) - 401 Unauthorized - 403 Forbidden   # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.download_binary_with_http_info(type, version, async_req=True)
        >>> result = thread.get()

        :param type: Type of binary to download (each requires separate licenses and entitlements)
        :type type: LuminesceBinaryType
        :param version: An explicit version of the binary.  Leave blank to get the latest version (recommended)
        :type version: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(bytearray, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'type',
            'version'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method download_binary" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('type') is not None:  # noqa: E501
            _query_params.append(('type', _params['type'].value))

        if _params.get('version') is not None:  # noqa: E501
            _query_params.append(('version', _params['version']))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/octet-stream', 'text/plain', 'application/json', 'text/json'])  # noqa: E501

        # authentication setting
        _auth_settings = ['oauth2']  # noqa: E501

        _response_types_map = {
            '200': "bytearray",
            '400': "LusidProblemDetails",
            '403': "LusidProblemDetails",
        }

        return self.api_client.call_api(
            '/api/Download/download', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @overload
    async def get_binary_versions(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to fetch available versions of")] = None, **kwargs) -> List[str]:  # noqa: E501
        ...

    @overload
    def get_binary_versions(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to fetch available versions of")] = None, async_req: Optional[bool]=True, **kwargs) -> List[str]:  # noqa: E501
        ...

    @validate_arguments
    def get_binary_versions(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to fetch available versions of")] = None, async_req: Optional[bool]=None, **kwargs) -> Union[List[str], Awaitable[List[str]]]:  # noqa: E501
        """[EXPERIMENTAL] GetBinaryVersions: Gets the list of available versions of a user-downloadable binary from Nexus  # noqa: E501

         Gets all available versions of a given binary type (from newest to oldest) This does not mean you are entitled to download them.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_binary_versions(type, async_req=True)
        >>> result = thread.get()

        :param type: Type of binary to fetch available versions of
        :type type: LuminesceBinaryType
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: List[str]
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the get_binary_versions_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        if async_req is not None:
            kwargs['async_req'] = async_req
        return self.get_binary_versions_with_http_info(type, **kwargs)  # noqa: E501

    @validate_arguments
    def get_binary_versions_with_http_info(self, type : Annotated[Optional[LuminesceBinaryType], Field(description="Type of binary to fetch available versions of")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """[EXPERIMENTAL] GetBinaryVersions: Gets the list of available versions of a user-downloadable binary from Nexus  # noqa: E501

         Gets all available versions of a given binary type (from newest to oldest) This does not mean you are entitled to download them.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_binary_versions_with_http_info(type, async_req=True)
        >>> result = thread.get()

        :param type: Type of binary to fetch available versions of
        :type type: LuminesceBinaryType
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(List[str], status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'type'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_binary_versions" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('type') is not None:  # noqa: E501
            _query_params.append(('type', _params['type'].value))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['text/plain', 'application/json', 'text/json'])  # noqa: E501

        # authentication setting
        _auth_settings = ['oauth2']  # noqa: E501

        _response_types_map = {
            '200': "List[str]",
            '400': "LusidProblemDetails",
            '403': "LusidProblemDetails",
        }

        return self.api_client.call_api(
            '/api/Download/versions', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))
