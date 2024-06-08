from telethon import TelegramClient
from pathlib import Path
import os
import json
import logging

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

if not api_id or not api_hash:
    logging.error("请确保在环境变量中设置了 'api_id' 和 'api_hash'")
    raise ValueError("请确保在环境变量中设置了 'api_id' 和 'api_hash'")

SESSION_FILE = Path(__file__).resolve().parent.parent.parent / 'TMBdata/session/session'

def start_client():
    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    config_path = Path(__file__).resolve().parent.parent.parent / 'TMBdata/config/config.json'
    with config_path.open() as f:
        config = json.load(f)
        prefix = config.get('prefix', '#')

    async def main():
        async with client:
            logging.info(f'登录成功！在任意对话框发送 {prefix}help 获取帮助~')
            from utils.utils import event_handler
            event_handler(client)
            await client.run_until_disconnected()

    client.loop.run_until_complete(main())
