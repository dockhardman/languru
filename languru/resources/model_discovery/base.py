from typing import Optional, Text

from yarl import URL

from languru.config import logger
from languru.types.model import Model


class ModelDiscovery:

    @classmethod
    def from_url(cls, url: Text | URL):
        url_str: Text = str(url).strip()
        if (
            url_str.startswith("sqlite")
            or url_str.startswith("postgresql")
            or url_str.startswith("postgres")
            or url_str.startswith("mysql")
        ):
            from languru.resources.model_discovery.sql import SqlModelDiscovery

            return SqlModelDiscovery(url)
        else:
            logger.error(f"Unsupported discovery url: {url_str}")
            raise ValueError(f"Unsupported discovery url: {url_str}")

    def touch(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    def register(self, model: Model) -> Model:
        raise NotImplementedError  # pragma: no cover

    def retrieve(self, id: Text) -> Model | None:
        raise NotImplementedError  # pragma: no cover

    def list(
        self,
        id: Optional[Text] = None,
        owned_by: Optional[Text] = None,
        created_from: Optional[int] = None,
        created_to: Optional[int] = None,
        limit: int = 20,
    ) -> list[Model]:
        raise NotImplementedError  # pragma: no cover
