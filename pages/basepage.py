

# Standard library imports
import os
import time
import logging
from typing import Tuple, Optional, Any, Union  # Type hints (critical for外企规范)
from datetime import datetime  # More precise timestamp

# Third-party imports
from selenium.webdriver.remote.webdriver import WebDriver  # Type hint for driver
from selenium.webdriver.support.ui import WebDriverWait as BaseWebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from appium.webdriver.webelement import WebElement  # Appium WebElement type
from appium.webdriver.common.appiumby import AppiumBy  # Standard locator type

# Project imports
from config.config import TIMEOUT, SCREENSHOT_DIR  # Use centralized config

# Configure logger (module-level, consistent with enterprise logging standards)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ====================== W3C/BrowserStack Compatibility Layer (Enterprise Grade) ======================
class WebDriverWait(BaseWebDriverWait):
    """
    Extended WebDriverWait with automatic dict-to-WebElement conversion
    Fixes BrowserStack's W3C-compliant element dictionary return format
    """
    def until(self, method: Any, message: str = '') -> Union[WebElement, Any]:
        """
        Override until() to convert element dictionaries to WebElement objects
        :param method: Expected condition method to execute
        :param message: Error message for timeout
        :return: WebElement object (or original result if not element)
        :raises TimeoutException: If condition not met within timeout
        """
        result = super().until(method, message)
        
        # Convert BrowserStack's W3C element dict to Appium WebElement
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
    4. Maintain Screenshot capture for failure debugging
    """
    
    def __init__(self, driver: WebDriver) -> None:
        """
        Initialize BasePage with Appium driver instance
        :param driver: Appium WebDriver instance (compliant with W3C standards)
        """
        self.driver = driver
        self.wait = WebDriverWait(self.driver, TIMEOUT)  # Use compatible wait class
        self._validate_driver()  # Defensive programming check

    def _validate_driver(self) -> None:
        """
        Defensive check to ensure valid driver instance
        :raises ValueError: If driver is None or invalid
        """
        if not self.driver:
            raise ValueError("Invalid Appium driver instance - cannot initialize BasePage")
        logger.debug(f"BasePage initialized with driver session: {self.driver.session_id}")

    # ------------------------------ Core Wait Methods ------------------------------
    def wait_for_element_visibility(
        self, 
        locator: Tuple[str, str], 
        timeout: Optional[int] = None
    ) -> WebElement:
        """
        Wait for element to be visible (enterprise-grade wait method)
        Replaces hard-coded sleep statements with explicit waits
        
        :param locator: Tuple of (By strategy, locator value), e.g., (AppiumBy.ID, "com.app:id/btn")
        :param timeout: Custom timeout in seconds (defaults to global TIMEOUT)
        :return: Visible WebElement object
        :raises TimeoutException: If element not visible within timeout
        """
        timeout = timeout or TIMEOUT
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"  # Human-readable locator
        
        try:
            logger.info(f"Waiting for element visibility: {locator_str} (timeout: {timeout}s)")
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            logger.info(f"Element {locator_str} is visible")
            return element
        
        except TimeoutException as e:
            error_msg = f"Element {locator_str} not visible within {timeout}s"
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            self.capture_screenshot(f"visibility_timeout_{locator[1]}")
            raise TimeoutException(error_msg) from e

    def wait_for_element_clickable(
        self, 
        locator: Tuple[str, str], 
        timeout: Optional[int] = None
    ) -> WebElement:
        """
        Wait for element to be clickable (interactable)
        Critical for reliable UI interactions
        
        :param locator: Tuple of (By strategy, locator value)
        :param timeout: Custom timeout in seconds (defaults to global TIMEOUT)
        :return: Clickable WebElement object
        :raises TimeoutException: If element not clickable within timeout
        """
        timeout = timeout or TIMEOUT
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            logger.info(f"Waiting for element clickable: {locator_str} (timeout: {timeout}s)")
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            logger.info(f"Element {locator_str} is clickable")
            return element
        
        except TimeoutException as e:
            error_msg = f"Element {locator_str} not clickable within {timeout}s"
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            self.capture_screenshot(f"clickable_timeout_{locator[1]}")
            raise TimeoutException(error_msg) from e

    # ------------------------------ Core Interaction Methods ------------------------------
    def click_element(
        self, 
        locator: Tuple[str, str], 
        timeout: Optional[int] = None
    ) -> WebElement:
        """
        Reliable element click with pre-validation (wait for clickable first)
        
        :param locator: Tuple of (By strategy, locator value)
        :param timeout: Custom timeout in seconds (defaults to global TIMEOUT)
        :return: Clicked WebElement object
        :raises TimeoutException: If element not clickable
        :raises WebDriverException: If click action fails
        """
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            element = self.wait_for_element_clickable(locator, timeout)
            element.click()
            logger.info(f"Successfully clicked element: {locator_str}")
            return element
        
        except WebDriverException as e:
            error_msg = f"Failed to click element {locator_str}"
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            self.capture_screenshot(f"click_failure_{locator[1]}")
            raise WebDriverException(error_msg) from e

    def input_text_to_element(
        self, 
        locator: Tuple[str, str], 
        text: str, 
        timeout: Optional[int] = None, 
        clear_first: bool = True
    ) -> WebElement:
        """
        Reliable text input with pre-validation and cleanup
        
        :param locator: Tuple of (By strategy, locator value)
        :param text: Text to input into the element
        :param timeout: Custom timeout in seconds (defaults to global TIMEOUT)
        :param clear_first: Whether to clear input field before typing (default: True)
        :return: WebElement object after text input
        :raises TimeoutException: If element not visible
        :raises WebDriverException: If input action fails
        """
        locator_str = f"{locator[0].split('.')[-1]}='{locator[1]}'"
        
        try:
            logger.info(f"Inputting text to element {locator_str}: '{text}'")
            element = self.wait_for_element_visibility(locator, timeout)
            
            if clear_first:
                element.clear()
                logger.debug(f"Cleared text from element {locator_str}")
            
            element.send_keys(text)
            logger.info(f"Successfully input text to element {locator_str}")
            return element
        
        except WebDriverException as e:
            error_msg = f"Failed to input text to element {locator_str}"
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            self.capture_screenshot(f"input_failure_{locator[1]}")
            raise WebDriverException(error_msg) from e

    # ------------------------------ Swipe/Scroll Methods ------------------------------
    def swipe_up(
        self, 
        times: int = 1, 
        duration: int = 1000, 
        start_y_ratio: float = 0.8, 
        end_y_ratio: float = 0.2
    ) -> None:
        """
        Perform upward swipe (bottom to top) with configurable parameters
        Deprecated: Prefer swipe_until_element_visible for element-specific scrolling
        
        :param times: Number of swipe iterations (default: 1)
        :param duration: Swipe duration in milliseconds (default: 1000ms)
        :param start_y_ratio: Start Y position as ratio of screen height (default: 0.8)
        :param end_y_ratio: End Y position as ratio of screen height (default: 0.2)
        :raises WebDriverException: If swipe fails after all attempts
        """
        screen_size = self.driver.get_window_size()
        width = screen_size["width"]
        height = screen_size["height"]
        
        for attempt in range(1, times + 1):
            try:
                logger.info(f"Performing upward swipe (attempt {attempt}/{times})")
                self.driver.swipe(
                    start_x=width / 2,
                    start_y=height * start_y_ratio,
                    end_x=width / 2,
                    end_y=height * end_y_ratio,
                    duration=duration
                )
                time.sleep(0.5)  # Short pause for page stabilization
                
            except WebDriverException as e:
                logger.warning(f"Swipe up attempt {attempt} failed: {str(e)}")
                if attempt == times:
                    self.capture_screenshot("swipe_up_failure")
                    raise WebDriverException(f"Failed to swipe up after {times} attempts") from e

    def swipe_left(self, duration: int = 800) -> None:
        """
        Perform left swipe (right to left) with fixed positioning
        Deprecated: Prefer swipe_until_element_visible with direction parameter
        
        :param duration: Swipe duration in milliseconds (default: 800ms)
        :raises WebDriverException: If swipe action fails
        """
        screen_size = self.driver.get_window_size()
        width = screen_size["width"]
        height = screen_size["height"]
        
        try:
            logger.info("Performing left swipe")
            self.driver.swipe(
                start_x=width * 0.8,
                start_y=height / 2,
                end_x=width * 0.2,
                end_y=height / 2,
                duration=duration
            )
            logger.info("Left swipe completed successfully")
            
        except WebDriverException as e:
            error_msg = "Failed to perform left swipe"
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            self.capture_screenshot("swipe_left_failure")
            raise WebDriverException(error_msg) from e

    # ------------------------------ Debug/Utility Methods ------------------------------
    def capture_screenshot(self, prefix: str = "error") -> str:
        """
        Capture and save screenshot with unique timestamp (enterprise-grade)
        Returns screenshot path for reporting integration
        
        :param prefix: Custom prefix for screenshot filename (default: "error")
        :return: Full path to saved screenshot
        :raises OSError: If screenshot directory cannot be created/written
        """
        # Use centralized screenshot directory from config (best practice)
        screenshot_dir = SCREENSHOT_DIR or os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # Generate unique filename with precise timestamp (avoid collisions)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Millisecond precision
        filename = f"{prefix}_{timestamp}.png"
        screenshot_path = os.path.abspath(os.path.join(screenshot_dir, filename))
        
        try:
            self.driver.save_screenshot(screenshot_path)
            logger.error(f"Screenshot captured: {screenshot_path}")
            return screenshot_path
        
        except (OSError, WebDriverException) as e:
            error_msg = f"Failed to capture screenshot to {screenshot_path}"
            logger.critical(f"{error_msg}: {str(e)}", exc_info=True)
            raise OSError(error_msg) from e

    # ------------------------------ Cleanup Methods ------------------------------
    def teardown(self) -> None:
        """
        Cleanup method for page resources (enterprise pattern)
        Can be extended for additional cleanup (e.g., close modals)
        """
        logger.debug("BasePage teardown initiated")
        # Add custom cleanup logic here (e.g., dismiss popups, reset app state)
