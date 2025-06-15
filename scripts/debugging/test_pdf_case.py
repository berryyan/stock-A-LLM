#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试巨潮资讯网PDF链接大小写敏感性问题
"""

import requests
from urllib.parse import urlparse, urlunparse
import time

def test_pdf_urls():
    """测试不同大小写的PDF URL"""
    
    # 测试用例
    test_cases = [
        {
            "name": "001356.SZ - 2024年年度报告",
            "original_url": "https://static.cninfo.com.cn/finalpage/2025-04-22/1223192304.PDF",
            "html_url": "https://www.cninfo.com.cn/new/disclosure/detail?stockCode=001356&announcementId=1223192304&orgId=9900056292&announcementTime=2025-04-22"
        },
        {
            "name": "002192.SZ - 2024年年度报告",
            "original_url": "https://static.cninfo.com.cn/finalpage/2025-04-22/1223197788.PDF",
            "html_url": "https://www.cninfo.com.cn/new/disclosure/detail?stockCode=002192&announcementId=1223197788"
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("=" * 80)
    print("测试PDF链接大小写敏感性")
    print("=" * 80)
    
    for case in test_cases:
        print(f"\n测试: {case['name']}")
        print(f"HTML页面: {case['html_url']}")
        print("-" * 60)
        
        # 测试原始URL（大写.PDF）
        original_url = case['original_url']
        print(f"\n1. 测试原始URL (大写.PDF): {original_url}")
        
        try:
            response = requests.head(original_url, headers=headers, timeout=10, allow_redirects=True)
            print(f"   状态码: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
        except Exception as e:
            print(f"   错误: {e}")
        
        time.sleep(1)
        
        # 测试小写版本
        lowercase_url = original_url.replace('.PDF', '.pdf')
        print(f"\n2. 测试小写URL (.pdf): {lowercase_url}")
        
        try:
            response = requests.head(lowercase_url, headers=headers, timeout=10, allow_redirects=True)
            print(f"   状态码: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('Content-Length', 'N/A')}")
            
            # 如果成功，尝试下载前1KB检查
            if response.status_code == 200:
                print("\n   尝试下载前1KB内容...")
                response = requests.get(lowercase_url, headers=headers, stream=True, timeout=10)
                content = response.raw.read(1024)
                if content.startswith(b'%PDF'):
                    print("   ✓ 确认是有效的PDF文件")
                else:
                    print("   ✗ 不是有效的PDF文件")
        except Exception as e:
            print(f"   错误: {e}")
        
        print("-" * 60)
        time.sleep(1)

def fix_pdf_url(url):
    """修复PDF URL的大小写问题"""
    if url.endswith('.PDF'):
        return url[:-4] + '.pdf'
    return url

def test_url_fix():
    """测试URL修复函数"""
    print("\n" + "=" * 80)
    print("测试URL修复函数")
    print("=" * 80)
    
    test_urls = [
        "https://static.cninfo.com.cn/finalpage/2025-04-22/1223192304.PDF",
        "https://static.cninfo.com.cn/finalpage/2025-04-22/1223192304.pdf",
        "https://static.cninfo.com.cn/finalpage/2025-04-22/1223192304.Pdf",
        "https://example.com/document.PDF"
    ]
    
    for url in test_urls:
        fixed = fix_pdf_url(url)
        print(f"原始: {url}")
        print(f"修复: {fixed}")
        print(f"改变: {'是' if url != fixed else '否'}")
        print("-" * 40)

if __name__ == "__main__":
    # 首先测试URL大小写敏感性
    test_pdf_urls()
    
    # 然后测试修复函数
    test_url_fix()
    
    print("\n建议：在document_processor.py中，构造PDF URL后立即将.PDF改为.pdf")
