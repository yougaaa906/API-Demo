import os
import sys
import pytest
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.config import APPIUM_REMOTE_URL, DESIRED_CAPS, TIMEOUT, LOG_DIR, SCREENSHOTS_DIR, REPORTS_DIR
from selenium.common.exceptions import WebDriverException

# ====================== Project Path Configuration ======================
# Add project root to system path to resolve relative import issues
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ====================== Log File Configuration ======================
# Generate unique log file name with timestamp for traceability
LOG_FILE_NAME = f"test_{datetime.now():%Y%m%d_%H%M%S}.log"

# Create required directories (idempotent - safe to run multiple times)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ====================== Logging Configuration ======================
# Configure standardized logging (file + console) with UTF-8 encoding
# Log format: [timestamp] - [log level] - [message] (industry standard)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE_NAME), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ====================== Core Appium Driver Fixture ======================
@pytest.fixture(scope="function")
def driver():
    """
    Function-scoped Appium driver fixture for Android automation (BrowserStack compatible)
    Key features:
    1. Isolated test sessions (clean app state per test)
    2. Config-driven implicit wait and capabilities
    3. Graceful teardown even on failure
    4. Explicit error handling for driver initialization
    Yields:
        webdriver.Remote: Initialized Appium driver instance
    Raises:
        WebDriverException: If driver initialization fails (fails fast)
    """
    appium_driver = None
    try:
        logger.info("Initializing Appium driver for BrowserStack cloud device...")
        
        # Initialize UiAutomator2 options (Android standard)
        options = UiAutomator2Options()
        
        # Enforce clean app state (critical for test isolation)
        options.set_capability("noReset", False)
        
        # Load BrowserStack capabilities from config (avoid hardcoding)
        for cap_key, cap_value in DESIRED_CAPS.items():
            if cap_key != "noReset":  # Prevent override of test isolation setting
                options.set_capability(cap_key, cap_value)

        # Connect to BrowserStack cloud Appium server (config-driven URL)
        appium_driver = webdriver.Remote(APPIUM_REMOTE_URL, options=options)
        
        # Set global implicit wait (configurable for maintainability)
        appium_driver.implicitly_wait(TIMEOUT)
        
        logger.info("BrowserStack driver initialized successfully (clean app state)")
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"BrowserStack driver initialization failed: {str(e)}")
        raise  # Re-raise to fail test explicitly (no silent failures)
    finally:
        # Ensure driver cleanup (critical for cloud device resource release)
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info("Test session completed - BrowserStack driver closed gracefully")
            except WebDriverException as e:
                logger.error(f"Failed to close BrowserStack driver: {str(e)}")

# ====================== Auto Screenshot Fixture (Failure Only) ======================
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    """
    Auto-executing fixture to capture screenshots for failed tests (BrowserStack compatible)
    Triggers only for test execution phase failures (not setup/teardown)
    Args:
        driver: Core Appium driver fixture (BrowserStack connected)
        request: Pytest request object (access test metadata)
    """
    yield  # Execute test logic first
    
    # Capture screenshot only if test failed during execution
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            # Generate unique screenshot filename (test name + timestamp)
            screenshot_filename = f"fail_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
            
            # Save screenshot for debugging (BrowserStack device screen capture)
            driver.save_screenshot(screenshot_path)
            logger.error(f"Failure screenshot saved: {screenshot_path}")
        except WebDriverException as e:
            logger.warning(f"Failed to capture screenshot for {request.node.name}: {str(e)}")

# ====================== Pytest Hook - Failure Tracking ======================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to track test failure status (triggers screenshot fixture)
    Marks failures only for execution phase (core test logic, not setup/teardown)
    Args:
        item: Pytest test item (individual test case)
        call: Pytest call report (test execution result)
    """
    outcome = yield
    test_report = outcome.get_result()
    
    # Flag test as failed only for execution phase errors (industry best practice)
    item._test_failed = (test_report.when == 'call' and test_report.failed)
