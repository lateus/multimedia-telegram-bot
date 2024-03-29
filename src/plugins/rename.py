import os, time, requests

from datetime import datetime as dt
from telethon import events
from telethon.tl.types import DocumentAttributeVideo
from ethon.telefunc import fast_download, fast_upload
from ethon.pyutils import rename
from ethon.pyfunc import video_metadata

from .. import Drone, BOT_UN

async def media_rename(event, msg, new_name):
    edit = await event.client.send_message(event.chat_id, 'Trying to process.', reply_to=msg.id)
    Drone = event.client
    DT = time.time()
    if hasattr(msg.media, "document"):
        file = msg.media.document
    else:
        file = msg.media
    mime = msg.file.mime_type
    if 'mp4' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4"
        out = new_name + ".mp4"
    elif msg.video:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp4"
        out = new_name + ".mp4"
    elif 'x-matroska' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mkv" 
        out = new_name + ".mkv"            
    elif 'webm' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".webm" 
        out = new_name + ".webm"
    elif 'zip' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".zip" 
        out = new_name + ".zip"            
    elif 'jpg' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".jpg" 
        out = new_name + ".jpg"
    elif 'png' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".png"
        out = new_name + ".png"
    elif 'pdf' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".pdf" 
        out = new_name + ".pdf"
    elif 'rar' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".rar"
        out = new_name + ".rar"
    elif 'mp3' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".mp3" 
        out = new_name + ".mp3"
    elif 'ogg' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".ogg" 
        out = new_name + ".ogg"          
    elif 'flac' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".flac"  
        out = new_name + ".flac"
    elif 'wav' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".wav" 
        out = new_name + ".wav"
    elif 'webp' in mime:
        name = "media_" + dt.now().isoformat("_", "seconds").replace(":", "_") + ".webp" 
        out = new_name + ".webp"
    else:
        default_name = msg.file.name
        if not default_name:
            await edit.edit("Failed fetching extension of your file.")
        else:
            try:
                name = msg.file.name
                ext = (name.split("."))[1]
                out = new_name + "." + ext
                await fast_download(name, file, Drone, edit, DT, "**DOWNLOADING:**")
                rename(name, out)
                UT = time.time()
                uploader = await fast_upload(out, out, UT, Drone, edit, '**UPLOADING:**')
                net_time = round(DT - UT)
                await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", force_document=True) # thumb
            except Exception as e:
                await edit.edit(f"An error occured.", link_preview=False)
                print(e)
                return
    try:  
        await fast_download(name, file, Drone, edit, DT, "**DOWNLOADING:**")
    except Exception as e:
        await edit.edit(f"An error occured while downloading.", link_preview=False)
        print(e)
        return
    await edit.edit("Renaming.")
    try:
        rename(name, out)
    except Exception as e:
        await edit.edit(f"An error occured while renaming.", link_preview=False)
        print(e)
        return
    try:
        if not 'video' in mime:
            UT = time.time()
            uploader = await fast_upload(out, out, UT, Drone, edit, '**UPLOADING:**')
            net_time = round(DT - UT)
            await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", force_document=True) # thumb
        else:
            if 'mp4' in mime:
                metadata = video_metadata(out)
                width = metadata["width"]
                height = metadata["height"]
                duration = metadata["duration"]
                attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
                UT = time.time()
                uploader = await fast_upload(f'{out}', f'{out}', UT, Drone, edit, '**UPLOADING:**')
                net_time = round(DT - UT)
                await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", attributes=attributes, force_document=False) # thumb
            elif msg.video:
                metadata = video_metadata(out)
                width = metadata["width"]
                height = metadata["height"]
                duration = metadata["duration"]
                attributes = [DocumentAttributeVideo(duration=duration, w=width, h=height, supports_streaming=True)]
                UT = time.time()
                uploader = await fast_upload(f'{out}', f'{out}', UT, Drone, edit, '**UPLOADING:**')
                net_time = round(DT - UT)
                await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", attributes=attributes, force_document=False)             # thumb
            else:
                UT = time.time()
                uploader = await fast_upload(out, out, UT, Drone, edit, '**UPLOADING:**')
                net_time = round(DT - UT)
                await Drone.send_file(event.chat_id, uploader, caption=f"**Renamed by** : @{BOT_UN}\n\nTotal time:{net_time} seconds.", force_document=True) # thumb
    except Exception as e:
        await edit.edit(f"An error occured while uploading.", link_preview=False)
        print(e)
        return
    await edit.delete()
    os.remove(out)
