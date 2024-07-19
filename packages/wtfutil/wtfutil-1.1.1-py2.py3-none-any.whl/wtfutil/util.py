from functools import wraps
import sys
import os
from pathlib import Path
import queue
import datetime
import time
from typing import Any, Dict, Iterable
from .strutil import *
from .fileutil import *
from .httputil import *


class UniqueQueue(queue.Queue):
    def __init__(self, maxsize=0):
        super().__init__(maxsize)
        self.queue_set = set()

    def put(self, item, block=True, timeout=None):
        """
        一个对象重复put将会忽略
        """
        hash_item = item
        if isinstance(item, dict):
            hash_item = tuple(item.items())
        if hash_item not in self.queue_set:  # 如果元素不在队列中，则添加
            self.queue_set.add(hash_item)
            super().put(item, block, timeout)


def measure_time(func):
    """Measure and print the execution time of a function.
    记录函数执行时间"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds")
        return result
    return wrapper


def unique_items(iterable: Iterable) -> list:
    """Return unique items from an iterable while preserving order.
    列表去重"""
    seen = set()
    return [x for x in iterable if x not in seen and not seen.add(x)]


def group_by_key(items: Iterable[Dict[str, Any]], key: str) -> Dict[Any, list]:
    """Group a list of dictionaries by a specific key.
    列表分组"""
    grouped = {}
    for item in items:
        grouped.setdefault(item[key], []).append(item)
    return grouped


def current_datetime():
    """Get the current date and time."""
    return datetime.datetime.now()

def format_datetime(dt: datetime, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format a datetime object as a string."""
    return dt.strftime(format)

def parse_datetime(date_string: str, format: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    """Parse a datetime string into a datetime object."""
    return datetime.datetime.strptime(date_string, format)


def cut_list(obj, size):
    return [obj[i:i + size] for i in range(0, len(obj), size)]



def get_resource_dir(basedir=None):
    if not basedir:
        basedir = sys._getframe(1).f_code.co_filename
    current_dir = resource_folder = getattr(sys, '_MEIPASS', os.path.dirname(basedir))

    while True:
        resource_folder = os.path.join(current_dir, "resource")

        if os.path.exists(resource_folder) and os.path.isdir(resource_folder):
            break

        # 到达根目录 (盘符根目录) 时停止搜索
        if len(current_dir) <= 3:
            break

        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

    return resource_folder


def get_resource(filename):
    if Path(filename).exists():
        return filename
    resource_path = get_resource_dir(sys._getframe(1).f_code.co_filename) + "/" + filename
    if Path(resource_path).exists():
        return str(Path(resource_path).absolute())
    if Path('~/'+filename).expanduser().exists():
        return str(Path('~/'+filename).expanduser().absolute())

