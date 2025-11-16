"""
京东自动登录使用示例
"""
from jd_auto_login import JDAutoLogin


def main():
    """主函数"""
    print("=" * 50)
    print("京东自动登录示例")
    print("=" * 50)

    # 创建登录实例
    jd_login = JDAutoLogin()

    try:
        # 执行登录
        print("\n开始登录...")
        success = jd_login.login()

        if success:
            print("\n✓ 登录成功！")

            # 获取cookies
            cookies = jd_login.get_cookies()
            print(f"\n获取到 {len(cookies)} 个cookies")

            # 保存cookies到文件
            jd_login.save_cookies("jd_cookies.txt")
            print("Cookies已保存到 jd_cookies.txt")

            # 保持浏览器打开30秒，方便查看结果
            print("\n浏览器将保持打开30秒...")
            jd_login.keep_browser_open(30)

        else:
            print("\n✗ 登录失败，请检查配置和日志")

    except KeyboardInterrupt:
        print("\n\n用户中断操作")

    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭浏览器
        print("\n关闭浏览器...")
        jd_login.close()
        print("完成！")


if __name__ == "__main__":
    main()
