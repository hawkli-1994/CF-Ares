"""
CF-Ares 会话管理示例

本示例展示了如何使用 CF-Ares 的显式挑战执行和会话管理功能。
"""

import os
import time
from cf_ares import AresClient, CloudflareSessionExpired

# 测试网站 URL
TEST_URL = "https://nowsecure.nl"  # 一个用于测试 Cloudflare 绕过的网站

def main():
    print("CF-Ares 会话管理示例")
    print("=" * 50)
    
    # 创建客户端实例
    client = AresClient(
        browser_engine="undetected",  # 使用 undetected-chromedriver 引擎
        headless=True,                # 无头模式
        timeout=30,                   # 超时时间
        debug=True                    # 启用调试输出
    )
    
    try:
        # 步骤 1: 显式执行 Cloudflare 挑战
        print("\n1. 执行 Cloudflare 挑战...")
        start_time = time.time()
        response = client.solve_challenge(TEST_URL)
        elapsed = time.time() - start_time
        
        print(f"挑战完成! 耗时: {elapsed:.2f} 秒")
        print(f"状态码: {response.status_code}")
        print(f"页面标题: {response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else '无标题'}")
        
        # 步骤 2: 获取会话信息
        print("\n2. 获取会话信息...")
        session_info = client.get_session_info(TEST_URL)
        
        print(f"获取到 {len(session_info.get('cookies', {}))} 个 cookies:")
        for name, value in session_info.get('cookies', {}).items():
            print(f"  {name}: {value[:10]}..." if len(str(value)) > 10 else f"  {name}: {value}")
        
        # 步骤 3: 保存会话到文件
        session_file = "cf_session.json"
        print(f"\n3. 保存会话到文件 {session_file}...")
        client.save_session(session_file)
        print(f"会话已保存! 文件大小: {os.path.getsize(session_file)} 字节")
        
        # 步骤 4: 使用保存的会话发送请求
        print("\n4. 使用会话发送请求...")
        for i in range(3):
            try:
                start_time = time.time()
                resp = client.get(f"{TEST_URL}?page={i}")
                elapsed = time.time() - start_time
                
                print(f"请求 {i+1} 成功! 状态码: {resp.status_code}, 耗时: {elapsed:.2f} 秒")
            except CloudflareSessionExpired as e:
                print(f"请求 {i+1} 失败: 会话已过期 - {e}")
                print("重新执行挑战...")
                client.solve_challenge(TEST_URL)
        
        # 步骤 5: 关闭当前客户端，创建新客户端并加载会话
        print("\n5. 创建新客户端并加载会话...")
        client.close()
        
        new_client = AresClient(debug=True)
        new_client.load_session(session_file)
        print("会话已加载!")
        
        # 步骤 6: 使用新客户端发送请求
        print("\n6. 使用新客户端发送请求...")
        try:
            start_time = time.time()
            resp = new_client.get(TEST_URL)
            elapsed = time.time() - start_time
            
            print(f"请求成功! 状态码: {resp.status_code}, 耗时: {elapsed:.2f} 秒")
            print(f"页面标题: {resp.text.split('<title>')[1].split('</title>')[0] if '<title>' in resp.text else '无标题'}")
        except CloudflareSessionExpired as e:
            print(f"请求失败: 会话已过期 - {e}")
            print("这是正常的，因为会话可能已经过期")
        
        # 清理
        if os.path.exists(session_file):
            os.remove(session_file)
            print(f"\n已删除会话文件 {session_file}")
    
    except Exception as e:
        print(f"发生错误: {e}")
    
    finally:
        # 关闭客户端
        print("\n关闭客户端...")
        client.close()
        if 'new_client' in locals():
            new_client.close()
        
        print("\n示例完成!")

if __name__ == "__main__":
    main() 