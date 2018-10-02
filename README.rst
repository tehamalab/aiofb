=====
aiofb
=====

.. image:: https://img.shields.io/pypi/v/aiofb.svg
        :target: https://pypi.python.org/pypi/aiofb

.. image:: https://img.shields.io/travis/tehamalab/aiofb.svg
        :target: https://travis-ci.org/tehamalab/aiofb

.. image:: https://readthedocs.org/projects/aiofb/badge/?version=latest
        :target: https://aiofb.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

A thin asynchronous Python wrapper for Facebook graph API.

This library requires Python 3.5+

Installation
-------------
Using pip

.. code-block:: console

    $ pip install aiofb


Basic usage
------------
Example

.. code-block:: python

    import asyncio
    import aiofb

    # initialize Graph API
    fb = aiofb.GraphAPI(access_token='YOUR_ACCESS_TOKEN')

    # Get an event loop
    loop = asyncio.get_event_loop()

    # Get results
    data = loop.run_until_complete(fb.get('/{some-endpoint}'))
