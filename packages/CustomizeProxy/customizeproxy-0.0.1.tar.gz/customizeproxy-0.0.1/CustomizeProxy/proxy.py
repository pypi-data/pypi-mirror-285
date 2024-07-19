import mitmproxy.http
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.options import Options,Optional
import asyncio
import subprocess
import os
import ctypes
import sys
import mitmproxy

def get_certificate_serial_number(cert_path):
    """获取证书序列号"""
    try:
        result = subprocess.run(
            ['certutil', '-dump', cert_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if '序列号:' in line:
                    return line.split('序列号:')[1].strip()
                elif  'Serial Number:' in line:
                    return line.split('Serial Number:')[1].strip()
    except Exception as e:
        return False
    
def is_certificate_installed(serial_number):
    """检查证书指纹是否在受信任的根证书颁发机构中"""
    try:
        result = subprocess.run(
            ['certutil', '-store', 'root'], 
            capture_output=True, 
            text=True
        )
        return serial_number in result.stdout
    except subprocess.CalledProcessError as e:
        return False

def delete_certificate(serial_number):
    """通过证书序列号删除根证书"""
    try:
        # 使用certutil删除证书
        result = subprocess.run(
            ['certutil', '-delstore', 'root', serial_number],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            if '正在删除证书' in result.stdout:
                return True
        return False
    except subprocess.CalledProcessError as e:
        return False

def add_certificate(cert_path):
    """添加证书到根"""
    try:
        # 使用certutil删除证书
        result = subprocess.run(
            ['certutil', '-addstore', 'root', cert_path],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            if '添加到存储' in result.stdout:
                return True
        elif result.returncode == 2147943140:
            if '使用选择的选项需要管理员权限' in result.stdout:
                raise Exception('需要管理员权限')
        return False
    except subprocess.CalledProcessError as e:
        return False

def check(cert_path):
    """检查是否已经安装该根证书

    Args:
        cert_path (_type_): 证书路径

    Returns:
        _type_: 序列号 or False
    """    
    # 获取证书的序列号
    serial_number = get_certificate_serial_number(cert_path)
    if serial_number:
        # 检查是否已经安装该证书
        if is_certificate_installed(serial_number):
            return serial_number
        return False
    else:
        return False

# 定义证书路径和 certutil 命令
Confdir = os.path.join(os.getcwd(), "config")
cert_path = os.path.join(Confdir, "mitmproxy-ca-cert.cer")
addons = [] # 用于添加拦截链路的对象


async def _onece(confdir):
    global addons,cert_path
    # 安装证书
    if os.path.exists(cert_path):
        serial_number = check(cert_path)
        if serial_number == False:
            add_certificate(cert_path)
            print("安装证书完毕")
        else:
            print("证书已经安装")
    else:
        options =  Options(confdir=confdir)
        dm = DumpMaster(options)
        dm.addons.add(*addons)
        await dm.running()
        print("证书下载完毕，下一步执行安装证书")
        await _onece(confdir)

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    
def init(confdir = None,cert_name = None):
    global Confdir,cert_path
    if confdir is None:
        confdir = Confdir
    else:
        Confdir = confdir
    if cert_name:
        cert_path = os.path.join(confdir, cert_name)
    asyncio.run(_onece(confdir))
    
    
async def _run(mode):
    global addons,Confdir
    options =  Options(mode=mode, confdir=Confdir)
    dm = DumpMaster(options)
    dm.addons.add(*addons)
    await dm.run()

def exec_listening(mode:list = ['local'], confdir = None, cert_name = None, show = 1):
    if is_admin():
        init(confdir, cert_name)
        asyncio.run(_run(mode))
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, '"{}"'.format(sys.argv[0]), None, show)

class HTTPInterceptor:

    def load(self, loader):
        loader.add_option(
            name="validate_inbound_headers",
            typespec=Optional[bool],
            default=False,
            help="Validate inbound HTTP headers. (default: False)",
        ) # 不检查请求头格式

    def request(self, flow: mitmproxy.http.HTTPFlow):
        print("拦截:",flow.server_conn.address)

if __name__ == "__main__":
    addons.append(HTTPInterceptor())
    exec_listening()
