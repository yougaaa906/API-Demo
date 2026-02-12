import os
import sys
import pytest
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.config import APPIUM_REMOTE_URL, DESIRED_CAPS, IMPLICIT_TIMEOUT
from selenium.common.exceptions import WebDriverException

# ========== 基础配置 ==========
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT) if PROJECT_ROOT not in sys.path else None

# 目录&日志（极简专业）
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "screenshots")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f"test_{datetime.now():%Y%m%d_%H%M%S}.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ========== 核心驱动（function级，每个用例独立） ==========
@pytest.fixture(scope="function")  # 关键：改成function级，每个用例独立驱动
def driver():
    appium_driver = None
    try:
        logger.info("🔄 初始化Appium驱动（独立用例会话）...")
        options = UiAutomator2Options()
        # 关键：关闭noReset，每个用例启动全新APP状态（彻底隔离）
        options.set_capability("noReset", False)
        # 保留你的核心配置
        for k, v in DESIRED_CAPS.items():
            if k != "noReset":  # 覆盖noReset为False
                options.set_capability(k, v)

        appium_driver = webdriver.Remote(APPIUM_REMOTE_URL, options=options)
        appium_driver.implicitly_wait(IMPLICIT_TIMEOUT)
        logger.info("✅ 驱动初始化完成，APP为全新状态")
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"❌ 驱动启动失败: {str(e)}")
        raise
    finally:
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info("🔚 用例执行完毕，驱动已关闭")
            except:
                pass


# ========== 失败截图（保留） ==========
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    yield
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            path = os.path.join(SCREENSHOTS_DIR, f"fail_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png")
            driver.save_screenshot(path)
            logger.error(f"📸 用例失败截图: {path}")
        except WebDriverException:
            logger.warning("⚠️ 截图失败，跳过")


# ========== pytest钩子（保留） ==========
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    item._test_failed = (rep.when == 'call' and rep.failed)

# ========== 无需返回首页夹具！！！ ==========
# 因为每个用例都是全新启动APP，直接到首页，无需任何返回操作