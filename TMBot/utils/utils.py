import json
import importlib
from pathlib import Path
from telethon import events
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from __main__ import plugConf

scheduler = AsyncIOScheduler()
scheduler.start()

def on_scheduler(cron: str, client):
    def decorator(func):
        async def wrapped():
            await func(client)
        scheduler.add_job(wrapped, CronTrigger.from_crontab(cron))
        return wrapped
    return decorator

def event_handler(client):
    config_path = Path(__file__).resolve().parent.parent.parent / 'TMBdata/config/config.json'
    with config_path.open() as f:
        config = json.load(f)
        prefix = config.get('prefix', '#')

    @client.on(events.NewMessage(outgoing=True))
    async def cmd_handler(event):
        message = event.message.message
        if message.startswith(prefix):
            cmd = message[len(prefix):].split()[0]
            for plugin in plugConf:
                plugin_path_prefix = 'utils.plugins.' if plugin['type'] == 'syscmd' else 'TMBdata.plugins.'
                if (plugin.get('type') == 'cmd' or plugin.get('type') == 'syscmd') and plugin.get('command') == cmd:
                    try:
                        module = importlib.import_module(f'{plugin_path_prefix}{plugin["filename"].replace(".py", "")}')
                        logging.info(f'执行命令：{message}')
                        await module.handle(event)
                    except Exception as e:
                        logging.error(f'插件出错：{plugin["filename"]}\n{e}')

    for plugin in plugConf:
        plugin_path_prefix = 'utils.plugins.' if plugin['type'] == 'syscmd' else 'TMBdata.plugins.'
        try:
            if plugin.get('type') == 'msg':
                module = importlib.import_module(f'{plugin_path_prefix}{plugin["filename"].replace(".py", "")}')
                client.add_event_handler(module.handle, events.NewMessage())
                logging.info(f'添加消息处理器：{plugin["filename"]}')
            elif plugin.get('type') == 'cron':
                cron_val = plugin.get('cron')
                if cron_val:
                    module = importlib.import_module(f'{plugin_path_prefix}{plugin["filename"].replace(".py", "")}')
                    cron_func = on_scheduler(cron_val, client)(module.cron_task)
                    client.loop.create_task(cron_func())
                    logging.info(f'添加计划任务：{plugin["filename"]}，cron：{cron_val}')
        except Exception as e:
            logging.error(f'插件出错：{plugin["filename"]}\n{e}')
