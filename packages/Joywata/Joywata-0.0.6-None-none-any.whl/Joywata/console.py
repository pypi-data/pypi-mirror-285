import os
from tabulate import tabulate
import sys
from pathlib import Path

def wata_list(argv):
    assert argv.__len__() == 2, 'error command'
    table_list = [
        ['终端命令', '功能'],
        ['wata', 'Hello JOYWATA !'],
        ['wata list', '列出wata终端命令'],
        ['wata install', '用清华源安装包'],
        ['wata uninstall', '卸载python包'],
        ['wata unzip', 'ubuntu解压文件'],
        ['wata show_size', 'ubuntu查看子目录的大小'],
        ['wata conda rm <env>', '删除conda中的env环境'],
        ['wata cuda list', '列出ubuntu系统中已安装的cuda版本'],
        ['wata tmux', '刷新tmux窗口'],

    ]
    print(tabulate(table_list, headers='firstrow', tablefmt='grid'))


def pip_install_by_tsinghua(argv):
    assert argv.__len__() > 2

    package = ''
    len_pack = argv.__len__()
    for i in range(2, len_pack):
        package = package + argv[i] + ' '
    if argv[1] =="install":
        print("pip install "+ package + "-i https://pypi.tuna.tsinghua.edu.cn/simple/")
        os.system("pip install " + package + "-i https://pypi.tuna.tsinghua.edu.cn/simple/")
    elif argv[1] == "uninstall":
        print("pip uninstall " + package)
        os.system("pip uninstall " + package)


def conda_cmd(argv):
    assert argv.__len__() > 3
    if argv[2] == "rm":
        print("conda rm " + argv[-1] + " --all")
        os.system("conda remove -n " + argv[-1] + " --all")


def unzip(argv):
    user = '' if argv[1] == 'unzip' else 'sudo '
    assert argv.__len__() > 2
    zip_file = argv[2]
    zip_ext = Path(zip_file).suffix[1:]
    print(zip_ext)
    if zip_ext == "zip":
        print(user + "unzip " + zip_file)
        os.system(user + "unzip " + zip_file)
    elif zip_ext == "tar":
        print(user + "tar -xvf " + zip_file)
        os.system(user + "tar -xvf " + zip_file)
    elif zip_ext == "tgz":
        print(user + "tar -xzvf " + zip_file)
        os.system(user + "tar -xzvf " + zip_file)
    elif zip_file.split(".")[-1] == "gz" and zip_file.split(".")[-2] == "tar":
        print(user + "tar -zxvf " + zip_file)
        os.system(user + "tar -zxvf " + zip_file)
    elif zip_file.split(".")[-1] == "xz" and zip_file.split(".")[-2] == "tar":
        print(user + "tar -xvf " + zip_file)
        os.system(user + "tar -xvf " + zip_file)
    else:
        print('Unable to decompress the file type temporarily')

def wata_console():
    if sys.argv.__len__() == 1:
        print("Hello JOYWATA !")
        print('Enter "wata list" to view the function')
        return None

    cmd = sys.argv[1]
    if cmd == 'install' or cmd == 'uninstall':
        pip_install_by_tsinghua(sys.argv)
        return None

    if cmd == 'install' or cmd == 'uninstall':
        pip_install_by_tsinghua(sys.argv)
        return None

    elif cmd == 'unzip' or (cmd == 'sudo' and sys.argv[2] == 'unzip'):
        unzip(sys.argv)
        return None

    elif cmd == 'list':
        wata_list(sys.argv)
        return None

    elif cmd == 'show_size':
        os.system("sudo du -h --max-depth=1")
        return None

    elif cmd == 'cuda':
        os.system("ls /usr/local/ | grep ^cuda-")
        return None

    elif cmd == 'conda':
        conda_cmd(sys.argv)
        return None

    elif cmd == 'tmux':
        conda_cmd("tmux detach -a")
        return None

    else:
        print("error command")


