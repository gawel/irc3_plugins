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
to have "admin", "operator" or "all_permissions" set in the config section for mask-based
policy.

=================
Existing commands
=================
* join - Tell the bot to join a channel. Requires "operator".
* part - Tell the bot to leave the current channel or a specific channel. Requires "operator".
* quit - Tell the bot to quit and shutdown. Requires "admin".
* nick - Change the nickname. Requires "admin".
* mode - Change user mode. Requires "operator".
* msg - Tell the bot to send a message. Useful when you want to authenticate with NickServ. Notice that the command will be seen in plain text in the channel so don't send sensitive information in the channel.

===============
On-invite event
===============
This event is triggered when the bot get an invite to a channel. It can either
automaticlly join the channel it was invited to or forward this to the user set
as admin in the configuration.

==========
Configfile
==========
Create a section name that is named "botui". There are 2 constants to be set.

* admin - The user to forward invites to. (Default: None)
* joininvite - true/false
    true: Try to auto-join channels invited to.
    false: Send a notice to admin that an invitation as been sent. (Default)
