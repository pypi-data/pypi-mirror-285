###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
# Classes that handle HTTP Connections.

# Url: https://requests.readthedocs.io/en/latest/
#      https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
#      https://developer.mozilla.org/en-US/docs/Glossary/Quality_values
#
import json
import random
import time
from os.path import dirname
from typing import Any

import requests
from everysk.core.exceptions import HttpError, InvalidArgumentError
from everysk.core.object import BaseObject
from everysk.core.compress import compress
from everysk.core.serialize import dumps, loads
from everysk.core.fields import BoolField, DictField, IntField, ListField, StrField
from everysk.core.log import Logger
from everysk.config import settings

log = Logger(name='everysk-lib-core-http-log')

###############################################################################
#   HttpConnectionConfig Class Implementation
###############################################################################
class HttpConnectionConfig(BaseObject):
    #
    user_agents_file = StrField()
    # List of user agents to be used in the requests.
    user_agents = ListField()

    # Activate/deactivate the use of the verify flag on HTTP requests.
    # By default this is defined in settings.HTTP_REQUESTS_VERIFY
    # but could be defined in the class configuration too.
    ssl_verify = BoolField(default=settings.HTTP_DEFAULT_SSL_VERIFY)

    # Limit for retries
    retry_limit = IntField(default=settings.HTTP_DEFAULT_RETRY_LIMIT)

    # Times that randrange will use to do the next retry
    retry_end_seconds = IntField(default=settings.HTTP_DEFAULT_RETRY_END_SECONDS)
    retry_start_seconds = IntField(default=settings.HTTP_DEFAULT_RETRY_START_SECONDS)

    def __after_init__(self) -> None:
        # Load the user agents from the file
        if self.user_agents_file is None:
            base_dir = dirname(__file__)
            self.user_agents_file = f'{base_dir}/fixtures/user_agents.json'

        if self.user_agents is None:
            with open(self.user_agents_file, 'r', encoding='utf-8') as fd:
                self.user_agents = json.load(fd)

    def get_ssl_verify(self) -> bool:
        """
        Returns a boolean indicating whether the SSL value
        is set.

        Returns:
            bool: True if the SSL verify is set, False otherwise.

        Example:
            >>> http_connection_config = HttpConnectionConfig()
            >>> http_connection_config.get_ssl_verify()
            True
        """
        return self.ssl_verify if settings.HTTP_REQUESTS_VERIFY is Undefined else settings.HTTP_REQUESTS_VERIFY

    def get_random_agent(self) -> str:
        """
        Return a random user agent from the list of user agents.
        """
        return random.choice(self.user_agents)


###############################################################################
#   HttpConnection Class Implementation
###############################################################################
class HttpConnection(BaseObject):
    """
    Base class to use for HTTP connections, has two attributes:
        - timeout: It's in and represent seconds, defaults to 30.
        - url: It's string and will be the destination.
    """
    class Config(HttpConnectionConfig):
        pass

    ## Private attributes
    _config: Config = None # To autocomplete correctly
    _retry_count = IntField(default=1) # Used to control how many times this connection was retry

    ## Public attributes
    headers = DictField(default=None)
    timeout = IntField(default=settings.HTTP_DEFAULT_TIMEOUT)
    url = StrField(default=None)

    def _clean_response(self, response: requests.models.Response) -> requests.models.Response:
        """
        Checks status_code for response, if status_code is different than 200 throws an exception.

        Args:
            response (requests.models.Response): Http response from server.

        Raises:
            HttpError: If something goes wrong raise exception with status_code and content.
        """
        if getattr(response, 'status_code', settings.HTTP_SUCCESS_STATUS_CODES[0]) not in settings.HTTP_SUCCESS_STATUS_CODES:
            raise HttpError(status_code=response.status_code, msg=response.content)

        return response

    def get_headers(self) -> dict:
        """
        Headers needed to send HTTP methods.
        Below are the most common Headers used by browsers,
        we use them to look less like a Bot and more like a valid access.

        Returns:
            dict: A dictionary containing the headers information.

        Example:
            >>> http_connection = HttpConnection()
            >>> http_connection.get_headers()
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'text/html; charset=UTF-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        """
        headers = settings.HTTP_DEFAULT_HEADERS.copy()
        if settings.HTTP_USE_RANDOM_USER_AGENT:
            headers['User-Agent'] = self._config.get_random_agent()

        if self.headers is not None:
            headers.update(self.headers)

        return headers

    def get_url(self) -> str:
        """
        Generate the correct url to fetch data from vendor on POST/GET requests.

        Returns:
            str: Containing the correct URL.
        """
        return self.url

    def message_error_check(self, message: str, status_code: int) -> bool: # pylint: disable=unused-argument
        """
        If this method returns True, the connection will be tried again.

        Args:
            message (str): The error message that occurred on the connection.
            status_code (int): The status code of the response.
        """
        return False

    def _get_response_from_url(self) -> requests.models.Response:
        """
        This will be implemented on child classes to really do the connection.
        """
        return None

    def get_response(self) -> requests.models.Response:
        """
        Try to fetch data from self.get_url and calling self._get_response_from_url for the complete response.
        On HttpError, if self.message_error_check is True we will try connect again for a few more times.
        """
        try:
            response = self._clean_response(self._get_response_from_url())
            # After a success we set the value to 1 again
            self._retry_count = 1
        except Exception as error: # pylint: disable=broad-exception-caught
            # Sometimes it can happen that the server is busy, if this happen the error message must be tested
            # and must return true to enable recursion and we will try again the connection.
            message = str(error).lower()
            status_code = getattr(error, 'status_code', 500)
            if self.message_error_check(message, status_code) and self._retry_count < self._config.retry_limit:
                self._retry_count += 1
                # As we have several processes, we use a random number to avoid collision between them.
                time.sleep(random.randint(self._config.retry_start_seconds, self._config.retry_end_seconds))
                response = self.get_response()
            else:
                raise error

        return response

###############################################################################
#   HttpGETConnection Class Implementation
###############################################################################
class HttpGETConnection(HttpConnection):
    """ Class that implements a interface for HTTP GET connections """
    params = DictField()
    user = StrField()
    password = StrField()

    def get_params(self) -> dict:
        """
        This method is used to make the correct params to pass on GET request.
        These params will be added to the URL with & separating then.
        """
        return self.params

    def _get_response_from_url(self) -> requests.models.Response:
        """
        Try to fetch data from url using GET request.
        Note that any dictionary key whose value is None will not be added to the URL's query string.
        """
        params = {
            'url': self.get_url(),
            'headers': self.get_headers(),
            'params': self.get_params(),
            'verify': self._config.get_ssl_verify(),
            'timeout': self.timeout
        }
        if self.user:
            params['auth'] = (self.user, self.password)

        if settings.HTTP_LOG_RESPONSE:
            dct = params.copy()
            # To remove the password in the logs
            if 'auth' in params:
                dct['auth'] = (params['auth'][0], '***********')

            log.debug('HTTP GET request: %s', dct)

        response = requests.get(**params)

        if settings.HTTP_LOG_RESPONSE:
            dct = {
                'status_code': response.status_code,
                'time': response.elapsed.total_seconds(),
                'headers': response.headers,
                'content': response.content
            }
            log.debug('HTTP GET response: %s', dct)

        return response

###############################################################################
#   HttpPOSTConnection Class Implementation
###############################################################################
class HttpPOSTConnection(HttpConnection):
    """
    Class that implements a interface for HTTP POST connections.
    If self.is_json is True the POST method will be a JSON POST,
    otherwise will be a Form POST Data.
    """
    is_json = BoolField(default=True)
    payload = DictField()

    def get_headers(self) -> dict:
        """
        Headers needed to send HTTP Post methods.

        Returns:
            dict: The headers info for POST requests.

        Example:
            >>> http_post = HttpPostConnection()
            >>> http_post.get_headers()
            {
                'Accept-Encoding': 'gzip, deflate;q=0.9',
                'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
                'Cache-control': 'no-cache',
                'Connection': 'close',
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
        """
        headers = super().get_headers()
        if self.is_json:
            headers['Content-Type'] = 'application/json; charset=utf-8'
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        return headers

    def get_payload(self) -> dict:
        """
        Make the correct payload body to pass on POST request.

        Returns:
            dict: With all the payload information to send alongside the request.
        """
        return self.payload

    def _get_response_from_url(self) -> requests.models.Response:
        """ Try to get/set data on url using POST request. """
        params = {
            'url': self.get_url(),
            'headers': self.get_headers(),
            'verify': self._config.get_ssl_verify(),
            'timeout': self.timeout
        }
        if self.is_json:
            params['json'] = self.get_payload()
        else:
            params['data'] = self.get_payload()

        if settings.HTTP_LOG_RESPONSE:
            log.debug('HTTP POST request: %s', params)

        response = requests.post(**params)

        if settings.HTTP_LOG_RESPONSE:
            dct = {
                'status_code': response.status_code,
                'time': response.elapsed.total_seconds(),
                'headers': response.headers,
                'content': response.content
            }
            log.debug('HTTP POST response: %s', dct)

        return response

###############################################################################
#   HttpPOSTCompressedConnection Class Implementation
###############################################################################
class HttpPOSTCompressedConnection(HttpPOSTConnection):

    def get_headers(self) -> dict:
        """ Headers needed to send HTTP Post methods. """
        headers = super().get_headers()
        headers['Content-Encoding'] = 'gzip'
        return headers

    def get_payload(self) -> dict:
        """ Make the correct payload body to pass on POST request. """
        return compress(self.payload, protocol='gzip', serialize='json')

    def get_response(self) -> dict:
        """
        Try to fetch data from self.get_url and calling self._get_response_from_url for the complete response.
        On HttpError, if self.message_error_check is True we will try connect again more 5 times.
        Decompress the response.content
        """
        response = super().get_response()
        return loads(response.content)

###############################################################################
#   HttpSDKPOSTConnection Class Implementation
###############################################################################
class HttpSDKPOSTConnection(HttpPOSTCompressedConnection):

    is_json = BoolField(default=False, readonly=True)

    class_name = StrField()
    method_name = StrField()
    self_obj: Any = None
    params = DictField()
    timeout = IntField(default=settings.EVERYSK_SDK_HTTP_DEFAULT_TIMEOUT)

    def get_url(self) -> str:
        return f'{settings.EVERYSK_SDK_URL}/{settings.EVERYSK_SDK_VERSION}/{settings.EVERYSK_SDK_ROUTE}'

    def get_payload(self) -> dict:
        """ Make the correct payload body to pass on POST request. """
        self.payload = {
            'class_name': self.class_name,
            'method_name': self.method_name,
            'self_obj': self.self_obj,
            'params': self.params
        }
        return super().get_payload()

    def get_headers(self) -> dict:
        """ Headers needed to send HTTP Post methods. """
        headers = super().get_headers()
        everysk_api_sid = settings.EVERYSK_API_SID
        everysk_api_token = settings.EVERYSK_API_TOKEN

        if not everysk_api_sid:
            raise InvalidArgumentError('Invalid API SID')
        if not everysk_api_token:
            raise InvalidArgumentError('Invalid API TOKEN')

        headers['Authorization'] = f'Bearer {everysk_api_sid}:{everysk_api_token}'

        return headers
