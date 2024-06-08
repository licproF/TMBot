import sys
import json
import subprocess
import importlib.util
import importlib.metadata
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s - %(funcName)s - %(message)s')

def create_dir(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

def create_config(file_path, content):
    if not file_path.exists():
        file_path.write_text(json.dumps(content, indent=4))

def loglevel(level):
    if level == 'DEBUG':
        return logging.DEBUG
    elif level == 'INFO':
        return logging.INFO
    elif level == 'ERROR':
        return logging.ERROR
    else:
        return logging.WARNING

base_path = Path(__file__).resolve().parent.parent / 'TMBdata'
for sub_dir in ['config', 'session', 'plugins']:
    create_dir(base_path / sub_dir)

config_path = base_path / 'config/config.json'

create_config(config_path, { "loglevel": "WARNING","prefix": "#" })

with config_path.open() as f:
    config = json.load(f)
    level = config.get('loglevel', 'WARNING')

logging.getLogger('apscheduler').setLevel(loglevel(level))
logging.getLogger('telethon').setLevel(loglevel(level))

sys.path.extend([str(Path(__file__).resolve().parent),
                 str(Path(__file__).resolve().parent.parent / 'TMBdata')])

plugConf = []

def impor_plugin(path):
    plugins = []
    if path.is_dir():
        for file in path.glob('*.py'):
            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugin_info = {
                    "filename": file.name,
                    "type": getattr(module, "type", None),
                    "command": getattr(module, "command", None),
                    "shortDescription": getattr(module, "shortDescription", ""),
                    "longDescription": getattr(module, "longDescription", ""),
                    "required": getattr(module, "required", []),
                }
                if plugin_info["type"] == "cron":
                    plugin_info["cron"] = getattr(module, "cron", None)
                if install_requirements(plugin_info["required"]):
                    plugins.append(plugin_info)
                    logging.info(f"加载插件：{file.name}")
                else:
                    logging.warning(f"依赖安装失败，未加载插件：{file.name}")
            except Exception as e:
                logging.error(f"加载插件失败：{file.name}\n{e}")
    return plugins

def install_requirements(requirements):
    for package in requirements:
        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logging.info(f"成功安装依赖：{package}")
            except subprocess.CalledProcessError as e:
                logging.error(f"安装依赖失败：{package}\n{e}")
                return False
    return True

def load_plugins():
    global plugConf
    sys_plugins_path = Path(__file__).resolve().parent / 'utils/plugins'
    data_plugins_path = Path(__file__).resolve().parent.parent / 'TMBdata/plugins'
    sys_plugins = impor_plugin(sys_plugins_path)
    data_plugins = impor_plugin(data_plugins_path)
    plugConf = sys_plugins + data_plugins
    logging.info("所有插件已加载完成~")

def main():
    load_plugins()

    from utils.client import start_client
    start_client()

if __name__ == "__main__":
    main()
