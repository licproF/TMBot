import os
import platform
from TMBot.utils.decorators import command

def format_bytes(b):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024

def get_cpu_model():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[1].strip()
    except FileNotFoundError:
        pass
    return platform.uname().machine

def get_memory_info():
    meminfo = {}
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                parts = line.split()
                meminfo[parts[0].rstrip(':')] = int(parts[1])
    except FileNotFoundError:
        pass
    total_memory = format_bytes(meminfo.get('MemTotal', 0) * 1024)
    used_memory = format_bytes((meminfo.get('MemTotal', 0) - meminfo.get('MemAvailable', 0)) * 1024)
    return used_memory, total_memory

def get_disk_info():
    total_disk = used_disk = 0
    try:
        with open('/proc/mounts', 'r') as f:
            for line in f:
                parts = line.split()
                if parts[1] == '/':
                    statvfs = os.statvfs(parts[1])
                    total_disk = statvfs.f_blocks * statvfs.f_frsize
                    used_disk = total_disk - (statvfs.f_bfree * statvfs.f_frsize)
                    break
    except FileNotFoundError:
        pass
    return format_bytes(used_disk), format_bytes(total_disk)

def get_network_info():
    interfaces = [iface for iface in os.listdir('/sys/class/net') if os.path.exists(os.path.join('/sys/class/net', iface, 'device'))]
    if not interfaces:
        interfaces = os.listdir('/sys/class/net')
    
    total_sent = total_received = 0
    try:
        with open('/proc/net/dev', 'r') as f:
            data = f.readlines()
        for line in data[2:]:
            columns = line.strip().split()
            if len(columns) >= 10 and columns[0].strip(':') in interfaces:
                total_received += int(columns[1])
                total_sent += int(columns[9])
    except FileNotFoundError:
        pass
    return format_bytes(total_sent), format_bytes(total_received)

def get_load_avg():
    try:
        with open('/proc/loadavg', 'r') as f:
            loadavg = f.readline().strip().split()[:3]
        return ','.join(loadavg)
    except FileNotFoundError:
        return ''

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
    except FileNotFoundError:
        return '00:00:00:00'
    
    uptime_years = int(uptime_seconds // (365 * 24 * 3600))
    uptime_seconds %= (365 * 24 * 3600)
    uptime_days = int(uptime_seconds // (24 * 3600))
    uptime_seconds %= (24 * 3600)
    uptime_hours = int(uptime_seconds // 3600)
    uptime_seconds %= 3600
    uptime_minutes = int(uptime_seconds // 60)
    return f'{uptime_years:02}:{uptime_days:02}:{uptime_hours:02}:{uptime_minutes:02}'

@command(
    name="sysinfo",
    description="获取系统信息",
    help_text=None
)
async def handler(event):
    response = f'**TMBot** 🤖\n❚ `{event.message.message}`\n\n'
    response += "**系统信息**\n"
    uname = platform.uname()
    response += f'**系统：**`{uname.system} {uname.release} {uname.version}`\n'
    response += f'**CPU：**`{get_cpu_model()}`\n'

    used_memory, total_memory = get_memory_info()
    response += f'**内存：**`{used_memory} / {total_memory}`\n'

    used_disk, total_disk = get_disk_info()
    response += f'**硬盘：**`{used_disk} / {total_disk}`\n'

    total_sent, total_received = get_network_info()
    response += f'**流量：**`↑ {total_sent} | ↓ {total_received}`\n'

    response += f'**负载：**`{get_load_avg()}`\n'

    response += f'**运行：**`{get_uptime()}`\n'

    await event.edit(response)