#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare SpeedTest 跨平台自动化脚本
支持 Windows、Linux、macOS (Darwin)
支持完整的 Cloudflare 数据中心机场码映射
"""

import os
import sys
import platform
import subprocess
import requests
import json
import csv
from pathlib import Path


# Cloudflare 数据中心完整机场码映射
# 数据来源：Cloudflare 官方数据中心列表
AIRPORT_CODES = {
    # 亚太地区 - 中国及周边
    "HKG": {"name": "香港", "region": "亚太", "country": "中国香港"},
    "TPE": {"name": "台北", "region": "亚太", "country": "中国台湾"},
    
    # 亚太地区 - 日本
    "NRT": {"name": "东京成田", "region": "亚太", "country": "日本"},
    "KIX": {"name": "大阪", "region": "亚太", "country": "日本"},
    "ITM": {"name": "大阪伊丹", "region": "亚太", "country": "日本"},
    "FUK": {"name": "福冈", "region": "亚太", "country": "日本"},
    
    # 亚太地区 - 韩国
    "ICN": {"name": "首尔仁川", "region": "亚太", "country": "韩国"},
    
    # 亚太地区 - 东南亚
    "SIN": {"name": "新加坡", "region": "亚太", "country": "新加坡"},
    "BKK": {"name": "曼谷", "region": "亚太", "country": "泰国"},
    "HAN": {"name": "河内", "region": "亚太", "country": "越南"},
    "SGN": {"name": "胡志明市", "region": "亚太", "country": "越南"},
    "MNL": {"name": "马尼拉", "region": "亚太", "country": "菲律宾"},
    "CGK": {"name": "雅加达", "region": "亚太", "country": "印度尼西亚"},
    "KUL": {"name": "吉隆坡", "region": "亚太", "country": "马来西亚"},
    "RGN": {"name": "仰光", "region": "亚太", "country": "缅甸"},
    "PNH": {"name": "金边", "region": "亚太", "country": "柬埔寨"},
    
    # 亚太地区 - 南亚
    "BOM": {"name": "孟买", "region": "亚太", "country": "印度"},
    "DEL": {"name": "新德里", "region": "亚太", "country": "印度"},
    "MAA": {"name": "金奈", "region": "亚太", "country": "印度"},
    "BLR": {"name": "班加罗尔", "region": "亚太", "country": "印度"},
    "HYD": {"name": "海得拉巴", "region": "亚太", "country": "印度"},
    "CCU": {"name": "加尔各答", "region": "亚太", "country": "印度"},
    
    # 亚太地区 - 澳洲
    "SYD": {"name": "悉尼", "region": "亚太", "country": "澳大利亚"},
    "MEL": {"name": "墨尔本", "region": "亚太", "country": "澳大利亚"},
    "BNE": {"name": "布里斯班", "region": "亚太", "country": "澳大利亚"},
    "PER": {"name": "珀斯", "region": "亚太", "country": "澳大利亚"},
    "AKL": {"name": "奥克兰", "region": "亚太", "country": "新西兰"},
    
    # 北美地区 - 美国西海岸
    "LAX": {"name": "洛杉矶", "region": "北美", "country": "美国"},
    "SJC": {"name": "圣何塞", "region": "北美", "country": "美国"},
    "SEA": {"name": "西雅图", "region": "北美", "country": "美国"},
    "SFO": {"name": "旧金山", "region": "北美", "country": "美国"},
    "PDX": {"name": "波特兰", "region": "北美", "country": "美国"},
    "SAN": {"name": "圣地亚哥", "region": "北美", "country": "美国"},
    "PHX": {"name": "凤凰城", "region": "北美", "country": "美国"},
    "LAS": {"name": "拉斯维加斯", "region": "北美", "country": "美国"},
    
    # 北美地区 - 美国东海岸
    "EWR": {"name": "纽瓦克", "region": "北美", "country": "美国"},
    "IAD": {"name": "华盛顿", "region": "北美", "country": "美国"},
    "BOS": {"name": "波士顿", "region": "北美", "country": "美国"},
    "PHL": {"name": "费城", "region": "北美", "country": "美国"},
    "ATL": {"name": "亚特兰大", "region": "北美", "country": "美国"},
    "MIA": {"name": "迈阿密", "region": "北美", "country": "美国"},
    "MCO": {"name": "奥兰多", "region": "北美", "country": "美国"},
    
    # 北美地区 - 美国中部
    "ORD": {"name": "芝加哥", "region": "北美", "country": "美国"},
    "DFW": {"name": "达拉斯", "region": "北美", "country": "美国"},
    "IAH": {"name": "休斯顿", "region": "北美", "country": "美国"},
    "DEN": {"name": "丹佛", "region": "北美", "country": "美国"},
    "MSP": {"name": "明尼阿波利斯", "region": "北美", "country": "美国"},
    "DTW": {"name": "底特律", "region": "北美", "country": "美国"},
    "STL": {"name": "圣路易斯", "region": "北美", "country": "美国"},
    "MCI": {"name": "堪萨斯城", "region": "北美", "country": "美国"},
    
    # 北美地区 - 加拿大
    "YYZ": {"name": "多伦多", "region": "北美", "country": "加拿大"},
    "YVR": {"name": "温哥华", "region": "北美", "country": "加拿大"},
    "YUL": {"name": "蒙特利尔", "region": "北美", "country": "加拿大"},
    
    # 欧洲地区 - 西欧
    "LHR": {"name": "伦敦", "region": "欧洲", "country": "英国"},
    "CDG": {"name": "巴黎", "region": "欧洲", "country": "法国"},
    "FRA": {"name": "法兰克福", "region": "欧洲", "country": "德国"},
    "AMS": {"name": "阿姆斯特丹", "region": "欧洲", "country": "荷兰"},
    "BRU": {"name": "布鲁塞尔", "region": "欧洲", "country": "比利时"},
    "ZRH": {"name": "苏黎世", "region": "欧洲", "country": "瑞士"},
    "VIE": {"name": "维也纳", "region": "欧洲", "country": "奥地利"},
    "MUC": {"name": "慕尼黑", "region": "欧洲", "country": "德国"},
    "DUS": {"name": "杜塞尔多夫", "region": "欧洲", "country": "德国"},
    "HAM": {"name": "汉堡", "region": "欧洲", "country": "德国"},
    
    # 欧洲地区 - 南欧
    "MAD": {"name": "马德里", "region": "欧洲", "country": "西班牙"},
    "BCN": {"name": "巴塞罗那", "region": "欧洲", "country": "西班牙"},
    "MXP": {"name": "米兰", "region": "欧洲", "country": "意大利"},
    "FCO": {"name": "罗马", "region": "欧洲", "country": "意大利"},
    "ATH": {"name": "雅典", "region": "欧洲", "country": "希腊"},
    "LIS": {"name": "里斯本", "region": "欧洲", "country": "葡萄牙"},
    
    # 欧洲地区 - 北欧
    "ARN": {"name": "斯德哥尔摩", "region": "欧洲", "country": "瑞典"},
    "CPH": {"name": "哥本哈根", "region": "欧洲", "country": "丹麦"},
    "OSL": {"name": "奥斯陆", "region": "欧洲", "country": "挪威"},
    "HEL": {"name": "赫尔辛基", "region": "欧洲", "country": "芬兰"},
    
    # 欧洲地区 - 东欧
    "WAW": {"name": "华沙", "region": "欧洲", "country": "波兰"},
    "PRG": {"name": "布拉格", "region": "欧洲", "country": "捷克"},
    "BUD": {"name": "布达佩斯", "region": "欧洲", "country": "匈牙利"},
    "OTP": {"name": "布加勒斯特", "region": "欧洲", "country": "罗马尼亚"},
    "SOF": {"name": "索非亚", "region": "欧洲", "country": "保加利亚"},
    
    # 中东地区
    "DXB": {"name": "迪拜", "region": "中东", "country": "阿联酋"},
    "TLV": {"name": "特拉维夫", "region": "中东", "country": "以色列"},
    "BAH": {"name": "巴林", "region": "中东", "country": "巴林"},
    "AMM": {"name": "安曼", "region": "中东", "country": "约旦"},
    "KWI": {"name": "科威特", "region": "中东", "country": "科威特"},
    "DOH": {"name": "多哈", "region": "中东", "country": "卡塔尔"},
    "MCT": {"name": "马斯喀特", "region": "中东", "country": "阿曼"},
    
    # 南美地区
    "GRU": {"name": "圣保罗", "region": "南美", "country": "巴西"},
    "GIG": {"name": "里约热内卢", "region": "南美", "country": "巴西"},
    "EZE": {"name": "布宜诺斯艾利斯", "region": "南美", "country": "阿根廷"},
    "BOG": {"name": "波哥大", "region": "南美", "country": "哥伦比亚"},
    "LIM": {"name": "利马", "region": "南美", "country": "秘鲁"},
    "SCL": {"name": "圣地亚哥", "region": "南美", "country": "智利"},
    
    # 非洲地区
    "JNB": {"name": "约翰内斯堡", "region": "非洲", "country": "南非"},
    "CPT": {"name": "开普敦", "region": "非洲", "country": "南非"},
    "CAI": {"name": "开罗", "region": "非洲", "country": "埃及"},
    "LOS": {"name": "拉各斯", "region": "非洲", "country": "尼日利亚"},
    "NBO": {"name": "内罗毕", "region": "非洲", "country": "肯尼亚"},
    "ACC": {"name": "阿克拉", "region": "非洲", "country": "加纳"},
}

# 在线机场码列表URL（GitHub社区维护）
AIRPORT_CODES_URL = "https://raw.githubusercontent.com/cloudflare/cf-ui/master/packages/colo-config/src/data.json"
AIRPORT_CODES_FILE = "airport_codes.json"

# Cloudflare IP列表URL
CLOUDFLARE_IP_URL = "https://www.cloudflare.com/ips-v4/"
CLOUDFLARE_IP_FILE = "Cloudflare.txt"

# GitHub Release版本 - 使用官方CloudflareSpeedTest
GITHUB_VERSION = "v2.3.4"
GITHUB_REPO = "XIU2/CloudflareSpeedTest"


def get_system_info():
    """获取系统信息"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    # 标准化系统名称
    if system == "darwin":
        os_type = "darwin"
    elif system == "linux":
        os_type = "linux"
    elif system == "windows":
        os_type = "win"
    else:
        print(f"不支持的操作系统: {system}")
        sys.exit(1)
    
    # 标准化架构名称
    if machine in ["x86_64", "amd64", "x64"]:
        arch_type = "amd64"
    elif machine in ["arm64", "aarch64"]:
        arch_type = "arm64"
    elif machine in ["armv7l", "armv6l"]:
        arch_type = "arm"
    else:
        print(f"不支持的架构: {machine}")
        sys.exit(1)
    
    return os_type, arch_type


def get_executable_name(os_type, arch_type):
    """获取可执行文件名 - 使用官方命名规则"""
    if os_type == "win":
        return f"CloudflareST_windows_{arch_type}.exe"
    elif os_type == "darwin":
        return f"CloudflareST_darwin_{arch_type}"
    else:  # linux
        return f"CloudflareST_linux_{arch_type}"


def download_file(url, filename):
    """下载文件 - 支持多种下载方法"""
    print(f"正在下载: {url}")
    
    # 方法1: 尝试使用 requests
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ 下载完成: {filename}")
        return True
    except Exception:
        # 静默失败，继续尝试其他方法
        pass
    
    # 方法2: 尝试使用 wget
    try:
        result = subprocess.run([
            "wget", "-O", filename, url
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(filename):
            print(f"✅ 下载完成: {filename}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # wget 不可用，静默继续
        pass
    except Exception:
        # wget 执行失败，静默继续
        pass
    
    # 方法3: 尝试使用 curl
    try:
        result = subprocess.run([
            "curl", "-L", "-o", filename, url
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(filename):
            print(f"✅ 下载完成: {filename}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # curl 不可用，静默继续
        pass
    except Exception:
        # curl 执行失败，静默继续
        pass
    
    # 方法3.5: Windows PowerShell 下载
    if sys.platform == "win32":
        try:
            ps_cmd = f'Invoke-WebRequest -Uri "{url}" -OutFile "{filename}"'
            result = subprocess.run([
                "powershell", "-Command", ps_cmd
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(filename):
                print(f"✅ 下载完成: {filename}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # PowerShell 不可用，静默继续
            pass
        except Exception:
            # PowerShell 执行失败，静默继续
            pass
    
    # 方法4: 尝试使用 urllib
    try:
        import urllib.request
        urllib.request.urlretrieve(url, filename)
        print(f"✅ 下载完成: {filename}")
        return True
    except Exception:
        # urllib 下载失败，静默继续
        pass
    
    # 方法5: 尝试 HTTP 版本
    if url.startswith("https://"):
        http_url = url.replace("https://", "http://")
        try:
            response = requests.get(http_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ 下载完成: {filename}")
            return True
        except Exception:
            # HTTP 下载失败，静默继续
            pass
    
    # 所有方法都失败
    print("❌ 下载失败")
    return False


def download_cloudflare_speedtest(os_type, arch_type):
    """下载 CloudflareSpeedTest 可执行文件（优先使用反代版本）"""
    # 优先检查反代版本
    if os_type == "win":
        proxy_exec_name = f"CloudflareST_proxy_{os_type}_{arch_type}.exe"
    else:
        proxy_exec_name = f"CloudflareST_proxy_{os_type}_{arch_type}"
    
    if os.path.exists(proxy_exec_name):
        print(f"✓ 使用反代版本: {proxy_exec_name}")
        return proxy_exec_name
    
    # 检查是否已下载反代版本
    print("反代版本不存在，开始下载反代版本...")
    
    # 构建下载URL - 使用您的GitHub仓库
    if os_type == "win":
        if arch_type == "amd64":
            archive_name = "CloudflareST_proxy_windows_amd64.zip"
        else:
            archive_name = "CloudflareST_proxy_windows_386.zip"
    elif os_type == "darwin":
        if arch_type == "amd64":
            archive_name = "CloudflareST_proxy_darwin_amd64.zip"
        else:
            archive_name = "CloudflareST_proxy_darwin_arm64.zip"
    else:  # linux
        if arch_type == "amd64":
            archive_name = "CloudflareST_proxy_linux_amd64.tar.gz"
        elif arch_type == "386":
            archive_name = "CloudflareST_proxy_linux_386.tar.gz"
        else:  # arm64
            archive_name = "CloudflareST_proxy_linux_arm64.tar.gz"
    
    download_url = f"https://github.com/byJoey/CloudflareSpeedTest/releases/download/v1.0/{archive_name}"
    
    if not download_file(download_url, archive_name):
        # 备用方案: 尝试 HTTP 下载
        http_url = download_url.replace("https://", "http://")
        if not download_file(http_url, archive_name):
            # 所有自动下载都失败，提供手动下载说明
            print("\n" + "="*60)
            print("自动下载失败，请手动下载反代版本:")
            print(f"下载地址: {download_url}")
            print(f"解压后文件名应为: CloudflareST_proxy_{os_type}_{arch_type}{'.exe' if os_type == 'win' else ''}")
            print("="*60)
            
            # 检查是否有手动下载的反代版本文件
            if os_type == "win":
                proxy_exec_name = f"CloudflareST_proxy_{os_type}_{arch_type}.exe"
            else:
                proxy_exec_name = f"CloudflareST_proxy_{os_type}_{arch_type}"
            
            if os.path.exists(proxy_exec_name):
                print(f"找到手动下载的反代版本: {proxy_exec_name}")
                # 手动下载的文件也需要赋予执行权限
                if os_type != "win":
                    os.chmod(proxy_exec_name, 0o755)
                    print(f"已赋予执行权限: {proxy_exec_name}")
                return proxy_exec_name
            else:
                print("未找到反代版本文件，程序无法继续")
                sys.exit(1)
    else:
        # 解压文件
        print(f"正在解压: {archive_name}")
        try:
            if archive_name.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(archive_name, 'r') as zip_ref:
                    zip_ref.extractall('.')
            elif archive_name.endswith('.tar.gz'):
                import tarfile
                with tarfile.open(archive_name, 'r:gz') as tar_ref:
                    tar_ref.extractall('.')
            
            # 查找反代版本可执行文件
            found_executable = None
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.startswith('CloudflareST_proxy_') and not file.endswith(('.zip', '.tar.gz')):
                        found_executable = os.path.join(root, file)
                        break
                if found_executable:
                    break
            
            if found_executable:
                # 获取最终文件名 - 使用标准格式
                if os_type == "win":
                    final_name = f"CloudflareST_proxy_{os_type}_{arch_type}.exe"
                else:
                    final_name = f"CloudflareST_proxy_{os_type}_{arch_type}"
                
                # 如果文件不在当前目录或文件名不匹配，移动到当前目录并重命名
                if os.path.abspath(found_executable) != os.path.abspath(final_name):
                    if os.path.exists(final_name):
                        os.remove(final_name)
                    # 确保源文件存在
                    if os.path.exists(found_executable):
                        os.rename(found_executable, final_name)
                    else:
                        print(f"❌ 源文件不存在: {found_executable}")
                        sys.exit(1)
                
                # 设置执行权限
                if os_type != "win":
                    os.chmod(final_name, 0o755)
                
                print(f"✓ 反代版本设置完成: {final_name}")
                return final_name
            else:
                print("解压后未找到反代版本可执行文件")
                # 列出解压后的所有文件用于调试
                print("解压后的文件:")
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if not file.endswith(('.zip', '.tar.gz', '.txt', '.md')):
                            print(f"  - {os.path.join(root, file)}")
                sys.exit(1)
            
            # 清理压缩包
            os.remove(archive_name)
            
        except Exception as e:
            print(f"解压失败: {e}")
            sys.exit(1)
    
    # 在Unix系统上赋予执行权限
    if os_type != "win":
        os.chmod(exec_name, 0o755)
        print(f"已赋予执行权限: {exec_name}")
    
    return exec_name


def download_cloudflare_ips():
    """下载 Cloudflare IP 列表"""
    # 检查文件是否已存在
    if os.path.exists(CLOUDFLARE_IP_FILE):
        print(f"✅ 使用已有IP文件: {CLOUDFLARE_IP_FILE}")
        return
    
    print("正在下载 Cloudflare IP 列表...")
    
    if not download_file(CLOUDFLARE_IP_URL, CLOUDFLARE_IP_FILE):
        print("下载 Cloudflare IP 列表失败")
        sys.exit(1)
    
    # 检查文件是否为空
    if os.path.getsize(CLOUDFLARE_IP_FILE) == 0:
        print("Cloudflare IP 列表文件为空")
        sys.exit(1)
    
    print(f"Cloudflare IP 列表已保存到: {CLOUDFLARE_IP_FILE}")


def load_local_airport_codes():
    """从本地文件加载机场码（如果存在）"""
    if os.path.exists(AIRPORT_CODES_FILE):
        try:
            with open(AIRPORT_CODES_FILE, 'r', encoding='utf-8') as f:
                custom_codes = json.load(f)
                AIRPORT_CODES.update(custom_codes)
                print(f"✓ 已加载本地机场码配置（{len(custom_codes)} 个）")
        except Exception as e:
            print(f"加载本地机场码失败: {e}")


def save_airport_codes():
    """保存机场码到本地文件"""
    try:
        with open(AIRPORT_CODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(AIRPORT_CODES, f, ensure_ascii=False, indent=2)
        print(f"✓ 机场码已保存到: {AIRPORT_CODES_FILE}")
    except Exception as e:
        print(f"保存机场码失败: {e}")


def display_airport_codes(region_filter=None):
    """显示所有支持的机场码，可按地区筛选"""
    # 按地区分组
    regions = {}
    for code, info in AIRPORT_CODES.items():
        region = info.get('region', '其他')
        if region not in regions:
            regions[region] = []
        regions[region].append((code, info))
    
    # 显示统计信息
    print(f"\n支持的机场码列表（共 {len(AIRPORT_CODES)} 个数据中心）")
    print("=" * 70)
    
    # 如果指定了地区筛选
    if region_filter:
        region_filter = region_filter.strip()
        if region_filter in regions:
            print(f"\n【{region_filter}地区】")
            print("-" * 70)
            for code, info in sorted(regions[region_filter], key=lambda x: x[0]):
                country = info.get('country', '')
                print(f"  {code:5s} - {info['name']:20s} ({country})")
        else:
            print(f"未找到地区: {region_filter}")
            print(f"可用地区: {', '.join(sorted(regions.keys()))}")
        return
    
    # 显示所有地区
    region_order = ["亚太", "北美", "欧洲", "中东", "南美", "非洲", "其他"]
    for region in region_order:
        if region in regions:
            print(f"\n【{region}地区】（{len(regions[region])} 个）")
            print("-" * 70)
            for code, info in sorted(regions[region], key=lambda x: x[0]):
                country = info.get('country', '')
                print(f"  {code:5s} - {info['name']:20s} ({country})")
    
    print("=" * 70)


def display_popular_codes():
    """显示热门机场码"""
    popular = {
        "HKG": "香港", "SIN": "新加坡", "NRT": "东京成田", "ICN": "首尔", 
        "LAX": "洛杉矶", "SJC": "圣何塞", "LHR": "伦敦", "FRA": "法兰克福"
    }
    
    print("\n热门机场码:")
    print("-" * 50)
    for code, name in popular.items():
        if code in AIRPORT_CODES:
            info = AIRPORT_CODES[code]
            region = info.get('region', '')
            print(f"  {code:5s} - {name:15s} [{region}]")
    print("-" * 50)


def find_airport_by_name(query):
    """根据城市名称查找机场码（支持模糊匹配）"""
    query = query.strip()
    if not query:
        return None
    
    # 先尝试精确匹配机场码
    query_upper = query.upper()
    if query_upper in AIRPORT_CODES:
        return query_upper
    
    # 构建城市名称到机场码的映射
    results = []
    
    for code, info in AIRPORT_CODES.items():
        name = info.get('name', '').lower()
        country = info.get('country', '').lower()
        query_lower = query.lower()
        
        # 精确匹配城市名称
        if name == query_lower:
            return code
        
        # 模糊匹配（包含关系）
        if query_lower in name or name in query_lower:
            results.append((code, info, 1))  # 优先级1
        elif query_lower in country:
            results.append((code, info, 2))  # 优先级2
    
    # 如果有匹配结果
    if results:
        # 按优先级排序
        results.sort(key=lambda x: x[2])
        
        # 如果只有一个结果，直接返回
        if len(results) == 1:
            return results[0][0]
        
        # 如果有多个结果，显示让用户选择
        print(f"\n找到 {len(results)} 个匹配的城市:")
        print("-" * 60)
        for idx, (code, info, _) in enumerate(results[:10], 1):  # 最多显示10个
            region = info.get('region', '')
            country = info.get('country', '')
            print(f"  {idx}. {code:5s} - {info['name']:20s} ({country}) [{region}]")
        print("-" * 60)
        
        try:
            choice = input(f"\n请选择 [1-{min(len(results), 10)}] 或按回车取消: ").strip()
            if choice:
                idx = int(choice) - 1
                if 0 <= idx < min(len(results), 10):
                    return results[idx][0]
        except (ValueError, IndexError):
            pass
    
    return None


def display_preset_configs():
    """显示预设配置"""
    print("\n" + "=" * 60)
    print(" 预设配置选项")
    print("=" * 60)
    print("  1. 快速测试 (10个IP, 1MB/s, 1000ms)")
    print("  2. 标准测试 (20个IP, 2MB/s, 500ms)")
    print("  3. 高质量测试 (50个IP, 5MB/s, 200ms)")
    print("  4. 自定义配置")
    print("=" * 60)


def get_user_input():
    """获取用户输入参数"""
    # 询问功能选择
    print("\n" + "=" * 60)
    print(" 功能选择")
    print("=" * 60)
    print("  1. 常规测速 - 测试指定机场码的IP速度")
    print("  2. 优选反代 - 从CSV文件生成反代IP列表")
    print("=" * 60)
    
    choice = input("\n请选择功能 [默认: 1]: ").strip()
    if not choice:
        choice = "1"
    
    if choice == "2":
        # 优选反代模式
        return handle_proxy_mode()
    else:
        # 常规测速模式
        return handle_normal_mode()


def select_csv_file():
    """选择CSV文件"""
    while True:
        csv_file = input("\n请输入CSV文件路径 [默认: result.csv]: ").strip()
        if not csv_file:
            csv_file = "result.csv"
        
        if os.path.exists(csv_file):
            print(f"找到文件: {csv_file}")
            return csv_file
        else:
            print(f"文件不存在: {csv_file}")
            print("请确保文件路径正确，或先运行常规测速生成result.csv")
            retry = input("是否重新输入？[Y/n]: ").strip().lower()
            if retry in ['n', 'no']:
                return None






def handle_proxy_mode():
    """处理优选反代模式"""
    print("\n" + "=" * 70)
    print(" 优选反代模式")
    print("=" * 70)
    print(" 此功能将从CSV文件中提取IP和端口信息，生成反代IP列表")
    print(" CSV文件格式要求：")
    print("   - 包含 'IP 地址' 和 '端口' 列")
    print("   - 或包含 'ip' 和 'port' 列")
    print("   - 支持逗号分隔的CSV格式")
    print("=" * 70)
    
    # 选择CSV文件
    csv_file = select_csv_file()
    
    if not csv_file:
        print("未选择有效文件，退出优选反代模式")
        return None, None, None, None
    
    # 生成反代IP列表
    print(f"\n正在处理CSV文件: {csv_file}")
    success = generate_proxy_list(csv_file, "ips_ports.txt")
    
    if success:
        print("\n" + "=" * 60)
        print(" 优选反代功能完成！")
        print("=" * 60)
        print(" 生成的文件:")
        print("   - ips_ports.txt (反代IP列表)")
        print("   - 格式: IP:端口 (每行一个)")
        print("\n 使用说明:")
        print("   - 可直接用于反代配置")
        print("   - 支持各种代理软件")
        print("   - 建议定期更新IP列表")
        print("=" * 60)
        
        # 询问是否进行测速
        print("\n" + "=" * 50)
        test_choice = input("是否对反代IP列表进行测速？[Y/n]: ").strip().lower()
        
        if test_choice in ['n', 'no']:
            print("跳过测速，优选反代功能完成")
        return None, None, None, None

        print("开始对反代IP列表进行测速...")
        print("注意: 反代模式直接对IP列表测速，不需要选择机场码")
    
    # 显示预设配置选项
    display_preset_configs()
    
    # 获取配置选择
    while True:
        config_choice = input("\n请选择配置 [默认: 1]: ").strip()
        if not config_choice:
            config_choice = "1"
        
        if config_choice == "1":
            # 快速测试
            dn_count = "10"
            speed_limit = "1"
            time_limit = "1000"
            print("✓ 已选择: 快速测试 (10个IP, 1MB/s, 1000ms)")
            break
        elif config_choice == "2":
            # 标准测试
            dn_count = "20"
            speed_limit = "2"
            time_limit = "500"
            print("✓ 已选择: 标准测试 (20个IP, 2MB/s, 500ms)")
            break
        elif config_choice == "3":
            # 高质量测试
            dn_count = "50"
            speed_limit = "5"
            time_limit = "200"
            print("✓ 已选择: 高质量测试 (50个IP, 5MB/s, 200ms)")
            break
        elif config_choice == "4":
            # 自定义配置
            print("\n自定义配置:")
            
            # 获取测试IP数量
            while True:
                dn_count = input("请输入要测试的 IP 数量 [默认: 10]: ").strip()
                if not dn_count:
                    dn_count = "10"
                
                try:
                    dn_count_int = int(dn_count)
                    if dn_count_int <= 0:
                        print("✗ 请输入大于0的数字")
                        continue
                    if dn_count_int > 200:
                        confirm = input(f"  警告: 测试 {dn_count_int} 个IP可能需要较长时间，是否继续？[y/N]: ").strip().lower()
                        if confirm != 'y':
                            continue
                    dn_count = str(dn_count_int)
                    break
                except ValueError:
                    print("✗ 请输入有效的数字")
            
            # 获取下载速度下限
            while True:
                speed_limit = input("请输入下载速度下限 (MB/s) [默认: 1]: ").strip()
                if not speed_limit:
                    speed_limit = "1"
                
                try:
                    speed_limit_float = float(speed_limit)
                    if speed_limit_float < 0:
                        print("✗ 请输入大于等于0的数字")
                        continue
                    if speed_limit_float > 100:
                        print("警告: 速度阈值过高，可能找不到符合条件的IP")
                        confirm = input("  是否继续？[y/N]: ").strip().lower()
                        if confirm != 'y':
                            continue
                    speed_limit = str(speed_limit_float)
                    break
                except ValueError:
                    print("✗ 请输入有效的数字")
            
            # 获取延迟阈值
            while True:
                time_limit = input("请输入延迟阈值 (ms) [默认: 1000]: ").strip()
                if not time_limit:
                    time_limit = "1000"
                
                try:
                    time_limit_int = int(time_limit)
                    if time_limit_int <= 0:
                        print("✗ 请输入大于0的数字")
                        continue
                    if time_limit_int > 5000:
                        print("警告: 延迟阈值过高，可能影响使用体验")
                        confirm = input("  是否继续？[y/N]: ").strip().lower()
                        if confirm != 'y':
                            continue
                    time_limit = str(time_limit_int)
                    break
                except ValueError:
                    print("✗ 请输入有效的数字")
            
            print(f"✓ 自定义配置: {dn_count}个IP, {speed_limit}MB/s, {time_limit}ms")
            break
        else:
            print("✗ 无效选择，请输入 1-4")
    
        print(f"\n测速参数: 测试{dn_count}个IP, 速度下限{speed_limit}MB/s, 延迟上限{time_limit}ms")
        print("模式: 反代IP列表测速")
        
        # 运行测速
        run_speedtest_with_file("ips_ports.txt", dn_count, speed_limit, time_limit)
        return None, None, None, None
    else:
        print("\n优选反代功能失败")
        return None, None, None, None


def handle_normal_mode():
    """处理常规测速模式"""
    print("\n开始检测可用地区...")
    print("正在使用HTTPing模式检测各地区可用性...")
    
    # 先运行一次HTTPing检测，获取可用地区
    available_regions = detect_available_regions()
    
    if not available_regions:
        print("❌ 未检测到可用地区，请检查网络连接")
        return None
    
    print(f"\n检测到 {len(available_regions)} 个可用地区:")
    for i, (region_code, region_name, count) in enumerate(available_regions, 1):
        print(f"  {i}. {region_code} - {region_name} (可用{count}个IP)")
    
    # 让用户选择地区
    while True:
        try:
            choice = int(input(f"\n请选择地区 [1-{len(available_regions)}]: ").strip())
            if 1 <= choice <= len(available_regions):
                selected_region = available_regions[choice - 1]
                cfcolo = selected_region[0]
                region_name = selected_region[1]
                count = selected_region[2]
                print(f"✓ 已选择: {region_name} ({cfcolo}) - 可用{count}个IP")
                break
            else:
                print(f"✗ 请输入 1-{len(available_regions)} 之间的数字")
        except ValueError:
            print("✗ 请输入有效的数字")
    
    # 显示预设配置选项
    display_preset_configs()
    
    # 获取配置选择
    while True:
        config_choice = input("\n请选择配置 [1-4]: ").strip()
        if config_choice == "1":
            dn_count = "10"
            speed_limit = "1"
            time_limit = "1000"
            print("✓ 快速测试: 10个IP, 1MB/s, 1000ms")
            break
        elif config_choice == "2":
            dn_count = "20"
            speed_limit = "5"
            time_limit = "500"
            print("✓ 标准测试: 20个IP, 5MB/s, 500ms")
            break
        elif config_choice == "3":
            dn_count = "50"
            speed_limit = "10"
            time_limit = "200"
            print("✓ 高质量测试: 50个IP, 10MB/s, 200ms")
            break
        elif config_choice == "4":
            # 自定义配置
            while True:
                try:
                    dn_count = input("请输入测试IP数量 [默认: 10]: ").strip()
                    if not dn_count:
                        dn_count = "10"
                    dn_count_int = int(dn_count)
                    if dn_count_int <= 0:
                        print("✗ 请输入大于0的数字")
                        continue
                    if dn_count_int > 1000:
                        print("警告: 测试数量过多，可能需要很长时间")
                        confirm = input("  是否继续？[y/N]: ").strip().lower()
                        if confirm != 'y':
                            continue
                    break
                except ValueError:
                    print("✗ 请输入有效的数字")
            
            # 获取下载速度下限
            while True:
                speed_limit = input("请输入下载速度下限 (MB/s) [默认: 1]: ").strip()
                if not speed_limit:
                    speed_limit = "1"
                
                try:
                    speed_limit_float = float(speed_limit)
                    if speed_limit_float < 0:
                        print("✗ 请输入大于等于0的数字")
                        continue
                    if speed_limit_float > 100:
                        print("警告: 速度阈值过高，可能找不到符合条件的IP")
                        confirm = input("  是否继续？[y/N]: ").strip().lower()
                        if confirm != 'y':
                            continue
                    break
                except ValueError:
                    print("✗ 请输入有效的数字")
            
            # 获取延迟阈值
            while True:
                time_limit = input("请输入延迟阈值 (ms) [默认: 1000]: ").strip()
                if not time_limit:
                    time_limit = "1000"
                
                try:
                    time_limit_int = int(time_limit)
                    if time_limit_int <= 0:
                        print("✗ 请输入大于0的数字")
                        continue
                    if time_limit_int > 5000:
                        print("警告: 延迟阈值过高，可能影响使用体验")
                        confirm = input("  是否继续？[y/N]: ").strip().lower()
                        if confirm != 'y':
                            continue
                    break
                except ValueError:
                    print("✗ 请输入有效的数字")
            
            print(f"✓ 自定义配置: {dn_count}个IP, {speed_limit}MB/s, {time_limit}ms")
            break
        else:
            print("✗ 无效选择，请输入 1-4")
    
    print(f"\n测速参数: 地区={cfcolo}, 测试{dn_count}个IP, 速度下限{speed_limit}MB/s, 延迟上限{time_limit}ms")
    print("模式: 常规测速（指定地区）")
    
    # 从地区扫描结果中提取该地区的IP进行测速
    if os.path.exists("region_scan.csv"):
        print(f"\n正在从扫描结果中提取 {cfcolo} 地区的IP...")
        
        # 读取该地区的IP
        region_ips = []
        with open("region_scan.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                colo = row.get('地区码', '').strip()
                if colo == cfcolo:
                    ip = row.get('IP 地址', '').strip()
                    if ip:
                        region_ips.append(ip)
        
        if region_ips:
            # 创建该地区的IP文件
            region_ip_file = f"{cfcolo.lower()}_ips.txt"
            with open(region_ip_file, 'w', encoding='utf-8') as f:
                for ip in region_ips:
                    f.write(f"{ip}\n")
            
            print(f"找到 {len(region_ips)} 个 {cfcolo} 地区的IP，开始测速...")
            
            # 使用该地区的IP文件进行测速
            os_type, arch_type = get_system_info()
            exec_name = download_cloudflare_speedtest(os_type, arch_type)
            
            # 构建测速命令
            if sys.platform == "win32":
                cmd = [exec_name]
            else:
                cmd = [f"./{exec_name}"]
            
            cmd.extend([
                "-f", region_ip_file,
                "-dn", dn_count,
                "-sl", speed_limit,
                "-tl", time_limit,
                "-o", "result.csv"
            ])
            
            print(f"\n运行命令: {' '.join(cmd)}")
            print("=" * 50)
            
            # 运行测速
            result = subprocess.run(cmd)
            
            # 清理临时文件
            if os.path.exists(region_ip_file):
                os.remove(region_ip_file)
            
            if result.returncode == 0:
                print("\n✅ 测速完成！结果已保存到 result.csv")
            else:
                print("\n❌ 测速失败")
        else:
            print(f"❌ 未找到 {cfcolo} 地区的IP")
    else:
        print("❌ 未找到地区扫描结果文件")
    
    return cfcolo, dn_count, speed_limit, time_limit


def generate_proxy_list(result_file="result.csv", output_file="ips_ports.txt"):
    """从测速结果生成反代IP列表"""
    if not os.path.exists(result_file):
        print(f"未找到测速结果文件: {result_file}")
        return False
    
    try:
        import csv
        
        print(f"\n正在生成反代IP列表...")
        
        # 读取CSV文件
        with open(result_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            print("测速结果文件为空")
            return False
        
        # 生成反代IP列表
        proxy_ips = []
        for row in rows:
            # 查找IP和端口列
            ip = None
            port = None
            
            # 查找IP列
            for key in row.keys():
                if 'ip' in key.lower() and '地址' in key:
                    ip = row[key].strip()
                    break
                elif key.lower() == 'ip':
                    ip = row[key].strip()
                    break
            
            # 查找端口列
            for key in row.keys():
                if '端口' in key:
                    port = row[key].strip()
                    break
                elif key.lower() == 'port':
                    port = row[key].strip()
                    break
            
            # 如果IP地址中包含端口信息（如 1.2.3.4:443），提取端口
            if ip and ':' in ip:
                ip_parts = ip.split(':')
                if len(ip_parts) == 2:
                    ip = ip_parts[0]  # 提取纯IP地址
                    if not port:  # 如果还没有找到端口，使用IP中的端口
                        port = ip_parts[1]
            
            # 如果没有找到端口，使用默认值
            if not port:
                port = '443'
            
            if ip and port:
                proxy_ips.append(f"{ip}:{port}")
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for proxy in proxy_ips:
                f.write(proxy + '\n')
        
        print(f"反代IP列表已生成: {output_file}")
        print(f"共生成 {len(proxy_ips)} 个反代IP")
        print(f"📝 格式: IP:端口 (如: 1.2.3.4:443)")
        
        # 显示前10个IP作为示例
        if proxy_ips:
            print(f"\n前10个反代IP示例:")
            for i, proxy in enumerate(proxy_ips[:10], 1):
                print(f"  {i:2d}. {proxy}")
            if len(proxy_ips) > 10:
                print(f"  ... 还有 {len(proxy_ips) - 10} 个IP")
        
        return True
        
    except Exception as e:
        print(f"生成反代IP列表失败: {e}")
        return False


def run_speedtest_with_file(ip_file, dn_count, speed_limit, time_limit):
    """使用指定IP文件运行测速（反代模式，不需要机场码）"""
    try:
        # 获取系统信息
        os_type, arch_type = get_system_info()
        exec_name = download_cloudflare_speedtest(os_type, arch_type)
        
        # 构建命令（反代模式使用TCPing，专注于端口信息）
        cmd = [
            f"./{exec_name}",
            "-f", ip_file,
            "-dn", dn_count,
            "-sl", speed_limit,
            "-tl", time_limit,
            "-p", "20"  # 显示前20个结果
        ]
        
        print(f"\n运行命令: {' '.join(cmd)}")
        print("=" * 50)
        
        # 运行测速 - 实时显示输出
        print("正在运行测速，请稍候...")
        result = subprocess.run(cmd, text=True)
        
        if result.returncode == 0:
            print("\n测速完成！")
            print("结果已保存到 result.csv")
        else:
            print(f"\n测速失败，返回码: {result.returncode}")
        
        # 等待用户按键，不自动关闭窗口
        input("\n按回车键退出...")
        return 0
        
    except Exception as e:
        print(f"运行测速失败: {e}")
        return 1


def run_speedtest(exec_name, cfcolo, dn_count, speed_limit, time_limit):
    """运行 CloudflareSpeedTest"""
    print(f"\n开始运行 CloudflareSpeedTest...")
    print(f"测试参数:")
    print(f"  - 机场码: {cfcolo} ({AIRPORT_CODES.get(cfcolo, {}).get('name', '未知')})")
    print(f"  - 测试 IP 数量: {dn_count}")
    print(f"  - 下载速度阈值: {speed_limit} MB/s")
    print(f"  - 延迟阈值: {time_limit} ms")
    print("-" * 50)
    
    # 构建命令
    if sys.platform == "win32":
        cmd = [exec_name]
    else:
        cmd = [f"./{exec_name}"]
    
    cmd.extend([
        "-dn", dn_count,
        "-sl", speed_limit,
        "-tl", time_limit,
        "-f", CLOUDFLARE_IP_FILE
    ])
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\nCloudflareSpeedTest 任务完成！")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"\n运行失败: {e}")
        return e.returncode
    except FileNotFoundError:
        print(f"\n找不到可执行文件: {exec_name}")
        return 1


def main():
    """主函数"""
    # 设置控制台编码（Windows 兼容）
    if sys.platform == "win32":
        try:
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
        except:
            pass
    
    print("=" * 80)
    print(" Cloudflare SpeedTest 跨平台自动化脚本")
    print("=" * 80)
    print(" 支持 Windows / Linux / macOS (Darwin)")
    print(f" 内置 {len(AIRPORT_CODES)} 个全球数据中心机场码")
    print(" 支持单个/多机场码/地区优选测速")
    print(" 支持优选反代IP列表生成")
    print("=" * 80)
    
    # 获取系统信息
    os_type, arch_type = get_system_info()
    print(f"\n[系统信息]")
    print(f"  操作系统: {os_type}")
    print(f"  架构类型: {arch_type}")
    print(f"  Python版本: {sys.version.split()[0]}")
    
    # 加载本地机场码配置（如果存在）
    print(f"\n[配置加载]")
    load_local_airport_codes()
    
    # 下载 CloudflareSpeedTest
    print(f"\n[程序准备]")
    exec_name = download_cloudflare_speedtest(os_type, arch_type)
    
    # 下载 Cloudflare IP 列表
    download_cloudflare_ips()
    
    # 获取用户输入
    print(f"\n[参数配置]")
    print("=" * 60)
    print(" GitHub https://github.com/byJoey/yx-tools")
    print(" YouTube https://www.youtube.com/@Joeyblog")
    print(" 博客 https://joeyblog.net")
    print(" Telegram交流群: https://t.me/+ft-zI76oovgwNmRh")
    print("=" * 60)
    result = get_user_input()
    
    # 检查是否是优选反代模式
    if result == (None, None, None, None):
        print("\n优选反代功能已完成，程序退出")
        return 0
    
    cfcolo, dn_count, speed_limit, time_limit = result
    
    # 常规测速模式已经在handle_normal_mode中完成测速
    print(f"\n常规测速已完成")
    return 0


def detect_available_regions():
    """检测可用地区"""
    # 检查是否已有检测结果文件
    if os.path.exists("region_scan.csv"):
        print("发现已有的地区扫描结果文件")
        choice = input("是否需要重新扫描？[y/N]: ").strip().lower()
        if choice != 'y':
            print("使用已有检测结果...")
            # 直接读取已有文件
            available_regions = []
            region_counts = {}
            
            with open("region_scan.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    colo = row.get('地区码', '').strip()
                    if colo and colo != 'N/A':
                        region_counts[colo] = region_counts.get(colo, 0) + 1
            
            # 构建地区列表（按IP数量排序）
            for colo, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                region_name = "未知地区"
                for code, info in AIRPORT_CODES.items():
                    if code == colo:
                        region_name = f"{info.get('name', '')} ({info.get('country', '')})"
                        break
                available_regions.append((colo, region_name, count))
            
            return available_regions
    
    print("正在检测各地区可用性...")
    
    # 获取系统信息
    os_type, arch_type = get_system_info()
    exec_name = download_cloudflare_speedtest(os_type, arch_type)
    
    # 构建检测命令 - 使用HTTPing模式快速检测
    if sys.platform == "win32":
        cmd = [exec_name]
    else:
        cmd = [f"./{exec_name}"]
    
    cmd.extend([
        "-dd",  # 禁用下载测速，只做延迟测试
        "-tl", "9999",  # 高延迟阈值
        "-f", CLOUDFLARE_IP_FILE,
        "-httping",  # 使用HTTPing模式获取地区码
        "-url", "https://cf.xiu2.xyz/url",
        "-o", "region_scan.csv"  # 输出到地区扫描文件
    ])
    
    try:
        print("运行地区检测...")
        print("正在扫描所有地区，请稍候（约需1-2分钟）...")
        print("=" * 50)
        
        # 直接运行命令，显示完整输出
        result = subprocess.run(cmd, timeout=120)
        
        if result.returncode == 0 and os.path.exists("region_scan.csv"):
            # 读取检测结果
            available_regions = []
            region_counts = {}  # 统计每个地区的IP数量
            
            with open("region_scan.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    colo = row.get('地区码', '').strip()
                    if colo and colo != 'N/A':
                        # 统计IP数量
                        if colo not in region_counts:
                            region_counts[colo] = 0
                        region_counts[colo] += 1
            
            # 构建地区列表（按IP数量排序）
            for colo, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True):
                # 查找地区名称
                region_name = "未知地区"
                for code, info in AIRPORT_CODES.items():
                    if code == colo:
                        region_name = f"{info.get('name', '')} ({info.get('country', '')})"
                        break
                available_regions.append((colo, region_name, count))
            
            # 保留地区扫描结果文件，不删除
            print("地区扫描结果已保存到 region_scan.csv")
            
            return available_regions
        else:
            print("地区检测失败，使用默认地区列表")
            # 返回默认的主要地区
            default_regions = [
                ('HKG', '香港 (中国)', 0),
                ('SIN', '新加坡 (新加坡)', 0),
                ('NRT', '东京 (日本)', 0),
                ('ICN', '首尔 (韩国)', 0),
                ('LAX', '洛杉矶 (美国)', 0),
                ('FRA', '法兰克福 (德国)', 0),
                ('LHR', '伦敦 (英国)', 0)
            ]
            return default_regions
            
    except Exception as e:
        print(f"地区检测出错: {e}")
        # 返回默认地区
        default_regions = [
            ('HKG', '香港 (中国)', 0),
            ('SIN', '新加坡 (新加坡)', 0),
            ('NRT', '东京 (日本)', 0),
            ('ICN', '首尔 (韩国)', 0),
            ('LAX', '洛杉矶 (美国)', 0),
            ('FRA', '法兰克福 (德国)', 0),
            ('LHR', '伦敦 (英国)', 0)
        ]
        return default_regions

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        sys.exit(0)

