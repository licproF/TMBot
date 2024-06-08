import os
import sys

type = 'syscmd'
command = 'restart'
shortDescription = '重启 bot'
filename = os.path.basename(__file__)

async def handle(event):
    await event.delete()
    os.execl(sys.executable, sys.executable, '-m', 'TMBot')