import os
import traceback
import datetime


class LogHandler:
    def __init__(self, config):
        self._config = config

    def log_message(self, message):
        if self._check_file_size():
            self._rotate_logs()
        with open(self._config['logger']['filename'], 'a') as f:
            f.write(message + '\n')

    def _check_file_size(self):
        filename = self._config['logger']['filename']
        max_bytes = self._config['logger'].get('max_bytes', 0)
        if os.path.exists(filename):
            return os.path.getsize(filename) >= max_bytes
        return False

    def _rotate_logs(self):
        filename = self._config['logger']['filename']
        backup_count = self._config['logger'].get('backup_count', 0)
        if backup_count > 0:
            for i in range(backup_count - 1, 0, -1):
                if os.path.exists(f"{filename}.{i}"):
                    os.rename(f"{filename}.{i}", f"{filename}.{i + 1}")
            if os.path.exists(filename):
                os.rename(filename, f"{filename}.1")

    def save_error_report(self, func_name, args, kwargs, error):
        error_report_dir = self._config['logger'].get('error_report_dir', 'error_reports')
        if not os.path.exists(error_report_dir):
            os.makedirs(error_report_dir)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')
        report_filename = os.path.join(error_report_dir, f'error_{func_name}_{timestamp}.txt')

        with open(report_filename, 'w') as file:
            file.write(f'FUNCTION: {func_name}\n')
            file.write(f'TIMESTAMP: {timestamp}\n')
            file.write(f'ARGS: {args}\n')
            file.write(f'KWARGS: {kwargs}\n')
            file.write(f'ERROR: {error}\n')
            file.write(f'TRASEBACK:\n')
            file.write(traceback.format_exc())
