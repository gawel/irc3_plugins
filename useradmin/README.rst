===============================
Useradmin - User administration
===============================
This plugin gives you a simple UI to control who can use the IRC-bot's commands. 
It will give simple commands that your bot will run. You have to use mask-based
policy for the existing "irc3.plugin.command"-plugin.

================
Running commands
================
If the default free-policy is used everyone can run the commands,
but it isn't recommended. So your IRC-bot isn't banned or kicked out for
various reasons. To be able to run a command in the plugin the user need
to have "admin" or "all_permissions" set in the config section for mask-based
policy.

=================
Existing commands
=================
* addop - Add a user to the list where you set permissions
* delop - Delete a user from the list
* modop - Modify a users permissions
* listop - List all users and their permissions

===========
Information
===========
When adding, deleting or modifying users you must use the mask that you can 
see with listop-command. Look in the documentation for irc3 on how to use
the mask-based policy. This plugin edits the conf and updates the existing
configurations. So you don't need to edit the config and restart the bot.

==========
Configfile
==========
No settings in the config.
