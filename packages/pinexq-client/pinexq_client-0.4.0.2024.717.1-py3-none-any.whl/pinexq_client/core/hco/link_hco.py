from typing import Self, Type

import httpx
from httpx import URL

from pinexq_client.core import Link, Entity, navigate, ensure_siren_response, ClientException
from pinexq_client.core.hco.hco_base import ClientContainer, TEntity
from pinexq_client.core.hco.unavailable import UnavailableLink


class LinkHco(ClientContainer):
    _client: httpx.Client
    _link: Link

    @classmethod
    def from_link_optional(cls, client: httpx.Client, link: Link | None) -> Self | UnavailableLink:
        if link is None:
            return UnavailableLink()

        instance = cls(client)
        instance._link = link
        return instance

    @classmethod
    def from_entity_optional(cls, client: httpx.Client, entity: Entity, link_relation: str) -> Self | UnavailableLink:
        if entity is None:
            return UnavailableLink()

        link = entity.find_first_link_with_relation(link_relation)
        return cls.from_link_optional(client, link)

    @classmethod
    def from_link(cls, client: httpx.Client, link: Link) -> Self:
        result = cls.from_link_optional(client, link)
        if isinstance(result, UnavailableLink):
            raise ClientException(f"Error while mapping mandatory link: link is None")

        return result

    @classmethod
    def from_entity(cls, client: httpx.Client, entity: Entity, link_relation: str) -> Self:
        result = cls.from_entity_optional(client, entity, link_relation)
        if isinstance(result, UnavailableLink):
            raise ClientException(
                f"Error while mapping mandatory link: entity contains no link with relation {link_relation}")

        return result

    def _navigate_internal(self, parse_type: Type[TEntity] = Entity) -> TEntity:
        response = navigate(self._client, self._link, parse_type)
        return ensure_siren_response(response)

    def get_url(self) -> URL:
        return URL(self._link.href)

    def __repr__(self):
        rel_names = ', '.join((f"'{r}'" for r in self._link.rel))
        return f"<{self.__class__.__name__}: {rel_names}>"
