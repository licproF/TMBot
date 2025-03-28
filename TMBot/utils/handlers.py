import logging
from telethon import events
from TMBot.utils.decorators import commands, messages

logger = logging.getLogger(__name__)

def setup_handlers(client, owner_id, prefix: str):
    @client.on(events.NewMessage(outgoing=True, pattern=f"^{prefix}"))
    async def command_handler(event):
        if event.message and getattr(event.message.from_id, 'user_id', None) == owner_id:
            cmd = event.message.text.split(" ")[0].removeprefix(prefix)
            if cmd in commands:
                logger.info(f"📋 命令事件：{prefix}{cmd}")
                await commands[cmd].handler(event)

    @client.on(events.NewMessage())
    async def message_handler(event):
        for name, info in messages.items():
            try:
                await info.handler(event)
            except Exception as e:
                logger.warning(f"⚠️ 消息处理器 {name} 错误: {str(e)}")
