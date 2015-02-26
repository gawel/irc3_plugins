# -*- coding: utf-8 -*-
from irc3.plugins.command import command
from irc3 import plugin


@plugin
class UserAdmin(object):
    """Plugin for user administration."""

    requires = [
        'irc3.plugins.command',
        'irc3.plugins.storage',
    ]
    key = 'irc3.plugins.command.masks'

    def __init__(self, bot):
        """Init"""
        self.bot = bot
        self.log = self.bot.log

    @property
    def config(self):
        return self.bot.db[self.key]

    def set_user(self, args):
        """Save new user configuration"""
        permissions = ""

        permissions = ' '.join(args['<permission>'])

        config = self.config
        config[args['<mask>']] = permissions
        self.bot.db[self.key] = config

    @command(permission="admin")
    def listop(self, mask, target, args):
        """
        Listop - Lists the masks for users and their permissions

        %%listop
        """

        yield "Mask | Permissions"

        for user, perms in self.config.items():
            yield "%s | %s" % (user, perms)

    @command(permission="admin")
    def addop(self, mask, target, args):
        """
        Addop - Adds an operator to the list and sets their permissions

        %%addop <mask> <permission>...
        """

        self.set_user(args)
        yield "Added operator."

    @command(permission="admin")
    def delop(self, mask, target, args):
        """
        Delop - Deletes an operator from the list

        %%delop <mask>
        """
        config = self.config
        try:
            del config[args['<mask>']]
        except KeyError:
            yield "Operator not found!"
        else:
            self.bot.db[self.key] = config
            yield "Deleted operator."

    @command(permission="admin")
    def modop(self, mask, target, args):
        """
        Modop - Modifies the permissions of an operator on the list

        %%modop <mask> <permission>...
        """

        if args['<mask>'] in self.config:
            self.set_user(args)
            yield "Modified operator."
        else:
            yield "Operator not found!"
