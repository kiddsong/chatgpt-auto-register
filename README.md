# ChatGPT 自动注册工具

一个基于 Python 和 undetected-chromedriver 的 ChatGPT 账号自动注册工具，可绕过 Cloudflare 验证。

---

## ⚠️ 免责声明

**本工具仅供教育和研究目的使用。**

- 本工具仅在本人电脑上实现，不提供任何形式的可用性保证
- 作者不对使用本工具产生的任何后果负责
- 使用本工具可能违反 OpenAI 的服务条款
- 自动创建账号可能导致账号被封禁或 IP 被封
- 使用风险自负，请确保遵守所有适用的法律法规
- 本工具仅应在授权的测试环境中使用

**使用本工具即表示您已阅读并理解这些警告。**

---

## 📋 功能特性

- ✅ 自动绕过 Cloudflare 验证
- ✅ 支持 SOCKS5 代理
- ✅ 自动创建临时邮箱
- ✅ 自动填写注册信息（邮箱、密码、姓名）——目前生日无法填写，但不影响注册成功
- ✅ 显示当前代理 IP 地址
- ✅ 浏览器自动移动到副屏（如果有）——目前副屏无法自动移动，只能自动移动到主屏右上方，但也不影响注册成功
- ✅ 支持多线程并发注册——只测试了单线程，多线程会怎样无法保证
- ✅ 自动保存注册成功的账号信息

这个项目是完全模拟人类操作浏览器的方式来进行注册的，所以注册过程中会自动打开浏览器，且浏览器不能关闭，过程中会自动填入邮箱，自动填入密码，自动填入邮箱验证码，到这一步时其实就已经注册成功了。下一步是填写姓名和日期，这部分有问题，无法填入，但并不影响注册成功，且此时注册成功的信息已经写入本地文档了。
实测一次注册流程大约需要耗时2分钟。

---

## 🔧 环境要求

### 必需软件

1. **Python 3.8+**
   - 下载地址：https://www.python.org/downloads/

2. **Google Chrome 浏览器**
   - 下载地址：https://www.google.com/chrome/

3. **代理工具（可选但强烈推荐）**
   - v2rayN 或其他 SOCKS5 代理工具
   - 默认端口：10808

### Python 依赖包

```bash
pip install -r requirements.txt
```

---

## 📦 安装步骤

### 1. 克隆或下载项目

```bash
git clone https://github.com/kiddsong/chatgpt-auto-register.git
cd chatgpt-auto-register
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填入配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 临时邮箱服务配置（必需）
WORKER_DOMAIN=your-mail-service.com:9000
FREEMAIL_TOKEN=your_freemail_api_token_here

# 代理配置（可选但推荐）
PROXY_URL=socks5://127.0.0.1:10808
```

---

## ⚙️ 配置说明

### 1. 临时邮箱服务

本工具需要临时邮箱服务 API。你需要自建临时邮箱服务，如果你不会，问ai，我也是问ai自建的。
- 在 `.env` 中配置 `WORKER_DOMAIN` 和 `FREEMAIL_TOKEN`

**邮箱服务要求：**
- 必须支持程序化创建邮箱
- 必须支持从邮件中获取验证码
- 必须兼容 `EmailService` 类接口

**邮箱服务实现：**

工具期望一个具有以下接口的 `EmailService` 类：

```python
class EmailService:
    def create_email(self):
        """创建临时邮箱地址"""
        # 返回: (邮箱地址, 邮箱ID) 或失败时返回 (None, None)
        pass

    def fetch_verification_code(self, email, max_attempts=60, debug=False):
        """从邮件中获取验证码"""
        # 返回: 验证码(字符串) 或超时时返回 None
        pass

    def delete_email(self, email):
        """删除临时邮箱"""
        pass
```

**注意：** 邮箱服务实现不包含在本仓库中。你需要自行实现邮箱服务。

### 2. 代理配置

**强烈推荐**使用代理以避免 IP 被封：

**v2rayN 用户：**
1. 打开 v2rayN
2. 确保本地监听端口为 10808（默认）
3. 选择一个节点并启动代理

**禁用代理：**
- 在 `.env` 中注释掉或删除 `PROXY_URL` 行

---

## 🚀 使用方法

### 基本用法

```bash
# 注册 1 个账号（单线程）
python chatgpt_v2.py --threads 1 --number 1

# 注册 5 个账号（单线程）
python chatgpt_v2.py --threads 1 --number 5

# 注册 10 个账号（2 线程）
python chatgpt_v2.py --threads 2 --number 10
```

### 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--threads` | 并发线程数 | 1 | `--threads 2` |
| `--number` | 目标注册数量 | 1 | `--number 10` |


---

## 📊 输出文件

注册成功的账号信息保存在 `keys/` 目录下：

**文件名格式：** `chatgpt_YYYYMMDD_HHMMSS_数量.txt`

**文件内容格式：**
```
邮箱----密码----邮箱:密码
example1@mail.com----Abc!@#123456----example1@mail.com:Abc!@#123456
example2@mail.com----Abc!@#123456----example2@mail.com:Abc!@#123456
```

---

## 🔍 浏览器窗口位置

脚本会自动检测显示器配置：

- **有副屏：** 浏览器自动移动到副屏左上角（偏移 50px）
- **无副屏：** 浏览器放置在主屏右侧

你可以在副屏监控注册进度，主屏继续工作。

（实际上不会移动到副屏，只会移动到主屏右上方）

---

## 🛠️ 切换代理节点

如果需要切换代理节点：

1. 在 v2rayN 中选择新的节点
2. 重新运行脚本
3. 查看控制台显示的新 IP 地址，确认切换成功

**示例：**
```
[*] 当前代理出口 IP: 1.45.67.8  ← 第一次运行
[*] 当前代理出口 IP: 9.76.54.3  ← 切换节点后
```

---

## ❓ 常见问题

### Q1: 提示 "ChromeDriver 版本不匹配"

```bash
pip uninstall undetected-chromedriver -y
pip install undetected-chromedriver --upgrade
```

### Q2: 提示 "无法连接到代理"

检查 v2rayN 是否正在运行，代理端口是否为 10808。

### Q3: 邮箱创建失败

检查 `.env` 中的邮件服务配置是否正确，邮件服务 API 是否可访问。

### Q4: 浏览器闪退

可能是内存不足或 Chrome 版本过旧，尝试更新 Chrome 浏览器或更换代理节点。

### Q5: 一直卡在 Cloudflare 验证

更换代理节点（使用住宅 IP 更佳），降低并发数（使用 `--threads 1`）。

---

## ⚠️ 重要提示

### 关于部署和使用

**本项目的所有代码和文档都是由 AI（Claude）编写的。**

作者本人其实不懂编程，所以：

- ✅ **强烈建议让 AI 帮你部署这个项目**
- ✅ **推荐使用 Claude**（本项目就是用 Claude 写的）
- ❌ **不推荐 Gemini**（一开始用 Gemini 死活写不出来）

如果在部署或使用过程中遇到任何问题：
1. 把错误信息复制给 Claude
2. 让 Claude 帮你解决
3. Claude 对这个项目的代码结构非常熟悉

### 法律声明

本工具仅供学习和研究使用，使用者需遵守相关法律法规和服务条款。作者不对使用本工具产生的任何后果负责。

---

## 📝 项目结构

```
chatgpt-auto-register/
├── chatgpt_v2.py              # 主程序
├── .env.example               # 环境配置模板
├── requirements.txt           # Python 依赖
├── README.md                  # 本文档
├── LICENSE                    # 许可证文件
├── .gitignore                 # Git 忽略规则
└── keys/                      # 账号输出目录
    └── chatgpt_*.txt         # 注册成功的账号
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## ⭐ Star

如果你觉得这个项目有帮助，请考虑给它一个 star！

---
