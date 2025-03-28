from apscheduler.schedulers.asyncio import AsyncIOScheduler
from TMBot.utils.decorators import schedules
from pytz import timezone, all_timezones
import logging
import os

logger = logging.getLogger(__name__)
TZ = os.getenv('tz', 'UTC')

def is_valid_timezone(tz_str):
    return tz_str in all_timezones

if not is_valid_timezone(TZ):
    TZ = 'UTC'

class SchedulerManager:
    def __init__(self, client):
        self.client = client
        self.scheduler = AsyncIOScheduler(timezone=timezone(TZ))
    
    async def start(self):
        for name, info in schedules.items():
            self._wrap_job(name, info)
            self.scheduler.add_job(
                self._get_job_wrapper(name, info.handler),
                'cron',
                **self._parse_cron(info.cron)
            )
        self.scheduler.start()
        logger.info("⏰ 定时任务调度器已启动")

    def _get_job_wrapper(self, name: str, func):
        async def wrapper():
            try:
                await func(self.client)
                logger.info(f"⏰ 定时事件: {name}")
            except Exception as e:
                logger.error(f"⏰ 定时事件失败 [{name}]: {str(e)}", exc_info=True)
        return wrapper

    def _parse_cron(self, cron: str) -> dict:
        parts = cron.split()
        return {
            'minute': parts[0],
            'hour': parts[1],
            'day': parts[2],
            'month': parts[3],
            'day_of_week': parts[4]
        }

    def _wrap_job(self, name: str, info):
        logger.debug(f"📅 注册定时事件 [{name}] - 计划: {info.cron}")