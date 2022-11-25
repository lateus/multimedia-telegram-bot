import asyncio, time, subprocess, re, os

from datetime import datetime as dt
from telethon import events
from telethon.tl.types import DocumentAttributeVideo
from ethon.telefunc import fast_download, fast_upload
from ethon.pyfunc import video_metadata

from .. import Drone, BOT_UN

from LOCAL.utils import ffmpeg_progress

async def encode(event, msg, scale=0):
    ps_name = str(f"**{scale}p ENCODING:**")
    _ps = str(f"{scale}p ENCODE")
    Drone = event.client
    edit = await Drone.send_message(event.chat_id, "Trying to process.", reply_to=msg.id)
    new_name = "out_" + dt.now().isoformat("_", "seconds").replace(":", "_")
    if hasattr(msg.media, "document"):
        file = msg.media.document
    else:
        file = msg.media
    mime = msg.file.mime_type
    if 'mp4' in mime:
        n = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4"
        out = new_name + ".mp4"
    elif msg.video:
        n = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4"
        out = new_name + ".mp4"
    elif 'x-matroska' in mime:
        n = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mkv"
        out = new_name + ".mp4"
    elif 'webm' in mime:
        n = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".webm"
        out = new_name + ".mp4"
    else:
        n = msg.file.name
        ext = (n.split("."))[1]
        out = new_name + ext
    DT = time.time()
    try:
        await fast_download(n, file, Drone, edit, DT, "**DOWNLOADING:**")
    except Exception as e:
        os.rmdir("encodemedia")
        print(e)
        return await edit.edit(f"An error occured while downloading.") 
    name = '__' + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4"
    os.rename(n, name)
    await edit.edit("Extracting metadata...")
    vid = video_metadata(name)
    hgt = int(vid['height'])
    wdt = int(vid['width'])
    if scale == hgt:
        os.rmdir("encodemedia")
        return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 240:
        if 426 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 360:
        if 640 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 480:
        if 854 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    if scale == 720:
        if 1280 == wdt:
            os.rmdir("encodemedia")
            return await edit.edit(f"The video is already in {scale}p resolution.")
    FT = time.time()
    progress = f"progress-{FT}.txt"
    cmd = ''
    if scale == 240:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 426x240 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 360:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 640x360 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 480:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 854x480 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    elif scale == 720:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx264 -pix_fmt yuv420p -preset faster -s 1280x720 -crf 24 -c:a libopus -ac 2 -ab 128k -c:s copy """{out}""" -y'
    try:
        await ffmpeg_progress(cmd, name, progress, FT, edit, ps_name)
    except Exception as e:
        os.rmdir("encodemedia")
        print(e)
        return await edit.edit(f"An error occured while FFMPEG progress.")
    out2 = dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4" 
    if msg.file.name:
        out2 = msg.file.name
    else:
        out2 = dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4"
    os.rename(out, out2)
    i_size = os.path.getsize(name)
    f_size = os.path.getsize(out2)
    text = f'**{_ps}D by** : @{BOT_UN}'
    UT = time.time()
    if 'x-matroska' in mime:
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, force_document=True) # thumb
        except Exception as e:
            os.rmdir("encodemedia")
            print(e)
            return await edit.edit(f"An error occured while uploading.")
    elif 'webm' in mime:
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, force_document=True) # thumb
        except Exception as e:
            os.rmdir("encodemedia")
            print(e)
            return await edit.edit(f"An error occured while uploading.")
    else:
        metadata = video_metadata(out2)
        width = metadata["width"]
        height = metadata["height"]
        duration = metadata["duration"]
        attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, attributes=attributes, force_document=False) # thumb
        except Exception:
            try:
                uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
                await Drone.send_file(event.chat_id, uploader, caption=text, force_document=True) # thumb
            except Exception as e:
                os.rmdir("encodemedia")
                print(e)
                return await edit.edit(f"An error occured while uploading.")
    await edit.delete()
    os.remove(name)
    os.remove(out2)
