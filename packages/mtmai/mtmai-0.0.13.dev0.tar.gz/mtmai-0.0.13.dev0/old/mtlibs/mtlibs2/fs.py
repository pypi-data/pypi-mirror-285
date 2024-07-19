import os
import sys
from time import sleep

from beeprint import pp

# ########################################################################################################
# 此版本还在设计中。
# 目的是提供一个统一的文件系统，文件系统应该能兼容云端S3之类的。
# 那么，对于本地的文件处理，应该有唯一的根目录。这样好方便同一处理，备份，同步等问题。
# 初步的编程想法：
#         看是否有合适的第三方库。
#         看是否合适使用 provider 模式

# 文件系统跟目录
LOCAL_ROOT = "/mtcli/data"


def writeText(filepath):
    """写入文件"""
    open(filepath, 'w')


def get_filepaths_by_walk(basedir, curr_dir=None, result=set()):
    if not curr_dir:
        curr_dir = basedir
    # print(f"curr_dir {curr_dir}")
    curr_dir = (curr_dir + "/").replace("//", "/")

    if not os.path.isdir(curr_dir):
        return
    dirlist = os.walk(curr_dir)
    for parent_dir, dirs, files in dirlist:
        for file in files:
            # print(os.path.join(root, file))
            result.add(os.path.join(parent_dir, file)[len(basedir) + 1:])
        for _dir in dirs:
            # print(f"_dir: {_dir}")
            next = os.path.join(curr_dir, _dir)
            # print(f"遍历下级：{next}")
            # sleep(1)
            get_filepaths_by_walk(basedir, next, result)

    return result
