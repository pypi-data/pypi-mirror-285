###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################

###############################################################################
#   Imports
###############################################################################
from typing import Any, Callable
from inspect import isclass

from everysk.config import settings
from everysk.core.exceptions import FieldValueError
from everysk.core.object import BaseDict
from everysk.core.string import import_from_string

from everysk.sdk.base import BaseSDK

###############################################################################
#   Base Script Implementation
###############################################################################
class Script(BaseDict, BaseSDK):
    """
    A base class for scripted queries.
    This class provides a base implementation for scripted queries.

    Attributes:
        - _klass (callable): The class to instantiate when fetching an entity.

    Example usage:
        To fetch an entity:
        >>> script = Script(klass=MyEntity)
        >>> entity = script.fetch(user_input, variant, workspace)
    """
    _klass: Callable = None

    def __init__(self, _klass: Callable) -> None:
        super().__init__(_klass=None)

        if _klass is not None and not isclass(_klass):
            try:
                _klass = import_from_string(settings.EVERYSK_SDK_ENTITIES_MODULES_PATH[_klass])
            except KeyError:
                raise FieldValueError(f"The _klass value '{_klass}' must be a class or a string with the class name") from KeyError

        self._klass = _klass

    def _process__klass(self, value: Any) -> Any:
        """
        This method is used to process the '_klass' attribute.
        """
        return value.__name__

    def fetch(self, user_input: Any, variant: str, workspace: str) -> Any:
        """
        Process a scripted query based on user input, variant, and workspace.

        This method provides a way to construct and execute different types of queries
        based on the specified variant. It's designed to handle a variety of scenarios
        and return the desired entity or entities based on the input parameters.

        Parameters:
            - user_input (Any): The input provided by the user, which can be used for filtering
            or as a direct entity ID.
            - variant (str): The type of scripted query to execute. Determines how the method
            processes the user input and constructs the query. Supported variants include
            'previousWorkers', 'tagLatest', any string starting with 'select', and potentially
            others.
            - workspace (str): The workspace context for the query. Used for scoping and
            verifying entity retrieval.

        Returns:
            - Any: Depending on the variant and user input, the method might return an entity,
            a list of entities, or None.

        Raises:
            - ValueError: If there's an attempted cross-workspace operation or other variant-specific
            error conditions are met.

        Note:
            The method behavior can vary greatly depending on the `variant` parameter, and it's
            important to ensure that the variant aligns with the expected user input structure.

        Example usage:
            To fetch an entity:
            >>> script = Script(klass=MyEntity)
            >>> entity = script.fetch(user_input, variant, workspace)
        """
        if user_input is None:
            return None

        if variant == 'previousWorkers' and user_input.get('id') is None:
            return self._klass(**user_input) # pylint: disable=not-callable

        response = self.get_response(self_obj=self, params={'user_input': user_input, 'variant': variant, 'workspace': workspace})

        if isinstance(response, list):
            response = [self._klass(**item) for item in response] # pylint: disable=not-callable
        elif isinstance(response, dict):
            response = self._klass(**response) # pylint: disable=not-callable

        return response

    def persist(self, entity: Any, persist: str, consistency_check: bool = False) -> Any:
        """
        This method provides a way to persist an entity based on the specified persist type.

        Parameters:
            - entity (Any): The entity to persist.
            - persist (str): The type of persist to execute. Determines how the method
            persists the entity. Supported persists include 'insert', 'update', and 'delete'.
            - consistency_check (bool): A flag to enable consistency checks before persisting.

        Returns:
            - Any: Depending on the persist type, the method might return an entity.

        Example usage:
            To persist an entity:
            >>> script = Script(klass=MyEntity)
            >>> entity = script.persist(entity, persist, consistency_check)
        """
        response = self.get_response(self_obj=self, params={'entity': entity, 'persist': persist, 'consistency_check': consistency_check})

        if isinstance(response, dict):
            response = self._klass(**response) # pylint: disable=not-callable

        return response
