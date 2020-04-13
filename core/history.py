# Manage a database of the last few months reverses and their links in order to save time
from datetime import date
from pony.orm import Database, PrimaryKey, Required, Optional, db_session, select, commit, Set, desc

from core.video import VideoHostManager
from core.hosts import Video as NewVideo_object
from core.hosts import VideoHost
from core.credentials import CredentialsLoader

db = Database()

def bind_db(db):
    creds = CredentialsLoader.get_credentials()['database']

    if creds['type'] == 'sqlite':
        db.bind(provider='sqlite', filename='../database.sqlite', create_db=True)
    elif creds['type'] == 'mysql':
        # Check for SSL arguments
        ssl = {}
        if creds.get('ssl-ca', None):
            ssl['ssl'] = {'ca': creds['ssl-ca'], 'key': creds['ssl-key'], 'cert': creds['ssl-cert']}

        db.bind(provider="mysql", host=creds['host'], user=creds['username'], password=creds['password'],
                db=creds['database'], ssl=ssl, port=int(creds.get('port', 3306)))
    else:
        raise Exception("No database configuration")

    db.generate_mapping(create_tables=True)


class VideoHosts(db.Entity):
    name = PrimaryKey(str)
    origin_videos = Set('Video', reverse='origin_host')
    reversed_videos = Set('Video', reverse='reversed_host')

class Video(db.Entity):
    id = PrimaryKey(int, auto=True)
    origin_host = Required(VideoHosts, reverse='origin_videos')
    origin_id = Required(str)
    reversed_host = Required(VideoHosts, reverse='reversed_videos')
    reversed_id = Required(str)
    time = Required(date)
    nsfw = Optional(bool)
    total_requests = Optional(int)
    last_requested_date = Optional(date)


bind_db(db)

vhm = VideoHostManager()

def sync_hosts():
    # Double check videohost bindings
    with db_session:
        for host in vhm.hosts:
            q = select(h for h in VideoHosts if h.name == host.name).first()
            if not q:
                new = VideoHosts(name=host.name)


sync_hosts()


def check_database(original_video: NewVideo_object):
    # Have we reversed this video before?
    with db_session:
        host = VideoHosts[original_video.host.name]
        video_id = original_video.id
        if original_video.host.name == "LinkVideo":
            if len(video_id) > 255:
                original_video.id = original_video.id[:255]
        query = select(g for g in Video if g.origin_host == host and
                       g.origin_id == video_id)
        video = query.first()
        # If we have, get it's host and id
        if video:
            host = video.reversed_host
            id = video.reversed_id
        # If this is not a video we have reversed before, perhaps this is a re-reverse?
        else:
            query = select(g for g in Video if g.reversed_host == host and
                           g.reversed_id == original_video.id)
            video = query.first()
            if video:
                host = video.origin_host
                id = video.origin_id
        if video:
            print("Found in database!", video.origin_id, video.reversed_id)
            video.last_requested_date = date.today()
            video.total_requests += 1
            return vhm.host_names[host.name].get_video(id, nsfw=video.nsfw)
    return None


def add_to_database(original_video, reversed_video):
    with db_session:
        # Extra checks for linkvideo
        if original_video.host.name == "LinkVideo":
            if len(original_video.id) > 255:
                original_video.id = original_video.id[:255]
        new_video = Video(origin_host=VideoHosts[original_video.host.name], origin_id=original_video.id,
                         reversed_host=VideoHosts[reversed_video.host.name], reversed_id=reversed_video.id, time=date.today(),
                         nsfw=original_video.nsfw, total_requests=1, last_requested_date=date.today())


def delete_from_database(original_video):
    with db_session:
        # Select video as original first
        query = select(g for g in Video if g.origin_host == VideoHosts[original_video.host.name] and
                       g.origin_id == original_video.id)
        video = query.first()
        # If we have it, delete it
        if video:
            video.delete()
        # Possibly a rereversed then
        else:
            query = select(g for g in Video if g.reversed_host == VideoHosts[original_video.host.name] and
                           g.reversed_id == original_video.id)
            video = query.first()
            if video:
                video.delete()


def list_by_oldest_access(reversed_host: VideoHost, cutoff):
    with db_session:
        query = select(g for g in Video if g.reversed_host == VideoHosts[reversed_host.name]
                       and g.last_requested_date < cutoff).order_by(Video.last_requested_date)

        print(query)
        return query[:]

