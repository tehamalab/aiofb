import logging
import asyncio
import aiohttp
import async_timeout


class Graph(object):

    def __init__(self, access_token=None, version='2.10', url='https://graph.facebook.com',
                 async_timeout=10):
        self.access_token = access_token
        self.version = version
        self.url = '{0}/v{1}'.format(url, self.version)
        self.default_http_headers = {'Content-Type': 'application/json'}
        self.async_timeout = async_timeout

    async def get(self, session, path, params=None, data=None, json_data=None, **kwargs):
        headers = self.default_http_headers.copy()
        headers.update(kwargs.pop('headers', {}))
        with async_timeout.timeout(self.async_timeout):
            return await session.get(self.url + path, params=params, data=data,
                                     json=json_data, headers=headers)

    async def post(self, session, path, params=None, data=None, json_data=None, **kwargs):
        headers = self.default_http_headers.copy()
        headers.update(kwargs.pop('headers', {}))
        with async_timeout.timeout(self.async_timeout):
            return await session.post(self.url + path, params=params, data=data,
                                      json=json_data, headers=headers)


class Messenger(Graph):

    def __init__(self, access_token=None, version='2.10', url='https://graph.facebook.com',
                 async_timeout=10):
        super().__init__(access_token=access_token, version=version, url=url,
                         async_timeout=async_timeout)
        self.default_user_profile_fields = ['first_name', 'last_name', 'profile_pic',
                                            'locale', 'timezone', 'gender',
                                            'is_payment_enabled', 'last_ad_referral']

    def update_profile(self, data):
        response = asyncio.ensure_future(self._update_profile(data))
        response.add_done_callback(log_response)
        return response

    def get_user_profile(self, psid, fields=None):
        response = asyncio.ensure_future(self._get_user_profile(psid, fields))
        response.add_done_callback(log_response)
        return response

    def send_message(self, data):
        response = asyncio.ensure_future(self._send_message(data))
        response.add_done_callback(log_response)
        return response

    def pass_thread_control(self, data):
        response = asyncio.ensure_future(self._pass_thread_control(data))
        response.add_done_callback(log_response)
        return response

    async def _update_profile(self, data):
        async with aiohttp.ClientSession() as session:
            return await self.post(
                session,
                '/me/messenger_profile',
                params={'access_token': self.access_token},
                json_data=data)

    async def _get_user_profile(self, psid, fields=None):
        if not fields:
            fields = self.default_user_profile_fields
        async with aiohttp.ClientSession() as session:
            return await self.get(
                session,
                '/{}'.format(psid),
                params={'access_token': self.access_token, 'fields': ','.join(fields)})

    async def _send_message(self, data):
        async with aiohttp.ClientSession() as session:
            return await self.post(
                session,
                '/me/messages',
                params={'access_token': self.access_token},
                json_data=data)

    async def _pass_thread_control(self, data):
        async with aiohttp.ClientSession() as session:
            return await self.post(
                session,
                '/me/pass_thread_control',
                params={'access_token': self.access_token},
                json_data=data)


async def _messenger_update_profile(access_token, data):
    """Update the Facebook messenger profile"""
    messenger = Messenger(access_token)
    task = messenger.update_profile(data)
    return await task


def messenger_update_profile(access_token, data):
    """Update the Facebook messenger profile"""
    return asyncio.get_event_loop().run_until_complete(_messenger_update_profile(access_token, data))


async def _log_response(task):
    response = task.result()
    body = await response.text()
    if response.status >= 400:
        logging.error('{0} {1} {2}'.format(response.status, response.url, body))
    else:
        logging.info('{0} {1} {2}'.format(response.status, response.url, body))


def log_response(task):
    asyncio.ensure_future(_log_response(task))
