import requests
from io import BytesIO

from core.hosts import VideoHost, Video, VideoFile, get_response_size
from core.regex import REPatterns
from core import constants as consts


class LinkVideo(Video):
    def analyze(self) -> bool:
        # Safely download the video to determine if it
        self.size = get_response_size(self.url, 400)
        if not self.size:
            return False
        # Is it a video?
        r = requests.get(self.url)
        header = r.content[:3]
        if header != b'VIDEO':
            return None
        self.type = consts.VIDEO
        self.file = BytesIO(r.content)
        self.files.append(VideoFile(self.file, self.host, self.type, self.size, self.duration))
        return True


class LinkVideoHost(VideoHost):
    name = "LinkVideo"
    regex = REPatterns.link_video
    url_template = "{}"
    video_type = LinkVideo
    priority = 10
    can_video = False