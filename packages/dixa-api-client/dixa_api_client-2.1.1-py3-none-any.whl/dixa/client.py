import logging
import time
from enum import Enum
from typing import Any, Mapping, Type, Union

from requests import Request, Response
from requests.exceptions import HTTPError, JSONDecodeError, RequestException
from requests.models import PreparedRequest
from requests.sessions import Session

from .exceptions import DixaAPIError, DixaHTTPError, DixaRequestException


class RequestMethod(Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class DixaClient:
    """Dixa API client."""

    def __init__(
        self,
        api_key: str,
        api_secret: str | None = None,
        max_retries: int = 3,
        retry_delay: int = 10,
        logger: logging.Logger | None = None,
    ):
        """Initializes the Dixa API client."""

        self._api_secret = api_secret
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._retries = 0
        self._logger = logger or logging.getLogger(__name__)

        self._session = Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": api_key,
            }
        )

    def _redact_auth(self, request: PreparedRequest) -> PreparedRequest:
        """Redacts the Authorization header from a request."""

        temp_request = request.copy()
        temp_request.headers["Authorization"] = "REDACTED"
        return temp_request

    def _retry(self, request: PreparedRequest) -> Response:
        """Retries a request."""
        redacted_request = self._redact_auth(request)
        if self._retries >= self._max_retries:
            self._logger.error(
                "Max retries reached",
                extra={
                    "retries": self._retries,
                    "max_retries": self._max_retries,
                    "url": redacted_request.url,
                    "body": redacted_request.body,
                    "headers": dict(redacted_request.headers)
                }
            )
            raise DixaAPIError("Max retries reached")

        self._retries += 1
        self._logger.info(
            "Retrying",
            extra={
                "retries": self._retries,
                "max_retries": self._max_retries,
                "delay": self._retry_delay,
                "url": redacted_request.url,
                "body": redacted_request.body,
                "headers": dict(redacted_request.headers),
            },
        )
        time.sleep(self._retry_delay)
        return self._send(request)

    def _extract_error_message(self, response: Response) -> str:
        """Extracts an error message from a response."""

        try:
            error_response = response.json()
            return error_response.get("message")
        except JSONDecodeError:
            self._logger.error(
                "Failed to decode JSON response", extra={"response": response.text}
            )
            return response.text

    def _send(self, request: PreparedRequest) -> Response:
        """Sends a request and handles retries and errors."""

        self._logger.debug(
            "Sending request", extra={"url": self._redact_auth(request).url}
        )
        try:
            response = self._session.send(request)

            if response.status_code == 429:
                self._logger.warning(
                    "Rate limited, retrying...", extra={"response": response.text}
                )
                return self._retry(request)

            if response.status_code >= 500:
                self._logger.error(
                    "Server error, retrying...",
                    extra={
                        "response": response.text,
                        "status_code": response.status_code,
                    },
                )
                return self._retry(request)

            self._retries = 0
            response.raise_for_status()

            self._logger.debug("Request successful", extra={"response": response.text})
            return response

        except HTTPError as http_error:
            self._logger.error(
                "HTTP error",
                extra={
                    "error": http_error.response.text,
                    "request": http_error.request,
                },
            )
            raise DixaHTTPError(
                self._extract_error_message(http_error.response)
            ) from http_error
        except RequestException as request_error:
            self._logger.error(
                "Request failed",
                extra={
                    "error": "An ambiguous error occured",
                    "request": request_error.request,
                },
            )
            raise DixaRequestException("Request failed") from request_error

    def _extract_data(
        self, response: Response, expected: Type[Union[dict, list]]
    ) -> Union[dict, list]:
        try:
            data = response.json().get("data", {})
        except JSONDecodeError:
            self._logger.error(
                "Failed to decode JSON response, expect missing data",
                extra={"response": response.text},
            )
            return expected()

        if not isinstance(data, expected):
            raise DixaAPIError(
                f"Expected {expected.__name__}, got {type(data).__name__}"
            )

        return data

    def _request(
        self,
        method: RequestMethod,
        url: str,
        query: Mapping[str, Any] | None = None,
        json: Mapping[str, Any] | None = None,
    ) -> Response:
        """Creates and sends a request."""

        request = Request(method.value, url, params=query, json=json)
        prepared_request = self._session.prepare_request(request)

        return self._send(prepared_request)

    def _has_next_page(self, data: dict) -> bool:
        """Checks if a response has a next page."""

        return data.get("meta", {}).get("next") is not None

    def paginate(self, url: str, query: Mapping[str, Any] | None = None) -> list:
        pages = 0
        data = []
        while True:
            pages += 1
            self._logger.debug(
                "Fetching page", extra={"page": pages, "url": url, "query": query}
            )
            response = self._request(RequestMethod.GET, url, query=query)
            if not isinstance(response, Response):
                return data

            try:
                response = response.json()
            except JSONDecodeError:
                self._logger.error(
                    "Failed to decode JSON response, expect missing data",
                    extra={"response": response.text},
                )
                break
            data.extend(response.get("data", []))

            url = response.get("meta", {}).get("next")
            if url is None:
                break

        self._logger.debug(
            "Fetched all pages", extra={"pages": pages, "records": len(data)}
        )

        return data

    def get(
        self,
        url: str,
        query: Mapping[str, Any] | None = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        """Sends a GET request."""

        response = self._request(RequestMethod.GET, url, query=query)
        return self._extract_data(response, expected)

    def post(
        self,
        url: str,
        json: Mapping[str, Any] | None = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        """Sends a POST request."""

        response = self._request(RequestMethod.POST, url, json=json)
        return self._extract_data(response, expected)

    def put(
        self,
        url: str,
        json: Mapping[str, Any] | None = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        """Sends a PUT request."""

        response = self._request(RequestMethod.PUT, url, json=json)
        return self._extract_data(response, expected)

    def delete(
        self,
        url: str,
        json: Mapping[str, Any] | None = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        """Sends a DELETE request."""

        response = self._request(RequestMethod.DELETE, url, json=json)
        return self._extract_data(response, expected)

    def patch(
        self,
        url: str,
        json: Mapping[str, Any] | None = None,
        expected: Type[Union[dict, list]] = dict,
    ) -> Union[dict, list]:
        """Sends a PATCH request."""

        response = self._request(RequestMethod.PATCH, url, json=json)
        return self._extract_data(response, expected)
