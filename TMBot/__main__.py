#!/usr/bin/env python3
#-*-coding:utf-8-*-

import logging
from pyrogram import idle

from . import app

async def main():
    logging.info("===========")
    logging.info("插件下载地址：https://lacp.eu.org/TMBot%20Plugins/")
    logging.info("===========")
    logging.info("TMBot，启动！")
    await app.start()
    await idle()

if __name__ == "__main__":
    app.run(main())
