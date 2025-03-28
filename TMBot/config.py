import configparser

DEFAULT_CONFIG = """
[sys]
TMBot_log_level = INFO
TMBot_log_max_bytes = 1048576
telethon_loglevel = WARNING
apscheduler_loglevel = WARNING
"""

def setup_config(data_dir) -> configparser.ConfigParser:
    config_file = data_dir / "config.ini"

    config = configparser.ConfigParser()

    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG.strip())

    config.read(config_file)

    if not config.has_section('sys'):
        config.add_section('sys')
    
    required = {
        'sys': {
            'TMBot_log_level': 'INFO',
            'TMBot_log_max_bytes': '1048576',
            'telethon_loglevel': 'WARNING',
            'apscheduler_loglevel': 'WARNING'
        }
    }

    updated = False
    for section, options in required.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, default in options.items():
            if not config.has_option(section, key):
                config.set(section, key, default)
                updated = True

    if updated:
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
    config.config_file = config_file
    return config

def get_log_config(config: configparser.ConfigParser) -> dict:
    try:
        return {
            'level': config.get('sys', 'TMBot_log_level', fallback='INFO'),
            'max_bytes': config.getint('sys', 'TMBot_log_max_bytes', fallback=1048576),
            'telethon_level': config.get('sys', 'telethon_loglevel', fallback='WARNING'),
            'apscheduler_level': config.get('sys', 'telethon_loglevel', fallback='WARNING')
        }
    except (ValueError, configparser.Error) as e:
        return {
            'level': 'INFO',
            'max_bytes': 1048576,
            'telethon_level': 'WARNING',
            'apscheduler_level': 'WARNING',
        }
