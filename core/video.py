from typing import Optional, List
from operator import itemgetter

import os
import importlib
from core import constants as consts
from core.hosts import VideoHost, VideoFile
from core.hosts import Video as NewVideo
from core.regex import REPatterns


# Message constants
# If a host is unable/unwilling to accept a specific video
CANNOT_UPLOAD = "CANNOT_UPLOAD"
# If a host had a temporary failure/problem that inhibited the upload
UPLOAD_FAILED = "UPLOAD_FAILED"


class VideoHostManager:
    hosts = []
    reddit = None
    video_priority = []
    host_names = []

    def __init__(self, reddit=None):
        if not self.hosts:
            # Dynamically load video hosts
            files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "hosts"))
            for f in files:
                #  __init__.py or __pycache__
                if f[:2] != "__" and f[-3:] == ".py":
                    i = importlib.import_module("." + f[:-3], 'core.hosts')
            hosts = []
            for host in VideoHost.__subclasses__():
                host.ghm = self
                hosts.append([host, host.priority])
            VideoHostManager.hosts = [i[0] for i in sorted(hosts, key=itemgetter(1))]
            # Create the priority lists
            # video_priority = [[i, i.video_size_limit] for i in self.hosts if i.can_video]
            VideoHostManager.video_priority = [i for i in sorted(VideoHostManager.hosts, key=lambda x: (x.priority,
                                           x.video_size_limit == 0, x.video_size_limit)) if i.can_video]
            # VideoHostManager.video_priority = [i[0] for i in sorted(video_priority, key=itemgetter(1))]
            VideoHostManager.host_names = {i.name: i for i in self.hosts}
            # print("priority", self.hosts, self.vid_priority, self.video_priority)
        if not self.reddit:
            VideoHostManager.reddit = reddit

    # def host_names(self):
    #     return [i.name for i in self.hosts]

    def extract_video(self, text, **kwargs) -> Optional[NewVideo]:
        for host in self.hosts:
            if host.match(text):
                return host.get_video(text=text, **kwargs)
        return None

    def get_upload_host(self, video_file: VideoFile, ignore: Optional[List[VideoHost]] = None) -> [Optional[VideoFile], Optional[VideoHost]]:
        """Return a host that can suitably upload a file of these parameters"""
        # Create priority lists

        priority = self.video_priority[:]

        # We prioritize the original video host
        if video_file.host in priority:
            priority.remove(video_file.host)
            priority.insert(0, video_file.host)
            print('File is in priority')
        if ignore:
            for video_host in ignore:
                priority.remove(video_host)

        for host in priority:
            if self._within_host_params(host, video_file):
                print("Decided to upload to", host, video_file)
                return host
            else:
                print("Not within params of host", host, video_file)
        return None

    def _within_host_params(self, host: VideoHost, video_file: VideoFile):
        """Determine whether a VideoFile is within a VideoHost's limitations"""
        # Several types of videos but only one type of video
        # Can video check may be redundant due to priority calculations
        if host.can_video and (host.vid_len_limit >= video_file.duration or host.vid_len_limit == 0) and \
            (host.vid_size_limit >= video_file.size or host.vid_size_limit == 0) and \
                (host.audio == video_file.audio or not video_file.audio):
            # Audio logic: if they match or if audio is false (meaning it doesn't matter)

            return True
        return False




class Video:
    def __init__(self, host, id, url=None, log=True, nsfw=False):
        self.host = host
        self.id = id
        # Do we log this video in the db?
        self.log = log
        self.audio = False

        self.nsfw = nsfw

        if url:
            self.url = url
        elif host == consts.REDDITVIDEO:
            self.url = "https://v.redd.it/{}".format(id)
            # self.audio = True
        elif host == consts.STREAMABLE:
            self.url = "https://streamable.com/{}".format(id)
            self.audio = True
        elif host == consts.LINKVIDEO:
            self.url = id
        else:
            self.url = None