###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################


class _BaseException(Exception):
    """
    Inherits from 'Exception' and adds its own features

    Custom Base Exception that will generate an attribute called msg
    with the error message and will be used to catch errors.
    """
    ## Private attributes
    _args: tuple = None

    ## Public attributes
    msg: str = 'Application error.'

    ## Properties
    @property
    def args(self) -> tuple:
        """ Keeps the args attribute in sync with the msg attribute. """
        return self._args

    @args.setter
    def args(self, value: tuple) -> None:
        """  Used to keep sync the args and the msg attribute. """
        if not isinstance(value, tuple):
            raise ValueError(f"The 'args' value must be a tuple not {type(value)}.")

        self.msg = value[0]
        self._args = value

    ## Methods
    def __init__(self, *args: list, **kwargs: dict) -> None:
        super().__init__(*args)
        if len(args) == 1:
            self.msg = args[0]

        if kwargs:
            for attr, value in kwargs.items():
                setattr(self, attr, value)

    def __str__(self):
        return f'{self.msg}'

class DateError(_BaseException):
    """
    Custom exception class for date-related errors

    This exception class inherits from _BaseException and is used to handle errors related to date operations.


    Example:
        To raise a DateError exception:
        >>> raise DateError("Invalid date format.")
    """
    pass

class DefaultError(_BaseException):
    """
    Custom exception class for default errors.
    This exception class inherits from _BaseException and serves as a generic
    error class for handling default or unspecified errors.

    Usage:
        To raise a DefaultError exception:
        >>> raise DefaultError("An error occurred")
    """
    pass

class FieldValueError(_BaseException, ValueError):
    """
    Custom exception class for field value erros.
    This exception class inherits from both _BaseException and ValueError.
    It is used to handle errors related to invalid field values.

    Example:
        To raise a FieldValueError exception:
        >>> raise FieldValueError("Invalid field value.")
    """
    pass

class SDKValueError(_BaseException, ValueError):
    pass

class SDKTypeError(_BaseException, TypeError):
    pass

class EntityNotFound(_BaseException):
    pass

class HttpError(_BaseException):
    status_code: int = 500

    def __str__(self):
        return f'{self.status_code} -> {self.msg}'

class ReadonlyError(_BaseException):
    pass

class RedisEmptyListError(_BaseException):
    pass

class RequiredError(_BaseException):
    pass

class SDKError(_BaseException):
    pass

class QueryError(_BaseException):
    pass

class EntityError(_BaseException):
    pass

class InvalidArgumentError(_BaseException):
    pass

class APIError(_BaseException):
    # pylint: disable=import-outside-toplevel

    def __init__(self, code, message):
        from everysk.core.serialize import loads
        super().__init__(message)
        self.__code = code
        self.__message = loads(message, protocol='json') if message else message

    def __str__(self):
        from everysk.core.serialize import dumps
        if self.__code and self.__message:
            return dumps(self.__message, sort_keys=True, indent=2, protocol='json')
        return 'API ERROR'

class WorkerError(_BaseException):
    pass
