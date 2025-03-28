import re
import sys
import subprocess
import logging
from pathlib import Path
from typing import List
import pkg_resources

logger = logging.getLogger(__name__)

class DependencyManager:
    def __init__(self, plugin_dir: Path, log_level: str = "INFO"):
        self.plugin_dir = plugin_dir
        self.log_level = log_level
        self.requirements = self._parse_requirements()

    def _parse_requirements(self) -> List[str]:
        requirements = []
        for py_file in self.plugin_dir.glob("*.py"):
            with open(py_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if match := re.match(r'^#\s*requires:\s*([^#\n]+)', line):
                        requirements.append(match.group(1).strip())
        return list(set(requirements))

    def _is_installed(self, spec: str) -> bool:
        try:
            pkg_resources.require(spec)
            return True
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            return False
        except Exception as e:
            logger.error(f"依赖检查异常: {spec} - {str(e)}")
            return False

    def _safe_install(self, specs: List[str]):
        if not specs:
            return

        quiet = self.log_level != "DEBUG"
        logger.info(f"开始安装依赖: {', '.join(specs)}")

        try:
            cmd = [sys.executable, "-m", "pip", "install"]
            if quiet:
                cmd.append("--quiet")
                kwargs = {"stdout": subprocess.DEVNULL}
            else:
                kwargs = {}
            
            subprocess.check_call(
                cmd + specs,
                **kwargs
            )
            logger.debug(f"依赖安装成功: {', '.join(specs)}")
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖安装失败，请手动执行: pip install {' '.join(specs)}")
            sys.exit(1)

    def ensure_dependencies(self):
        missing = [s for s in self.requirements if not self._is_installed(s)]
        
        if missing:
            self._safe_install(missing)
            for s in missing:
                if not self._is_installed(s):
                    logger.critical(f"依赖安装后验证失败: {s}")
                    sys.exit(1)
