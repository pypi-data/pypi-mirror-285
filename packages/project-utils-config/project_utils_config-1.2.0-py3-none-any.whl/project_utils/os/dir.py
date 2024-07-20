import os

from pathlib import Path


def mkdir(path: str) -> bool:
    try:
        os.mkdir(path)
    except:
        return False
    else:
        return True


def remove(path: str):
    def remove_inner(p: str):
        try:
            os.remove(p)
        except:
            pass

    # 如果被删除的路径是文件夹
    if os.path.isdir(path):
        # 文件夹不为空
        if len(os.listdir(path)) > 0:
            for file in os.listdir(path):
                # 删除文件夹内部的文件
                remove_inner(os.path.join(path, file))
    # 删除操作
    remove_inner(path)


def is_empty(path: str) -> int:
    if len(os.listdir(path)) > 0:
        return len(os.listdir(path))
    else:
        return 0
