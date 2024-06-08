import os
import json
import aiohttp
import asyncio
from pathlib import Path
from __main__ import plugConf

sys = True
type = 'syscmd'
command = 'help'
filename = os.path.basename(__file__)
shortDescription = '获取帮助'

def get_prefix():
    config_path = Path(__file__).resolve().parent.parent.parent.parent / 'TMBdata/config/config.json'
    with config_path.open() as f:
        config = json.load(f)
        return config.get('prefix', '#')

prefix = get_prefix()
longDescription = f'发送 `{prefix}{command} <命令>/<插件名>` 获取插件详细信息。'

async def get_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                return content 
            else:
                return '内容获取失败~'

async def handle(event):
    message = event.message.message
    cmd = message.split()
    response = f'**TMBot** 🤖 \n❚ `{message}`\n\n'

    if len(cmd) == 1:
        sorted_plugins = sorted(sorted(plugConf, key=lambda x: x['filename']), key=lambda p: (p['type'] != 'syscmd', p['type'] != 'cmd', p['type'] != 'msg', p['type'] != 'cron'))
        for plugin in sorted_plugins:
            plugin_cmd = plugin.get('command', plugin['filename'])
            response += f"`{prefix + plugin_cmd if plugin_cmd else plugin['filename']}`：{plugin['shortDescription']}\n"
        response += f"\n__{longDescription}__"
    elif len(cmd) >= 2:
        name = cmd[1]
        plugin_info = next((p for p in plugConf if ((prefix + p.get('command')) if p.get('command') else '') == name or p.get('filename') == name), None)
        if plugin_info:
            if plugin_info['command']:
                response += f'命令：`{prefix}{plugin_info['command']}`\n'
            response += f'插件：`{plugin_info['filename']}`\n'
            response += f'描述：{plugin_info['shortDescription']}\n'
            if plugin_info['longDescription']:
                response += f'说明：{plugin_info['longDescription']}\n'
        elif name == "TMBot":
            response += await get_content('https://file.pbpz.net/TMBot%20Plugins/README')
        else:
            response += f"未找到插件：`{name}`"

    await event.edit(response)
