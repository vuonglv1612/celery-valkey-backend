"""
Celery backend implementation using ValKey as the storage engine.
"""
import logging
import time
from datetime import timedelta

from celery.backends.base import KeyValueStoreBackend
from celery.exceptions import ImproperlyConfigured

from celery_valkey_backend.utils import mask_url_password

try:
    from valkey import Valkey
except ImportError:  # pragma: no cover
    Valkey = None

logger = logging.getLogger(__name__)


class ValKeyBackend(KeyValueStoreBackend):
    """
    ValKey backend for Celery.
    """

    scheme = 'valkey'  # URL scheme for the backend
    supports_native_join = False
    supports_autoexpire = True

    # Default settings
    default_url = "valkey://localhost:6379/0"
    expires = None
    connection_timeout = 5
    connection_retry = True
    connection_retry_backoff = 1
    connection_max_retries = 3

    def __init__(self, url=None, expires=None, **kwargs):
        """Initialize the ValKey backend.

        Args:
            url (str): URL in the format 'valkey://host:port/db'
            expires (int): Time in seconds before entries expire
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)

        if Valkey is None:
            raise ImproperlyConfigured(
                'You need to install valkey package to use the valkey backend.'
            )

        if not url:
            url = self.default_url

        self.url = url
        self.expires = self.prepare_expires(expires)
        self.connection_retry = kwargs.get('connection_retry', self.connection_retry)
        self.connection_retry_backoff = kwargs.get('connection_retry_backoff', self.connection_retry_backoff)
        self.connection_max_retries = kwargs.get('connection_max_retries', self.connection_max_retries)
        self.connection_timeout = kwargs.get('connection_timeout', self.connection_timeout)

        # Client will be initialized on first use
        self._client = self._get_client()

    @property
    def client(self) -> Valkey:
        """Get or create ValKey client.

        Returns:
            valkey.Client: ValKey client instance
        """
        if self._client is None:
            self._client = self._get_client()
        return self._client

    def _get_client(self):
        """Create new ValKey client.

        Returns:
            valkey.Client: New ValKey client instance
        """
        return Valkey.from_url(self.url, socket_timeout=self.connection_timeout)

    def _retry_on_error(self, fun, *args, **kwargs):
        """Execute a function with retry logic.

        Args:
            fun: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            The result of the function execution
        """
        retries = 0
        while True:
            try:
                return fun(*args, **kwargs)
            except Exception as exc:  # pylint: disable=broad-except
                if not self.connection_retry or retries >= self.connection_max_retries:
                    raise
                retries += 1
                backoff = self.connection_retry_backoff * retries
                logger.warning(
                    'ValKey operation failed: %r. Retry %d/%d in %.2f seconds.',
                    exc, retries, self.connection_max_retries, backoff,
                )
                time.sleep(backoff)
                self._client = None  # Force client recreation

    def get(self, key):
        """Get a value from ValKey.

        Args:
            key (str): Key to retrieve

        Returns:
            The value associated with the key
        """
        logger.debug('Getting key %s from ValKey', key)
        return self._retry_on_error(self.client.get, key)

    def _set(self, key, value, expire=None):
        expire = expire or self.expires
        if expire is None:
            return self.client.set(key, value)
        self.client.set(key, value, ex=timedelta(seconds=expire))

    def set(self, key, value):
        """Set a value in ValKey.

        Args:
            key (str): Key to set
            value: Value to store
        """
        logger.debug('Setting key %s in ValKey', key)
        return self._retry_on_error(
            self._set,
            key,
            value,
            expire=self.expires,
        )

    def delete(self, key):
        """Delete a key from ValKey.

        Args:
            key (str): Key to delete
        """
        return self._retry_on_error(self.client.delete, key)

    def mget(self, keys):
        """Get multiple values from ValKey.

        Args:
            keys (list): List of keys to retrieve

        Returns:
            list: List of values associated with the keys
        """
        return self._retry_on_error(self.client.mget, keys)

    def cleanup(self):
        """Close the client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None

    def as_uri(self, include_password=False):
        if include_password:
            return self.url
        else:
            return mask_url_password(self.url)
