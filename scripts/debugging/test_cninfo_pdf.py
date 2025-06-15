import requests
import logging
import time

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)

# 测试URL
urls = [
    "https://static.cninfo.com.cn/finalpage/2025-04-23/1223214399.pdf",
    "https://static.cninfo.com.cn/finalpage/2025-04-23/1223214399.PDF"
]

# 更完整的请求头，模拟真实浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

print("=" * 80)
print("测试1: 使用GET请求（推荐）")
print("=" * 80)

session = requests.Session()
session.headers.update(headers)

for url in urls:
    print(f"\n测试GET请求: {url}")
    try:
        # 先访问主站获取可能的cookies
        main_site = "https://www.cninfo.com.cn"
        print(f"先访问主站: {main_site}")
        main_response = session.get(main_site, timeout=10)
        print(f"主站响应: {main_response.status_code}")
        
        # 等待一下，模拟真实用户行为
        time.sleep(1)
        
        # 现在尝试下载PDF
        print(f"\n尝试下载PDF...")
        response = session.get(url, timeout=30, stream=True, allow_redirects=True)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Content-Length: {response.headers.get('content-length', 'Unknown')}")
            print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            # 读取前1KB以验证是PDF
            first_chunk = response.raw.read(1024)
            if first_chunk.startswith(b'%PDF'):
                print("✓ 确认是PDF文件")
                # 保存测试文件
                test_file = f"test_download_{url.split('/')[-1]}"
                with open(test_file, 'wb') as f:
                    f.write(first_chunk)
                    # 继续下载剩余部分
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"✓ 文件已保存到: {test_file}")
            else:
                print("✗ 不是PDF文件")
                print(f"前20个字节: {first_chunk[:20]}")
        else:
            print(f"响应头: {dict(response.headers)}")
            print(f"响应内容前100字符: {response.text[:100]}")
            
    except Exception as e:
        print(f"错误: {type(e).__name__}: {e}")
    finally:
        if 'response' in locals():
            response.close()

print("\n" + "=" * 80)
print("测试2: 使用不同的User-Agent")
print("=" * 80)

# 测试不同的User-Agent
user_agents = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    # 简单的Python请求
    'Python-urllib/3.8',
]

test_url = "https://static.cninfo.com.cn/finalpage/2025-04-23/1223214399.PDF"

for ua in user_agents:
    print(f"\n测试User-Agent: {ua[:50]}...")
    try:
        test_headers = {'User-Agent': ua}
        response = requests.get(test_url, headers=test_headers, timeout=10, stream=True)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✓ 成功")
            break
    except Exception as e:
        print(f"错误: {e}")

print("\n" + "=" * 80)
print("测试3: 直接使用curl命令（如果可用）")
print("=" * 80)

import subprocess
import platform

if platform.system() == "Windows":
    curl_cmd = "curl"
else:
    curl_cmd = "curl"

try:
    # 测试大写PDF
    url = "https://static.cninfo.com.cn/finalpage/2025-04-23/1223214399.PDF"
    cmd = [curl_cmd, "-I", "-L", "--max-time", "10", url]
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("输出:")
    print(result.stdout)
    if result.stderr:
        print("错误:")
        print(result.stderr)
except Exception as e:
    print(f"无法执行curl命令: {e}")

print("\n" + "=" * 80)
print("测试4: 检查是否需要Referer")
print("=" * 80)

# 测试添加Referer
test_url = "https://static.cninfo.com.cn/finalpage/2025-04-23/1223214399.PDF"
referer_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.cninfo.com.cn/',
}

print(f"测试URL: {test_url}")
print("添加Referer: https://www.cninfo.com.cn/")

try:
    response = requests.get(test_url, headers=referer_headers, timeout=30)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 成功！看来需要Referer头")
    else:
        print("✗ 仍然失败")
except Exception as e:
    print(f"错误: {e}")
