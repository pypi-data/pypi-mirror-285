#!/usr/bin/env python3

import os
import sys
import re
from version_parser import Version
from pathlib import Path
import shutil
from dotenv import load_dotenv, find_dotenv
import  argparse

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

load_dotenv(".env")

import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def credential():        
    pypirc = os.path.join(os.path.expanduser("~"),".pypirc")
    if Path(pypirc).exists():
        logger.info(f"file: {pypirc} exists,skip config pypirc")
    else:
        pypi_username = os.environ.get("PYPI_USERNAME")
        pypi_password = os.environ.get("PYPI_PASSWORD")
        
        logger.error(f"need PYPI_USERNAME and PYPI_PASSWORD env")
        content = f"""[pypi]
username:{pypi_username}
password:{pypi_password}"""
        # path = os.path.join(os.path.expanduser("~"),".pypirc")
        
        with open(pypirc,"w") as fd:
            fd.write(content)
                
# def version_patch(package_dir="."):        
#     init_py_path = os.path.join(os.getcwd(),package_dir,"__init__.py")
#     logger.info(f"init_py_path: {init_py_path}")
#     version = "0.0.1"
#     search=None
#     with open(init_py_path, 'r') as fd:
#         search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
#                             fd.read(), re.MULTILINE)
        

#         if search:
#             version = search.group(1)
#             v1 = Version(version)
#             build_version = int(v1.get_build_version()) +1
#             newVersion = f"{v1.get_major_version()}.{v1.get_minor_version()}.{build_version}"
#             logger.info(f"new version: {newVersion}")
#             with open(init_py_path, 'w') as fd:
#                 fd.write(f"""__version__="{newVersion}" """)
#         else:
#             raise Exception(f"文件:{init_py_path},中没有版本相关字段")


def version_patch(package_dir="."):        
    init_py_path = os.path.join(os.getcwd(),package_dir,"version.txt")
    logger.info(f"init_py_path: {init_py_path}")
    
    version = '0.0.1'
    with open(init_py_path, "r") as fd:
        version = fd.read()
    v1 = Version(version)
    build_version = int(v1.get_build_version()) +1
    newVersion = f"{v1.get_major_version()}.{v1.get_minor_version()}.{build_version}"
    logger.info(f"新版本号：{newVersion}")
    with open(init_py_path, "w") as fd:
        fd.write(newVersion)


def clear_dist(package_dir="."):
    dist_dir = os.path.join(os.getcwd(),"dist")
    logger.info(f"dist_dir: {dist_dir}")
    if Path(dist_dir).exists():        
        shutil.rmtree(dist_dir)
        
def clear_build(package_dir="."):
    build_dir = os.path.join(os.getcwd(),"build")
    logger.info(f"build_dir: {build_dir}")
    if Path(build_dir).exists():        
        shutil.rmtree(build_dir)
        
def sub_publish_pypi(args):
    """
        用于二进制包发布到可自由下载的公网地址。
        目前仅支持python setuptools 的方式，
        打算后续支持npm , docker hub 等方式。
    """
    target_dir = getattr(args,"dir") if hasattr(args,"dir") else "."    
    logger.info(f"目标目录：{target_dir}")          

    credential()
    for sub_dir in target_dir:
        logger.info(f"开始处理{sub_dir}")
        version_patch(sub_dir)
        clear_dist(sub_dir)
        clear_build(sub_dir)
        os.system(f"""python3 {sub_dir}/setup.py bdist_wheel""")
        print("上传")
        os.system(f"""twine upload dist/*""")
    
    
app_name = "mtxcli"
def main():    
    parser = argparse.ArgumentParser(description="%s service" % app_name)
    # subparsers = parser.add_subparsers(help="%s service" % app_name)
    # sub agent
    # sub_agent = subparsers.add_parser('agent', help='mtxp agent')
    # sub_agent.set_defaults(func=sub_publish_pypi)
    # parser.add_argument('--dir')
    parser.add_argument('dir',default=".", nargs="*")       
    #设置默认函数
    parser.set_defaults(func=sub_publish_pypi)
    args = parser.parse_args()
    #执行函数功能
    args.func(args)
    
if __name__ == "__main__":
    main()