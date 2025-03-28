import importlib
import pkgutil
import sys
from pathlib import Path
from typing import List
from TMBot.utils.validator import PluginValidator
from TMBot.utils.deps_manager import DependencyManager

def load_plugins(system_plugins: List[str], user_plugins: List[str], log_level: str, logger, data_dir: Path, config):
    logger.info("🔌 开始加载插件系统")

    for pkg in system_plugins:
        _load_system_package(pkg, data_dir, logger, config)

    for path in user_plugins:
        _load_user_plugins(Path(path), log_level, data_dir, logger, config)
    
    logger.info("✅ 插件加载完成")

def _load_system_package(package: str, data_dir: Path, logger, config):
    try:
        logger.info(f"🛠️ 正在加载系统插件: {package}")
        package_module = importlib.import_module(package)
        package_path = Path(package_module.__file__).parent
        for finder, name, _ in pkgutil.iter_modules([str(package_path)]):
            try:
                full_name = f"{package}.{name}"
                spec = finder.find_spec(full_name)
                module = importlib.util.module_from_spec(spec)
                module.data_dir = data_dir
                module.config = config
                module.logger = logger
                spec.loader.exec_module(module)
                logger.info(f"  ├─ ✅ 系统插件: {name}")
            except Exception as e:
                logger.warning(f"  ├─ ❌ 加载失败 [{name}]: {str(e)}")
    except Exception as e:
        logger.warning(f"⛔ 系统插件包加载异常 [{package}]: {str(e)}")

def _load_user_plugins(plugins_dir: Path, log_level: str, data_dir: Path, logger, config):
    if not plugins_dir.exists():
        logger.warning(f"⏭️ 用户插件目录不存在: {plugins_dir}")
        return
    
    logger.info(f"📦 正在扫描用户插件目录: {plugins_dir}")
    sys.path.insert(0, str(plugins_dir.parent))
    
    try:
        for file in plugins_dir.glob("*.py"):
            if not PluginValidator.validate_filename(file.name):
                logger.warning(f"  ├─ ⚠️ 跳过非法文件: {file.name}")
                continue
            
            try:
                dm = DependencyManager(plugins_dir, log_level=log_level)
                dm.ensure_dependencies()
                spec = importlib.util.spec_from_file_location(
                    f"plugins.{file.stem}", file
                )
                module = importlib.util.module_from_spec(spec)
                module.data_dir = data_dir
                module.config = config
                module.logger = logger
                spec.loader.exec_module(module)
                logger.info(f"  ├─ ✅ 用户插件: {file.stem}")
            except Exception as e:
                logger.warning(f"  ├─ ❌ 加载失败 [{file.stem}]: {str(e)}")
    finally:
        sys.path.pop(0)
