==========================
Bot-UI - A UI for IRC-bots
==========================
This plugin gives you a simple UI to control IRC-bots that are based
upon irc3. It will give simple commands that your bot will run. To make
it more secure it's recommended to use the mask-based policy for the existing
"irc3.plugin.command"-plugin.

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
* join - Tell the bot to join a channel
* part - Tell the bot to leave the current channel or a specific channel
* quit - Tell the bot to quit and shutdown

===============
On-invite event
===============
This event is triggered when the bot get an invite to a channel. It can either
automaticlly join the channel it was invited to or forward this to the user set
as admin in the configuration.

==========
Configfile
==========
Create a section name that is the absolute path for the module. You can get it
by checking the "__name__"-variable for the package or the module, if only the
file is used. There are 2 constants to be set.

Example:
Having the entire package placed as a subpackage to the bot.

[botui.botui]
admin = TestUser
joininvite = true

* admin - The user to forward invites to. (Default: None)
* joininvite - true/false
    true: Try to auto-join channels invited to.
    false: Send a notice to admin that an invitation as been sent. (Default)