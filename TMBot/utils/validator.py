import re
from croniter import croniter

class PluginValidator:
    @staticmethod
    def validate_name(name: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9_]{3,32}$', name))
    
    @staticmethod
    def validate_filename(name: str) -> bool:
        return bool(re.match(r'^[a-z0-9_]{3,32}\.py$', name))
    
    @staticmethod
    def validate_cron(cron: str) -> bool:
        return croniter.is_valid(cron)
    
    @staticmethod
    def check_unique(collection: dict, name: str, item_type: str):
        if name in collection:
            raise ValueError(f"{item_type} {name} 已存在")
