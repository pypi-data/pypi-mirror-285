import os
import sys 
import re

#print("load os")

Stdin = sys.stdin
Stdout = sys.stdout

def Touch(path:str):
    from pathlib import Path
    Path(path).touch()

def Chdir(path:str):
    os.chdir(path)

def Exit(num:int=0):
    sys.exit(num)

def System(cmd:str) -> int:
    import subprocess
    return subprocess.call(cmd, stderr=sys.stderr, stdout=sys.stdout, shell=True)

def Mkdir(*path:str):
    for p in path:
        os.makedirs(p, exist_ok=True)

def ListDir(path:str=".") -> list[str]:
    return os.listdir(path)

def ListFiles(path:str) -> list[str]:
    import glob
    return glob.glob(path)

Args = sys.argv 

def Getenv(varname:str, defaultValue:str=None) -> str | None:
    v = os.environ.get(varname)
    if not v:
        return defaultValue
    else:
        return v

def Getcwd() -> str:
    return os.getcwd()

def Unlink(path:str):
    import shutil
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

def Move(src:str, dst:str, force:bool=True):
    import shutil
    if os.path.exists(dst):
        if not os.path.isdir(dst):
            if not force:
                raise Exception("目标已存在")
            else:
                os.unlink(dst)
        else:
            dst = os.path.join(dst, os.path.basename(src))

    ddir = os.path.dirname(dst)
    if ddir != "":
        if not os.path.exists(ddir):
            Mkdir(ddir)
    
    shutil.move(src, dst)

def Copy(src:str, dst:str, force:bool=True):
    import shutil
    if os.path.exists(dst):
        if not os.path.isdir(dst):
            if not force:
                raise Exception("目标已存在")
            else:
                os.unlink(dst)
        else:
            dst = os.path.join(dst, os.path.basename(src))
    
    ddir = os.path.dirname(dst)
    if ddir != "":
        if not os.path.exists(ddir):
            Mkdir(ddir)
    
    shutil.copy2(src, dst)

def GetLoginUserName() -> str:
    return os.getlogin()

def Walk(path:str, type:str=None) -> str:
    """
    Walk through a directory and yield the names.
    
    :param path: The path to the directory you want to walk
    :type path: str
    :param type: The type of file you want to search for. "d" for directory and "f" for file, None(default) for all
    :type type: str
    """
    for root, dirs, files in os.walk(path, topdown=False):
        if type == None:
            for name in files:
                yield os.path.join(root, name)
            for name in dirs:
                yield os.path.join(root, name)
        elif type == "f":
            for name in files:
                yield os.path.join(root, name)
        elif type == "d":
            for name in dirs:
                yield os.path.join(root, name)

def GetUID() -> int:
    return os.getuid()

def GetCurrentThreadID() -> str:
    import threading
    import multiprocessing
    return multiprocessing.current_process().name.replace("Process-", "P").replace("MainProcess", "MP") + re.sub("\([a-zA-Z0-9]+\)", "", threading.current_thread().name.replace("Thread-", "T").replace(" ", "").replace("MainThread", "MT")) 

def GetIPByInterface(interface:str) -> str:
    import psutil
    import socket

    addrs = psutil.net_if_addrs()
    if interface in addrs:
        for addr in addrs[interface]:
            if addr.family == socket.AF_INET:  # 使用 socket.AF_INET
                return addr.address
            
    raise Exception("No IP address found for this interface")

if __name__ == "__main__":
    # Move("a", "b") # 移动当前目录的a到b
    # Move("b", "c/d/e") # 移动b到c/d/e, 会先递归创建目录c/d
    # Move("c/d/e", "d") # 移动c/d/e文件到d目录, 没有指定文件名就自动使用原来的文件名
    for i in Walk(".", type="d"):
        print(i)