import os
import sys
import pytest
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.config import APPIUM_REMOTE_URL, DESIRED_CAPS, TIMEOUT, LOG_DIR, SCREENSHOTS_DIR, REPORTS_DIR
from selenium.common.exceptions import WebDriverException

# Project Path Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Log File Configuration
LOG_FILE_NAME = f"test_{datetime.now():%Y%m%d_%H%M%S}.log"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE_NAME), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Core Appium Driver Fixture
@pytest.fixture(scope="function")
def driver():
    """
    Function-scoped Appium driver fixture for BrowserStack cloud
    """
    appium_driver = None
    try:
        logger.info("Initializing BrowserStack driver...")
        options = UiAutomator2Options()
        options.set_capability("noReset", False)
        
        for cap_key, cap_value in DESIRED_CAPS.items():
            if cap_key != "noReset":
                options.set_capability(cap_key, cap_value)

        appium_driver = webdriver.Remote(APPIUM_REMOTE_URL, options=options)
        appium_driver.implicitly_wait(TIMEOUT)
        logger.info("BrowserStack driver initialized successfully")
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"Driver init failed: {str(e)}")
        raise
    finally:
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info("BrowserStack driver closed")
            except WebDriverException as e:
                logger.error(f"Failed to close driver: {str(e)}")

# Auto Screenshot Fixture
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    """
    Auto screenshot for failed tests
    """
    yield
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            screenshot_filename = f"fail_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
            driver.save_screenshot(screenshot_path)
            logger.error(f"Screenshot saved: {screenshot_path}")
        except WebDriverException as e:
            logger.warning(f"Failed to capture screenshot: {str(e)}")

# Pytest Hook for Failure Tracking
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    test_report = outcome.get_result()
    item._test_failed = (test_report.when == 'call' and test_report.failed)
