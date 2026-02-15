import os
import sys
import pytest
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.config import APPIUM_REMOTE_URL, DESIRED_CAPS, IMPLICIT_TIMEOUT
from selenium.common.exceptions import WebDriverException

# Basic configuration - Add project root to system path for module import
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Directory & Log configuration - Create necessary directories if not exist
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "screenshots")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Configure logging with file and stream handlers
# Log format: timestamp - log level - message
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
# Purpose: Initialize clean Appium driver for each test and ensure proper teardown
@pytest.fixture(scope="function")
def driver():
    appium_driver = None
    try:
        logger.info("Initializing Appium driver (independent test session)...")
        # Initialize UiAutomator2 options for Android device
        options = UiAutomator2Options()
        
        # Force noReset=False to ensure clean app state (fresh install/clear data) for each test
        # This avoids test contamination from previous test data
        options.set_capability("noReset", False)
        
        # Load desired capabilities from config file, exclude noReset to prevent override
        for k, v in DESIRED_CAPS.items():
            if k != "noReset":
                options.set_capability(k, v)

        # Connect to Appium server and create driver instance
        appium_driver = webdriver.Remote(APPIUM_REMOTE_URL, options=options)
        # Set implicit wait time for element lookup (global for all find_element calls)
        appium_driver.implicitly_wait(IMPLICIT_TIMEOUT)
        
        logger.info("Driver initialized successfully, app in clean state")
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"Driver initialization failed: {str(e)}")
        raise  # Re-raise exception to fail the test explicitly
    finally:
        # Ensure driver is closed even if test fails
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info("Test case completed, driver closed gracefully")
            except WebDriverException as e:
                logger.error(f"Failed to close driver properly: {str(e)}")


# Screenshot fixture for failed tests (autouse for all function scope tests)
# Purpose: Automatically capture screenshot when test fails for debugging
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    yield  # Execute test first, then check failure status
    # Check if test failed during execution phase
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            # Generate unique screenshot filename with test name and timestamp
            screenshot_filename = f"fail_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
            driver.save_screenshot(screenshot_path)
            logger.error(f"Screenshot saved for failed test: {screenshot_path}")  # Fixed: path -> screenshot_path
        except WebDriverException as e:
            logger.warning(f"Failed to capture screenshot for test {request.node.name}: {str(e)}")


# Pytest hook to mark test failure status
# Purpose: Track test failure status to trigger screenshot capture
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    # Mark test as failed only if failure occurs during test execution (not setup/teardown)
    item._test_failed = (rep.when == 'call' and rep.failed)
