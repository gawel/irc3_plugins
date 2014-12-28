===================================================
Transmission plugin
===================================================

Notify a channel when a torrent is done downloading

Add a ``torrent`` command to list downloading file and add new url/magnet

..
    >>> from irc3.testing import IrcBot
    >>> from irc3.testing import patch
    >>> patcher = patch('transmissionrpc.client.Client')
    >>> patched = patcher.start()

Usage::

    >>> bot = IrcBot(includes=['transmission'],
    ...              transmission=dict(channel='#mychan', host='', port='',
    ...                                user='', password=''))

..
    >>> patcher.stop()

