import shutil
import warnings
from collections.abc import Iterator
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

from frykit._typing import PathType


def new_dir(dirpath: PathType) -> Path:
    '''新建目录'''
    dirpath = Path(dirpath)
    if not dirpath.exists():
        dirpath.mkdir(parents=True)

    return dirpath


def del_dir(dirpath: PathType) -> Path:
    '''删除目录。目录不存在时会报错。'''
    dirpath = Path(dirpath)
    shutil.rmtree(str(dirpath))

    return dirpath


def renew_dir(dirpath: PathType) -> Path:
    '''重建目录'''
    dirpath = Path(dirpath)
    if dirpath.exists():
        shutil.rmtree(str(dirpath))
    dirpath.mkdir(parents=True)

    return dirpath


def split_list(lst: list, n: int) -> Iterator[list]:
    '''将列表尽量等分为 n 份'''
    size, rest = divmod(len(lst), n)
    start = 0
    for i in range(n):
        step = size + 1 if i < rest else size
        stop = start + step
        yield lst[start:stop]
        start = stop


# TODO: 低版本 shapely 的几何对象
def is_sequence(obj: Any) -> bool:
    '''判断是否为序列'''
    if isinstance(obj, str):
        return False

    try:
        len(obj)
    except Exception:
        return False

    return True


def to_list(obj: Any) -> list:
    '''将对象转为列表'''
    if is_sequence(obj):
        return list(obj)
    return [obj]


class DeprecationError(Exception):
    pass


def deprecator(
    new_func: Optional[Callable], raise_error: bool = False
) -> Callable:
    '''提示弃用的装饰器'''

    def decorator(old_func: Callable) -> Callable:
        info = f'{old_func.__name__} is deprecated'
        if new_func is not None:
            info += f', use {new_func.__name__} instead'

        @wraps(old_func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if raise_error:
                raise DeprecationError(info)
            warnings.warn(info, DeprecationWarning, stacklevel=2)
            result = old_func(*args, **kwargs)
            return result

        return wrapper

    return decorator
