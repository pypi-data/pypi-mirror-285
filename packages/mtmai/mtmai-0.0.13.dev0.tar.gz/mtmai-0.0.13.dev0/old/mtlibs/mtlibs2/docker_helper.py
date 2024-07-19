import os
import tarfile
from io import BytesIO
from pathlib import Path
# import docker
import tar_helper


def isInContainer():
    return os.path.exists("/.dockerenv")

def is_docker():
    cgroup = Path("/proc/self/cgroup")
    return Path('/.dockerenv').is_file() or cgroup.is_file() and cgroup.read_text().find("docker") > -1

def copy_dir(container, local_dir, container_dir):
    """ 将本地文件或文件夹打包复制到容器内
        : container 容器实例
        : local_dir 本地文件夹路径
        : container_dir 容器文件夹路径F
    """
    bytesObj = BytesIO()
    tar_helper.tarFolder(local_dir, bytesObj)
    bytesObj.seek(0)
    # 参考:https://gist.github.com/michaelconnor00/b3c332a2d6b70f6443d33459d3a731aa
    container.exec_run("mkdir {}/".format(container_dir))
    container.put_archive(container_dir, bytesObj.getvalue())


def copy_file(container, targetPath, bytes):
    """
        将二进制文件写入容器
        : targetPath : 容器内的绝对路径

        注意,目前只支持单文件, 如果需要同时传多个文件,可以变通为先打包为tar,传上去后自己解压.
    """
    _parent_dir = str(Path(targetPath).parent)
    _file_name = Path(targetPath).name

    # 创建文件夹
    container.exec_run("mkdir {}".format(_parent_dir))

    bytesObj = BytesIO()
    tar_obj = tarfile.TarFile(fileobj=bytesObj, mode='w')
    tarinfo = tarfile.TarInfo(name=_file_name)
    tarinfo.size = len(bytes)
    # 可以设置文件的其他属性
    # tarinfo.mtime = time.time()
    # tarinfo.mode = 0600
    tar_obj.addfile(tarinfo, BytesIO(bytes))
    bytesObj.seek(0)

    container.put_archive(_parent_dir, bytesObj.getvalue())
