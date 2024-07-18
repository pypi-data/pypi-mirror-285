import toml
import os


class Config:
    def __init__(self, config_file='logger_config.toml'):
        self._config_file = config_file
        self._config = {}
        self._load_config()

    def _load_config(self):
        if os.path.exists(self._config_file):
            self._config = toml.load(self._config_file)
        else:
            self._config = {
                'logger': {
                    'filename': 'app.log',
                    'max_bytes': 1048576,
                    'backup_count': 2,
                    'level': 'INFO',
                    'error_report_dir': 'error_reports'
                }
            }

    def _save_config(self):
        with open(self._config_file, 'w') as f:
            toml.dump(self._config, f)

    def create_config(self, filename, level='INFO', error_report_dir='error_reports'):
        self._config = {
            'logger': {
                'filename': filename,
                'max_bytes': 0,
                'backup_count': 0,
                'level': level,
                'error_report_dir': error_report_dir
            }
        }
        self._save_config()

    def get_config(self):
        return self._config