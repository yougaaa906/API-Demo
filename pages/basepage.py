# Standard library imports
import os
import time
import logging
from typing import Tuple, Optional, Any, Union
from datetime import datetime

# Third-party imports
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait as BaseWebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from appium.webdriver.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy

# Project imports
from config.config import TIMEOUT, SCREENSHOTS_DIR

# Configure logger (module-level, enterprise standard)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ====================== W3C/BrowserStack Compatibility Layer ======================
class WebDriverWait(BaseWebDriverWait):
    """
    Extended WebDriverWait with automatic dict-to-WebElement conversion
    Fixes BrowserStack's W3C-compliant element dictionary return format
    """
    def until(self, method: Any, message: str = '') -> Union[WebElement, Any]:
        result = super().until(method, message)
        if isinstance(result, dict) and "element-6066-11e4-a52e-28c025000000" in result:
            logger.debug("Converting W3C element dict to WebElement object")
            return WebElement(self._driver, result["element-6066-11e4-a52e-28c025000000"])
        return result

class BasePage:
    """
    Base Page Object Model (POM) class for mobile automation
    Core responsibilities:
    1. Provide reusable UI interaction methods (wait, click, input, swipe)
    2. Ensure cross-environment compatibility (local/emulator/BrowserStack)
    3. Implement consistent error handling and logging
    4. Maintain screenshot capture for failure debugging
    """
    logger = logging.getLogger(__name__)

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self._validate_driver()

    def _validate_driver(self) -> None:
        """
        Defensive check to ensure valid driver instance
        :raises ValueError: If driver is None or invalid
        """
        if not self.driver:
            raise ValueError("Invalid Appium driver instance - cannot initialize BasePage")
        logger.debug(f"BasePage initialized with driver session: {self.driver.session_id}")

    # ------------------------------ Original Method Names (Fully Compatible) ------------------------------
    def wait_elem_visibility(self, locator, timeout=None):
        """
        Wait until the element is visible on the screen
        :param locator: Element locator tuple (by, value)
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Visible web element object
        :raise: TimeoutException if element is not visible within timeout
        """
        timeout = timeout or TIMEOUT
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            self.logger.info(f"Waiting for element visibility: {locator_str}, timeout: {timeout}s")
            elem = self.wait.until(
                EC.visibility_of_element_located(locator)
            )
            self.logger.info(f"Element {locator_str} is visible")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Element {locator_str} not visible within {timeout}s: {str(e)}", exc_info=True)
            self.screenshot(f"visibility_timeout_{locator[1]}")
            raise TimeoutException(f"Element not found: {locator_str}, error: {str(e)}") from e

    def elem_clickable(self, locator, timeout=None):
        """
        Wait until the element is clickable
        :param locator: Element locator tuple (by, value)
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Clickable web element object
        :raise: TimeoutException if element is not clickable within timeout
        """
        timeout = timeout or TIMEOUT
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            self.logger.info(f"Waiting for element clickable: {locator_str}, timeout: {timeout}s")
            elem = self.wait.until(
                EC.element_to_be_clickable(locator)
            )
            self.logger.info(f"Element {locator_str} is clickable")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Element {locator_str} not clickable within {timeout}s: {str(e)}", exc_info=True)
            self.screenshot(f"clickable_timeout_{locator[1]}")
            raise TimeoutException(f"Element {locator_str} not clickable, error: {str(e)}") from e

    def elem_input(self, locator, text, timeout=None):
        """
        Wait for element visibility then input text
        :param locator: Element locator tuple (by, value)
        :param text: Text to be inputted into the element
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Element object after text input
        :raise: TimeoutException if element is not visible within timeout
        """
        timeout = timeout or TIMEOUT
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            self.logger.info(f"Inputting text '{text}' to element {locator_str}")
            elem = self.wait_elem_visibility(locator, timeout)
            elem.clear()
            elem.send_keys(text)
            self.logger.info(f"Text '{text}' inputted to element {locator_str} successfully")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Input element {locator_str} not found within {timeout}s: {str(e)}")
            raise TimeoutException(f"Input element {locator_str} not found, error: {str(e)}") from e

    def elem_click(self, locator, timeout=None):
        """
        Wait for element clickable then perform click action
        :param locator: Element locator tuple (by, value)
        :param timeout: Custom timeout in seconds, uses global TIMEOUT if None
        :return: Element object after click
        :raise: TimeoutException if element is not clickable within timeout
        """
        timeout = timeout or TIMEOUT
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            self.logger.info(f"Preparing to click element: {locator_str}")
            elem = self.elem_clickable(locator, timeout)
            elem.click()
            self.logger.info(f"Element {locator_str} clicked successfully")
            return elem
        except TimeoutException as e:
            self.logger.error(f"Failed to click element {locator_str}: {str(e)}")
            raise TimeoutException(f"Failed to click element {locator_str}, error: {str(e)}") from e

    # ------------------------------ Original Swipe Methods (Fully Compatible) ------------------------------
    def swipe_up(self, times=1, duration=1000):
        """
        Perform upward swipe on screen (bottom to top)
        :param times: Number of swipe iterations (default: 1)
        :param duration: Swipe duration in milliseconds (default: 1000ms)
        :raise: Exception if swipe fails after all iterations
        """
        for attempt in range(times):
            screen_size = self.driver.get_window_size()
            start_x = screen_size["width"] / 2
            start_y = screen_size["height"] * 0.8
            end_y = screen_size["height"] * 0.2
            
            try:
                self.driver.swipe(start_x, start_y, start_x, end_y, duration)
                self.logger.info(f"Swipe up attempt {attempt+1}/{times} completed")
                time.sleep(0.5)
            except Exception as e:
                self.logger.warning(f"Swipe up attempt {attempt+1} failed: {str(e)}")
                if attempt == times - 1:
                    self.screenshot()
                    raise Exception(f"Failed to perform swipe up after {times} attempts: {str(e)}") from e
                continue

    def swipe_left(self):
        """
        Perform left swipe on screen (right to left) with fixed duration (800ms)
        """
        screen_size = self.driver.get_window_size()
        start_x = screen_size["width"] * 0.8
        start_y = screen_size["height"] / 2
        end_x = screen_size["width"] * 0.2
        
        try:
            self.driver.swipe(start_x, start_y, end_x, start_y, 800)
            self.logger.info("Swipe left action completed successfully")
        except Exception as e:
            self.logger.error(f"Failed to perform swipe left: {str(e)}")
            self.screenshot()
            raise

    # ------------------------------ Original Screenshot Method (Fully Compatible) ------------------------------
    def screenshot(self, prefix: str = "error") -> str:
        """
        Capture and save screenshot to screenshots directory with timestamp
        :param prefix: Custom prefix for screenshot filename (default: "error")
        :return: Full path to saved screenshot
        :raises OSError: If screenshot directory cannot be created/written
        """
        screenshot_dir = SCREENSHOTS_DIR or os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{prefix}_{timestamp}.png"
        screenshot_path = os.path.abspath(os.path.join(screenshot_dir, filename))
        
        try:
            self.driver.save_screenshot(screenshot_path)
            self.logger.error(f"Error screenshot saved to: {screenshot_path}")
            return screenshot_path
        except (OSError, WebDriverException) as e:
            error_msg = f"Failed to capture screenshot to {screenshot_path}"
            self.logger.critical(f"{error_msg}: {str(e)}", exc_info=True)
            raise OSError(error_msg) from e

    # ------------------------------ Cleanup Method ------------------------------
    def teardown(self) -> None:
        """
        Cleanup method for page resources (enterprise pattern)
        Can be extended for additional cleanup (e.g., close modals)
        """
        logger.debug("BasePage teardown initiated")
