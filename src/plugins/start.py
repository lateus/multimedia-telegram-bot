from telethon import events

from .. import Drone, AUTH_USERS

from LOCAL.localization import START_TEXT

@Drone.on(events.NewMessage(incoming=True, pattern="/start"))
async def start(event):
    await event.reply(START_TEXT)