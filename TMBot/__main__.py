import sys
import json
import subprocess
import importlib.util
import importlib.metadata
from pathlib import Path

sys.path.extend([str(Path(__file__).resolve().parent),
                 str(Path(__file__).resolve().parent.parent / 'TMBdata')])

plugConf = []

def create_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def create_file_if_not_exists(file_path, content):
    if not file_path.exists():
        file_path.write_text(json.dumps(content, indent=4))

def read_plugins_info(path):
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
                    print(f"加载插件：{file.name}")
                else:
                    print(f"依赖安装失败，未加载插件：{file.name}")
            except Exception as e:
                print(f"加载插件失败：{file.name}\n{e}")
    return plugins

def install_requirements(requirements):
    for package in requirements:
        try:
            importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError as e:
                print(f"安装依赖失败：{package}\n{e}")
                return False
    return True

def load_plugins():
    global plugConf
    sys_plugins_path = Path(__file__).resolve().parent / 'utils/plugins'
    data_plugins_path = Path(__file__).resolve().parent.parent / 'TMBdata/plugins'
    sys_plugins = read_plugins_info(sys_plugins_path)
    data_plugins = read_plugins_info(data_plugins_path)
    plugConf = sys_plugins + data_plugins

def main():
    base_path = Path(__file__).resolve().parent.parent / 'TMBdata'
    for sub_dir in ['tmp', 'config', 'session', 'plugins']:
        create_dir(base_path / sub_dir)

    create_file_if_not_exists(base_path / 'config/config.json', { "prefix": "#" })

    load_plugins()

    from utils.client import start_client
    start_client()

if __name__ == "__main__":
    main()