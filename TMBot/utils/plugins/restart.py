import os
import sys
from TMBot.utils.decorators import command

@command(
    name="restart",
    description="重启 bot",
    help_text=None
)
async def handler(event):
    await event.delete()
    logger.info("重启中...")
    args = [sys.executable, "-m", "TMBot"]
    os.execv(sys.executable, args)
