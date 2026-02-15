import os
import sys
import pytest
import logging
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.config import APPIUM_REMOTE_URL, DESIRED_CAPS, IMPLICIT_TIMEOUT
from selenium.common.exceptions import WebDriverException

# ====================== Project Configuration ======================
# Add project root to system path for module import (resolve relative import issues)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ====================== Directory & Log Constants ======================
# Define directory paths for logs and screenshots (centralized for easy maintenance)
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
SCREENSHOTS_DIR = os.path.join(PROJECT_ROOT, "screenshots")
LOG_FILE_NAME = f"test_{datetime.now():%Y%m%d_%H%M%S}.log"

# Create directories if they don't exist (idempotent operation)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# ====================== Logging Configuration ======================
# Configure logging with file (UTF-8 encoding) and stream handlers
# Log format: [timestamp] - [log level] - [message] (standard format for readability)
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
    Function-scoped Appium driver fixture for Android automation
    Key features:
    1. Initializes clean driver (noReset=False) for each test to avoid data contamination
    2. Sets global implicit wait from config
    3. Ensures proper driver teardown even on failure
    4. Raises explicit exception on driver initialization failure
    :yield: Initialized Appium WebDriver instance
    :raise: WebDriverException if driver initialization fails
    """
    appium_driver = None
    try:
        logger.info("Initializing Appium driver (independent test session)...")
        
        # Initialize UiAutomator2 options for Android device
        options = UiAutomator2Options()
        
        # Force clean app state (noReset=False) - critical for test isolation
        options.set_capability("noReset", False)
        
        # Load desired capabilities from config (exclude noReset to prevent override)
        for cap_key, cap_value in DESIRED_CAPS.items():
            if cap_key != "noReset":
                options.set_capability(cap_key, cap_value)

        # Create driver instance by connecting to Appium server
        appium_driver = webdriver.Remote(APPIUM_REMOTE_URL, options=options)
        
        # Set global implicit wait for element lookup (config-driven)
        appium_driver.implicitly_wait(IMPLICIT_TIMEOUT)
        
        logger.info("Driver initialized successfully, app in clean state")
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"Driver initialization failed: {str(e)}")
        raise  # Re-raise to fail test explicitly (avoid silent failures)
    finally:
        # Ensure driver is closed gracefully (even if test fails)
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info("Test case completed, driver closed gracefully")
            except WebDriverException as e:
                logger.error(f"Failed to close driver properly: {str(e)}")

# ====================== Auto Screenshot Fixture ======================
@pytest.fixture(scope="function", autouse=True)
def fail_screenshot(driver, request):
    """
    Auto-triggered fixture to capture screenshots for failed tests
    Scope: Function-level (runs for every test)
    Logic: Executes after test, captures screenshot only if test failed in 'call' phase
    :param driver: Core Appium driver fixture
    :param request: Pytest request object (access test metadata)
    """
    yield  # Execute test first, then post-test logic
    
    # Check if test failed during execution (not setup/teardown)
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            # Generate unique screenshot filename (test name + timestamp)
            screenshot_filename = f"fail_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png"
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
            
            # Save screenshot and log path for debugging
            driver.save_screenshot(screenshot_path)
            logger.error(f"Screenshot saved for failed test: {screenshot_path}")
        except WebDriverException as e:
            logger.warning(f"Failed to capture screenshot for test {request.node.name}: {str(e)}")

# ====================== Pytest Hook for Failure Tracking ======================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to mark test failure status (triggers screenshot capture)
    Only marks failure if test fails in 'call' phase (execution, not setup/teardown)
    :param item: Pytest test item object
    :param call: Pytest call report object
    """
    # Execute the test and get result report
    outcome = yield
    test_report = outcome.get_result()
    
    # Mark test as failed only for execution phase failures (core test logic)
    item._test_failed = (test_report.when == 'call' and test_report.failed)
