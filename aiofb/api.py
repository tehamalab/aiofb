import aiohttp
import async_timeout
from .exceptions import GraphAPIException


class GraphAPI:
    """A Facebook Graph API wrapper.

    https://developers.facebook.com/docs/graph-api/
    """

    ROOT_URL = 'https://graph.facebook.com'
    VERSION = '3.0'
    URL = '{0}/v{1}'.format(ROOT_URL, VERSION)

    def __init__(self, access_token=None, session=None, timeout=10):
        """
        Parameters
        ----------
        access_token : str
            Facebook Graph API access token.
        session: aiohttp.ClientSession, optional
            An aiohttp.ClientSession instance to be used for making requests.
        timeout: int, optional
            timeout for API requests.
        """

        self.access_token = access_token  #: str: API access token

        self.http_headers = {'Content-Type': 'application/json'}
        #: dict: default HTTP headers

        self.async_timeout = timeout  #: int: timeout for HTTP requests

        self.session = session  #: aiohttp.ClientSession: Aiohttp session.

    async def request(self, method, path, session=None, **kwargs):
        """Make an HTTP request to the API

        Parameters
        ----------
        method : str
            HTTP method
        path : str
            API endpoint
        session : ClientSession, optional
            An aiohttp.ClientSession to be used for making the request.
        \*\*kwargs
            Keyword arguments to be passed to aiohttp request. For more info check
            http://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientSession.request
        """
        _session = session or self.session

        kwargs['params'] = kwargs.get('params', {})
        kwargs['params']['access_token'] = self.access_token

        if not kwargs.get('headers'):
            kwargs['headers'] = self.http_headers

        async with _session or aiohttp.ClientSession() as _session:
            async with async_timeout.timeout(self.async_timeout):
                async with _session.request(
                        method, self.__class__.URL + path, **kwargs) as response:
                    if response.status < 400:
                        return await response.json()
                    else:
                        message = await response.text()
                        raise GraphAPIException(message, response=response)

    async def get(self, path, session=None, **kwargs):
        """Make a HTTP GET request to the API.

        A wrapper to :func:`~aiofb.api.GraphAPI.request` for GET requests.
        """
        return await self.request('GET', path, session, **kwargs)

    async def post(self, path, session=None, **kwargs):
        """Make a HTTP POST request to the API.

        A wrapper to :func:`~aiofb.api.GraphAPI.request` for POST requests.
        """
        return await self.request('POST', path, session, **kwargs)


class Messenger(GraphAPI):
    """Messenger Platform API wrapper.

    This class provides some additional for accessing Messenger API
    a bit more conveniently
    """

    #: list of str: Default user profile properties to be requested
    DEFAULT_USER_PROFILE_FIELDS = ['name', 'first_name', 'last_name', 'profile_pic']

    async def update_profile(self, data, session=None):
        """Update bot's Messenger profile properties.

        Sets the values of one or more Messenger Profile properties.
        Only properties set in the request body will be overwritten.

        To set or update Messenger Profile properties you must have the
        'Administrator' role for the Page associated with the bot.

        https://developers.facebook.com/docs/graph-api/reference/page/messenger_profile#post

        Parameters
        ----------
        data : dict
            data for the update
        """
        return await self.post(
            '/me/messenger_profile',
            session=session,
            json=data
        )

    async def get_user_profile(self, psid, fields=None, session=None):
        """Retrieve user profile information using PSID.

        https://developers.facebook.com/docs/messenger-platform/identity/user-profile

        Parameters
        ----------
        psid : str
            User PSID
        fields : list
            List of field to be retieved. If not provided
            ``Messenger.DEFAULT_USER_PROFILE_FIELDS`` will be used.
        """
        _fields = fields or self.__class__.DEFAULT_USER_PROFILE_FIELDS
        return await self.get(
            '/{}'.format(psid),
            session=session,
            params={'fields': ','.join(_fields)}
        )

    async def send_message(self, data, session=None):
        """Send messages to user

        This may include text, attachments, structured message templates,
        sender actions, and more.

        https://developers.facebook.com/docs/messenger-platform/reference/send-api

        Parameters
        ----------
        data : dict
            Message data.
        """
        return await self.post(
            '/me/messages',
            session=session,
            json=data
        )

    async def pass_thread_control(self, data, session=None):
        """Pass thread control from your app to another app.

        https://developers.facebook.com/docs/messenger-platform/reference/handover-protocol/pass-thread-control

        Parameters
        ----------
        data : dict
            Data for the handover.
        """
        return await self.post(
            '/me/pass_thread_control',
            session=session,
            json=data
        )
