import sys,os,time
import asyncio
import logging
import shlex
import subprocess
import threading

logger = logging.getLogger(__name__)


def process_output(process):
    while True:
        output = process.stdout.readline().decode()
        if process.poll() is not None:
            break
        if output:
            print(output, flush=True)


def process_output_threadhandler(process):
    """用线程的方式将进程的输出显示到终端上"""

    def _handler(process):
        while True:
            result = process.poll()
            if result is not None:
                print(f'进程结束:{result}')
                break
            else:
                output = process.stdout.readline().decode()
                if output:
                    print(output.rstrip(), flush=True)
                if process.stderr:
                    err = process.stderr.readline().decode()
                    if err:
                        print(f"stderr, {err}", flush=True)

    threading.Thread(target=_handler, args=(process, )).start()


def exec_cmd(cmd):
    """
        助手函数, 启动系统进程,并直接从sys.stdout 回显
    """

    def handle_output(process):
        while True:
            output = process.stdout.readline().decode()
            if process.poll() is not None:
                break
            if output:
                logger.info(output)
                # sys.stdout.flush()

    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
    threading.Thread(target=handle_output, args=(process, )).start()


def exec_cmd2(cmd, output_file="/var/log/clilog.log"):
    """
        助手函数, 启动系统进程,并将进程的输出写入到文件中
        TODO: 应该升级为流模式, 这样就不用关日志是不是文件,可以使用StringIO
    """

    def handle_output(process):
        try:
            with open(output_file, 'ab+') as logfile:
                while True:
                    if process.stdout:
                        bytes = process.stdout.read()
                        logfile.write(bytes)
                        logfile.flush()
                    if process.stderr:
                        bytes = process.stderr.read()
                        logfile.write(bytes)
                        logfile.flush()

                    if process.poll() is not None:
                        break
        except Exception as e:
            print(e)

    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
    threading.Thread(target=handle_output, args=(process, )).start()


def exec(cmd, check=True):
    """
    执行命令,并返回命令的输出作为返回值
    如果命令执行失败,会抛出异常
    """
    logger.info("exec>{}".format(cmd))
    # print("exec env:")
    # print(os.environ)
    return subprocess.run(shlex.split(cmd), check=check, env=os.environ)


def bash(shelltext):
    """
    运行shell脚本并，等到进程结束后，返回执行结果
    说明： 推荐使用异步的方式，本函数是同步的方式，感觉有点不方便。
    """
    proc = subprocess.Popen(shlex.split("bash -"),
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    # communicate 会等待执行完毕,获取stdout,和 stderr
    return proc.communicate(input=shelltext.encode())


async def subprocess_shell(script):
    """以异步的方式运行shell"""
    # logger.info("[subprocess_shell 开始]")
    proc = await asyncio.create_subprocess_shell(
        script,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)
    # 循环读取，能达到效果，更高级的写法是使用protocol
    # 参考：http://songcser.github.io/2017/10/26/working-with-subprocesses/
    line = await proc.stdout.readline()
    while line:
        logger.info(line.decode().strip())
        line = await proc.stdout.readline()


def is_tool(name):
    """Check whether `name` is on PATH."""
    from distutils.spawn import find_executable
    return find_executable(name) is not None
