from core.credentials import CredentialsLoader

user_agent = "CoffinBot v{} by /u/nGoline"
spoof_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"
version = "0.0.1"
sleep_time = 90
username = CredentialsLoader.get_credentials()['reddit']['username']

bot_footer = "---\n\n^(I am a bot.) [^(Report an issue)]" \
                 "(https://www.reddit.com/message/compose/?to=nGoline&subject=CoffinBot%20Issue&message=" \
             "Add a link to the video or comment in your message%2C I'm not always sure which request is being " \
             "reported. Thanks for helping me out!)"


nsfw_reply_template = "##NSFW\n\nHere is your video!\n{}\n\n" + bot_footer

reply_template = "Here is your coffin meme!\n{}\n\n" + bot_footer

reply_ban_subject = "Here is your coffin meme!"

reply_ban_template = "Hi! Unfortunately, I am banned in that subreddit so I couldn't reply to your comment. " \
                       "I was still able to add the coffin meme to your video though!\n{}\n\n" + bot_footer

unnecessary_manual_message = "\n\nJust so you know, you don't have to manually give the video URL if it is in " \
                             "a parent comment or the post. I would have known what you meant anyways :)\n\n"

ignore_messages = ["Welcome to Moderating!", "re: Here is your coffin meme!", "Your reddit premium subscription has expired."]

MP4 = 'mp4'
VIDEO = 'video'
OTHER = 3
LINK = 4
WEBM = 'webm'

REDDITVIDEO = 1
STREAMABLE = 2
LINKVIDEO = 3

SUCCESS = 0         # Reverse and upload succeeded
USER_FAILURE = 1    # Something about the user's request doesn't make sense (ignore it)
UPLOAD_FAILURE = 2  # The video failed to upload (try again later)
