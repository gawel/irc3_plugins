# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
from . import Alarm
import os


class TestAlarm(BotTestCase):

    name = 'alarm'

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
        plugin = bot.get_plugin(Alarm)
        plugin.ring = lambda x: x
        db = bot.db
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm set matin 0618 0 9 * * 1-2')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm set matin 0618 0 9 * * 1-2')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm set soir 0618 0 21 * * 1-2')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm test soir')
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm list')

        plugin.whois('matin')
        plugin.rpl_whois_idle('matin', 'gawel', '60000')

        assert db[plugin.key]['matin'] is True

        alarm = plugin.get_alarm('matin')
        assert 'cron' in alarm
        assert 'event' in alarm

        assert alarm.enable
        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm toogle matin')
        assert not plugin.get_alarm(alarm.name).enable

        bot.dispatch(
            ':gawel!a@a.com PRIVMSG nono :!alarm delete matin')
        self.assertRaises(LookupError, plugin.get_alarm, alarm.name)
