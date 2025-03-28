from dataclasses import dataclass
from typing import Dict
from TMBot.utils.validator import PluginValidator

@dataclass
class CommandInfo:
    handler: callable
    description: str
    help_text: str

@dataclass
class MessageInfo:
    handler: callable
    description: str
    help_text: str

@dataclass
class ScheduleInfo:
    handler: callable
    cron: str
    description: str
    help_text: str

commands: Dict[str, CommandInfo] = {}
messages: Dict[str, MessageInfo] = {}
schedules: Dict[str, ScheduleInfo] = {}

def command(name: str, description: str, help_text: str = None):
    def decorator(func):
        PluginValidator.check_unique(commands, name, "命令事件")
        PluginValidator.validate_name(name)
        
        commands[name] = CommandInfo(
            func, description, help_text or description
        )
        return func
    return decorator

def message(name: str, description: str, help_text: str = None):
    def decorator(func):
        PluginValidator.check_unique(messages, name, "消息事件")
        PluginValidator.validate_name(name)
        
        messages[name] = MessageInfo(
            func, description, help_text or description
        )
        return func
    return decorator

def schedule(name: str, cron: str, description: str, help_text: str = None):
    def decorator(func):
        PluginValidator.check_unique(schedules, name, "定时事件")
        PluginValidator.validate_name(name)
        PluginValidator.validate_cron(cron)
        
        schedules[name] = ScheduleInfo(
            func, cron, description, help_text or description
        )
        return func
    return decorator
