"""
京东自动登录模块
使用Selenium自动化浏览器，支持大模型识别验证码
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from captcha_solver import CaptchaSolver
from config import Config


class JDAutoLogin:
    """京东自动登录类"""

    def __init__(self):
        """初始化浏览器和验证码识别器"""
        Config.validate()

        self.driver = None
        self.wait = None
        self.captcha_solver = CaptchaSolver()
        self.setup_driver()

    def setup_driver(self):
        """设置Chrome浏览器"""
        chrome_options = Options()

        if Config.HEADLESS:
            chrome_options.add_argument('--headless')

        # 添加常用选项
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 设置User-Agent
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 初始化driver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        self.wait = WebDriverWait(self.driver, Config.WAIT_TIME)

        print("浏览器初始化完成")

    def login(self):
        """执行登录流程"""
        try:
            print(f"正在访问京东登录页面: {Config.JD_LOGIN_URL}")
            self.driver.get(Config.JD_LOGIN_URL)
            time.sleep(2)

            # 切换到账号密码登录
            self._switch_to_password_login()

            # 输入用户名和密码
            self._input_credentials()

            # 处理验证码（如果存在）
            self._handle_captcha()

            # 点击登录按钮
            self._click_login_button()

            # 等待登录成功
            if self._wait_for_login_success():
                print("登录成功！")
                return True
            else:
                print("登录失败，请检查用户名密码或验证码识别")
                return False

        except Exception as e:
            print(f"登录过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def _switch_to_password_login(self):
        """切换到账号密码登录模式"""
        try:
            # 等待页面加载
            time.sleep(1)

            # 查找并点击"账户登录"标签
            account_login_tab = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "login-tab-l"))
            )
            account_login_tab.click()
            print("已切换到账号密码登录模式")
            time.sleep(1)

        except Exception as e:
            print(f"切换登录模式时出现问题（可能已经是账号密码模式）: {str(e)}")

    def _input_credentials(self):
        """输入用户名和密码"""
        try:
            # 输入用户名
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "loginname"))
            )
            username_input.clear()
            username_input.send_keys(Config.JD_USERNAME)
            print(f"已输入用户名: {Config.JD_USERNAME}")

            # 输入密码
            password_input = self.driver.find_element(By.ID, "nloginpwd")
            password_input.clear()
            password_input.send_keys(Config.JD_PASSWORD)
            print("已输入密码")

            time.sleep(1)

        except Exception as e:
            print(f"输入用户名密码时出错: {str(e)}")
            raise

    def _handle_captcha(self):
        """处理验证码"""
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 检查是否存在图片验证码
                captcha_element = self.driver.find_element(By.ID, "JD_Verification1")

                if captcha_element.is_displayed():
                    print(f"检测到图片验证码，尝试识别（第{retry_count + 1}次）...")

                    # 截取验证码图片
                    captcha_screenshot = captcha_element.screenshot_as_png

                    # 保存验证码图片（调试用）
                    captcha_path = "captcha_temp.png"
                    with open(captcha_path, 'wb') as f:
                        f.write(captcha_screenshot)
                    print(f"验证码图片已保存到: {captcha_path}")

                    # 使用AI识别验证码
                    captcha_text = self.captcha_solver.solve_captcha_from_element(captcha_screenshot)
                    print(f"识别到验证码: {captcha_text}")

                    # 输入验证码
                    captcha_input = self.driver.find_element(By.ID, "authcode")
                    captcha_input.clear()
                    captcha_input.send_keys(captcha_text)
                    print("已输入验证码")

                    time.sleep(1)
                    break
                else:
                    print("图片验证码元素存在但不可见")
                    break

            except NoSuchElementException:
                print("未检测到图片验证码元素")
                break

            except Exception as e:
                print(f"处理验证码时出错: {str(e)}")
                retry_count += 1

                if retry_count < max_retries:
                    print("刷新验证码...")
                    time.sleep(2)
                else:
                    print("验证码识别失败次数过多")
                    raise

        # 检查是否有滑块验证码
        self._check_slider_captcha()

    def _check_slider_captcha(self):
        """检查是否有滑块验证码"""
        try:
            # 京东可能使用的滑块验证码类名
            slider_selectors = [
                "JDJR-button-slide",
                "slider-button",
                "slide-verify",
                "slidetounlock"
            ]

            for selector in slider_selectors:
                try:
                    slider = self.driver.find_element(By.CLASS_NAME, selector)
                    if slider.is_displayed():
                        print(f"⚠️  检测到滑块验证码（类名: {selector}）")
                        print("提示：当前版本暂不支持自动滑块验证，请手动完成滑块验证")
                        # 保存截图
                        self.driver.save_screenshot("slider_captcha.png")
                        print("滑块验证码截图已保存到: slider_captcha.png")
                        return True
                except NoSuchElementException:
                    continue

            # 尝试查找iframe中的滑块
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    if "jd" in iframe.get_attribute("src").lower() or "captcha" in iframe.get_attribute("src").lower():
                        print(f"⚠️  检测到验证码iframe: {iframe.get_attribute('src')}")
                        print("提示：可能需要手动完成验证")
                        return True
            except:
                pass

        except Exception as e:
            print(f"检查滑块验证码时出错: {str(e)}")

        return False

    def _click_login_button(self):
        """点击登录按钮"""
        try:
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "loginsubmit"))
            )
            login_button.click()
            print("已点击登录按钮")
            time.sleep(3)  # 增加等待时间，让验证码有时间出现

            # 保存点击后的页面截图
            self.driver.save_screenshot("after_login_click.png")
            print("登录后页面截图已保存到: after_login_click.png")

        except Exception as e:
            print(f"点击登录按钮时出错: {str(e)}")
            raise

    def _wait_for_login_success(self, timeout=15):
        """等待登录成功"""
        try:
            # 检查是否需要处理验证
            for i in range(timeout):
                current_url = self.driver.current_url

                # 只在前3秒和后3秒打印URL，避免刷屏
                if i < 3 or i >= timeout - 3:
                    print(f"当前URL [{i+1}/{timeout}]: {current_url}")
                elif i == 3:
                    print("...")

                # 检查是否有滑块验证码需要处理
                if self._check_slider_captcha():
                    print("\n需要手动完成滑块验证，等待60秒...")
                    time.sleep(60)
                    continue

                # 检查各种错误提示
                error_selectors = [
                    ("class", "error-msg"),
                    ("class", "err-tip"),
                    ("id", "error"),
                    ("class", "msg-error")
                ]

                for selector_type, selector_value in error_selectors:
                    try:
                        if selector_type == "class":
                            error_elem = self.driver.find_element(By.CLASS_NAME, selector_value)
                        else:
                            error_elem = self.driver.find_element(By.ID, selector_value)

                        if error_elem.is_displayed():
                            error_text = error_elem.text
                            print(f"❌ 登录错误: {error_text}")
                            self.driver.save_screenshot("login_error.png")
                            print("错误页面截图已保存到: login_error.png")
                            return False
                    except:
                        pass

                # 检查是否跳转到京东首页或其他页面
                if 'www.jd.com' in current_url or 'home.jd.com' in current_url or current_url == 'https://www.jd.com/':
                    print("✓ 检测到已跳转到京东首页")
                    return True

                # 检查是否存在用户信息元素
                try:
                    user_info = self.driver.find_element(By.CLASS_NAME, "nickname")
                    if user_info:
                        print(f"✓ 检测到用户信息: {user_info.text}")
                        return True
                except:
                    pass

                time.sleep(1)

            print("⏱️  等待登录超时")
            print("最终页面URL:", self.driver.current_url)
            self.driver.save_screenshot("login_timeout.png")
            print("超时页面截图已保存到: login_timeout.png")

            # 打印页面源代码的一部分用于调试
            page_source = self.driver.page_source
            if "验证码" in page_source or "captcha" in page_source.lower():
                print("\n⚠️  页面源代码中包含'验证码'相关内容，可能需要验证")
            if "滑块" in page_source or "slider" in page_source.lower():
                print("\n⚠️  页面源代码中包含'滑块'相关内容，可能需要滑块验证")

            return False

        except Exception as e:
            print(f"等待登录成功时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_cookies(self):
        """获取登录后的cookies"""
        cookies = self.driver.get_cookies()
        print(f"获取到 {len(cookies)} 个cookies")
        return cookies

    def save_cookies(self, filename="jd_cookies.txt"):
        """保存cookies到文件"""
        cookies = self.get_cookies()
        with open(filename, 'w') as f:
            for cookie in cookies:
                f.write(f"{cookie['name']}={cookie['value']}\n")
        print(f"Cookies已保存到: {filename}")

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

    def keep_browser_open(self, duration=60):
        """保持浏览器打开一段时间"""
        print(f"浏览器将保持打开{duration}秒...")
        time.sleep(duration)


if __name__ == "__main__":
    # 测试登录
    jd_login = JDAutoLogin()
    try:
        success = jd_login.login()
        if success:
            # 保存cookies
            jd_login.save_cookies()
            # 保持浏览器打开30秒以便查看
            jd_login.keep_browser_open(30)
    finally:
        jd_login.close()
