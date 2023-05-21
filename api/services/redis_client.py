from redis import Redis
from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    TimeoutError
)

from django.conf import settings


# TODO: Add password and username for Redis
class RedisClient:
    REDIS_HOST: str = settings.REDIS_HOST
    REDIS_PORT: int = settings.REDIS_PORT
    REDIS_DATABASE: int = settings.REDIS_DATABASE
    MAX_RETRIES: int = settings.MAX_RETRIES if settings.MAX_RETRIES else 3

    def __init__(self):
        self.redis_instance: Redis = self._get_connection()

    def _get_connection(self) -> Redis:
        # Run MAX_RETRIES with exponential backoff
        retry: Retry = Retry(ExponentialBackoff(), self.MAX_RETRIES)
        redis_instance: Redis = Redis(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            db=self.REDIS_DATABASE,
            decode_responses=True,
            retry=retry,
            retry_on_error=[
                BusyLoadingError,
                ConnectionError,
                TimeoutError
            ]
        )

        return redis_instance

    def set_context(self, user_id: int, chat_id: int, message: str) -> None:
        message = message.replace("'", '"')
        self.redis_instance.rpush(f'user_{user_id}_context_in_chat_{chat_id}', message)

    def get_context(self, user_id: int, chat_id: int) -> list:
        MAX_MESSAGES: int = 100
        # Returns only the last 100 messages from the list
        result: list = self.redis_instance.lrange(
            f'user_{user_id}_context_in_chat_{chat_id}',
            -MAX_MESSAGES,
            -1
        )

        return [message for message in result]
