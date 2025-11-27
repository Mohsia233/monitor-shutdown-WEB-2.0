import psutil
from flask import Flask, render_template, jsonify, send_from_directory
import os
import platform
import socket
import threading
import time
from datetime import datetime

app = Flask(__name__)

# 定义端口
PORT = 8097

def get_system_info():
    """获取系统资源使用情况"""
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    mem_total = round(mem.total / (1024 ** 3), 2)  # GB
    mem_used = round(mem.used / (1024 ** 3), 2)    # GB
    
    # 获取网络信息
    net_io = psutil.net_io_counters()
    net_sent = round(net_io.bytes_sent / (1024 ** 2), 2)  # MB
    net_recv = round(net_io.bytes_recv / (1024 ** 2), 2)  # MB
    
    return {
        "cpu": cpu_percent,
        "mem": mem_percent,
        "mem_used": mem_used,
        "mem_total": mem_total,
        "net_sent": net_sent,
        "net_recv": net_recv,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

@app.route('/')
def index():
    # 直接渲染模板，不传递访问地址
    return render_template('index.html')

@app.route('/system-data')
def system_data():
    return jsonify(get_system_info())

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 1")
        return "关机命令已发送"
    else:
        return "此功能仅支持Windows系统"

@app.route('/restart', methods=['POST'])
def restart():
    if platform.system() == "Windows":
        os.system("shutdown /r /t 1")
        return "重启命令已发送"
    else:
        return "此功能仅支持Windows系统"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def print_access_info():
    """打印访问信息到控制台"""
    time.sleep(1)  # 等待服务器启动
    
    print("\n" + "="*70)
    print("🚀 系统监控面板已启动！")
    print("="*70)
    
    # 获取所有IP地址（只在控制台显示）
    ips = []
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if (ip != '127.0.0.1' and 
                        not ip.startswith('169.254.') and
                        not ip.startswith('172.17.') and
                        not interface.startswith('vEthernet')):
                        if ip not in ips:
                            ips.append(ip)
    except:
        ips = []
    
    print("📡 本地访问地址：")
    print(f"   • http://localhost:{PORT}")
    print(f"   • http://127.0.0.1:{PORT}")
    
    if ips:
        print("\n🌐 网络访问地址：")
        for ip in ips:
            print(f"   • http://{ip}:{PORT}")
    
    print("\n💡 使用说明：")
    print("   1. 在同一网络下的其他设备浏览器中打开任一网络地址")
    print("   2. 首次运行可能需要允许防火墙访问")
    print("   3. 按 Ctrl+C 停止服务")
    print("="*70)
    print("⏰ 服务启动时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("📊 监控端口:", PORT)
    print("="*70 + "\n")

if __name__ == '__main__':
    # 在后台线程中打印访问信息
    url_thread = threading.Thread(target=print_access_info)
    url_thread.daemon = True
    url_thread.start()
    
    try:
        # 在所有网络接口上启动服务
        print("🔄 启动系统监控服务...")
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
