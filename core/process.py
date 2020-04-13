from io import BytesIO

from core.context import CommentContext
from core.reply import reply
from core.video import VideoHostManager, CANNOT_UPLOAD, UPLOAD_FAILED
from core.history import check_database, add_to_database, delete_from_database
from core import constants as consts
from core.hosts import VideoFile, Video
from core.constants import SUCCESS, USER_FAILURE, UPLOAD_FAILURE


def process_comment(reddit, comment=None, queue=None, original_context=None):
    vhm = VideoHostManager(reddit)
    if not original_context:    # If we were not provided context, make our own
        # Check if comment is deleted
        if not comment.author:
            print("Comment doesn't exist????")
            print(vars(comment))
            return USER_FAILURE

        print("New request by " + comment.author.name)

        # Create the comment context object
        context = CommentContext(reddit, comment, vhm)
        if not context.url:         # Did our search return nothing?
            print("Didn't find a URL")
            return USER_FAILURE

        if context.rereverse and not context.reupload:  # Is the user asking to rereverse?
            reply(context, context.url)
            return SUCCESS

    else:   # If we are the client, context is provided to us
        context = original_context

    # Create object to grab video from host
    # print(context.url)
    # video_host = VideoHost.open(context, reddit)

    # new_original_video = ghm.extract_video(context.url, context=context)
    new_original_video = context.url
    print(new_original_video)

    # If the link was not recognized, return
    # if not video_host:
    #     return USER_FAILURE

    if not new_original_video:
        return USER_FAILURE

    # If the video was unable to be acquired, return
    # original_video = video_host.get_video()
    # if not original_video:
    #     return USER_FAILURE

    if not new_original_video.id:
        return USER_FAILURE

    if queue:
        # Add to queue
        print("Adding to queue...")
        queue.add_job(context.to_json(), new_original_video)
        return SUCCESS

    # Check database for video before we reverse it
    video = check_database(new_original_video)

    # Requires new database setup
    # db_video = check_database(new_original_video)

    if video:  # db_video
        # If we were asked to reupload, double check the video
        if context.reupload:
            print("Doing a reupload check...")
            if not is_reupload_needed(reddit, video):
                # No reupload needed, do normal stuff
                reply(context, video)
                print("No reupload needed")
                return SUCCESS
            else:
                # Reupload is needed, delete this from the database
                delete_from_database(video)
                print("Reupload needed")
        # Proceed as normal
        else:
            # If it was in the database, reuse it
            reply(context, video)
            return SUCCESS

    # Analyze how the video should be reversed
    # in_format, out_format = video_host.analyze()

    # If there was some problem analyzing, exit
    # if not in_format or not out_format:
    #     return USER_FAILURE

    if not new_original_video.analyze():
        return USER_FAILURE

    uploaded_video = None

    # This video cannot be uploaded and it is not our fault
    cant_upload = False

    # Try every option we have for reversing a video
    for file in new_original_video.files:
        original_video_file = file
        upload_video_host = vhm.get_upload_host(file)

        if not upload_video_host:
            print("File too large {}s {}MB".format(new_original_video.files[0].duration, new_original_video.files[0].size))
            cant_upload = True
            continue
        else:
            cant_upload = False

        # Using the provided host, perform the upload
        for i in range(2):
            result = upload_video_host.upload(original_video_file.id, original_video_file.type, new_original_video.nsfw,
                                                  original_video_file.audio)
            # If the host simply cannot accept this file at all
            if result == CANNOT_UPLOAD:
                cant_upload = True
                break
            # If the host was unable to accept the video at this time
            elif result == UPLOAD_FAILED:
                cant_upload = False
                continue    # Try again?
            # No error and not None, success!
            elif result:
                uploaded_video = result
                break

        # If we have the uploaded video, break out and continue
        if uploaded_video:
            break

    # If there was an error, return it
    if cant_upload:
        return USER_FAILURE
    # It's not that it was an impossible request, there was something else
    elif not uploaded_video:
        return UPLOAD_FAILURE

    if uploaded_video:
        # Add video to database
        # if reversed_video.log:
        add_to_database(new_original_video, uploaded_video)
        # Reply
        print("Replying!", uploaded_video.url)
        reply(context, uploaded_video)
        return SUCCESS
    else:
        return UPLOAD_FAILURE


def process_mod_invite(reddit, message):
    subreddit_name = message.subject[26:]
    # Sanity
    if len(subreddit_name) > 2:
        subreddit = reddit.subreddit(subreddit_name)
        subreddit.mod.accept_invite()
        print("Accepted moderatorship at", subreddit_name)
        return subreddit_name

def is_reupload_needed(reddit, video: Video):
    if video.id:
        if video.analyze():
            return False
    return True
