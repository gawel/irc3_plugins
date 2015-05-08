# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from irc3.testing import MagicMock
from irc3.testing import patch
from panoramisk.message import Message
import os


class Event(Message):

    def __init__(self, **kwargs):
        content = kwargs.pop('content', '')
        super(Event, self).__init__(kwargs, content=content)


class TestAsterirc(BotTestCase):

    config = dict(
        nick='nono',
        includes=['irc3_plugins.asterisk'],
        asterisk=dict(
            resolver='irc3_plugins.asterisk.asterisk.default_resolver',
            channel='#asterirc',
            testing=True),
    )

    def setUp(self):
        self.patch_asyncio()
        self.mocks = {}
        for name in ('connect', 'close'):
            patcher = patch('panoramisk.Manager.' + name)
            self.mocks[name] = patcher.start()
            self.addCleanup(patcher.stop)

    def callFTU(self, level=1000, **kwargs):
        if 'stream' in kwargs:
            kwargs['stream'] = os.path.join(os.path.dirname(__file__),
                                            kwargs['stream'])
        config = self.config.copy()

        config['asterisk'].update(**kwargs)
        bot = super(TestAsterirc, self).callFTU(**config)
        plugin = bot.asterisk
        return bot, plugin

    def test_connect(self):
        bot, plugin = self.callFTU(debug=True)
        bot.notify('connection_made')
        self.assertTrue(plugin.connect())
        self.assertTrue(plugin.manager is not None)

    def test_shutdown(self):
        bot, plugin = self.callFTU()
        plugin.connect()
        bot.notify('SIGINT')
        self.assertTrue(self.mocks['close'].called)

        event = MagicMock(manager=plugin.manager)

        plugin.handle_event(event, MagicMock())
        plugin.handle_shutdown(event, MagicMock())
