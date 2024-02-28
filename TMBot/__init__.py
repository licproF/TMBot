import os
import sys
import psutil
import cpuinfo
import logging
import requests
import platform
import asyncio
from pathlib import Path
from datetime import timedelta, datetime
from importlib import import_module

from pyrogram.handlers.handler import Handler
from pyrogram.raw.functions import Ping

from .client import app
from .updater import on_msg, on_draft_cmd, on_message_cmd, on_scheduler

from .config import tz, proxies, scheduler, packages_required

i = 100

def get_size(b, factor = 1000, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor

async def check_net_handler():
    url = "https://telegram.org/"
    i = 0
    while i < 5:
        try:
            if proxies:
                response = requests.get(url, timeout=5, proxies=proxies)
            else:
                response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except:
            pass
        i += 1
        await asyncio.sleep(5)
    os.execl(sys.executable, sys.executable, "-m", "TMBot")

scheduler.add_job(check_net_handler, CronTrigger.from_crontab("*/5 * * * *", tz))

@on_message_cmd("restart")
async def restart_handler(_, message):
    await message.delete()
    os.execl(sys.executable, sys.executable, "-m", "TMBot")

@on_message_cmd("sysinfo")
async def sysinfo_handler(_, message):
    await message.edit_text("ㅤ")
    text = "**系统信息**\n\n"

    uname = platform.uname()
    text += f"**系统**：`{uname.system} {uname.release}, {uname.version}`\n"

    if cpuinfo.get_cpu_info()['arch'] == "X86_64":
        text += f"**CPU**：`{cpuinfo.get_cpu_info()['brand_raw']}`\n"
    else:
        text += f"**CPU**：`{cpuinfo.get_cpu_info()['arch']} ({cpuinfo.get_cpu_info()['count']}) `\n"

    svmem = psutil.virtual_memory()
    text += f"**内存**：`{get_size(svmem.used, factor = 1024)} / {get_size(svmem.total, 1024)}`\n"

    if os.path.exists("/hostfs"):
        with open("/hostfs/proc/mounts", "r") as f:
            lines = f.readlines()
        partitions = [x.split()[1] for x in lines if x.startswith('/dev') and "/hostfs" in x.split()[1] and'/boot' not in x.split()[1] ]
    else:
        partitions = ["/"]

    if len(partitions) == 1:
        diskusage = psutil.disk_usage(partitions[0])
        text += f"**硬盘**：`{get_size(diskusage.used)} / {get_size(diskusage.total)}`\n"
    else:
        _text = ""
        for partition in partitions:
            diskusage = psutil.disk_usage(partition)
            partition = partition.replace("/hostfs", "/")
            partition = partition.replace("//", "/")
            _text += f"ㅤ`{partition} - {get_size(diskusage.used)} / {get_size(diskusage.total)}`\n"
        text += f"**分区**：\n{_text}"

    interface = psutil.net_io_counters()
    text += f"**流量**：↑ `{get_size(interface.bytes_sent)}` | ↓ `{get_size(interface.bytes_recv)}`\n"

    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            if any(keyword in name.lower() for keyword in ["coretemp", "cpu"]):
                text += f"**温度**：`{entries[0].current}°C`\n"

    load1, load5, load15 = psutil.getloadavg()
    text += f"**负载**：`{psutil.cpu_percent()}%, {'%.2f' %load1}, {'%.2f' %load5}, {'%.2f' %load15}`\n"

    boot_time = psutil.boot_time()
    uptime_seconds = int(psutil.time.time() - boot_time)
    uptime = timedelta(seconds=uptime_seconds)
    uptime_str = "{:0}:{:02}:{:02}:{:02}".format(
        uptime.days // 365,
        uptime.days % 365,
        uptime.seconds // 3600,
        (uptime.seconds % 3600) // 60
    )
    text += f"**运行**：`{uptime_str}`\n"

    await message.edit_text(text)

@on_message_cmd("ping")
async def ping_handler(client, message):
    msg_start = datetime.now()
    await message.edit_text("Pong!")
    msg_end = datetime.now()
    msg_duration = (msg_end - msg_start).microseconds / 1000

    ping_start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    ping_end = datetime.now()
    ping_duration = (ping_end - ping_start).microseconds / 1000

    await message.edit(f"Pong!| PING: {ping_duration} | MSG: {msg_duration}")

modules = __name__ if "__name__" in globals() else "__main__"
if modules in sys.modules:
    tmbot_module = sys.modules[modules]
else:
    tmbot_module = __import__(modules)

tmbot_module_copy = vars(tmbot_module).copy()
for name in tmbot_module_copy.keys():
    if name in ["restart_handler", "sysinfo_handler", "ping_handler"]:
        for handler, group in getattr(tmbot_module, name).handlers:
            group = group + i
            i += 1
            app.add_handler(handler, group)

for path in sorted(Path("data.plugins".replace(".", "/")).rglob("*.py")):
    try:
        module_path = '.'.join(path.parent.parts + (path.stem,))
        module = import_module(module_path)
    except Exception as e:
        logging.error(f'加载失败：{module_path}\n{e}')
        continue

    for name in vars(module).keys():
        try:
            if name == "on_scheduler":
                logging.info(f"加载插件：'{name}' - '{module_path}'")
                continue
            for handler, group in getattr(module, name).handlers:
                if isinstance(handler, Handler) and isinstance(group, int):
                    group = group + i
                    app.add_handler(handler, group)
                    i += 1
        except Exception:
            continue
        else:
            logging.info(f"加载插件：'{name}' - '{module_path}'")

scheduler.start()
