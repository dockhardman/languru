import pickle
import time
from typing import List, Optional, Text

from diskcache import Cache
from yarl import URL

from languru.config import logger
from languru.types.model import Model


class ModelDiscovery:
    url: URL

    def __str__(self) -> Text:
        url: Text = str(self.url) if getattr(self, "url", None) else "NotSet"
        return f"{self.__class__.__name__}({url})"

    @classmethod
    def from_url(cls, url: Text | URL):
        url_str: Text = str(URL(url))
        # SQL
        if (
            url_str.startswith("sqlite")
            or url_str.startswith("postgresql")
            or url_str.startswith("postgres")
            or url_str.startswith("mysql")
        ):
            from languru.resources.model_discovery.sql import SqlModelDiscovery

            return SqlModelDiscovery(url)

        # Local
        elif (
            url_str.startswith("diskcache")
            or url_str.startswith("local")
            or url_str.startswith("localhost")
            or url_str.startswith("file")
            or url_str.startswith("fs")
        ):
            return DiskCacheModelDiscovery(url)

        # Undefined
        else:
            logger.error(f"Unsupported discovery url: {url_str}")
            raise ValueError(f"Unsupported discovery url: {url_str}")

    def touch(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    def register(self, model: Model, created: int | None = None) -> Model:
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


class DiskCacheModelDiscovery(ModelDiscovery):
    def __init__(self, url: Text | URL):
        self.url = URL(url)
        self.file_root = f"{self.url.host or ''}{self.url.path}"
        self.query_params = self.url.query
        self.cache = Cache(self.file_root, size_limit=50 * 1024 * 1024)
        self.global_expire: int = 60 * 60

    def touch(self) -> bool:
        self.cache.set("__touch__", b"", expire=self.global_expire)
        return True

    def register(self, model: Model, created: int | None = None) -> Model:
        if not isinstance(model, Model):
            raise TypeError(f"Expected Model, got {type(model)}")
        if not model.id:
            raise ValueError("Model id is required")

        created = int(time.time()) if created is None else created
        model.created = created
        self.cache.set(model.id, pickle.dumps(model), expire=self.global_expire)
        return model

    def retrieve(self, id: Text) -> Model | None:
        model_bytes: Optional[bytes] = self.cache.get(id, default=None)  # type: ignore
        if model_bytes is None:
            return None
        return pickle.loads(model_bytes)

    def list(
        self,
        id: Optional[Text] = None,
        owned_by: Optional[Text] = None,
        created_from: Optional[int] = None,
        created_to: Optional[int] = None,
        limit: int = 20,
    ) -> list[Model]:
        models: List[Model] = []
        for model_id in self.cache:
            model_bytes = self.cache[model_id]
            try:
                model: Model = pickle.loads(model_bytes)  # type: ignore
                if id is not None and model.id != id:
                    continue
                if owned_by is not None and model.owned_by != owned_by:
                    continue
                if created_from is not None and model.created < created_from:
                    continue
                if created_to is not None and model.created > created_to:
                    continue
                models.append(model)
            except (TypeError, EOFError):
                continue
            if len(models) >= limit:
                break
        return models
