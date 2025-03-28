from TMBot.utils.decorators import command, schedules, messages, commands

@command(
    name="help",
    description="显示帮助信息",
    help_text="使用 `{prefix}help <名称>/<命令>` 查看插件详细信息"
)
async def handler(event):
    prefix = event.client.prefix
    args = event.text.split()[1:]

    letterhead = f'**TMBot** 🤖\n❚ `{event.message.message}`'

    if not args:
        response = [
            f"📋 **命令事件**",
            *[f"`{prefix}{name}` - {info.description}" for name, info in commands.items()],
            "\n📩 **消息事件**",
            *[f"`{name}` - {info.description}" for name, info in messages.items()],
            "\n🕒 **定时事件**",
            *[f"`{name}` - {info.description}" for name, info in schedules.items()]
        ]
        await event.edit( letterhead + "\n\n" + "\n".join(response))
    else:
        query = args[0].removeprefix(prefix)
        if query in commands:
            info = commands[query]
            await event.edit(
                f"{letterhead}\n\n📋 **命令：**`{prefix}{query}`\n📃 **说明：**{info.help_text.format(prefix=prefix)}"
            )
        elif query in schedules:
            info = schedules[query]
            await event.edit(
                f"{letterhead}\n\n⏰ **名称：**{query}\n**Cron：** `{info.cron}`\n📃 **说明：**{info.help_text}"
            )
        elif query in messages:
            info = messages[query]
            await event.edit(
                f"{letterhead}\n\n📩 **名称：**{query}\n📃 **说明：**{info.help_text}"
            )
        else:
            await event.edit(f"{letterhead}\n\n未找到: {query}")
