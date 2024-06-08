import os
import json
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
            response += f'''**关于 TMBot**
https://github.com/licproF/TMBot

基于 [telethon](https://github.com/LonamiWebs/Telethon) 的 userbot 程序，代码百分百由 ChatGPT 完成。

部署：```
docker run -it \\
    --restart always \\
    --name TMBot \\
    --net host \\
    -v /path/to/TMBdata:/TMBdata \\
    -e api_id=1234567 \\
    -e api_hash=1a2b3c...8x9y0z \\
    noreph/tmbot
```
插件目录：`TMBdata/plugins`。
配置文件目录：`TMBdata/config`。
账号登录数据：`TMBdata/session`。
api_id、api_hash 请前往 my.telegram.org 申请。

__⚠️⚠️⚠️ 温馨提示：谨慎使用，不对使用后出现任何结果负责，包括但不限于封号、被群组管理员禁言、踢出等等__。
'''
        else:
            response += f"未找到插件：`{name}`"

    await event.edit(response)
