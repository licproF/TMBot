import uvloop
from pyrogram import Client

from .config import api_id, api_hash, proxy, workdir

uvloop.install()

app = Client(
    "TMBot",
    api_id,
    api_hash,
    proxy = proxy,
    workdir = workdir
)
