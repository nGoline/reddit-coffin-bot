import praw
from core.credentials import CredentialsLoader
from core import constants as consts
from core.context import CommentContext
from core.video import VideoHostManager

"""These tests rely on comments on in my test subreddit so they'll need some work for other people to use"""


credentials = CredentialsLoader().get_credentials()

reddit = praw.Reddit(user_agent=consts.user_agent,
                     client_id=credentials['reddit']['client_id'],
                     client_secret=credentials['reddit']['client_secret'],
                     username=credentials['reddit']['username'],
                     password=credentials['reddit']['password'])
ghm = VideoHostManager(reddit)

context = CommentContext(reddit, reddit.comment('eomsgqq'), ghm)
print(vars(context))
#
# video = ghm.host_names['Gfycat'].get_video(text="https://gfycat.com/SkeletalShallowArmadillo")
# video.analyze()
