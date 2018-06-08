# Deprecated and retired.

# O.S.C.A.R.
the Obscure Speedruns Club Advertising Robot.

O.S.C.A.R. is a Discord bot used by the OSC community to advertise streamers doing runs of sponsored games on Twitch and notify when new runs are approved to the SRC leaderboards.

![OSC](https://cdn.discordapp.com/attachments/396119968175095810/397961256075526154/OSC.png) [![Discord](https://cdn.discordapp.com/attachments/393162131840958466/401418832029417475/Discord-Logo-Black.png)](discord.gg/FyTGQy4)

# How to use

O.S.C.A.R. has been tested and works on [Python 3.5](https://www.python.org/downloads/) and above, though it is likely it works on lower versions too. To be sure, use the newest Python 3 binaries. Python 2 is not supported.

The script will look for your [Discord bot API token](https://discordapp.com/developers/applications/me) and [Twitch API Client-ID](https://dev.twitch.tv/dashboard/apps/create) in ```~/.oscar/discord.key``` and ```~/.oscar/twitch.key```, respectively. You should write your tokens to these files on a single line, without a newline character at the end. The SRC API requires no token to make requests.

The ```debug``` variable being set to ```True``` will enable verbose output and logging, and the ```dSend``` variable will enable sending messages to Discord (useful for local testing).
