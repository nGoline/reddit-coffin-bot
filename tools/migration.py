from pony.orm import db_session, select
from core.history import Video, VideoHosts, OldVideo
from core.video import VideoHostManager

vhm = VideoHostManager()

hosts = ["", "RedditVideo", "Streamable", "LinkVideo"]

with db_session:
    for i in select(g for g in OldVideo):
        new = Video(origin_host=VideoHosts[hosts[i.origin_host]], origin_id=i.origin_id,
                  reversed_host=VideoHosts[hosts[i.reversed_host]], reversed_id=i.reversed_id, time=i.time, nsfw=i.nsfw,
                  total_requests=i.total_requests, last_requested_date=i.last_requested_date)
