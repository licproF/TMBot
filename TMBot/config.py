import os
import sys
import pytz
import logging
import subprocess
import pkg_resources
from datetime import datetime
from urllib.parse import urlparse

from apscheduler.schedulers.asyncio import AsyncIOScheduler

tz = os.getenv("TZ") if os.getenv("TZ") else "Etc/UTC"
log_level = os.getenv("loglevel") if os.getenv("loglevel") else 'WARNING'

if log_level == "INFO":
    loglevel = logging.INFO
elif log_level == "ERROR ":
    loglevel =logging.ERROR
elif log_level == "WARNING":
    loglevel = logging.WARNING

logging.Formatter.converter = lambda *args: datetime.now(tz=pytz.timezone(tz)).timetuple()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

logging.getLogger("pyrogram").setLevel(loglevel)
logging.getLogger("apscheduler").setLevel(loglevel)

def parse_url(url):
    try:
        parsed_url = urlparse(url)
        result = {
            "scheme": parsed_url.scheme,
            "hostname": parsed_url.hostname,
            "port": parsed_url.port
        }
        if parsed_url.username:
            result["username"] = parsed_url.username
        if parsed_url.password:
            result["password"] = parsed_url.password
        return result
    except Exception as e:
        raise e

def requests_proxy(proxy_url):
    if proxy_url.startswith("http://"):
        return {"http": proxy_url, "https": proxy_url}
    elif proxy_url.startswith("https://"):
        return {"https": proxy_url}
    elif proxy_url.startswith("socks5://"):
        return {"http": proxy_url, "https": proxy_url}

def check_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)

def packages_required(packages):
    required = set(packages.lower().split())
    installed = {str(pkg.key).lower() for pkg in pkg_resources.working_set}
    missing = required - installed
    if not missing:
        return True
    try:
        if subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing]) == 0:
            return True
    except Exception as e:
        logger.error("安装依赖失败：{}".format(e))
        return False

scheduler = AsyncIOScheduler(timezone=pytz.timezone(tz))

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
proxy = parse_url(os.getenv("proxy")) if os.getenv("proxy") else None
proxies = requests_proxy(os.getenv("proxy")) if os.getenv("proxy") else None
prefix = os.getenv("prefix") if os.getenv("prefix") else ""
datadir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'data')
workdir = os.path.join(datadir, 'session')
pluginsdir = os.path.join(datadir, 'plugins')

check_dir(datadir)
check_dir(workdir)
check_dir(pluginsdir)
