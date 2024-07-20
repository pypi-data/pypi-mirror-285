from heaobject.root import DesktopObject
from heaobject.root import AssociationContext
from heaobject.user import NONE_USER
from heaobject.account import AWSAccount
from heaserver.service import client
from heaserver.service.oidcclaimhdrs import SUB
from heaserver.service.db.aws import AWSPermissionContext
from typing import TypeVar
from yarl import URL
from aiohttp.web import Request
from collections.abc import Mapping, Sequence
from copy import copy
from multidict import MultiDict

T = TypeVar('T', bound=DesktopObject)

class AWSAssociationContext(AssociationContext):
    """
    Helper class for getting desktop object's associations with other desktop objects.
    """

    def __init__(self, request: Request, query_params: Mapping[str, str] | None = None, **kwargs):
        """
        Accepts an aiohttp Application object, a desktop object type, and any query parameters. Any additional keyword
        arguments will be passed onto the next class in the method resolution order.
        """
        super().__init__(**kwargs)
        self.__sub = request.headers.get(SUB, NONE_USER)
        self.__app = request.app
        self.__query_params = copy(query_params)

    async def get_association_many(self, obj: DesktopObject, attr: str, type_: type[T]) -> list[T]:
        """
        Gets the associated objects when the association is one-to-many or many-to-many. For one-to-one and many-to-one
        associations, an empty list or list of one is returned. This default implementation raises a ValueError.

        :param sub: the user (required).
        :param obj: the desktop object (required).
        :param attr: the attribute (required).
        :param type_: the type of the target objects in the association.
        :raises ValueError: if an error occurred, or the attr does not represent an association.
        """
        url = URL(await client.get_resource_url(self.__app, self.__type))
        query_params = MultiDict() if self.__query_params is None else self.__query_params
        for val in getattr(obj, attr):
            query_params.add(attr.removesuffix('s'), val)
        return await client.get_all_list(self.__app, url.with_query(query_params), type_, query_params, headers={SUB: self.__sub})


