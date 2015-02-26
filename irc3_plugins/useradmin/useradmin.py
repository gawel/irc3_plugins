# -*- coding: utf-8 -*-

from irc3.plugins.command import command
from irc3 import plugin
from irc3.compat import configparser


@plugin
class UserAdmin(object):
    """Plugin for user administration."""

    def __init__(self, bot):
        """Init"""
        self._bot = bot
        self._log = self._bot.log

    def _setuser(self, args):
        """Save new user configuration"""
        permissions = ""

        for perm in args['<permission>']:
            permissions += "%s " % perm

        permissions = permissions.strip()

        self._bot.config['irc3.plugins.command.masks'][args['<mask>']] = \
            permissions

        conf = configparser.ConfigParser(allow_no_value=False)
        conf.optionxform = str
        conf.read("./botconf.ini")
        conf.set("irc3.plugins.command.masks", args['<mask>'], permissions)

        with open("./botconf.ini", "wb") as f:
            conf.write(f)

    @command(permission="admin")
    def listop(self, mask, target, args):
        """
        Listop - Lists the masks for users and their permissions

        %%listop
        """

        self._bot.notice(mask.nick, "Mask | Permissions")

        for user in self._bot.config['irc3.plugins.command.masks']:
            self._bot.notice(mask.nick, "%s | %s" % (user,
                self._bot.config['irc3.plugins.command.masks'][user]))

    @command(permission="admin")
    def addop(self, mask, target, args):
        """
        Addop - Adds an operator to the list and sets their permissions

        %%addop <mask> <permission>...
        """

        self._setuser(args)
        self._bot.notice(mask.nick, "Added operator.")

    @command(permission="admin")
    def delop(self, mask, target, args):
        """
        Delop - Deletes an operator from the list

        %%delop <mask>
        """

        del self._bot.config['irc3.plugins.command.masks'][args['<mask>']]

        conf = configparser.ConfigParser(allow_no_value=False)
        conf.optionxform = str
        conf.read("./botconf.ini")
        conf.remove_option("irc3.plugins.command.masks", args['<mask>'])

        with open("./botconf.ini", "wb") as f:
            conf.write(f)

        self._bot.notice(mask.nick, "Deleted operator.")

    @command(permission="admin")
    def modop(self, mask, target, args):
        """
        Modop - Modifies the permissions of an operator on the list

        %%modop <mask> <permission>...
        """

        if args['<mask>'] in self._bot.config['irc3.plugins.command.masks']:
            self._setuser(args)
            self._bot.notice(mask.nick, "Modified operator.")
        else:
            self._bot.notice(mask.nick, "Operator not found!")
