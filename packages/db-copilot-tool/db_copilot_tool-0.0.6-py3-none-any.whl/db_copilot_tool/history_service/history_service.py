"""File for the HistoryService Class."""

import logging
from dataclasses import dataclass

import diskcache
from db_copilot_tool.history_service.dialogue_sessions import DialogueSession


@dataclass
class HistoryServiceConfig:
    """HistoryServiceConfig Class."""

    history_service_enabled: bool
    cache_dir: str
    expire_seconds: int
    max_cache_size_mb: int


# HistoryService will use diskcache to cache the history. Use pickle to serialize the history.
class HistoryService:
    """HistoryService Class."""

    def __init__(self, config: HistoryServiceConfig):
        """Initialize the class."""
        self.config = config
        if not config.history_service_enabled:
            self.cache = None
            return
        if not config.cache_dir:
            raise ValueError("cache_dir is required")
        self.cache = diskcache.Cache(
            config.cache_dir, size_limit=config.max_cache_size_mb * 1024 * 1024
        )

    @property
    def enabled(self):
        """Verify config is enabled."""
        return self.config.history_service_enabled

    def get_dialogue_session(self, session_id):
        """get_dialogue_session."""
        key = f"dialogue_session_{session_id}"
        session = self.cache.get(key)
        if session is None:
            session = DialogueSession()
        return session

    def set_dialogue_session(
        self, session_id, dialogue_session: DialogueSession, expire_seconds: int = None
    ):
        """set_dialogue_session."""
        key = f"dialogue_session_{session_id}"
        self.cache.set(
            key,
            dialogue_session,
            expire=expire_seconds if expire_seconds else self.config.expire_seconds,
        )

    def get_obj(self, obj_id):
        """get_obj."""
        result = self.cache.get(obj_id)
        logging.info(f"get_obj {obj_id}:{result}")
        return result

    def set_obj(self, obj_id, obj, expire_seconds):
        """set_obj."""
        logging.info(f"set_obj {obj_id}:{obj}")
        self.cache.set(obj_id, obj, expire=expire_seconds)

    def __del__(self):
        """__del__."""
        if self.cache is not None:
            self.cache.close()

    def get_db_context(self, db_context_id, db_context_uri):
        """get_db_context."""
        db_context_key = f"db_context_id_{db_context_id}_url_{db_context_uri}"
        context = self.cache.get(db_context_key)
        if context is None:
            return None
        return context

    def set_db_context(
        self,
        db_context_id,
        db_context_uri,
        grounding_context,
        expire_seconds: int = 60 * 60 * 24,
    ):
        db_context_key = f"db_context_id_{db_context_id}_url_{db_context_uri}"
        return self.cache.set(
            db_context_key,
            grounding_context,
            expire=expire_seconds,
        )


def history_cache(
    cache_name: str,
    history_service: HistoryService,
    expire_seconds: int = 60 * 60 * 24,
):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if history_service and history_service.enabled:
                result = history_service.get_obj(cache_name)
                if result:
                    return result
            result = func(*args, **kwargs)
            if history_service and history_service.enabled:
                history_service.set_obj(cache_name, result, expire_seconds)
            return result

        return wrapper

    return decorator
