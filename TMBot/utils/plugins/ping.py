from datetime import datetime
from telethon import functions

import os

type = 'syscmd'
command = 'ping'
shortDescription = 'Ping'
filename = os.path.basename(__file__)

async def handle(event):
    response = f'**TMBot** [🤖](https://github.com/licproF/TMBot) \n❚ `{event.message.message}`\n\n'
    msg_start = datetime.now()
    response += "Pong!"
    await event.edit(response)
    msg_end = datetime.now()
    msg_duration = (msg_end - msg_start).microseconds / 1000

    ping_start = datetime.now()
    await event.client(functions.PingRequest(ping_id=0))
    ping_end = datetime.now()
    ping_duration = (ping_end - ping_start).microseconds / 1000

    response += f"| PING: {ping_duration} ms | MSG: {msg_duration} ms"
    await event.edit(response)
