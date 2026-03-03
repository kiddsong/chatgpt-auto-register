import os, sys, json, random, time, re, threading, argparse
import concurrent.futures
from dotenv import load_dotenv

# ── 加载配置 ──────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

PROXY_URL = os.getenv("PROXY_URL", "").strip()
if PROXY_URL:
    print(f"[*] 使用代理: {PROXY_URL}")
else:
    print("[*] 未配置代理，使用直连")

# ── 邮件服务 ──────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'grok'))
from g.email_service import EmailService

# ── 常量 ──────────────────────────────────────────────────
PASSWORD    = "Abc!@#123456"
# 直接访问注册页面
SIGNUP_URL  = "https://chatgpt.com/"

# ── 线程安全计数器 ─────────────────────────────────────────
lock        = threading.Lock()
success_cnt = 0
fail_cnt    = 0
output_file = ""

# ── 工具函数 ──────────────────────────────────────────────
def get_proxy_ip():
    """获取当前代理的出口 IP"""
    import requests
    try:
        if PROXY_URL:
            proxies = {
                'http': PROXY_URL,
                'https': PROXY_URL
            }
            # 使用多个 IP 查询服务作为备选
            ip_services = [
                'https://api.ipify.org?format=json',
                'https://ifconfig.me/ip',
                'https://icanhazip.com',
                'https://api.ip.sb/ip'
            ]

            for service in ip_services:
                try:
                    response = requests.get(service, proxies=proxies, timeout=10)
                    if response.status_code == 200:
                        # 处理不同服务的响应格式
                        if 'json' in service:
                            return response.json().get('ip', response.text.strip())
                        else:
                            return response.text.strip()
                except:
                    continue
            return "无法获取"
        else:
            # 直连模式
            response = requests.get('https://api.ipify.org?format=json', timeout=10)
            return response.json().get('ip', '无法获取')
    except Exception as e:
        return f"获取失败: {e}"

def random_name():
    first = random.choice(["James","Emma","Liam","Olivia","Noah","Ava",
                            "William","Sophia","Oliver","Mia","Ethan",
                            "Charlotte","Lucas","Amelia","Mason","Harper"])
    last  = random.choice(["Smith","Johnson","Williams","Brown","Jones",
                            "Garcia","Miller","Davis","Wilson","Moore",
                            "Taylor","Anderson","Thomas","Jackson","White"])
    return first, last

def random_birthdate():
    year  = random.randint(1985, 2000)
    month = random.randint(1, 12)
    day   = random.randint(1, 28)
    return year, month, day

# ── 使用 undetected-chromedriver 方案 ──────────────────────
def register_account_undetected(email, email_svc, thread_id):
    """使用 undetected-chromedriver 绕过检测"""
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
    except ImportError:
        print("[-] 请先安装: pip install undetected-chromedriver selenium")
        raise

    first, last = random_name()
    name = f"{first} {last}"
    year, month, day = random_birthdate()

    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if PROXY_URL:
        # 转换代理格式
        proxy = PROXY_URL.replace('socks5://', '')
        options.add_argument(f'--proxy-server=socks5://{proxy}')

    # 自动匹配 Chrome 版本
    driver = uc.Chrome(options=options, version_main=145, use_subprocess=True)

    # 将浏览器窗口移动到副屏（第二个显示器）
    try:
        # 获取屏幕信息
        import ctypes
        user32 = ctypes.windll.user32

        # 获取主屏幕宽度
        primary_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        primary_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN

        # 获取所有屏幕的总宽度
        virtual_width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN

        # 如果有副屏（总宽度大于主屏宽度）
        if virtual_width > primary_width:
            # 将窗口移动到副屏（主屏宽度之后的位置）
            # 设置窗口大小和位置
            driver.set_window_size(1200, 900)
            driver.set_window_position(primary_width + 50, 50)
            print(f"[*] 浏览器已移动到副屏 (位置: {primary_width + 50}, 50)")
        else:
            # 没有副屏，放在主屏右侧
            driver.set_window_size(800, 600)
            driver.set_window_position(primary_width - 850, 50)
            print(f"[*] 未检测到副屏，浏览器已放置在主屏右侧")
    except Exception as e:
        print(f"[!] 窗口定位失败: {e}，使用默认位置")
        pass

    try:
        print(f"[*] [{thread_id}] Step1: 打开注册页...")
        driver.get(SIGNUP_URL)
        time.sleep(8)  # 等待页面加载和可能的 CF 验证

        # 点击 Sign up 按钮进入注册流程
        print(f"[*] [{thread_id}] Step1.5: 点击 Sign up...")
        try:
            # 尝试多种可能的注册按钮定位
            signup_selectors = [
                "a[href*='signup']",
                "button:has-text('Sign up')",
                "a:has-text('Sign up')",
                "[data-testid='signup-button']",
                "//a[contains(text(), 'Sign up')]",
                "//button[contains(text(), 'Sign up')]"
            ]

            signup_btn = None
            for selector in signup_selectors:
                try:
                    if selector.startswith("//"):
                        from selenium.webdriver.common.by import By as BY
                        signup_btn = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((BY.XPATH, selector))
                        )
                    else:
                        signup_btn = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if signup_btn:
                        break
                except:
                    continue

            if signup_btn:
                driver.execute_script("arguments[0].scrollIntoView(true);", signup_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", signup_btn)
                time.sleep(5)
            else:
                # 如果找不到按钮，直接访问注册 URL
                print(f"[*] [{thread_id}] 未找到 Sign up 按钮，直接访问注册页...")
                driver.get("https://chatgpt.com/auth/signup")
                time.sleep(5)
        except Exception as e:
            print(f"[!] [{thread_id}] 点击 Sign up 失败: {e}，尝试直接访问注册页...")
            driver.get("https://chatgpt.com/auth/signup")
            time.sleep(5)

        # Step 2: 输入邮箱
        print(f"[*] [{thread_id}] Step2: 输入邮箱 {email}")
        wait = WebDriverWait(driver, 30)

        # 等待页面完全加载
        time.sleep(3)

        # 使用 JavaScript 查找并聚焦输入框
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='email'], input[type='email']")))

        # 滚动到元素可见
        driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
        time.sleep(1)

        # 使用 JavaScript 点击
        driver.execute_script("arguments[0].click();", email_input)
        time.sleep(1)

        # 逐字符输入
        for char in email:
            email_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        time.sleep(3)

        # 点击 Continue
        continue_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        driver.execute_script("arguments[0].scrollIntoView(true);", continue_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", continue_btn)
        time.sleep(5)

        # Step 3: 输入密码
        print(f"[*] [{thread_id}] Step3: 输入密码...")
        try:
            # 等待密码输入框出现
            time.sleep(3)

            # 尝试多种密码输入框定位
            pwd_selectors = [
                "input[name='new-password']",
                "input[autocomplete='new-password']",
                "input[type='password']",
                "input[name='password']"
            ]

            pwd_input = None
            for selector in pwd_selectors:
                try:
                    pwd_input = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if pwd_input:
                        break
                except:
                    continue

            if not pwd_input:
                raise Exception("未找到密码输入框")

            # 滚动到元素
            driver.execute_script("arguments[0].scrollIntoView(true);", pwd_input)
            time.sleep(1)

            # 移除可能覆盖的元素
            driver.execute_script("""
                var labels = document.querySelectorAll('._typeableLabelTextPositioner_10s5b_88');
                labels.forEach(function(label) {
                    label.style.display = 'none';
                });
            """)
            time.sleep(0.5)

            # 使用 JavaScript 聚焦并输入
            driver.execute_script("arguments[0].focus();", pwd_input)
            time.sleep(0.5)

            # 逐字符输入
            for char in PASSWORD:
                pwd_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            time.sleep(3)

            # 点击提交按钮
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(5)
        except TimeoutException:
            print(f"[!] [{thread_id}] 密码输入框未找到")
            driver.save_screenshot(f"debug_err_{thread_id}.png")
            raise

        # Step 4: 等待 OTP
        print(f"[*] [{thread_id}] Step4: 等待 OTP...")
        otp = email_svc.fetch_verification_code(email, max_attempts=60, debug=False)
        if not otp:
            raise Exception("OTP 超时（60s）")
        print(f"[*] [{thread_id}] 获取到 OTP: {otp}")

        # Step 5: 填入 OTP
        print(f"[*] [{thread_id}] Step5: 填入 OTP...")
        try:
            # 尝试 6 格式
            otp_inputs = driver.find_elements(By.CSS_SELECTOR, "input[data-testid^='otp-'], input.otp-input, input[maxlength='1']")
            if len(otp_inputs) >= 6:
                for i, ch in enumerate(otp[:6]):
                    otp_inputs[i].send_keys(ch)
                    time.sleep(0.1)
            else:
                # 单框
                single = driver.find_element(By.CSS_SELECTOR, "input[name='code'], input[autocomplete='one-time-code']")
                single.send_keys(otp)
                time.sleep(2)
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_btn.click()
        except Exception as e:
            print(f"[!] [{thread_id}] OTP 输入失败: {e}")
        time.sleep(3)

        # Step 6: 填姓名
        print(f"[*] [{thread_id}] Step6: 填姓名 {name}")
        try:
            name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='name']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", name_input)
            time.sleep(1)
            driver.execute_script("arguments[0].focus();", name_input)
            time.sleep(0.5)
            name_input.send_keys(name)
            time.sleep(2)
            submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", submit_btn)
            time.sleep(3)

            print(f"[✓] [{thread_id}] 注册成功（已完成邮箱、密码、姓名）")
        except TimeoutException:
            print(f"[!] [{thread_id}] 姓名页不存在，可能已跳过")
            print(f"[✓] [{thread_id}] 注册成功（已完成邮箱、密码）")

        # 注册已完成，不再填写生日等其他信息
        # 直接返回账号信息
        return f"{email}:{PASSWORD}", name

    except Exception as e:
        try:
            driver.save_screenshot(f"debug_err_{thread_id}.png")
            with open(f"debug_err_{thread_id}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except:
            pass
        raise e
    finally:
        driver.quit()

# ── 线程工作函数 ───────────────────────────────────────────
def worker(thread_id, target, results):
    global success_cnt, fail_cnt

    email_svc = EmailService()

    while True:
        with lock:
            if success_cnt + fail_cnt >= target:
                break

        # 1. 创建临时邮箱
        email = None
        for _ in range(3):
            e, _ = email_svc.create_email()
            if e:
                email = e
                break
            print(f"[-] [{thread_id}] 邮箱创建失败，5秒后重试...")
            time.sleep(5)

        if not email:
            with lock:
                fail_cnt += 1
            print(f"[-] [{thread_id}] 邮箱创建失败，跳过")
            continue

        print(f"[*] [{thread_id}] 开始注册: {email}")

        try:
            token, name = register_account_undetected(email, email_svc, thread_id)
            with lock:
                success_cnt += 1
                cnt = success_cnt
            line = f"{email}----{PASSWORD}----{token}"
            results.append(line)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            print(f"[✓] [{thread_id}] 注册成功: {cnt}/{target} | {email} | {name}")
        except Exception as e:
            print(f"[-] [{thread_id}] 注册失败 {email}: {e}")
            with lock:
                fail_cnt += 1
        finally:
            try:
                email_svc.delete_email(email)
            except:
                pass

# ── 主程序 ────────────────────────────────────────────────
def main():
    global output_file

    parser = argparse.ArgumentParser(description="ChatGPT 批量注册工具 (undetected-chromedriver)")
    parser.add_argument("--threads", type=int, default=1,  help="并发线程数 (默认: 1)")
    parser.add_argument("--number",  type=int, default=1,  help="目标注册数量 (默认: 1)")
    args = parser.parse_args()

    os.makedirs("keys", exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"keys/chatgpt_{ts}_{args.number}.txt"

    print("=" * 60)
    print("  ChatGPT 注册机 (undetected-chromedriver)")
    print("=" * 60)
    print(f"[*] 启动 {args.threads} 个线程，目标 {args.number} 个")
    print(f"[*] 输出: {output_file}")

    # 获取并显示当前代理 IP
    print("[*] 正在检测代理 IP...")
    proxy_ip = get_proxy_ip()
    print(f"[*] 当前代理出口 IP: {proxy_ip}")
    print("=" * 60)

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [
            executor.submit(worker, f"T{i}", args.number, results)
            for i in range(args.threads)
        ]
        concurrent.futures.wait(futures)

    print(f"\n[✓] 完成: 成功 {success_cnt} 个 / 失败 {fail_cnt} 个")
    print(f"[*] Token 已保存到: {output_file}")
    print(f"[*] 本次使用的代理 IP: {proxy_ip}")

if __name__ == "__main__":
    main()
