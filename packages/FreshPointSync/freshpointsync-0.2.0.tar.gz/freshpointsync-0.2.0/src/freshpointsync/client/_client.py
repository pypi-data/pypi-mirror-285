import asyncio
import logging
import ssl
from typing import Optional, Tuple, Type, TypeVar, Union

import aiohttp
import certifi

logger = logging.getLogger('freshpointsync.client')
"""Logger for the `freshpointsync.client` package."""


TClient = TypeVar('TClient', bound='ProductDataFetchClient')


class ProductDataFetchClient:
    """Asynchronous utility for fetching contents of a specified FreshPoint.cz
    web page.

    This class wraps an `aiohttp.ClientSession` object and provides additional
    features like retries, timeouts, logging, and comprehensive error handling.
    """

    BASE_URL = 'https://my.freshpoint.cz'
    """The base URL of the FreshPoint.cz website."""

    def __init__(self) -> None:
        self._timeout = self._check_timeout(timeout=None)
        self._max_retries = self._check_max_retries(max_retries=5)
        self._client_session: Optional[aiohttp.ClientSession] = None
        self._ssl_context: Optional[ssl.SSLContext] = None

    async def __aenter__(self: TClient) -> TClient:
        """Asynchronous context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> None:
        """Asynchronous context manager exit."""
        await self.close_session()

    @classmethod
    def get_page_url(cls, location_id: int) -> str:
        """Generate a page URL for a given location ID.

        Args:
            location_id (int): The ID of the location, as it appears in
                the FreshPoint.cz web page URL. For example, in
                https://my.freshpoint.cz/device/product-list/296,
                the ID is 296.

        Returns:
            str: The full page URL for the given location ID.
        """
        return f'{cls.BASE_URL}/device/product-list/{location_id}'

    @staticmethod
    def _check_timeout(timeout: object) -> aiohttp.ClientTimeout:
        """Validate the given timeout value and convert it to an
        `aiohttp.ClientTimeout` object.

        Args:
            timeout (Any): The timeout value to be checked.

        Returns:
            aiohttp.ClientTimeout: The validated client timeout object. If the
                timeout value is None, the default `aiohttp.ClientTimeout`
                object is returned. If the timeout value is already an instance
                of `aiohttp.ClientTimeout`, it is returned as is.

        Raises:
            ValueError: If the timeout value is invalid.
        """
        if timeout is None:
            return aiohttp.ClientTimeout()
        if isinstance(timeout, (int, float)):
            return aiohttp.ClientTimeout(total=float(timeout))
        if isinstance(timeout, aiohttp.ClientTimeout):
            return timeout
        raise ValueError(f'Invalid timeout argument "{timeout}".')

    @property
    def timeout(self) -> aiohttp.ClientTimeout:
        """Client request timeout."""
        return self._timeout

    def set_timeout(
        self, timeout: Optional[Union[aiohttp.ClientTimeout, int, float]]
    ) -> None:
        """Set the client request timeout.

        Args:
            timeout (Optional[Union[aiohttp.ClientTimeout, int, float]]):
                The timeout value. It can be an `aiohttp.ClientTimeout` object,
                an integer or a float representing the total timeout in seconds,
                or None for the default `aiohttp.ClientTimeout` timeout.

        Raises:
            ValueError: If the timeout value is negative or invalid.
        """
        self._timeout = self._check_timeout(timeout)

    @staticmethod
    def _check_max_retries(max_retries: object) -> int:
        """Check if the given max_retries value is valid.

        Args:
            max_retries (Any): The number of max retries.

        Returns:
            int: The validated value.

        Raises:
            ValueError: If the value is not an integer or is less than 1.
        """
        if not isinstance(max_retries, int):
            raise ValueError('The number of max retries must be an integer.')
        if max_retries < 0:
            raise ValueError('The number of max retries cannot be negative.')
        return max_retries

    @property
    def max_retries(self) -> int:
        """The maximum number of retries for fetching data."""
        return self._max_retries

    def set_max_retries(self, max_retries: int) -> None:
        """Set the maximum number of retries for the fetching data.

        Args:
            max_retries (int): The maximum number of retries.

        Raises:
            TypeError: If the max_retries value is not an integer.
            ValueError: If the max_retries value is less than 1.
        """
        self._max_retries = self._check_max_retries(max_retries)

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        """The `aiohttp.ClientSession` object used for fetching data."""
        return self._client_session

    @property
    def is_session_closed(self) -> bool:
        """Check if the client session is closed.

        Returns:
            bool: True if the client session is closed, False otherwise.
        """
        return not self._client_session or self._client_session.closed

    async def start_session(self, force: bool = False) -> None:
        """Start a new `aiohttp` client session and create an SSL context.

        If a session is already started, a new session is not created unless
        the `force` parameter is set to `True`. If the SSL context is already
        created, it is not recreated.

        Args:
            force (bool, optional): If True, forcefully close the existing
                session and start a new one. If no session is started,
                this parameter has no effect. Defaults to False.
        """
        if not self.is_session_closed and force:
            logger.info(
                'Closing existing client session for "%s".', self.BASE_URL
            )
            await self.close_session()
        if self.is_session_closed:
            logger.info('Starting new client session for "%s".', self.BASE_URL)
            self._client_session = aiohttp.ClientSession(base_url=self.BASE_URL)
            logger.debug(
                'Successfully started client session for "%s".', self.BASE_URL
            )
        else:
            logger.debug(
                'Client session for "%s" is already started.', self.BASE_URL
            )
        if self._ssl_context is None:
            logger.debug('Creating SSL context for "%s".', self.BASE_URL)
            context = ssl.create_default_context(cafile=certifi.where())
            self._ssl_context = context

    async def set_session(self, session: aiohttp.ClientSession) -> None:
        """Set the client session object. If the previous session
        is not closed, it is closed before setting the new one.

        Args:
            session (aiohttp.ClientSession): The client session to set.
        """
        if not isinstance(session, aiohttp.ClientSession):
            raise TypeError(
                'The session must be an aiohttp.ClientSession object.'
            )
        if not self.is_session_closed:
            await self.close_session()
        self._client_session = session

    async def close_session(self) -> None:
        """Close the `aiohttp` client session if one is open.

        If the session is already closed, this method has no effect on
        the client session object. If an SSL context has been created,
        it is also cleared after closing the session.
        """
        if self._client_session:
            logger.info('Closing client session for "%s".', self.BASE_URL)
            if not self._client_session.closed:
                await self._client_session.close()
            self._client_session = None
            logger.debug(
                'Successfully closed client session for "%s".', self.BASE_URL
            )
        else:
            logger.debug(
                'Client session for "%s" is already closed.', self.BASE_URL
            )
        if self._ssl_context is not None:
            logger.debug('Clearing SSL context for "%s".', self.BASE_URL)
            self._ssl_context = None

    def _check_fetch_args(
        self, location_id: object, timeout: object, max_retries: object
    ) -> Tuple[aiohttp.ClientSession, str, aiohttp.ClientTimeout, int]:
        """Check and validate the arguments for fetching data. Note that this
        method may raise exceptions via the checks for timeout and max_retries.

        Args:
            location_id (Any): The ID of the location.
            timeout (Any): The timeout value for the request.
            max_retries (Any): The maximum number of retries for the request.

        Returns:
            tuple[aiohttp.ClientSession, str, aiohttp.ClientTimeout, int]:
                A tuple containing the client session, relative URL, timeout,
                and max retries.
        """
        if not self._client_session or self._client_session.closed:
            raise ValueError('Client session is not initialized or is closed.')
        else:
            session = self._client_session
        if timeout is None:
            timeout = self._timeout
        else:
            timeout = self._check_timeout(timeout)
        if max_retries is None:
            max_retries = self._max_retries
        else:
            max_retries = self._check_max_retries(max_retries)
        relative_url = f'/device/product-list/{location_id}'
        return session, relative_url, timeout, max_retries

    async def _fetch_once(
        self,
        session: aiohttp.ClientSession,
        ssl_context: ssl.SSLContext,
        relative_url: str,
        timeout: aiohttp.ClientTimeout,
    ) -> Optional[str]:
        """Fetch data from the specified URL using the provided session and
        timeout.

        Args:
            session (aiohttp.ClientSession): The client session to use for
                the request.
            ssl_context (ssl.SSLContext): The SSL context to use
                for the request.
            relative_url (str): The relative URL to fetch data from.
            timeout (aiohttp.ClientTimeout): The timeout for the request.

        Returns:
            Optional[str]: The fetched data as a string,
                or None if an error occurred.
        """
        try:
            async with session.get(
                relative_url,
                ssl=ssl_context,
                timeout=timeout,
                allow_redirects=False,
            ) as response:
                logger.debug(
                    'Server response for "%s": %s %s',
                    response.url,
                    response.status,
                    response.reason,
                )
                if response.status == 302:
                    return ''  # inexistent page, no need to retry
                if response.status != 200:
                    return None  # fetch failed, should retry
                return await response.text()
        except asyncio.TimeoutError:
            logger.warning(
                'Timeout occurred while fetching data from "%s%s"',
                self.BASE_URL,
                relative_url,
            )
        except aiohttp.ClientConnectionError as exc:
            logger.warning(
                'Connection error occurred while fetching data from "%s%s": %s',
                self.BASE_URL,
                relative_url,
                exc,
            )
        except Exception as exc:
            exc_type = exc.__class__.__name__
            logger.error(
                'Exception "%s" occurred while fetching data from "%s%s": %s',
                exc_type,
                self.BASE_URL,
                relative_url,
                exc,
            )
        return None  # fetch failed, should retry

    async def fetch(
        self,
        location_id: Union[int, str],
        timeout: Optional[Union[aiohttp.ClientTimeout, int, float]] = None,
        max_retries: Optional[int] = None,
    ) -> Optional[str]:
        """Fetch HTML data from a FreshPoint.cz web page.

        Args:
            location_id (Union[int, str]): The ID the FreshPoint location.
            timeout (Optional[Union[aiohttp.ClientTimeout, int, float]]):\
            The timeout for the request. If None, the default timeout is used.
            max_retries (Optional[int]): The maximum number of retries.
                If None, the default number of retries is used.

        Returns:
            Optional[str]: The fetched data as a string,\
                or None if the fetch failed.
        """
        assert self._ssl_context is not None
        args = self._check_fetch_args(location_id, timeout, max_retries)
        session, relative_url, timeout, max_retries = args
        attempt = 0
        while attempt < max_retries:
            logger.info(
                'Fetching data from "%s%s" (attempt %s of %s)',
                self.BASE_URL,
                relative_url,
                attempt + 1,
                max_retries,
            )
            text = await self._fetch_once(
                session, self._ssl_context, relative_url, timeout
            )
            if text == '':  # noqa: PLC1901  # inexistent page
                return None
            if text is not None:
                return text
            attempt += 1
            if attempt < max_retries:
                wait_time: int = 2**attempt  # exponential backoff
                logger.debug('Retrying in %i seconds...', wait_time)
                await asyncio.sleep(wait_time)
        return None
