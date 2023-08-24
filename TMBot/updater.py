import logging
import asyncio
from typing import Callable, Union, List

from pyrogram import Client, handlers, filters
from pyrogram.filters import Filter
from pyrogram.raw.functions.messages import ClearAllDrafts
from pyrogram.raw import types

from apscheduler.triggers.cron import CronTrigger

from .config import scheduler, prefix, tz
from .client import app

def on_msg(self=None, filters=None, group: int = 0 ) -> Callable:
    def decorator(func: Callable) -> Callable:
        if isinstance(self, Client):
            self.add_handler(handlers.MessageHandler(func, filters), group)
        elif isinstance(self, Filter) or self is None:
            if not hasattr(func, "handlers"):
                func.handlers = []
            func.handlers.append(
                (
                    handlers.MessageHandler(func, self),
                    group if filters is None else filters
                )
            )
        return func

    return decorator

def on_draft_cmd(commands: str, group: int = 0) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.handlers = []
        async def raw_update(client, update, users, chats):
            async with asyncio.Lock():
                if isinstance(update, types.UpdateDraftMessage) and isinstance(update.draft, types.DraftMessage):
                    msg = update.draft.message.strip().split()
                    if len(msg) > 0:
                        if msg[0] == f"{prefix}{commands}":
                            logging.info("执行指令：{}".format(commands))
                            await client.invoke(ClearAllDrafts())
                            await func(client, update, users, chats)
        func.handlers.append(
            (
                handlers.RawUpdateHandler(raw_update),
                group
            )
        )
        return func
    return decorator

def on_message_cmd(commands: Union[str, List[str]], self = None, group: int = 0) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.handlers = []
        async def on_message(client, message):
            async with asyncio.Lock():
                logging.info("执行指令：{}".format(commands))
                await func(client, message)
        func.handlers.append(
            (
                handlers.MessageHandler(on_message, ~filters.forwarded & filters.command(commands, prefix) & filters.me),
                group
            )
        )
        return func
    return decorator

def on_scheduler(cron: str = "*/30 * * * *") -> Callable:
    def decorator(func: Callable) -> Callable:
        scheduler.add_job(func, CronTrigger.from_crontab(cron, tz), kwargs={'client': app})
        return func
    return decorator
