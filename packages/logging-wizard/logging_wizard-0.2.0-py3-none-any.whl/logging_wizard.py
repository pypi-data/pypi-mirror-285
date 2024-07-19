
import os
import logging
import sys
from datetime import datetime
from pathlib import Path

# root = 'module_name'
# log_name = 'scrappy'
# log_level = 'debug'
# log_level = 'info'
# log_level = 'error'
# log_level = 'warning'

# log_to_file = True
# log_to_file = False


class LoggingWizard(logging.getLoggerClass()):
    def __init__(self, log_file_name: str = None , log_level: str='info', log_to_file: bool = True, log_to_var: bool = False, log_dir: str = None, ):
        self.log_to_var = log_to_var
        name = log_file_name
        if name is None:
            name = self.resolve_package_name()

        super().__init__(name)
        if name.endswith('.log'):
            name = name[:-len('.log')]

        self.log_level = log_level
        self.set_log_level()

        # Create stream handler for logging to stdout (log all five levels)
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.set_log_level(self.stdout_handler)
        # self.stdout_handler.setLevel(logging.DEBUG)
        fmt = '%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)d | %(message)s'
        # fmt = '%(message)s'
        self.stdout_handler.setFormatter(logging.Formatter(fmt))
        self.enable_console_output()

        self.file_handler = None
        if log_to_file:
            self.add_file_handler(name, log_dir)

    def set_log_level(self, handler=None):
        if handler is None:
            handler = self

        if self.log_level.upper() == 'DEBUG':
            handler.setLevel(logging.DEBUG)
        elif self.log_level.upper() == 'INFO':
            handler.setLevel(logging.INFO)
        elif self.log_level.upper() == 'ERROR':
            handler.setLevel(logging.ERROR)
        elif self.log_level.upper() == 'WARNING':
            handler.setLevel(logging.WARNING)
        elif self.log_level.upper() == 'CRITICAL':
            handler.setLevel(logging.CRITICAL)

    @staticmethod
    def is_root():
        return os.geteuid() == 0

    def add_file_handler(self, name, log_dir):
        """Add a file handler for this logger with the specified `name` (and
        store the log file under `log_dir`)."""
        # Format for file log
        if log_dir is None:
            # current_dir = os.getcwd()
            if self.log_to_var:
                if self.is_root() is False:
                    print('\n######################################################################################################################################')
                    print('WARNING: logging might not be possible into /var/log due permission. Please run as root or give the user rights to write into var/log !')
                    print('######################################################################################################################################\n')
                log_dir = os.path.normpath(os.path.join("/var", "log", str(self.resolve_package_name())))
            else:
                package_dir = str(self.resolve_package_path())
                log_dir = os.path.normpath(os.path.join(package_dir, "log"))

        fmt = '%(asctime)s | %(levelname)8s | %(filename)s:%(lineno)d | %(message)s'
        formatter = logging.Formatter(fmt)

        # Determine log path/file name; create log_dir if necessary
        if self.log_level.upper() == 'DEBUG':
            # now = datetime.now().strftime('%Y_%m_%d_%H:%M:%S')
            now = datetime.now().strftime('%Y_%m_%d')
        else:
            now = datetime.now().strftime('%Y_%m_%d')
        log_name = f'{str(name).replace(" ", "_")}_{now}'
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                print('{}: Cannot create directory {}. '.format(
                    self.__class__.__name__, log_dir),
                    end='', file=sys.stderr)
                log_dir = '/tmp' if sys.platform.startswith('linux') else '.'
                print(f'Defaulting to {log_dir}.', file=sys.stderr)

        log_file = os.path.normpath(os.path.join(log_dir, log_name) + '.log')

        # Create file handler for logging to a file (log all five levels)
        self.file_handler = logging.FileHandler(log_file)
        self.set_log_level(self.file_handler)
        # self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(formatter)
        self.addHandler(self.file_handler)
        print(f'Logging to: {log_name} - Path: {log_dir}')

    def has_console_handler(self):
        return len([h for h in self.handlers if type(h) == logging.StreamHandler]) > 0

    def has_file_handler(self):
        return len([h for h in self.handlers if isinstance(h, logging.FileHandler)]) > 0

    def disable_console_output(self):
        if not self.has_console_handler():
            return
        self.removeHandler(self.stdout_handler)

    def enable_console_output(self):
        if self.has_console_handler():
            return
        self.addHandler(self.stdout_handler)

    def disable_file_output(self):
        if not self.has_file_handler():
            return
        self.removeHandler(self.file_handler)

    def enable_file_output(self):
        if self.has_file_handler():
            return
        self.addHandler(self.file_handler)

    @staticmethod
    def get_current_directory():
        executed_from_directory = Path(os.getcwd()).resolve()
        return executed_from_directory

    def resolve_package_name(self):
        executed_directory = self.get_current_directory()
        # Check if the executed directory's name is 'bin' or 'src'
        if executed_directory.name in ['bin', 'src']:
            return executed_directory.parent.name
        else:
            return executed_directory.name

    def resolve_package_path(self):
        executed_directory = self.get_current_directory()
        # Check if the executed directory's name is 'bin' or 'src'
        print(str(executed_directory.parent))
        if executed_directory.name in ['bin', 'src']:
            return str(executed_directory.parent)
        else:
            return str(executed_directory)
