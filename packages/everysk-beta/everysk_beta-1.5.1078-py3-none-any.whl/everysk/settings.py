###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from everysk.core.fields import BoolField, ChoiceField, DictField, IntField, ListField, StrField

## Project settings
DEBUG = BoolField(default=True)

# PROD | DEV | LOCAL
PROFILE = ChoiceField(default='DEV', choices=('PROD', 'DEV', 'LOCAL'))

## Redis
REDIS_HOST = StrField(default='0.0.0.0')
REDIS_PORT = IntField(default=6379)

## Google Cloud
EVERYSK_GOOGLE_CLOUD_LOCATION = StrField(default='us-central1')
EVERYSK_GOOGLE_CLOUD_PROJECT = StrField()

# This enables/disables the Google Cloud Logging Handler
EVERYSK_GOOGLE_CLOUD_LOGGING_INTEGRATION = BoolField(default=True)

## Slack URL to send messages
SLACK_URL = StrField()

## Activate/deactivate HTTP Log for every request/response
HTTP_LOG_RESPONSE = BoolField(default=False)

## List of HTTP Success status codes that do not raise HTTPError
HTTP_SUCCESS_STATUS_CODES = ListField(default=[200, 201, 202, 303], readonly=True)

## HTTP default headers used to send requests
HTTP_DEFAULT_HEADERS = DictField(
    default={
        'Accept-Encoding': 'gzip, deflate;q=0.9',
        'Accept-Language': 'en-US, en;q=0.9, pt-BR;q=0.8, pt;q=0.7',
        'Cache-control': 'no-cache',
        'Connection': 'close', # Remove on HTTP/2 requests
        'Content-Type': 'text/html; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    },
    readonly=True
)
HTTP_DEFAULT_TIMEOUT = IntField(default=30)
HTTP_DEFAULT_SSL_VERIFY = BoolField(default=True)
HTTP_DEFAULT_RETRY_LIMIT = IntField(default=5)
HTTP_DEFAULT_RETRY_END_SECONDS = IntField(default=30)
HTTP_DEFAULT_RETRY_START_SECONDS = IntField(default=5)

## Serialization settings
SERIALIZE_DATE_FORMAT = StrField()
SERIALIZE_DATE_KEY = StrField(default='__date__')
SERIALIZE_DATETIME_FORMAT = StrField()
SERIALIZE_DATETIME_KEY = StrField('__datetime__')
SERIALIZE_UNDEFINED_KEY = StrField('__undefined__')
SERIALIZE_USE_UNDEFINED = BoolField(default=False)

## Activate/deactivate the use of the verify flag on HTTP requests.
# By default the value is Undefined and the value comes from the self._config.ssl_verify
# attribute in the HttpConnection class, if it is defined we use it.
HTTP_REQUESTS_VERIFY = BoolField(default=Undefined)

# Activate/deactivate the use of random user agents on HTTP requests
HTTP_USE_RANDOM_USER_AGENT = BoolField(default=False)
