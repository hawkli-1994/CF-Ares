"""
CF-Ares 基本用法示例

本示例展示了 CF-Ares 的基本用法，包括创建客户端、执行挑战和发送请求。
"""

from cf_ares import AresClient, CloudflareSessionExpired

# 测试网站 URL
TEST_URL = "https://nowsecure.nl"  # 一个用于测试 Cloudflare 绕过的网站

def main():
    print("CF-Ares 基本用法示例")
    print("=" * 50)
    
    # 创建客户端实例
    client = AresClient(
        browser_engine="auto",  # 自动选择浏览器引擎
        headless=True,          # 无头模式
        timeout=30,             # 超时时间
        debug=True              # 启用调试输出
    )
    
    try:
        # 方法 1: 隐式挑战 - 直接发送请求，CF-Ares 会自动处理挑战
        print("\n方法 1: 隐式挑战")
        print("-" * 30)
        
        try:
            print("发送 GET 请求...")
            response = client.get(TEST_URL)
            
            print(f"请求成功! 状态码: {response.status_code}")
            print(f"页面标题: {response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else '无标题'}")
            
            # 打印 cookies
            print("\nCookies:")
            for name, value in client.cookies.items():
                print(f"  {name}: {value[:10]}..." if len(str(value)) > 10 else f"  {name}: {value}")
        
        except Exception as e:
            print(f"请求失败: {e}")
        
        # 方法 2: 显式挑战 - 先执行挑战，再发送请求
        print("\n方法 2: 显式挑战")
        print("-" * 30)
        
        try:
            print("执行 Cloudflare 挑战...")
            challenge_response = client.solve_challenge(TEST_URL)
            
            print(f"挑战成功! 状态码: {challenge_response.status_code}")
            
            print("\n发送 POST 请求...")
            post_response = client.post(
                f"{TEST_URL}/submit",
                data={"test": "data"},
                headers={"X-Test": "test-header"}
            )
            
            print(f"POST 请求状态码: {post_response.status_code}")
            
            # 获取会话信息
            session_info = client.get_session_info(TEST_URL)
            print(f"\n会话信息包含 {len(session_info.get('cookies', {}))} 个 cookies")
        
        except CloudflareSessionExpired as e:
            print(f"会话已过期: {e}")
            print("重新执行挑战...")
            client.solve_challenge(TEST_URL)
        
        except Exception as e:
            print(f"发生错误: {e}")
    
    finally:
        # 关闭客户端
        print("\n关闭客户端...")
        client.close()
        
        print("\n示例完成!")

if __name__ == "__main__":
    main() 