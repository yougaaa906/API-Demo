import os
import sys
import pytest
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.config import APPIUM_REMOTE_URL, DESIRED_CAPS, IMPLICIT_TIMEOUT
from selenium.common.exceptions import WebDriverException

# Basic configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Directory & Log configuration
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


# Core driver fixture (function scope, independent for each test case)
@pytest.fixture(scope="function")
def driver():
    appium_driver = None
    try:
        logger.info("🔄 Initializing Appium driver (independent test session)...")
        options = UiAutomator2Options()
        # Force noReset=False to ensure clean app state for each test
        options.set_capability("noReset", False)
        # Load desired capabilities from config, exclude noReset to avoid override
        for k, v in DESIRED_CAPS.items():
            if k != "noReset":
                options.set_capability(k, v)

        appium_driver = webdriver.Remote(APPIUM_REMOTE_URL, options=options)
        appium_driver.implicitly_wait(IMPLICIT_TIMEOUT)
        logger.info("✅ Driver initialized successfully, app in clean state")
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"❌ Driver initialization failed: {str(e)}")
        raise
    finally:
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info("🔚 Test case completed, driver closed")
            except Exception:
                pass


# Screenshot fixture for failed tests (autouse for all function scope tests)
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    yield
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fail_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png")
            driver.save_screenshot(screenshot_path)
            logger.error(f"📸 Screenshot saved for failed test: {path}")
        except WebDriverException:
            logger.warning("⚠️ Failed to capture screenshot, skip")


# Pytest hook to mark test failure status
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    item._test_failed = (rep.when == 'call' and rep.failed)
