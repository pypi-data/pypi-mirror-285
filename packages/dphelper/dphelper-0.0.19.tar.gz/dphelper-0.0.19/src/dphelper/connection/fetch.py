import typing as _typing
import logging as _logging
from typing import Optional as _Optional

import requests as _requests
import concurrent.futures
from requests import Response as _Response
from requests.exceptions import ConnectionError as _ConnectionError
from time import sleep as _sleep
from urllib import parse as _parse
from fake_headers import Headers as _Headers

from ..config import Config as __Config


class FetchModule(__Config):
    def create_headers(
        self, authority: _Optional[str] = None, extra_headers: dict = {}
    ) -> dict:
        """create prefilled headers with custom authority value, append extra_headers.
        :param authority: what authority to use? If None, then no authority will be set.
        :param extra_headers: dict of headers that shall be appended
        :return: ready to use headers
        """
        headers = {}
        if authority is not None:
            headers["authority"] = authority
        headers.update(self.DEFAULT_HEADERS)
        headers.update(extra_headers)
        return headers

    def _get_headers_or_generate(self, headers: _Optional[dict] = ...) -> dict:
        "return headers or generate new ones"
        if isinstance(headers, dict) or headers is None:
            return headers
        new_headers = _Headers().generate()
        # generates:
        # 'Accept': '*/*'
        # 'Connection': 'keep-alive'
        # 'User-Agent': random_agent
        new_headers.update(self.HEADERS_UPDATE_ON_EMPTY)
        return new_headers

    @staticmethod
    def _compare_headers(left_headers: dict, right_headers: dict) -> str:
        """returns headers differences for debug purposes"""
        normalize = lambda headers: (  # keys to lowercase
            None
            if headers is None
            else {str(key).lower(): value for key, value in headers.items()}
        )
        left_headers = normalize(left_headers)
        right_headers = normalize(right_headers)
        if left_headers == right_headers:
            return "Headers equal"
        elif left_headers is None:
            return "Left-header is None"
        elif right_headers is None:
            return "Right-header is None"

        # what is unique in left-headers? in right-headers? what is unequal?
        exclusives = []
        unequalities = []
        left_keys, right_keys = set(left_headers), set(right_headers)
        exclusives.extend(
            f"exclusive to left-headers: {key}" for key in left_keys - right_keys
        )
        exclusives.extend(
            f"exclusive to right-headers: {key}" for key in right_keys - left_keys
        )

        for key in left_keys.intersection(right_keys):  # shared keys
            if left_headers[key] != right_headers[key]:
                unequalities.append(f"left-headers != right-headers at ({key}):")
                unequalities.append(f"({left_headers[key]}) != ({right_headers[key]})")

        return "\n".join(unequalities + exclusives)

    def __get_proxy_full_url(self):
        url = _parse.urljoin(self.BACKEND_URL, self.BACKEND_UTILS_PATH)
        return _parse.urljoin(url, "proxy/")

    def _request_or_repeat(self, function: callable, *args, **kwargs) -> _Response:
        """Makes a request (call provided function with args and kwargs).
        * If it fails because of ConnectionError, retries;
        * If it fails because status_code >= 500, retries;
        retry count and sleep times are specified in package_consts.py

        :param function: function to call; expected to get response object from it.
        :param *args: what args to pass to function.
        :param **kwargs: what kwargs to pass to function.
        :return: `Response` or raises RuntimeError after all failures
        """

        failures_count = 0
        sleep_time = self.REQUEST_INITIAL_SLEEP_AFTER_FAILURE_IN_S
        failure_reason = ""

        def _handle_failure():
            nonlocal failures_count, sleep_time
            sleep_time = (
                sleep_time**self.REQUEST_SLEEP_INCREASE_POWER
                if failures_count > 0
                else sleep_time
            )
            failures_count = failures_count + 1

        while failures_count < self.REQUEST_DROP_ON_FAILURE_COUNT:
            if failures_count > 0:
                if self.IS_VERBOSE:
                    _logging.error(
                        f"Request failed: {failure_reason}. Retrying in {sleep_time} seconds"
                    )
                _sleep(sleep_time)
            try:
                response: _Response = function(*args, **kwargs)
                if response.status_code >= 500:
                    # server tripped, not we (internal server error)
                    raise RuntimeError
                else:
                    return response
            except _ConnectionError:
                _handle_failure()
                failure_reason = "Server inexistant or check Network settings"
            except RuntimeError:
                _handle_failure()
                failure_reason = "Remote server had an internal error"

        raise RuntimeError(
            f"[internal] Could not make connection for {self.REQUEST_DROP_ON_FAILURE_COUNT} times. Last reason of failure: {failure_reason}"
        )

    @staticmethod
    def _response_ok_or_raise(response: _requests.Response) -> None:
        """Raises ValueError if response returned failure code"""
        try:
            response.raise_for_status()
        except Exception as ex:
            raise ValueError(
                "The response was not ok. "
                f"Response code: {response.status_code} "
                f"response text: {response.text}"
            ) from ex

    def fetch_html(
        self,
        url: str,
        *,
        proxy_provider: _Optional[str] = ...,
        params: _Optional[dict] = None,
        headers: _Optional[dict] = ...,
        data: _typing.Any = None,
        json: _typing.Any = None,
        cookies: _Optional[dict] = None,
        method: str = "GET",
        is_repeat_on_failure: bool = True,
        proxy_params: _Optional[dict] = ...,
        stream: _Optional[bool] = None,
        verify: _Optional[bool] = None,
    ) -> _requests.Response:
        """returns Response object.
        :param proxy_provider: "scrapingbee" or "any" or your secret provider
        :param method: one of "POST" "GET" "PUT" "PATCH" "DELETE"
        """
        headers = self._get_headers_or_generate(headers)
        # no proxy_provider given? check is one given via DPHelper(proxy_provider="qqq")
        proxy_provider = (
            self.PROXY_PROVIDER if proxy_provider is ... else proxy_provider
        )
        proxy_params = self.PROXY_PARAMS if proxy_params is ... else proxy_params
        # to use default proxy provider, proxy_provider must be empty string or string "any".
        # using None would not use proxy, would make a direct request
        proxy_provider = "" if str(proxy_provider).lower() == "any" else proxy_provider

        # prepare perform_method and call it with request_kwargs
        if proxy_provider is None:
            # no proxy
            perform_method = (
                _requests.request  # request once
                if not is_repeat_on_failure
                else lambda *args, **kwargs: self._request_or_repeat(
                    _requests.request, *args, **kwargs
                )  # request and retry on 5xx, connection errors
            )

            request_kwargs = {
                "method": method,
                "url": url,
                "params": params,
                "headers": headers,
                "cookies": cookies,
                "data": data,
                "json": json,
                "stream": stream,
                "verify": verify,
            }
        else:
            # proxy yes
            # whoops cookies
            if cookies is not None:
                raise NotImplementedError(
                    "Current ",
                    self.PACKAGE_NAME,
                    " version does not support cookies in Proxy.",
                )
            # verify the proxy?
            if verify and self.IS_VERBOSE:
                _logging.warning("`verify` argument is ignored when using proxy")
            # perform_method + request_kwargs
            perform_method = (
                _requests.post  # once
                if not is_repeat_on_failure
                else lambda *args, **kwargs: self._request_or_repeat(
                    _requests.post,
                    *args,
                    **kwargs,
                )
            )

            request_kwargs = {
                "url": self.__get_proxy_full_url(),
                "params": {"provider": str(proxy_provider)},
                "json": {
                    "url": url,
                    "headers": headers,
                    "params": params,
                    "data": data,
                    "json": json,
                    "method": method,
                    "proxy_params": proxy_params,
                },
                "stream": stream,
            }

        # do request
        return perform_method(**request_kwargs)

    def from_url(
        self,
        url,
        verify=True,
        headers: _Optional[dict] = ...,
        *,
        proxy_provider: _Optional[str] = ...,
        proxy_params: _Optional[dict] = ...,
        encoding: _Optional[str] = None,
        trim_whitespaces=True,
    ):
        "return content with stripped trailing whitespaces (newlines) from each line"
        response = self.fetch_html(
            url,
            verify=verify,
            headers=headers,
            proxy_provider=proxy_provider,
            proxy_params=proxy_params,
        )

        # ISO-8859-1 is default encoding for html < 5
        # encoding order: user supplied one > one from response > default utf-8
        encoding_by_response = (
            "utf-8" if response.encoding in [None, "ISO-8859-1"] else response.encoding
        )
        encoding = encoding or encoding_by_response

        if not trim_whitespaces:
            return response.content.decode(encoding)
        else:
            return "".join(
                [line.decode(encoding).strip() for line in response.iter_lines()]
            )

    def crawl(self, urls, parser, max_concurrent=50, param_func=None):
        results = {}

        # Define a function that fetches and parses an URL, to be run in a thread
        def fetch_and_parse(url: str) -> None:
            try:
                params = param_func(url) if param_func else {}
                html = self.fetch_html(url, **params).text
                results[url] = parser(html)
            except Exception:
                results[url] = None

        # Use a ThreadPoolExecutor to run fetch_and_parse in parallel for all URLs
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent
        ) as executor:
            executor.map(fetch_and_parse, urls)

        return results

    def upload_all_images(self, urls, max_concurrent=50):
        # Bulk upload of images
        results = {}

        def upload_image(url: str) -> bytes:
            try:
                results[url] = self.upload_image_from_url(url)
            except Exception:
                results[url] = None

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_concurrent
        ) as executor:
             executor.map(upload_image, urls)
    
        return results