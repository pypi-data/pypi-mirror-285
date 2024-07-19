from pathlib import Path
import yaml
from time import sleep
from datetime import datetime
from threading import Thread
from sys import argv
import logging
from .pub import Frequency

log = logging.getLogger('CellTasker')
log.addHandler(logging.StreamHandler())


def default_boot_cmd(root_path: Path):
    default_bat = root_path / 'cell_run.bat'
    if not default_bat.exists() or not default_bat.is_file():
        log.info('No default bat file found, creating a default bat file for you.')
        with open(default_bat, 'w', encoding='utf-8') as f:
            f.write('@echo This is a default bat file created by cell module, you should change it for booting your cell instance.\n')
    cmd = f'cd {root_path.absolute()} && start cmd /K {default_bat.absolute()}'
    return cmd


class Cell(Thread):
    def __init__(self, name: str, timerange: str, interval: int,
                 register_path: Path | str, update_path: Path | str,
                 boot_cmd: str, frequency_reset_b_times: Frequency = Frequency.daily) -> None:
        super().__init__()
        # 参数校验：
        if not isinstance(name, str):
            raise Exception('name should be a string')
        if not isinstance(timerange, str):
            raise Exception('timerange should be a string')
        if not isinstance(interval, int):
            raise Exception('interval should be an integer')
        if isinstance(register_path, str):
            register_path = Path(register_path)
        if not register_path.exists() or not register_path.is_dir():
            raise Exception('register_path should be a directory')
        if isinstance(update_path, str):
            update_path = Path(update_path)
        if not update_path.exists() or not update_path.is_dir():
            raise Exception('update_path should be a directory')
        if not isinstance(boot_cmd, str):
            raise Exception('boot_cmd should be a string')
        # 初始化
        self.name = f'cell_{name}'
        self.timerange = timerange
        self.interval = interval
        self.register_path = register_path
        self.update_path = update_path
        self.boot_cmd = boot_cmd
        self.status = 'init'
        self.frequency_reset_b_times = frequency_reset_b_times

    @property
    def timestamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def change_status(self, status):
        self.status = status

    def register(self):
        if not self.register_path.exists() or not self.register_path.is_dir():
            raise Exception('register_path should be a directory')
        self.register_path.mkdir(parents=True, exist_ok=True)
        with open(self.register_path / f'{self.name}.yml', 'w', encoding='utf-8') as f:
            yaml.dump({
                'name': self.name,
                'timerange': self.timerange,
                'interval': self.interval,
                'register_path': self.register_path.absolute().as_posix(),
                'update_path': self.update_path.absolute().as_posix(),
                'boot_cmd': self.boot_cmd,
                'frequency_reset_b_times': self.frequency_reset_b_times.value
            }, f, encoding='utf-8', allow_unicode=True)

    def update(self):
        if not self.update_path.exists() or not self.update_path.is_dir():
            raise Exception('update_path should be a directory')
        self.update_path.mkdir(parents=True, exist_ok=True)
        update_file = self.update_path / f'{self.name}.txt'
        update_file.write_text(f'{self.status}\n{self.timestamp}', encoding='utf-8')

    def run(self):
        while True:
            self.update()
            if self.status in ['done', 'auto_done', 'error']:
                break
            sleep(self.interval)


seen = set()


def task(name: str, timerange: str, interval: int,
         register_path: Path | str, update_path: Path | str, boot_cmd: str = None,
         frequency_reset_b_times: Frequency = Frequency.daily):
    if name in seen:
        raise Exception(f'{name} has been registered')
    root_path = Path(argv[0]).parent
    cell = Cell(name, timerange, interval, register_path, update_path,
                boot_cmd or default_boot_cmd(root_path), frequency_reset_b_times)
    seen.add(name)

    def decorator(func):
        def wrapper(*args, **kwargs):
            cell.register()
            cell.start()
            kwargs.update(change_status=cell.change_status)
            try:
                t = Thread(name=f'main_{name}', target=func, args=args, kwargs=kwargs)
                t.start()
                t.join()
                if cell.status != 'done':
                    cell.status = 'auto_done'
            except Exception as e:
                log.error(f'Error in main_{name}: {e.with_traceback()}')
                cell.status = 'error'
            cell.join()
        return wrapper
    return decorator
