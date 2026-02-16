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

# Logging Configuration - Standard for CI/CD and remote debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, LOG_FILE_NAME), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Core Appium Driver Fixture - BrowserStack Cloud Integration
@pytest.fixture(scope="function")
def driver():
    """
    Function-scoped Appium driver fixture for BrowserStack cloud execution.
    Initializes UiAutomator2 driver with W3C-compliant capabilities,
    implicit wait configuration, and proper teardown.
    Critical fix: Custom element factory to resolve W3C dict -> WebElement issue
    
    Yields:
        webdriver.Remote: Initialized Appium driver instance
    Raises:
        WebDriverException: If driver initialization/teardown fails
    """
    appium_driver = None
    try:
        logger.info("Initializing BrowserStack remote driver...")
        
        # Initialize UiAutomator2 options with W3C compliance
        options = UiAutomator2Options()
        
        # Core Android capabilities (W3C standard)
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
        options.set_capability("appium:noReset", False)
        options.set_capability("appium:newCommandTimeout", 30)
        options.set_capability("appium:app", "bs://19db12aefeee97f9eed40b499feb88911af3100e")
        options.set_capability("appium:deviceName", "Samsung Galaxy S23 Ultra")
        options.set_capability("appium:platformVersion", "13.0")
        
        # BrowserStack-specific capabilities (preserve nested structure for W3C compliance)
        options.set_capability("bstack:options", {
            "userName": DESIRED_CAPS["bstack:options"]["userName"],
            "accessKey": DESIRED_CAPS["bstack:options"]["accessKey"],
            "projectName": "API_Demo",
            "buildName": "GitHub-Actions",
            "sessionName": "API_Demo-Test",
        })
        
        # Initialize driver (Appium 2.0 recommended pattern - options parameter)
        appium_driver = webdriver.Remote(
            command_executor=APPIUM_REMOTE_URL,
            options=options
        )
        appium_driver.implicitly_wait(TIMEOUT)
        
        # ====================== BROWSERSTACK COMPATIBILITY FIX ======================
        # Critical: Replace element factory to force WebElement encapsulation
        # Fixes "dict has no attribute is_displayed" error
        from appium.webdriver.webelement import WebElement
        from selenium.webdriver.remote.webelement import WebElement as SeleniumWebElement

        def appium_element_factory(driver, resp):
            """Custom element factory to handle W3C element dict from BrowserStack"""
            # Case 1: W3C standard element dict (BrowserStack response)
            if isinstance(resp, dict) and "element-6066-11e4-a52e-28c025000000" in resp:
                return WebElement(driver, resp["element-6066-11e4-a52e-28c025000000"])
            # Case 2: Legacy element ID string
            elif isinstance(resp, str):
                return WebElement(driver, resp)
            # Case 3: Fallback to Selenium WebElement (compatibility)
            else:
                return SeleniumWebElement(driver, resp)

        # Override driver's element factory (global effect)
        appium_driver._web_element_cls = appium_element_factory
        # =============================================================================
        
        logger.info(
            f"BrowserStack driver initialized successfully | Session ID: {appium_driver.session_id}"
        )
        yield appium_driver

    except WebDriverException as e:
        logger.error(f"Driver initialization failed: {str(e)}", exc_info=True)
        raise
    finally:
        # Ensure proper driver teardown to avoid hanging sessions
        if appium_driver:
            try:
                appium_driver.quit()
                logger.info(f"BrowserStack session {appium_driver.session_id} closed successfully")
            except WebDriverException as e:
                logger.error(f"Failed to close driver session: {str(e)}", exc_info=True)

# Auto Screenshot Fixture - Failure Debugging
@pytest.fixture(scope="function", autouse=True)
def capture_failure_screenshot(driver, request):
    """
    Auto-generates screenshots for failed test cases (autouse fixture).
    Saves screenshots to dedicated directory with test name and timestamp for traceability.
    
    Args:
        driver: Initialized Appium driver instance
        request: Pytest request object (test context)
    """
    yield
    # Check if test failed during execution phase
    if hasattr(request.node, '_test_failed') and request.node._test_failed:
        try:
            screenshot_filename = (
                f"failure_{request.node.name}_{datetime.now():%Y%m%d%H%M%S}.png"
            )
            screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_filename)
            
            driver.save_screenshot(screenshot_path)
            logger.error(f"Failure screenshot saved to: {screenshot_path}")
            
        except WebDriverException as e:
            logger.warning(f"Screenshot capture failed: {str(e)}", exc_info=True)

# Pytest Hook - Failure Tracking
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook to track test failure status for screenshot automation.
    Marks test as failed only if failure occurs during test execution (call phase).
    
    Args:
        item: Pytest test item object
        call: Pytest call object (test execution context)
    """
    outcome = yield
    test_report = outcome.get_result()
    # Track failures only in the test execution phase (ignore setup/teardown failures)
    item._test_failed = (test_report.when == 'call' and test_report.failed)
