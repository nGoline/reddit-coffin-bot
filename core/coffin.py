import os
import wget
import subprocess
from io import BytesIO


def add_coffin(submission):
    """
    Combines video and audio and adds the coffin meme
    :param submission: submission object
    :return:
    """

    # Get video and audio URL
    print("Downloading files...")
    video_url = submission.media['reddit_video']['fallback_url']
    audio_url = video_url[:video_url.rfind('/')] + '/audio'
    # Download video and audio
    wget.download(video_url, f'tmp/{submission.id}_v.mp4')
    wget.download(audio_url, f'tmp/{submission.id}_a.mp4')

    # Add audio and video together
    print("Combining audio and video...")
    subprocess.call(['ffmpeg', '-i', f'tmp/{submission.id}_v.mp4', '-i', f'tmp/{submission.id}_a.mp4',
                     '-c', 'copy', '-bsf:v', 'h264_mp4toannexb', '-f', 'mpegts', f'tmp/{submission.id}.ts'])

    # Delete intermediate files
    os.remove(f'tmp/{submission.id}_v.mp4')
    os.remove(f'tmp/{submission.id}_a.mp4')

    # Merge videos
    subprocess.call(['ffmpeg', '-i', f'tmp/{submission.id}.ts', '-i', 'media/ending_best.ts', '-filter_complex',
                     '[0:v] [0:a] [1:v] [1:a] concat=n=2:v=1:a=1 [v] [a]', '-map', '[v]', '-map', '[a]', f'tmp/{submission.id}.mp4'])

    # Delete source
    os.remove(f'tmp/{submission.id}.ts')

    with open(f'tmp/{submission.id}.mp4', 'rb') as f:
        file = BytesIO(f.read())
    return file
