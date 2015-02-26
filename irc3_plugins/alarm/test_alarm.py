# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from . import Alarms
import os


class TestAlarm(BotTestCase):

    name = 'irc3_plugins.alarm'

    config = dict(
        nick='nono',
        includes=[name],
        storage='json:///tmp/alarm.json',
    )

    def test_commands(self):
        try:
            os.remove('/tmp/alarm.json')
        except:  # pragma: no cover
            pass
        bot = self.callFTU()
        bot.notify('connection_made')
        plugin = bot.get_plugin(Alarms)
        plugin.ring = lambda x: x
        db = bot.db
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :'
            '!alarm set matin irc 0 9 * * 1-2')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :'
            '!alarm set matin irc 0 9 * * 1-2')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :'
            '!alarm set soir irc 0 21 * * 1-2')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :'
            '!alarm test soir')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :'
            '!alarm list')

        assert db[plugin.key]['matin'] is True

        alarm = plugin.get('matin')
        assert 'cron' in alarm
        assert 'idle' in alarm

        assert alarm.enable
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm toogle matin')
        assert not plugin.get(alarm.name).enable

        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm delete matin')
        self.assertRaises(LookupError, plugin.get, alarm.name)
