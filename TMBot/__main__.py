import os
import asyncio
import logging
from pathlib import Path
from telethon import TelegramClient
from logging.handlers import RotatingFileHandler
from TMBot.utils import handlers, plugin_loader, scheduler
from TMBot.config import setup_config, get_log_config

BASE_DIR = Path(__file__).parent.parent
data_dir = BASE_DIR / "TMBdata"
sessions_dir = data_dir / "sessions"
plugins_dir = data_dir / "plugins"

data_dir.mkdir(parents=True, exist_ok=True)
sessions_dir.mkdir(parents=True, exist_ok=True)
plugins_dir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

config = setup_config(data_dir)

def setup_logging(data_dir: Path):
    log_config = get_log_config(config)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        filename=data_dir / 'TMBot.log',
        maxBytes=log_config['max_bytes'],
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=log_config['level'],
        handlers=[file_handler, console_handler]
    )

    telethon_logger = logging.getLogger('telethon')
    apscheduler_logger = logging.getLogger('apscheduler')

    telethon_logger.setLevel(log_config['telethon_level'])
    apscheduler_logger.setLevel(log_config['apscheduler_level'])


async def main_async():
    config = setup_config(data_dir)
    log_config = get_log_config(config)

    client = TelegramClient(
        session=sessions_dir / "TMBot",
        api_id=os.getenv('api_id'),
        api_hash=os.getenv('api_hash')
    )
    client.prefix = os.getenv('prefix', '#')

    await client.start()
    owner_id = await client.get_peer_id('me')
    me = await client.get_me()
    user = me.username if me.username else me.first_name
    logger.info(f"hi，{user}！请在任意对话框发送 {client.prefix}help 获取帮助~")

    handlers.setup_handlers(client, owner_id, client.prefix)
    plugin_loader.load_plugins(
        system_plugins=["TMBot.utils.plugins"],
        user_plugins=[plugins_dir],
        log_level=log_config['level'],
        logger=logger,
        data_dir=data_dir,
        config=config
    )

    await scheduler.SchedulerManager(client).start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    setup_logging(data_dir)
    asyncio.run(main_async())
