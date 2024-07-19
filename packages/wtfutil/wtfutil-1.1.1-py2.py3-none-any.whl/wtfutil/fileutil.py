import hashlib
import json
import os
from pathlib import Path
from typing import Union


def file_md5(file_path) -> str:
    md5lib = hashlib.md5()
    with open(file_path, 'rb') as f:
        md5lib.update(f.read())
    return md5lib.hexdigest()


def file_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        sha1.update(f.read())
    return sha1.hexdigest()


def file_sha256(file_path):
    sha1 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        sha1.update(f.read())
    return sha1.hexdigest()

def list_files(directory):
    """List all files in a directory."""
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

def list_directories(directory):
    """List all directories in a directory."""
    return [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]

def touch(filepath, mode=0o666, exist_ok=True):
    return Path(filepath, mode=mode, exist_ok=exist_ok).touch()


def read_text(filepath: Union[Path, str], mode='r', encoding='utf-8', not_exists_ok: bool = False, errors=None) -> str:
    """
    errors-->
    'ignore'：忽略无法解码的字符。直接跳过无法处理的字符，继续解码其他部分。
    'replace'：使用特定字符替代无法解码的字符，默认使用 '�' 代替。例如，b'\xe4\xb8\x96\xe7\x95\x8c'.decode('utf-8', errors='replace') 输出 '世界�'。
    'strict'：默认行为，如果遇到无法解码的字符，抛出 UnicodeDecodeError 异常。
    'backslashreplace'：使用 Unicode 转义序列替代无法解码的字符。例如，b'\xe4\xb8\x96\xe7\x95\x8c'.decode('ascii', errors='backslashreplace') 输出 '\\xe4\\xb8\\x96\\xe7\\x95\\x8c'。
    'xmlcharrefreplace'：使用 XML 实体替代无法解码的字符。例如，b'\xe4\xb8\x96\xe7\x95\x8c'.decode('ascii', errors='xmlcharrefreplace') 输出 '&#19990;&#30028;'。
    'surrogateescape'：将无法解码的字节转换为 Unicode 符号 '�' 的转义码。例如，当解码 Latin-1 字符串时，b'\xe9'.decode('latin-1', errors='surrogateescape') 输出 '\udce9'。
    """
    if isinstance(filepath, Path):
        filepath = str(filepath)
    if mode == 'rb':
        encoding = None
    if not_exists_ok and not Path(filepath).is_file():
        return ''
    with open(filepath, mode, encoding=encoding, errors=errors) as f:
        content = f.read()
    return content


def read_json(filepath: Union[Path, str], encoding='utf-8', not_exists_ok: bool = False) -> dict:
    if isinstance(filepath, Path):
        filepath = str(filepath)
    if not_exists_ok and not Path(filepath).is_file():
        return {}
    with open(filepath, 'r', encoding=encoding) as f:
        return json.load(f)


def read_lines(filepath: Union[Path, str], encoding='utf-8', not_exists_ok: bool = False) -> list:
    if isinstance(filepath, Path):
        filepath = str(filepath)
    lines = []
    if not_exists_ok and not Path(filepath).is_file():
        return lines
    with open(filepath, 'r', encoding=encoding) as f:
        # lines = f.readlines()
        # lines = [line.rstrip() for line in lines]  只会创建一个生成器 不会有性能问题
        for line in f:
            line = line.rstrip()
            if line:
                lines.append(line)
    return lines


def write_text(filepath: Union[Path, str], content, mode='w', encoding='utf-8'):
    if isinstance(filepath, Path):
        filepath = str(filepath)
    if mode == 'wb':
        encoding = None
    if content is None:
        raise ValueError('content must not be None')
    with open(filepath, mode, encoding=encoding) as f:
        f.write(content)


def write_lines(filepath: Union[Path, str], lines, mode='w', encoding='utf-8'):
    if isinstance(filepath, Path):
        filepath = str(filepath)
    if lines is None:
        raise ValueError('lines must not be None')
    with open(filepath, mode, encoding=encoding) as f:
        for l in lines:
            f.write(l + '\n')


def write_json(filepath: Union[Path, str], json_obj: dict, encoding='utf-8'):
    if isinstance(filepath, Path):
        filepath = str(filepath)
    if json_obj is None:
        raise ValueError('json_obj must not be None')
    with open(filepath, 'w', encoding=encoding) as f:
        json.dump(json_obj, f, indent=4, ensure_ascii=False)