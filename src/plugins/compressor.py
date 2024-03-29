import asyncio, time, subprocess, re, os

from datetime import datetime as dt
from telethon import events
from telethon.tl.types import DocumentAttributeVideo
from ethon.telefunc import fast_download, fast_upload
from ethon.pyfunc import video_metadata

from .. import Drone, BOT_UN

from LOCAL.utils import ffmpeg_progress

async def compress(event, msg, ffmpeg_cmd=0, ps_name=None):
    if ps_name is None:
        ps_name = '**COMPRESSING:**'
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
    _ps = "COMPRESS"
    if ps_name != "**COMPRESSING:**":
        _ps = "ENCODE"
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
    if ffmpeg_cmd == 2:
        if hgt == 360 or wdt == 640:
            await edit.edit("Fast compress cannot be used for this media, try using HEVC!")
            os.rmdir("encodemedia")
            return
    FT = time.time()
    progress = f"progress-{FT}.txt"
    cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" None """{out}""" -y'
    if ffmpeg_cmd == 1:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -preset ultrafast -vcodec libx265 -crf 28 -acodec copy -c:s copy """{out}""" -y'
    elif ffmpeg_cmd == 2:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -c:v libx265 -crf 22 -preset ultrafast -s 640x360 -c:a copy -c:s copy """{out}""" -y'
    elif ffmpeg_cmd == 3:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -preset faster -vcodec libx265 -crf 22 -acodec copy -c:s copy """{out}""" -y'
    elif ffmpeg_cmd == 4:
        cmd = f'ffmpeg -hide_banner -loglevel quiet -progress {progress} -i """{name}""" -preset faster -vcodec libx264 -crf 22 -acodec copy -c:s copy """{out}""" -y'
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
    text = F'**ENCODED by:** @{BOT_UN}'
    if ps_name != "**ENCODING:**":
        text = f'**COMPRESSED by** : @{BOT_UN}\n\nbefore compressing : `{i_size}`\nafter compressing : `{f_size}`'
    UT = time.time()
    if 'x-matroska' in mime:
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, thumb=JPG, force_document=True)
        except Exception as e:
            os.rmdir("encodemedia")
            print(e)
            return await edit.edit(f"An error occured while uploading.")
    elif 'webm' in mime:
        try:
            uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
            await Drone.send_file(event.chat_id, uploader, caption=text, force_document=True) # thumbs
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
            await Drone.send_file(event.chat_id, uploader, caption=text, attributes=attributes, force_document=False) # thumbs
        except Exception:
            try:
                uploader = await fast_upload(f'{out2}', f'{out2}', UT, Drone, edit, '**UPLOADING:**')
                await Drone.send_file(event.chat_id, uploader, caption=text, force_document=True) # thumbs
            except Exception as e:
                os.rmdir("encodemedia")
                print(e)
                return await edit.edit(f"An error occured while uploading.")
    await edit.delete()
    os.remove(name)
    os.remove(out2)
