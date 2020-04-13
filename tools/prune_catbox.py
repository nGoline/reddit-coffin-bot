import praw
import datetime
from pprint import pprint
from core import constants as consts
from core.credentials import CredentialsLoader
from core.video import VideoHostManager, CANNOT_UPLOAD, UPLOAD_FAILED
from core.history import check_database, add_to_database, delete_from_database, list_by_oldest_access

CUTOFF = datetime.date.today() - datetime.timedelta(weeks=9*4)

print(CUTOFF)

credentials = CredentialsLoader().get_credentials()

# Only needed to initialize ghm
reddit = praw.Reddit(user_agent=consts.user_agent,
                     client_id=credentials['reddit']['client_id'],
                     client_secret=credentials['reddit']['client_secret'],
                     username=credentials['reddit']['username'],
                     password=credentials['reddit']['password'])


ghm = VideoHostManager(reddit)
catbox = ghm.host_names['Catbox']

videos = list_by_oldest_access(catbox, CUTOFF)
print(len(videos))
print(videos[0].reversed_id, videos[0].last_requested_date)

for video in videos:
    catbox_video = catbox.get_video(id=video.reversed_id)
    catbox.delete(catbox_video)
    delete_from_database(catbox_video)




