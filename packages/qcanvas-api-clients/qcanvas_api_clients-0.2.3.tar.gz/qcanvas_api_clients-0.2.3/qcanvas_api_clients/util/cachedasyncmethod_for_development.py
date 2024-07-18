import os
from typing import Any

import cachetools
from shelved_cache import PersistentCache, cachedasyncmethod

enable_api_caching = os.environ.get("ENABLE_API_CACHE", "false").lower() == "true"
_pc = PersistentCache(
    filename="/tmp/qcanvas_cache", wrapped_cache_cls=cachetools.LRUCache, maxsize=10000
)


def cachedasyncmethod_for_development(**kwargs) -> Any:
    def decorate(fn) -> Any:
        return (
            (cachedasyncmethod(lambda x: _pc, **kwargs))(fn)
            if enable_api_caching
            else fn
        )

    return decorate
