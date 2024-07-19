"""
BASH like tools

I have included debug logging in order to support
clean deployment script support

@author: jldupont
"""
import os
import shutil
import logging
from pathlib import Path

debug = logging.debug


def ls(path: str = ".", stdout: bool = True):
    assert isinstance(path, str)
    result = os.listdir(path)
    if stdout:
        print(result)
    return result


def cd(path):
    assert isinstance(path, str)
    debug(f"cd({path})")
    os.chdir(path)


def mkdir(path: str, parents: bool = True, exist_ok: bool = True):
    assert isinstance(path, str)
    debug(f"mkdir({path})")
    p: Path = Path(path)
    p.mkdir(parents=parents, exist_ok=exist_ok)


def cp(src: str, dst: str):
    assert isinstance(src, str)
    assert isinstance(dst, str)
    debug(f"cp({src}, {dst})")
    shutil.copy2(src, dst)


def cptree(src: str, dst: str, dirs_exist_ok: bool = True):
    assert isinstance(src, str)
    assert isinstance(dst, str)
    debug(f"cptree({src}, {dst})")
    shutil.copytree(src, dst, dirs_exist_ok=dirs_exist_ok)
