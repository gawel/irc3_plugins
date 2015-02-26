# -*- coding: utf-8 -*-
from irc3.testing import BotTestCase
import os


class TestUserAdmin(BotTestCase):

    name = 'irc3_plugins.useradmin'

    config = dict(
        nick='nono',
        includes=[name],
        storage='json:///tmp/admin.json',
        **{
            'irc3.plugins.command': {
                'guard': 'irc3.plugins.command.mask_based_policy'},
            'irc3.plugins.command.masks': {'gawel!*': 'admin'}}
    )

    def test_commands(self):
        try:
            os.remove('/tmp/admin.json')
        except:  # pragma: no cover
            pass
        bot = self.callFTU()
        bot.dispatch(':gawel!u@h PRIVMSG nono :!addop new!* admin')
        self.assertSent(['PRIVMSG gawel :Added operator.'])

        bot.dispatch(':gawel!u@h PRIVMSG nono :!listop')
        self.assertSent(['PRIVMSG gawel :Mask | Permissions',
                         'PRIVMSG gawel :new!* | admin'])

        bot.dispatch(':new!u@h PRIVMSG nono :!modop new!* view admin')
        self.assertSent(['PRIVMSG new :Modified operator.'])

        bot.dispatch(':new!u@h PRIVMSG nono :!delop new!*')
        self.assertSent(['PRIVMSG new :Deleted operator.'])

        bot.dispatch(':gawel!u@h PRIVMSG nono :!listop')
        self.assertSent(['PRIVMSG gawel :Mask | Permissions'])
