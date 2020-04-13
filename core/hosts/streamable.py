import requests
import json
from requests.auth import HTTPBasicAuth
from requests_toolbelt.multipart.encoder import MultipartEncoder
from io import BytesIO
from core.credentials import CredentialsLoader
from core import constants as consts
from core.hosts import VideoHost, Video, VideoFile
from core.regex import REPatterns

# import subprocess
from subprocess import check_output


class StreamableClient:
    instance = None

    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def __init__(self):
        creds = CredentialsLoader.get_credentials()['streamable']
        self.email = creds['email']
        self.password = creds['password']
        self.headers = {'User-Agent': consts.user_agent}

    def download_video(self, id):
        r = requests.get('https://api.streamable.com/videos/{}'.format(id),
                         headers=self.headers, auth=self.auth)
        if r.status_code == 404:
            return None
        
        return r.json()['files']['mp4']

    def upload_file(self, filestream):
        # tries = 3
        # while tries:
        files = {"file": filestream}
        # m = MultipartEncoder(fields=files)
        print("Uploading to streamable...")
        r = requests.post('https://api.streamable.com/upload',
                          headers=self.headers, files=files, auth=self.auth)
        if r.text:
            return r.json()['shortcode']

    def upload_file_new(self, file_name):
        out = check_output(['curl', 'https://api.streamable.com/upload', '-u', f"{self.email}:{self.password}", '-F', f'file=@tmp/{file_name}.mp4'])
        return json.loads(out.decode("utf-8"))['shortcode']


streamable = StreamableClient()


class StreamableVideo(Video):
    def analyze(self):
        info = streamable.download_video(self.id)
        if not info:
            return False
        file = BytesIO(requests.get("https:" + info['url']).content)
        self.files.append(VideoFile(file, self.id, host=self.host, video_type=consts.MP4, audio=False, duration=info['duration'],
                                  size=info['size']/1000000))
        return True


class StreamableHost(VideoHost):
    name = "Streamable"
    regex = REPatterns.streamable
    url_template = "https://streamable.com/{}"
    audio = True
    video_type = StreamableVideo
    can_video = True

    @classmethod
    def upload(cls, file, video_type, nsfw, audio=False):
        id = streamable.upload_file_new(file)
        if id:
            return StreamableVideo(cls, id, nsfw=nsfw)
