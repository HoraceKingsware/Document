# 京东自动登录工具

基于 Selenium 和大模型的京东自动登录工具，支持使用 Claude 或 OpenAI 自动识别验证码。

## 功能特点

- 自动化浏览器操作，模拟真实用户登录
- 支持使用 Claude 或 OpenAI 识别验证码
- 自动保存登录后的 Cookies
- 支持有头/无头模式运行
- 详细的日志输出，方便调试

## 技术栈

- Python 3.8+
- Selenium - 浏览器自动化
- Claude API / OpenAI API - 验证码识别
- Chrome WebDriver - Chrome 浏览器驱动

## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Chrome 浏览器

确保系统已安装 Chrome 浏览器（ChromeDriver 会自动下载）

## 配置

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

```bash
# 京东登录配置
JD_USERNAME=your_jd_username        # 你的京东用户名/手机号
JD_PASSWORD=your_jd_password        # 你的京东密码

# 大模型API配置（选择其中一种）
# 使用Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# 或使用OpenAI API
# OPENAI_API_KEY=your_openai_api_key

# 模型选择：claude 或 openai
AI_MODEL=claude

# 浏览器配置
HEADLESS=false      # 是否无头模式运行浏览器
WAIT_TIME=10        # 页面加载等待时间（秒）
```

### 3. 获取 API Key

#### Claude API Key
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制 Key 到 `.env` 文件中的 `ANTHROPIC_API_KEY`

#### OpenAI API Key
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制 Key 到 `.env` 文件中的 `OPENAI_API_KEY`

## 使用方法

### 快速开始

```bash
python example.py
```

### 代码示例

```python
from jd_auto_login import JDAutoLogin

# 创建登录实例
jd_login = JDAutoLogin()

try:
    # 执行登录
    success = jd_login.login()

    if success:
        # 获取cookies
        cookies = jd_login.get_cookies()

        # 保存cookies
        jd_login.save_cookies("jd_cookies.txt")

        # 保持浏览器打开30秒
        jd_login.keep_browser_open(30)

finally:
    # 关闭浏览器
    jd_login.close()
```

## 项目结构

```
.
├── jd_auto_login.py      # 京东登录主模块
├── captcha_solver.py     # 验证码识别模块
├── config.py             # 配置管理
├── example.py            # 使用示例
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量模板
├── .env                  # 环境变量配置（需自行创建）
├── .gitignore           # Git忽略文件
└── README.md            # 说明文档
```

## 核心模块说明

### JDAutoLogin (jd_auto_login.py)

主要功能类，负责京东登录流程：

- `__init__()` - 初始化浏览器和验证码识别器
- `login()` - 执行完整的登录流程
- `get_cookies()` - 获取登录后的cookies
- `save_cookies(filename)` - 保存cookies到文件
- `close()` - 关闭浏览器

### CaptchaSolver (captcha_solver.py)

验证码识别类，支持多种AI模型：

- `solve_captcha_from_file(image_path)` - 从文件识别验证码
- `solve_captcha_from_element(screenshot_bytes)` - 从截图识别验证码

### Config (config.py)

配置管理类，从环境变量加载配置：

- 京东登录信息
- AI模型配置
- 浏览器配置

## 工作流程

1. 访问京东登录页面
2. 切换到账号密码登录模式
3. 输入用户名和密码
4. 检测并识别验证码（如果存在）
   - 截取验证码图片
   - 使用大模型识别验证码文本
   - 自动填入识别结果
5. 点击登录按钮
6. 等待登录成功并保存Cookies

## 注意事项

1. **安全性**
   - 不要将 `.env` 文件提交到代码仓库
   - 妥善保管你的API Key和京东账号密码
   - 建议使用环境变量或密钥管理工具

2. **合规性**
   - 仅用于个人学习和测试
   - 请遵守京东网站的使用条款
   - 不要用于商业用途或恶意行为

3. **API费用**
   - Claude API 和 OpenAI API 都是按使用量计费
   - 每次识别验证码都会调用API
   - 建议查看对应平台的定价信息

4. **调试建议**
   - 首次使用建议设置 `HEADLESS=false` 以便观察浏览器行为
   - 验证码图片会保存为 `captcha_temp.png` 方便调试
   - 查看终端输出的详细日志

## 常见问题

### 1. 浏览器无法启动

- 确保已安装 Chrome 浏览器
- 检查 ChromeDriver 是否正确安装
- 尝试更新 selenium 和 webdriver-manager

### 2. 验证码识别失败

- 检查 API Key 是否正确配置
- 确认 API Key 有足够的额度
- 查看验证码图片 `captcha_temp.png` 是否清晰
- 尝试切换不同的AI模型

### 3. 登录失败

- 确认用户名和密码是否正确
- 检查是否有安全验证（如短信验证）
- 查看浏览器中的错误提示

### 4. 网络问题

- 确保网络连接正常
- 如在国内使用OpenAI，可能需要配置代理
- Claude API 在国内可直接访问

## 开发计划

- [ ] 支持更多验证码类型（滑块、点选等）
- [ ] 添加短信验证码处理
- [ ] 支持多账号批量登录
- [ ] 添加登录状态保持功能
- [ ] 提供Web界面

## 许可证

MIT License

## 免责声明

本项目仅供学习和研究使用，请勿用于任何违法用途。使用本工具产生的任何后果由使用者自行承担。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请提交 Issue。
