# CoffinBot

Reddit bot that reverses videos. Currently running under [/u/coffinbot](https://reddit.com/user/coffinbot).

## Setup

Create a file named `credentials.ini` in the root directory with the following content

```ini
[general]
mode = development|production
operator = username to be pinged on crash/other stuff

[database]
type = sqlite|mysql
# Settings for mysql
host = 
username =
password = 
database =

[reddit]
client_id = Reddit client id
client_secret = Reddit client secret
username = Reddit username
password = Reddit password

[imgur]
imgur_id = Imgur api id
imgur_secret = Imgur api secret
imgur_cookie = Cookie generated from an Imgur upload

[gfycat]
gfycat_id = gftcat id
gfycat_secret = gfycat secret

[streamable]
email = streamable account email
password = password

[catbox]
hash = your catbox account hash

```

From there run `python main.py` from the root directory to start. CoffinBot requires Python 3.6+.

You will also need [`FFmpeg`](http://ffmpeg.org/), [`FFprobe`](http://ffmpeg.org/), and [`videoski`](https://video.ski/) 
binaries on the path or in the same directory. 

## Commentary

Here's some notes on the more interesting parts of the bot.

### Context detection

The bot goes through a couple of steps to determine what the user was asking for. First thing it checks is whether or 
not the user gave a link in the summon comment themselves. Then it looks through the comment chain to see if there was 
a video in the parent comments (it will choose the one last referenced in the chain). Finally, it checks the post for a
link. 

The bot recognizes "re-reverses" (wherein someone tries to have the bot reverse it's own video) when it encounters 
it's own comment while searching through parent comments. When this happens, it searches up the chain a bit farther to 
find the original link and replies with that.

### Reversing videos/mp4s

VideoReversingBot uses two different reversing procedures which it chooses based on a few different circumstances. If it 
is reversing an mp4 (which is the most common video type nowadays, go figure), it does the reversal process with FFmpeg. 
For videos, it exports each frame with FFmpeg and then reassembles them with videoski. Although videoski produces great videos, 
it's very slow and so this process is usually avoided. The bot chooses a reversal method by making an educated guess 
as to whether the source was originally a video or an mp4. 

### Video Host Library

v3 of VideoReversingBot introduces the new Video Host Library, a new implementation of the code used to describe videos and 
hosting websites. It aims to share as much code as possible between the sites, reducing implementation efforts as well 
as surface area for bugs. Hosts define several properties such as how to parse their links, upload capabilities,and 
limits. Instead of hard coding where the bot should upload videos for every host, it is now decided dynamically through 
the properties of a video, limits of the hosting sites, and other priorities. It's fairly sturdy even though it's new 
and abstracts away many annoyances, differences, and difficulties managing the video host sites.
